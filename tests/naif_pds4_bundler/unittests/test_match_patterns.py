"""Unit tests for pattern matching."""
import os
import unittest
from unittest import TestCase

from pds.naif_pds4_bundler.utils import match_patterns


class TestMatchPatterns(TestCase):
    """Test family for the match_patterns utils function."""

    @classmethod
    def setUpClass(cls):
        """Constructor.

        Chose the appropriate working directory.

        Method that will be executed once for this test case class.
        It will execute before all tests methods.
        """
        print(f"NPB - Unit Tests - {cls.__name__}")

        os.chdir(os.path.dirname(__file__))

    def setUp(self):
        """Setup Test.

        This method will be executed before each test function.
        """
        unittest.TestCase.setUp(self)
        print(f"    * {self._testMethodName}")

    def tearDown(self):
        """Clean-up Test.

        This method will be executed after each test function.
        """
        unittest.TestCase.tearDown(self)

    def test_match_patterns_basic(self):
        """Test match_patterns utils function."""
        name_w_pattern = "insight_$YEAR_v$VERSION.tm"
        name = "insight_2021_v02.tm"
        patterns = [
            {"@length": "2", "#text": "VERSION"},
            {"@length": "4", "#text": "YEAR"},
        ]

        values = match_patterns(name, name_w_pattern, patterns)

        assert values == {"YEAR": "2021", "VERSION": "02"}

        name_w_pattern = "insight_$YEAR_v$VERSION.tm"
        name = "insight_2021_v02.tm"
        patterns = [{"@length": "2", "#text": "VERSION"}]

        with self.assertRaises(RuntimeError):
            () = match_patterns(name, name_w_pattern, patterns)

        name_w_pattern = "insight_$YER_v$VERSION.tm"
        name = "insight_2021_v02.tm"
        patterns = [
            {"@length": "2", "#text": "VERSION"},
            {"@length": "4", "#text": "YEAR"},
        ]

        with self.assertRaises(RuntimeError):
            () = match_patterns(name, name_w_pattern, patterns)

        name_w_pattern = "insight_$YEAR_v$VERSION.tm"
        name = "insight_2021_v02.tm"
        patterns = [
            {"@length": "2", "#text": "VERSION"},
            {"@length": "4", "#text": "YAR"},
        ]

        with self.assertRaises(RuntimeError):
            () = match_patterns(name, name_w_pattern, patterns)

        name_w_pattern = "insight_$YEAR_v$VERSION.tm"
        name = "insight_2021_v02.tm"
        patterns = [
            {"@length": "2", "#text": "VERSION"},
            {"@length": "10", "#text": "YEAR"},
        ]

        with self.assertRaises(RuntimeError):
            () = match_patterns(name, name_w_pattern, patterns)


if __name__ == "__main__":
    unittest.main()
