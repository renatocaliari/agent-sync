
import unittest
import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agent_sync.publish.local_source import _is_valid_skill_name as local_val
from agent_sync.publish.external_source import _is_valid_skill_name as external_val

class TestSkillValidationSentinel(unittest.TestCase):
    def test_newline_injection_local(self):
        self.assertTrue(local_val("valid-skill-123"))
        self.assertFalse(local_val("invalid-skill\n"))
        self.assertFalse(local_val("invalid\nskill"))
        self.assertFalse(local_val("\ninvalid"))

    def test_newline_injection_external(self):
        self.assertTrue(external_val("valid-skill-123"))
        self.assertFalse(external_val("invalid-skill\n"))
        self.assertFalse(external_val("invalid\nskill"))
        self.assertFalse(external_val("\ninvalid"))

if __name__ == '__main__':
    unittest.main()
