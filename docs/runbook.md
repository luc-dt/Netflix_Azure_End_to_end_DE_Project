# Netflix Azure Lakehouse Runbook

This runbook makes the portfolio project reproducible and explains how to promote it from a demo into a production-style workflow.

## Project Status

The original Azure and Databricks resources for this portfolio project have been deleted to avoid ongoing cost. Use this runbook as a rebuild guide if you want to recreate the environment in a new Azure subscription or Databricks workspace.

## 1. Prerequisites

- Azure subscription with permission to create Resource Groups, Storage Accounts, Data Factory, and Databricks workspaces.
- ADLS Gen2 storage account with hierarchical namespace enabled.
- Azure Databricks Premium workspace for Unity Catalog.
- Power BI Desktop for dashboard development.
- GitHub repository connected to Databricks Repos or a CI/CD deployment workflow.

## 2. Expected Azure Resources

| Resource | Purpose |
| --- | --- |
| ADLS Gen2 containers: `raw`, `bronze`, `silver`, `gold` | Separate operational and curated data zones. |
| Azure Data Factory | Parameterized ingestion of lookup CSV files from GitHub into ADLS. |
| Azure Databricks workspace | Auto Loader ingestion, PySpark transformations, Delta tables, and workflows. |
| Unity Catalog metastore | Centralized governance, table discovery, and SQL access. |
| Databricks SQL Warehouse | Serving Gold tables to Power BI. |
| Power BI report | Business dashboard for catalog composition, ratings, release trends, and genres. |

## 3. Configuration Pattern

Use `config/dev.yml` as the source of truth for environment-specific values:

- storage account name,
- container names,
- checkpoint prefix,
- Unity Catalog catalog/schema names,
- lookup dataset metadata,
- required quality columns,
- valid domain values.

In Databricks Workflows, pass these values as job parameters or widgets instead of editing notebook code for each environment.

## 4. Execution Order

1. Run `01_Autoloader.ipynb` to incrementally ingest `netflix_titles` from Raw into Bronze Delta.
2. Run `03_Lookup_Ingestion.ipynb` to publish lookup metadata as Databricks task values.
3. Run `02_Silver_Titles.ipynb` once per lookup dataset using workflow parameters.
4. Run `04_Silver_Transformation.ipynb` to clean and validate the main titles dataset.
5. Run `05_Gold_Notebook.ipynb` to build content, rating, and release-year aggregates.
6. Run `05_Gold_Top_Geners.ipynb` to build the genre distribution table.
7. Refresh the Power BI report from the Databricks SQL Warehouse.

## 5. Data Quality Gates

Minimum gates before publishing Gold tables:

- Silver title table is not empty.
- `show_id` is unique in the Silver title table.
- Required columns have no null values.
- Lookup Silver tables are deduplicated by their natural keys.
- Gold tables return at least one row.
- Gold table counts reconcile with Silver source counts where applicable.

## 6. Production Hardening Backlog

- Replace full Silver overwrite with Delta `MERGE` keyed by `show_id`.
- Store checkpoints in a dedicated operational prefix, not inside curated data paths.
- Add malformed-record quarantine paths for Auto Loader and lookup ingestion.
- Add workflow retry policies, alerts, and run-level audit tables.
- Deploy notebooks/jobs with Databricks Asset Bundles.
- Add Power BI refresh ownership and service-principal documentation.
