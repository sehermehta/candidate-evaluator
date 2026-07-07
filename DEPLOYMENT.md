# Deploying Candidate Evaluator To Streamlit Cloud

This app is a Streamlit app. Deploy it on Streamlit Community Cloud, not Vercel.

## Before You Deploy

- Do not upload `.venv/`, `work/`, `outputs/`, or local result files to GitHub.
- Do not hardcode an OpenAI API key. The app asks for the key in the UI.
- Uploaded candidate JSON files and rubrics should be uploaded through the deployed app UI.

## GitHub Files Needed

Upload these files and folders:

- `app.py`
- `requirements.txt`
- `.streamlit/config.toml`
- `candidate_evaluator/`
- `README.md`
- `DEPLOYMENT.md`

Do not upload:

- `.venv/`
- `work/`
- `outputs/`
- `__pycache__/`
- `.pytest_cache/`

## Streamlit Cloud Steps

1. Go to `https://share.streamlit.io`.
2. Sign in with GitHub.
3. Click **Create app** or **New app**.
4. Choose the GitHub repo that contains this project.
5. Choose the branch, usually `main`.
6. Set the main file path to `app.py`.
7. Click **Deploy**.

## After Deploying

1. Open the deployed app URL.
2. Upload the LinkedIn JSON file.
3. Upload the rubric Markdown file.
4. Choose the evaluation role.
5. Paste the OpenAI API key.
6. Preview the first five candidates.
7. Approve API calls.
8. Start evaluation.
9. Download CSV/Excel when complete.

## Important Cloud Note

Streamlit Cloud storage is not meant to be permanent. Always download CSV/Excel outputs after a run.
