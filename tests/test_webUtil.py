#!/usr/bin/env python2.7

import unittest
import reflect_web as test
from testUtil import message

class Test_reflect(unittest.TestCase):

    def test_getProjMajorWhenNoMinor(self):
        """Function should echo a string when no / is present."""
        correct = "tester"
        attempt = test.getProjMajor(correct)
        self.assertTrue(
            attempt == correct,
            message(attempt, correct)
        )

    def test_getProjMinorWhenNoMinor(self):
        """Function should return None."""
        correct = None
        testMapId = "tester"
        attempt = test.getProjMinor(testMapId)
        self.assertTrue(
            attempt is correct,
            message(attempt, correct)
        )

    def test_mapIdDecomposition(self):
        """Function should return both a major and minor correctly."""
        testMapId = "this/test"
        correct = ["this", "test"]
        attempt = \
            test.getProjMajor(testMapId), test.getProjMinor(testMapId)
        self.assertTrue(
            attempt[0] == correct[0] and attempt[1] == correct[1],
            message(attempt, correct)
        )

if __name__ == '__main__':
    unittest.main()
