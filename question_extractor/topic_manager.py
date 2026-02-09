import json
import os
from pathlib import Path
from typing import List, Dict, Optional

class TopicManager:
    """Manages topic configuration and filtering for ICSE syllabus."""
    
    def __init__(self, profile: str = "class_10", config_path: str = None):
        """
        Initialize with topic configuration.
        
        Args:
            profile: Profile name (e.g., "class_10", "class_8")
            config_path: Explicit path to config file (overrides profile)
        """
        if config_path is None:
            # Assumes configs is in the same directory as this file or parent
            # Adjusting path to match original structure
            base_dir = Path(__file__).parent
            config_path = base_dir / "configs" / f"{profile}.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self._all_topics_cache = None
        self._enabled_topics_cache = None
    
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            # Fallback for backward compatibility if file exists in root of package
            old_path = Path(__file__).parent / "topics_config.json"
            if old_path.exists():
                print(f"Warning: Config not found at {self.config_path}, falling back to topics_config.json")
                with open(old_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                
            raise FileNotFoundError(
                f"Topic configuration not found: {self.config_path}\n"
                f"Please ensure configs/{self.config_path.name} exists."
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_syllabus_info(self) -> dict:
        """Get syllabus metadata."""
        return self.config.get("syllabus_info", {})
    
    def get_all_units(self) -> Dict[str, dict]:
        """Get all units in the syllabus."""
        return self.config.get("units", {})
    
    def get_enabled_topics(self) -> Dict[str, dict]:
        """Get all topics that are enabled across all units."""
        if self._enabled_topics_cache is not None:
            return self._enabled_topics_cache

        enabled = {}
        units = self.config.get("units", {})
        
        for unit_key, unit_data in units.items():
            if not unit_data.get("enabled", True):
                continue
            
            topics = unit_data.get("topics", {})
            for topic_key, topic_data in topics.items():
                if topic_data.get("enabled", True):
                    # Add unit info to topic
                    topic_with_unit = topic_data.copy()
                    topic_with_unit["unit"] = unit_data.get("unit_name", unit_key)
                    topic_with_unit["unit_key"] = unit_key
                    enabled[topic_key] = topic_with_unit
        
        self._enabled_topics_cache = enabled
        return enabled
    
    def get_all_topics(self) -> Dict[str, dict]:
        """Get all topics regardless of enabled status."""
        if self._all_topics_cache is not None:
            return self._all_topics_cache

        all_topics = {}
        units = self.config.get("units", {})
        
        for unit_key, unit_data in units.items():
            topics = unit_data.get("topics", {})
            for topic_key, topic_data in topics.items():
                topic_with_unit = topic_data.copy()
                topic_with_unit["unit"] = unit_data.get("unit_name", unit_key)
                topic_with_unit["unit_key"] = unit_key
                all_topics[topic_key] = topic_with_unit
        
        self._all_topics_cache = all_topics
        return all_topics
    
    def get_topic_names(self, enabled_only: bool = True) -> List[str]:
        """Get list of topic names."""
        if enabled_only:
            return list(self.get_enabled_topics().keys())
        return list(self.get_all_topics().keys())
    
    def get_topic_keywords(self, topic_name: str) -> List[str]:
        """Get keywords for a specific topic."""
        topics = self.get_all_topics()
        if topic_name in topics:
            return topics[topic_name].get("keywords", [])
        return []
    
    def get_topic_by_name(self, topic_name: str) -> Optional[dict]:
        """Get full topic data by name."""
        topics = self.get_all_topics()
        return topics.get(topic_name)
    
    def enable_topic(self, topic_name: str) -> bool:
        """Enable a topic in the configuration."""
        units = self.config.get("units", {})
        for unit_data in units.values():
            topics = unit_data.get("topics", {})
            if topic_name in topics:
                topics[topic_name]["enabled"] = True
                self._all_topics_cache = None
                self._enabled_topics_cache = None
                return True
        return False
    
    def disable_topic(self, topic_name: str) -> bool:
        """Disable a topic in the configuration."""
        units = self.config.get("units", {})
        for unit_data in units.values():
            topics = unit_data.get("topics", {})
            if topic_name in topics:
                topics[topic_name]["enabled"] = False
                self._all_topics_cache = None
                self._enabled_topics_cache = None
                return True
        return False
    
    def save_config(self):
        """Save current configuration back to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def get_extraction_settings(self) -> dict:
        """Get extraction settings from config."""
        return self.config.get("extraction_settings", {
            "include_marks": True,
            "include_question_number": True,
            "include_sub_parts": True,
            "output_format": "txt"
        })
