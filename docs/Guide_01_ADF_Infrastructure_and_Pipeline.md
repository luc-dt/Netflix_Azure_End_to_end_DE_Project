# Azure Netflix DE Project — Guide 01
## ADF: Infrastructure → Linked Services → Datasets → Pipeline

> **Video reference:** The ONLY Azure End-To-End Data Engineering Project You NEED in 2025
> **Session scope:** Azure resource setup through Copy pipeline execution

---

## Architecture Overview

```
GitHub (CSVs)
     │
     ▼
Azure Data Factory ──► Bronze Container (ADLS Gen2)
                              │
                              ▼
                       Databricks (Auto Loader) ──► Silver ──► Gold (DLT)
                                                              │
                                                              ▼
                                                         SQL Warehouse + Power BI
```

**Star Schema:**
| Table | Role | Join Key |
|---|---|---|
| `netflix_titles` | Fact table | `show_id` (PK) |
| `directors` | Dimension | `show_id` |
| `cast` | Dimension | `show_id` |
| `countries` | Dimension | `show_id` |
| `category` | Dimension | `show_id` |

---

## Phase 1: Azure Infrastructure

### Step 1 — Create Resource Group
- Azure Portal → Resource Groups → Create
- Name: `RG-NetflixProject`
- Region: **Southeast Asia** *(East US blocked on Azure for Students)*
- Click: Review + Create

> **Why a Resource Group?** It's a logical container — delete one RG and all services inside are cleaned up. No orphaned billing.

### Step 2 — Create Storage Account (ADLS Gen2)
- Search: Storage Accounts → Create
- Resource Group: `RG-NetflixProject`
- Name: `nextflixprojectdtl` *(must be lowercase, no hyphens — becomes a DNS endpoint)*
- Region: Southeast Asia
- **Advanced tab → Enable hierarchical namespace** ✅ ← this is what makes it ADLS Gen2
- Click: Review + Create

> **Why hierarchical namespace?** Enables real folder/directory semantics needed by Spark. Without it, it's just blob storage.

### Step 3 — Create Containers
Inside the storage account → Containers → + Container

| Container | Layer | Purpose |
|---|---|---|
| `raw` | Landing zone | Raw files as-is |
| `bronze` | Bronze | ADF copy destination |
| `silver` | Silver | PySpark transforms output |
| `gold` | Gold | DLT output |

### Step 4 — Create Azure Data Factory
- Search: Data Factory → Create
- Name: `adf-netflix-luc-dt`
- Region: **Southeast Asia**
- Click: Review + Create → then **Launch Studio**

---

## Phase 2: Linked Services

> **What is a Linked Service?** A connection string with credentials — it tells ADF *how to reach* an external system (driver + auth layer).

### Step 5 — GitHub Linked Service (Source)
- ADF Studio → Manage → Linked Services → New
- Search: **HTTP**
- Fill in:

| Field | Value |
|---|---|
| Name | `github_con` |
| Base URL | `https://raw.githubusercontent.com/` |
| Authentication type | **Anonymous** |

- Click: Test Connection → **Create**

> **Why raw.githubusercontent.com?** This is GitHub's raw content CDN — the domain you see when you click "Raw" on any GitHub file. Regular `github.com` URLs return HTML, not the file content itself.

### Step 6 — ADLS Gen2 Linked Service (Sink)
- Manage → Linked Services → New
- Search: **Azure Data Lake Storage Gen2**
- Fill in:

| Field | Value |
|---|---|
| Name | `datalake_con` |
| Authentication type | **Account Key** |
| Storage account | `nextflixprojectdtl` |

- Click: Test Connection → **Create**

> **Production note:** In real teams, use **Managed Identity** instead of Account Key — Azure handles auth automatically between services, no credentials stored in ADF.

---

## Phase 3: Datasets

> **What is a Dataset?** Sits on top of a Linked Service — says "use this connection, point to this specific file or folder."

### Step 7 — Source Dataset (GitHub CSVs)
- Author → Datasets → + → New Dataset
- Search: **HTTP** → Select **DelimitedText** → Continue
- Fill in:

| Field | Value |
|---|---|
| Name | `ds_github_raw` |
| Linked Service | `github_con` |

- Click **Parameters tab** → + New:

| Name | Type |
|---|---|
| `file_name` | String |

- Click **Connection tab** → Relative URL:
```
@{concat('anshlambagit/Netflix_Azure_Data_Engineering_Project/refs/heads/main/RawData_AND_Notebooks/', dataset().file_name, '.csv')}
```
- First row as header: ✅
- Click: **Publish All**

> **Why parameterize?** One dataset handles all 5 CSVs dynamically instead of 5 hardcoded datasets. `dataset().file_name` gets injected at runtime by the ForEach loop.

### Step 8 — Sink Dataset (ADLS Gen2 Bronze)
- Author → Datasets → + → New Dataset
- Search: **Azure Data Lake Storage Gen2** → Select **DelimitedText** → Continue
- Fill in:

| Field | Value |
|---|---|
| Name | `ds_adls_bronze` |
| Linked Service | `datalake_con` |
| Container | `bronze` |
| File path | *(leave blank — pipeline sets filename)* |
| First row as header | ✅ |

- Click: **Publish All**

---

## Phase 4: Pipeline — ForEach + Copy Activity

> **Mental model:**
> ```python
> files = ["netflix_titles", "netflix_cast", "netflix_category",
>          "netflix_countries", "netflix_directors"]
> for file_name in files:
>     copy_from_github_to_bronze(file_name)
> ```
> This is exactly what the ForEach + Copy Activity does.

### Step 9 — Create Pipeline
- Author → Pipelines → + → New Pipeline
- Name: `pl_ingest_github_to_bronze`

### Step 10 — Add ForEach Activity
- Activities panel → search **ForEach** → drag to canvas
- Name: `fe_loop_files`
- **Settings tab** → Items:
```json
["netflix_titles", "netflix_cast", "netflix_category", "netflix_countries", "netflix_directors"]
```

### Step 11 — Add Copy Activity inside ForEach
- Double-click the ForEach activity → inner canvas opens
- Drag **Copy Data** onto inner canvas
- Name: `cp_github_to_bronze`

**Source tab:**
| Field | Value |
|---|---|
| Dataset | `ds_github_raw` |
| `file_name` parameter | `@{item()}` |

**Sink tab:**
| Field | Value |
|---|---|
| Dataset | `ds_adls_bronze` |
| File name | `@{concat(item(), '.csv')}` |

> **What is `@{item()}`?** The current value from the ForEach loop — equivalent to `file_name` in the Python loop above.

### Step 12 — Publish & Run
- Click **Publish All**
- Click **Add Trigger** → **Trigger Now**
- Monitor → **Pipeline Runs** → watch 5 copy activities run

---

## Phase 5: Verify ✅

- Azure Portal → Storage Account `nextflixprojectdtl`
- Containers → `bronze`
- Confirm 5 files landed:
  - `netflix_titles.csv`
  - `netflix_cast.csv`
  - `netflix_category.csv`
  - `netflix_countries.csv`
  - `netflix_directors.csv`

---

## Files in Source Repo
```
anshlambagit/Netflix_Azure_Data_Engineering_Project
└── RawData_AND_Notebooks/
    ├── netflix_titles.csv
    ├── netflix_cast.csv
    ├── netflix_category.csv
    ├── netflix_countries.csv
    └── netflix_directors.csv
```

---

## Next Session — Guide 02
**Topic:** Databricks Auto Loader (Bronze → Silver incremental ingestion)

1. Create Databricks workspace (Southeast Asia)
2. Create cluster (auto-terminating)
3. Mount ADLS Gen2 to Databricks
4. Write Auto Loader notebook — incrementally read from Bronze
5. Parameterize the notebook
6. Orchestrate with Databricks Workflows (ForEach equivalent in Databricks)
