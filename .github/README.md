# MLOps Demo: Streamlit + Supabase + GitHub Actions

A complete, end-to-end MLOps demonstration project showing:

-   Model training with scikit-learn
-   Inference via Streamlit
-   Prediction logging to Supabase
-   Data drift monitoring with Evidently
-   Automated monitoring via GitHub Actions
-   CI with Ruff, Mypy, and Pytest

This repository is designed for introductory-to-intermediate MLOps
training.

## Architecture Overview

``` mermaid
flowchart TD
    A[User] --> B[Streamlit App]
    B --> C[Sklearn Model Pipeline]
    C --> D[Prediction Output]

    D --> E[Supabase - predictions table]

    E --> F[GitHub Actions - Daily Cron]
    F --> G[Fetch Last 7 Days Predictions]
    G --> H[Compute Drift - Evidently]
    H --> I{Drift >= Threshold?}

    I -- No --> J[Log Monitoring Metrics]
    I -- Yes --> K[Raise Alert]
    K --> J

    J --> L[Supabase - monitoring_metrics table]
```

## Tech Stack

  |Component        | Tool|
  |-----------------| -------------------------------------------|
  |Model            | scikit-learn (GradientBoostingClassifier)|
  |Pipeline         | sklearn Pipeline + ColumnTransformer
  |App UI           | Streamlit
  |Logging DB       | Supabase (Postgres)
  |Drift Detection  | Evidently
  |CI               | GitHub Actions
  |Linting          | Ruff
  |Type Checking    | Mypy
  |Testing          | Pytest
  |Local Dev        | Anaconda

## Project Structure

    .
    ├── app/
    │   ├── Home.py
    │   └── pages/
    │       ├── 1_Inference.py
    │       └── 2_Monitoring.py
    ├── src/
    │   ├── config.py
    │   ├── train.py
    │   ├── inference.py
    │   ├── transformers.py
    │   └── supabase.py
    ├── monitoring/
    │   ├── drift.py
    │   ├── log_metrics.py
    │   └── retrain_if_needed.py
    ├── tests/
    ├── data/
    ├── models/
    ├── requirements.txt
    ├── pyproject.toml
    └── ruff.toml


## Create Local Environment

``` bash
conda create -n mlops-demo python=3.11 -y
conda activate mlops-demo
pip install -r requirements.txt
```

## Train Initial Model

``` bash
python -m src.train
```

## Supabase Setup



### 1. Create a Free Supabase Account

1. Go to: https://supabase.com  
2. Click **Start your project**  
3. Sign up using:
   - GitHub (recommended), or  
   - Email and password  

After signing in, you will be redirected to the Supabase dashboard.

---

### 2. Create a New Project

1. Click **New Project**
2. Choose your **Organization** (a default one is created automatically)
3. Enter:
   - **Project name** (e.g., `mlops-demo`)
   - **Database password** (save this securely)
4. Click **Create new project**



---

### 3. Find Your Project URL

1. In the project dashboard, go to:

   **Settings → General**

2. Under **Project ID**, copy the project ID. The project URL is 
https://``your-project-id``.supabase.co

This is your:
- `SUPABASE_URL`

You will use this in:
- Local `.env` file
- Streamlit secrets
- GitHub Actions secrets

---

### 4. Find Your API Keys

In 

**Settings → API Keys**

you will see:

#### Publishable Key

Use this for:
- Streamlit app

Store this as:

- `SUPABASE_KEY`

---

#### Secret Keys

Use this for:
- GitHub Actions
- Backend monitoring jobs
- Reading full tables
- Writing monitoring metrics

This key bypasses Row Level Security (RLS).

Store in GitHub as:

- `SUPABASE_SERVICE_ROLE_KEY`

Do NOT expose this key in frontend code.

---


### 5. Recommended Local Setup

Create a `.env` file in your repo root:

    SUPABASE_URL=https://``your-project-id``.supabase.co
    SUPABASE_KEY=your_anon_public_key

Add `.env` to `.gitignore`.

---

### 6. Supabase Table Initialisation

Run the SQL schema located in `Supabase/schema.sql` on supabase to set up tables.

---

## Add GitHub Secrets

GitHub Secrets let you store sensitive values (API keys, passwords, URLs) securely so they can be used in GitHub Actions without committing them to your repository.

In this project, GitHub Secrets are used so the monitoring workflow can connect to Supabase.

---

### 1. Go to Your Repository Settings

1. Open your GitHub repository in the browser
2. Click the **Settings** tab (top menu)

---

### 2. Open the Secrets Page

In the left sidebar:

1. Click **Secrets and variables**
2. Click **Actions**

You should now see a page titled:

- **Actions secrets and variables**

---

### 3. Add a New Repository Secret

1. Click **New repository secret**
2. Enter the secret name and value

---

### 4. Secrets You Need for This Project

Add the following secrets:

#### `SUPABASE_URL`

- Name: `SUPABASE_URL`
- Value: your Supabase Project URL, e.g.


https://``your-project-id``.supabase.co


#### `SUPABASE_SERVICE_ROLE_KEY`

- Name: `SUPABASE_SERVICE_ROLE_KEY`
- Value: your Supabase **service_role** API key

Important:
- This key is highly privileged
- Never commit it to your repository
- Never use it inside Streamlit Community Cloud

---

### 5. Using Secrets in GitHub Actions

Once saved, secrets can be referenced inside workflows like this:

```yaml
env:
  SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
  SUPABASE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
```

## Run App Locally
``` bash
streamlit run app/Home.py
```

Open http://localhost:8501

## Deploy App to Streamlit Community Cloud
### 1. Push Your Code to GitHub

Ensure your repository is public and contains:

- `app/Home.py`
- `requirements.txt`
- All necessary source files (`src/`, `monitoring/`, etc.)

Push everything to GitHub.

---

### 2. Go to Streamlit Community Cloud

1. Visit: https://share.streamlit.io  
2. Sign in with GitHub  
3. Click **Create app**
4. Deploy a public app from GitHub

---

### 3. Configure the App

Fill in:

- **Repository**: Select your GitHub repo  
- **Branch**: `main` (or your default branch)  
- **Main file path**:  `app/Home.py`
- **URL**: `app-name.streamlit.app`
- Click **Deploy**

Streamlit will automatically install packages from `requirements.txt`.

---

### 4. Add Supabase Secrets

After deployment:

1. Go to **App settings → Secrets**
2. Add:
    - SUPABASE_URL = "https://your-project-id.supabase.co"
    - SUPABASE_KEY = "your_anon_public_key"


Important:
- Use the **Public key**
- Do NOT use the service role key in Streamlit Cloud

Click **Save**

The app will automatically restart.

---

### 5. Verify Deployment

- Open your deployed app URL
- Make a prediction
- Confirm rows appear in Supabase `predictions` table

---


## Monitoring

Daily GitHub Action:

1.  Fetch recent predictions
2.  Compute drift
3.  Save HTML drift report
4.  Log monitoring metrics
5.  Raise alert if threshold exceeded
6.  Retrain automatically if drift exceeded

Drift threshold configured in:

    monitoring/drift_threshold.txt

Drift share = number of drifted features / total features

## CI

On every push automatically runs through a github action:

-   Ruff
-   Mypy
-   Pytest

Run locally:

``` bash
ruff check .
mypy ./src
pytest -q
```

## Summary

Train → Deploy → Log → Monitor → Alert
