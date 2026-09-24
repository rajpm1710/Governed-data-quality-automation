"""Synthetic procurement data quality and governance pipeline; standard library only."""
import argparse
import csv
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REQUIRED = ('invoice_id', 'vendor_id', 'invoice_date', 'amount', 'currency', 'description', 'owner_email')
EMAIL = re.compile(r'\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b')


def redact(text):
    return EMAIL.sub('[EMAIL_REDACTED]', str(text))


def assess(rows):
    seen, clean, rejected = set(), [], []
    for row in rows:
        reasons = []
        if any(not row.get(field, '').strip() for field in REQUIRED):
            reasons.append('missing_required_field')
        invoice_id = row.get('invoice_id', '').strip()
        if invoice_id in seen:
            reasons.append('duplicate_invoice_id')
        seen.add(invoice_id)
        try:
            amount = float(row.get('amount', ''))
            if amount <= 0:
                reasons.append('nonpositive_amount')
        except ValueError:
            reasons.append('invalid_amount')
            amount = 0
        try:
            datetime.strptime(row.get('invoice_date', ''), '%Y-%m-%d')
        except ValueError:
            reasons.append('invalid_invoice_date')
        if reasons:
            rejected.append({'invoice_id': invoice_id, 'reasons': reasons})
        else:
            clean.append({'invoice_id': invoice_id, 'vendor_id': row['vendor_id'],
                          'invoice_date': row['invoice_date'], 'amount': amount,
                          'currency': row['currency'], 'description': redact(row['description'])})
    totals = defaultdict(float)
    for item in clean:
        totals[item['vendor_id']] += item['amount']
    return {'metrics': {'input_rows': len(rows), 'accepted_rows': len(clean),
                        'rejected_rows': len(rejected), 'acceptance_rate': round(len(clean) / len(rows), 3) if rows else 0},
            'rejection_reasons': dict(sorted({reason: sum(reason in r['reasons'] for r in rejected)
                                               for r in rejected for reason in r['reasons']}.items())),
            'vendor_totals': dict(sorted((k, round(v, 2)) for k, v in totals.items())),
            'silver_records': clean, 'quarantine': rejected}


def triage(report):
    """Deterministic local fallback with the same shape as an LLM triage response."""
    reasons = report['rejection_reasons']
    leading = max(reasons, key=reasons.get) if reasons else None
    return {'severity': 'high' if report['metrics']['acceptance_rate'] < .8 else 'low',
            'top_issue': leading or 'none',
            'recommended_action': f'Review upstream mapping for {leading} and replay quarantined records after correction.' if leading else 'Continue monitoring.',
            'human_review_required': bool(reasons)}


def run(source, output):
    source, output = Path(source), Path(output)
    rows = list(csv.DictReader(source.open(newline='', encoding='utf-8')))
    report = assess(rows)
    report['triage'] = triage(report)
    report['lineage'] = {'source_file': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                         'transformation': 'src.pipeline.assess', 'layers': ['bronze', 'silver', 'gold']}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/synthetic_invoices.csv')
    parser.add_argument('--output', default='output/report.json')
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output)['metrics'], indent=2))
