"""Checks for the arithmetic behind the Education panel."""
import unittest
from datetime import date

from build_record import duration, enrolment, gpa4


class RecordMaths(unittest.TestCase):
    def test_cgpa_converts_linearly_to_four_point_scale(self):
        self.assertEqual(gpa4(8.5), 3.4)
        self.assertEqual(gpa4(10), 4.0)

    def test_time_enrolled_and_year_of_study(self):
        self.assertEqual(enrolment(date(2026, 11, 25))[:2], (27, 3))
        self.assertEqual(enrolment(date(2024, 8, 1))[:2], (0, 1))
        self.assertEqual(enrolment(date(2025, 7, 31))[:2], (11, 1))
        self.assertEqual(enrolment(date(2025, 8, 1))[:2], (12, 2))

    def test_progress_is_clamped_after_graduation(self):
        months, year, share = enrolment(date(2030, 1, 1))
        self.assertEqual((year, share), (4, 1.0))

    def test_duration_reads_naturally(self):
        self.assertEqual(duration(27), '2 YEARS, 3 MONTHS')
        self.assertEqual(duration(13), '1 YEAR, 1 MONTH')
        self.assertEqual(duration(24), '2 YEARS')
        self.assertEqual(duration(0), '0 MONTHS')


if __name__ == '__main__':
    unittest.main()
