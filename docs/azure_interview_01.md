# Azure Netflix DE Project — Interview Prep
## Guide 01: Infrastructure, ADF, Linked Services, Datasets, Pipelines

> Format: Q → Your Answer → Depth (likely follow-up)
> Build your answers in your own words. The model answers here are a starting point.

---

## Topic 1: Azure Resource Architecture

**Q1: Why do you put all your Azure resources in one Resource Group?**

A: A Resource Group is a logical container in Azure. By grouping all project resources (ADF, Storage, Databricks) under `RG-NetflixProject`, I can manage their lifecycle together — when the project is done, I delete one RG and everything is cleaned up. No orphaned resources running in the background.

Depth → *"What happens if you put resources in different Resource Groups?"*
→ You can still connect them across RGs, but lifecycle management becomes fragmented. You'd need to track and delete each service individually.

---

**Q2: What is ADLS Gen2, and how is it different from regular Azure Blob Storage?**

A: ADLS Gen2 is Azure Blob Storage with **hierarchical namespace** enabled. This one setting enables real folder/directory semantics — proper paths like `/bronze/2024/01/file.csv` — rather than flat key-value object storage. This matters for:
- Spark, which expects filesystem-style paths
- Partitioned data reads (reading a specific folder, not scanning all objects)
- Atomic rename operations needed for ACID transactions

Depth → *"Could you use regular Blob Storage for this project?"*
→ Technically yes for simple storage, but Databricks Auto Loader and Delta Lake perform significantly better on ADLS Gen2 due to the hierarchical namespace.

---

**Q3: Why did you deploy to Southeast Asia instead of East US?**

A: Azure for Students subscription has regional restrictions — East US was blocked. Southeast Asia was available and is also geographically closest to my location in Ho Chi Minh City, giving lower latency. Importantly, I kept all services (ADF, Storage, Databricks) in the same region to avoid cross-region data transfer costs and latency.

Depth → *"What is the risk of having ADF in one region and your storage in another?"*
→ Cross-region egress costs — you pay for data transferred between regions. Also higher latency for each read/write operation.

---

**Q4: Why must Azure storage account names be lowercase with no hyphens and max 24 characters?**

A: Because the storage account name becomes a DNS hostname:
```
https://nextflixprojectdtl.dfs.core.windows.net
```
DNS labels must be lowercase (DNS is case-insensitive, Azure enforces lowercase to avoid collisions), must not contain special characters that break URL parsing, and must be globally unique across all Azure accounts — the 24-character limit helps enforce uniqueness.

Depth → *"Where else in cloud platforms do you see this same naming constraint?"*
→ AWS S3 bucket names, GCS bucket names — same reason: the bucket name is embedded in a URL/DNS endpoint.

---

## Topic 2: ADF Linked Services

**Q5: What is a Linked Service in ADF?**

A: A Linked Service is a connection definition — it stores the endpoint and authentication details needed to connect to an external system. Think of it as the "driver + credentials" layer. Every dataset and copy activity needs a Linked Service underneath it to know where to connect.

Depth → *"If you change the password of your storage account, what happens to your Linked Service?"*
→ If using Account Key, the Linked Service breaks immediately — you must update the key in ADF. If using Managed Identity, nothing breaks — Azure handles rotation automatically. This is why Managed Identity is preferred in production.

---

**Q6: Why did you use an HTTP Linked Service to connect to GitHub instead of a GitHub connector?**

A: The CSV files are in a **public** GitHub repo, so they're accessible via raw HTTP without authentication. ADF's HTTP connector connects to `https://raw.githubusercontent.com/` — the CDN that serves raw file content. A GitHub API connector would be needed for private repos or metadata operations.

Depth → *"What would change if the repo were private?"*
→ You'd need a GitHub Personal Access Token (PAT). The Linked Service authentication type changes from Anonymous to Basic/Token, and you store the PAT in Azure Key Vault rather than directly in ADF.

---

**Q7: Account Key vs Managed Identity for ADLS Gen2 — what's the difference?**

A: 
- **Account Key**: A storage credential stored directly in ADF. Simple to set up, but if the key leaks, your entire storage account is exposed. Must be manually rotated.
- **Managed Identity**: Azure automatically handles authentication between services — ADF gets an identity token from Azure AD without any stored credentials. No key to leak, no rotation needed.

In production: Managed Identity is always preferred. Account Key is acceptable for learning projects.

Depth → *"How do you grant ADF access to the storage account when using Managed Identity?"*
→ You assign the ADF's managed identity the **Storage Blob Data Contributor** role on the storage account via Azure RBAC (Role-Based Access Control).

---

## Topic 3: Datasets and Parameterization

**Q8: What is a Dataset in ADF, and how does it relate to a Linked Service?**

A: A Dataset defines *what* data and *where* — it points a Linked Service to a specific file, folder, table, or pattern. The Linked Service provides the connection; the Dataset uses that connection to reference actual data. You can't have a Dataset without a Linked Service underneath it.

Depth → *"Can multiple datasets share the same Linked Service?"*
→ Yes — that's the point. One `datalake_con` Linked Service can back many datasets pointing to different containers or paths.

---

**Q9: Why did you parameterize the source dataset instead of creating 5 separate datasets?**

A: The 5 CSV files share the same connection (GitHub HTTP) and the same path structure — only the filename differs. A parameterized dataset with a `file_name` parameter means:
- One dataset object to maintain
- No copy-paste errors across 5 configurations
- The ForEach loop can pass each filename at runtime
- Adding a 6th file requires zero dataset changes

Depth → *"When would you NOT use a parameterized dataset?"*
→ When the source files have different schemas, connections, or formats — then they genuinely need separate dataset configurations.

---

## Topic 4: Pipeline Design

**Q10: Explain what the ForEach + Copy Activity pattern does in this pipeline.**

A: ForEach is ADF's loop construct — it takes a list of items and executes its inner activities once per item. In this pipeline:
1. ForEach receives the list: `["netflix_titles", "netflix_cast", ...]`
2. For each item, it runs one Copy Activity
3. The Copy Activity passes `@{item()}` as the `file_name` parameter to the source dataset
4. ADF constructs the full URL, reads the CSV from GitHub, writes it to the Bronze container

Conceptually identical to a Python `for` loop calling a function per filename.

Depth → *"What does `@{item()}` mean in ADF expression syntax?"*
→ `item()` is the built-in ADF function that returns the current element from the ForEach loop iteration. The `@{}` wraps it in ADF's expression language.

---

**Q11: What is the difference between a static notebook and a parameterized notebook in Databricks?**

A: A static notebook has hardcoded values — one specific table name, one specific path, one specific date. A parameterized notebook accepts input parameters (like `file_name`, `layer`, `run_date`) injected at runtime by Databricks Workflows or ADF. This means one notebook can process any table by passing different parameters — the same logic, different data. In real teams, static notebooks are considered an anti-pattern because they don't scale.

Depth → *"How do you pass parameters into a Databricks notebook from a Databricks Workflow?"*
→ In the Workflow job configuration, under the Task settings, you define Widget parameters. Inside the notebook, you read them with `dbutils.widgets.get("param_name")`.

---

## Topic 5: Data Quality

**Q12: What data quality issues did you find in the Netflix dataset, and how did you handle them?**

A:
| Column | Issue | Fix |
|---|---|---|
| `show_id` | 4 null values — violates PK constraint | Drop null rows |
| `duration_minutes` | Mixed NaN + numeric strings (object dtype) | Cast to int after null handling |
| `duration_seasons` | Object dtype | Cast to int |
| `date_added` | String instead of date | Parse to date type |
| `release_year` | float64 due to NaN coercion | Cast to int |

**Key insight:** `duration_minutes` and `duration_seasons` have intentional nulls — Movies have minutes but no seasons, TV Shows have seasons but no minutes. This is schema design, not dirty data. Dropping these nulls would be incorrect.

Depth → *"How do you distinguish intentional nulls from dirty data nulls?"*
→ Business logic and data profiling. In this case, the `type` column (`Movie` vs `TV Show`) perfectly explains the null pattern — every Movie has `duration_minutes` populated and every TV Show has `duration_seasons` populated. A random dirty null wouldn't follow that pattern.

---

## Topic 6: Architecture Concepts

**Q13: Explain the Medallion Architecture used in this project.**

A: Medallion architecture organizes data lake storage into quality layers:
- **Bronze (Raw):** Exact copy of source data — no transforms, no filtering. The single source of truth that can always be replayed.
- **Silver (Cleaned):** Validated, typed, and deduplicated data. Business logic applied but not yet aggregated.
- **Gold (Aggregated):** Consumption-ready data — joined, aggregated, optimized for analytics and BI tools.

In this project: ADF lands data in Bronze, Databricks PySpark transforms Bronze → Silver, Delta Live Tables builds Silver → Gold.

Depth → *"Why keep Bronze as a raw copy? Couldn't you transform during ingestion?"*
→ Bronze is your insurance policy. If a transformation bug corrupts Silver, you can replay from Bronze. If requirements change and you need a different transformation, Bronze is always there. Transforming during ingestion means you lose the original data.

---

*Next session: Guide 02 — Databricks Auto Loader (Bronze → Silver)*
