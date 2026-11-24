"""Checks for the privacy and date-boundary rules in public telemetry."""
import unittest
from update_activity import public_projects


def entry(owner, name, private=False, nodes=None, truncated=False):
    return {'repository': {'name': name, 'nameWithOwner': f'{owner}/{name}',
                           'url': f'https://github.com/{owner}/{name}', 'isPrivate': private},
            'contributions': {'nodes': nodes or [], 'pageInfo': {'hasNextPage': truncated}}}


class ActivityRules(unittest.TestCase):
    def test_private_and_maintenance_repositories_are_excluded(self):
        nodes = [{'occurredAt': '2026-11-20T00:00:00Z', 'commitCount': 4}]
        items = [entry('ishaans04','secret',True,nodes), entry('ishaans04','ishaans04',False,nodes),
                 entry('ishaans04','public',False,nodes)]
        result = public_projects(items, '2026-11-01', '2026-11-25')
        self.assertEqual([r['name'] for r in result], ['public'])

    def test_utc_date_bounds_and_same_named_repositories(self):
        nodes = [{'occurredAt':'2026-10-31T23:59:00Z','commitCount':9},
                 {'occurredAt':'2026-11-01T00:00:00Z','commitCount':2},
                 {'occurredAt':'2026-11-25T23:59:00Z','commitCount':3},
                 {'occurredAt':'2026-11-26T00:00:00Z','commitCount':8}]
        result = public_projects([entry('ishaans04','Ratchet',False,nodes),
                                  entry('another-owner','Ratchet',False,nodes)], '2026-11-01','2026-11-25')
        self.assertEqual(len(result),2)
        self.assertEqual({r['full_name'] for r in result}, {'ishaans04/Ratchet','another-owner/Ratchet'})
        self.assertTrue(all(r['commits']==5 for r in result))

    def test_incomplete_pages_do_not_replace_valid_data(self):
        with self.assertRaises(ValueError):
            public_projects([entry('ishaans04','public',truncated=True)],'2026-11-01','2026-11-25')


if __name__ == '__main__':
    unittest.main()
