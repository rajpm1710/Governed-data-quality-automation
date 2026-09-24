import csv
import unittest
from pathlib import Path
from src.pipeline import assess, triage


class PipelineTests(unittest.TestCase):
    def test_governance_rules_and_redaction(self):
        with Path('data/synthetic_invoices.csv').open(newline='') as handle:
            report = assess(list(csv.DictReader(handle)))
        self.assertEqual(report['metrics']['accepted_rows'], 3)
        self.assertEqual(report['rejection_reasons']['duplicate_invoice_id'], 1)
        self.assertNotIn('alice@example.test', str(report))
        self.assertEqual(report['vendor_totals']['V-10'], 1250.0)
        self.assertTrue(triage(report)['human_review_required'])


if __name__ == '__main__':
    unittest.main()
