import unittest
import sys
import io

def run_tests():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add tests
    try:
        from question_extractor.test_pdf_processor import TestPDFProcessor
        suite.addTest(loader.loadTestsFromTestCase(TestPDFProcessor))
    except ImportError as e:
        print(f"Failed to import TestPDFProcessor: {e}")

    try:
        # Dynamic import for TestQuestionBankParser and TestBasePaperGenerator
        # Assuming test_paper_generator.py is in question_extractor/
        sys.path.append(os.getcwd())
        from question_extractor.test_paper_generator import TestQuestionBankParser, TestBasePaperGenerator
        suite.addTest(loader.loadTestsFromTestCase(TestQuestionBankParser))
        suite.addTest(loader.loadTestsFromTestCase(TestBasePaperGenerator))
    except ImportError as e:
        print(f"Failed to import paper generator tests: {e}")

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    if not result.wasSuccessful():
        sys.exit(1)

if __name__ == "__main__":
    import os
    run_tests()
