"""Checks for the Stack hive list."""
import unittest

from build_stack import GLYPHS, ICONS, STACK, techs


class StackHive(unittest.TestCase):
    def test_every_technology_appears_once(self):
        names = techs()
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(len(names), 27)

    def test_every_icon_resolves(self):
        for _, items in STACK:
            for name, key in items:
                ok = key[6:] in GLYPHS if key.startswith('glyph:') else key in ICONS
                self.assertTrue(ok, f'{name}: no icon {key}')


if __name__ == '__main__':
    unittest.main()
