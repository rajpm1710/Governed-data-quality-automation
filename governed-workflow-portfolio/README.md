# Governed workflow automation for cloud data quality

A portfolio demonstration connecting **Python data validation**, **n8n orchestration**, **prompt design**, **privacy controls**, and a **cloud lakehouse deployment plan**. All records are synthetic. The executable demo requires Python 3.11+ and no API keys.

## What it does

1. Bronze: ingest synthetic invoice CSV and record its SHA-256 fingerprint.
2. Silver: validate required fields, dates, amounts, and unique invoice IDs; quarantine invalid records and redact email addresses in free text.
3. Gold: compute vendor totals and acceptance metrics.
4. Triage: produce a deterministic, reviewable recommendation. The Kaggle notebook also shows a constrained LLM prompt template; it makes **no LLM API call**.
5. Orchestrate: optional n8n schedule executes the local Python pipeline.

```bash
python -m src.pipeline
python -m unittest discover -s tests -v
```

The report is written to `output/report.json` (ignored by Git). The report intentionally contains no owner email or raw rejected source records. Quarantine output includes invoice IDs and reason codes only.

## Kaggle

Upload `notebooks/governed_invoice_quality_kaggle.ipynb` as a new Kaggle notebook. Select the Python environment and run all cells; Internet and GPU are unnecessary. The notebook embeds the synthetic data, so no Kaggle dataset attachment is needed. Add a description of the governance checks and publish after reviewing its outputs. The repository and Kaggle notebook are independently runnable demonstrations of the same business flow.

## GitHub

Create a repository and upload this folder, or run:

```bash
git init
git add .
git commit -m "Build governed invoice quality workflow"
git branch -M main
git remote add origin YOUR_REPOSITORY_URL
git push -u origin main
```

GitHub Actions runs unit checks and the pipeline on every push or pull request. Replace `YOUR_REPOSITORY_URL` with your own repository URL. Do not commit real invoices, credentials, or generated reports.

## n8n

Import `n8n/daily_quality_workflow.json`, change `/ABSOLUTE/PATH/TO/governed-workflow-portfolio` to the working directory in the n8n **runtime**, test manually, then activate the schedule. The Execute Command node runs in the n8n runtime and may be unavailable or disabled on hosted plans; in that case use an authenticated webhook to trigger a separately hosted job. This workflow does not send external notifications or use credentials.

## Cloud extension (architecture design, not deployed)

| Local demonstration | Azure deployment mapping |
| --- | --- |
| CSV input | ADLS Gen2 landing zone |
| Python checks and quarantine | Databricks job, Delta bronze/silver tables |
| Vendor totals | Delta gold table or SQL analytics layer |
| n8n daily trigger | n8n webhook to authenticated job endpoint or Azure scheduler |
| Local JSON report | Governed metrics table and monitored alert |
| Fingerprint and reason codes | Catalog lineage, access policies, and retention controls |

A deployment needs cloud resources, secrets management, least privilege, monitoring, and a retention policy. The local artifact does not claim Databricks or n8n was deployed.

## Interview explanation

“I built a public, synthetic invoice quality workflow: Python validates and redacts records, isolates failures, produces governed aggregates, and creates a reviewable incident summary. I added a Kaggle walkthrough, a GitHub CI check, and an optional n8n schedule. I documented how the same stages map to an Azure Databricks lakehouse.”
