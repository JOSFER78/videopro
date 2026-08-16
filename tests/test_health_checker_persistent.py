import os
import sys
import time
import unittest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.core.providers import health_checker

class TestHealthCheckerPersistent(unittest.TestCase):
    def test_fast_cached_matrix_no_network(self):
        t0 = time.time()
        matrix = health_checker.get_all_providers_matrix(force=False)
        elapsed_ms = (time.time() - t0) * 1000
        self.assertIsInstance(matrix, dict)
        self.assertGreater(len(matrix), 0)
        # Must be ultra-fast (local memory or disk read < 100ms)
        self.assertLess(elapsed_ms, 100, f"Expected < 100ms, got {elapsed_ms}ms")

    def test_health_meta_structure(self):
        meta = health_checker.get_health_meta()
        self.assertIn("last_checked_str", meta)
        self.assertIn("time_ago", meta)
        self.assertIn("total", meta)
        self.assertIn("active", meta)
        self.assertGreater(meta["total"], 0)

    def test_persistence_file_created(self):
        self.assertTrue(os.path.exists(health_checker.HEALTH_STORAGE_FILE))

if __name__ == "__main__":
    unittest.main()
