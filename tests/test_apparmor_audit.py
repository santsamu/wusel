"""Audit filtering must never hide a current profile's denial."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.check_apparmor import profile_denials


class AppArmorAuditTests(unittest.TestCase):
    def test_filters_by_kernel_time_and_exact_profile(self):
        lines = [
            '[ 9.5] audit: apparmor="DENIED" profile="local_wusel" old',
            '[10.5] audit: apparmor="DENIED" profile="other_wusel" unrelated',
            '[11.5] audit: apparmor="ALLOWED" profile="local_wusel" allowed',
            '<5>[12.5] audit: apparmor="DENIED" profile="local_wusel" current',
        ]
        self.assertEqual(profile_denials('\n'.join(lines), 'local_wusel', 10), [lines[-1]])

    def test_unparseable_relevant_denial_is_an_error(self):
        with self.assertRaises(ValueError):
            profile_denials('audit: apparmor="DENIED" profile="local_wusel"', 'local_wusel', 10)


if __name__ == '__main__':
    unittest.main()
