#!/usr/bin/env python3
import unittest
import sys
from test_refactored import TestTools

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTools)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)