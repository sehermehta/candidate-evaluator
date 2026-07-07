# Candidate Evaluator

A local Streamlit app for evaluating Apify LinkedIn profile JSON files against a rubric with the OpenAI API.

## Run

```bash
.venv/bin/streamlit run app.py
```

The app opens with the sample JSON and rubric paths prefilled when those files are available:

- `/Users/sehermehta/Documents/Documents - Seher’s MacBook Air/Codex/candidate-evaluator/sample.json`
- `/Users/sehermehta/Documents/Documents - Seher’s MacBook Air/Codex/candidate-evaluator/rubric.md`

You can also upload a different LinkedIn JSON file and rubric.

Use **Evaluation role** to choose the scoring mode:

- **Design / Product UX** keeps the original 60-point design evaluator.
- **QA Automation Engineer** uses the 100-point QA automation rubric and QA-specific output columns.

Each saved run stores its role, so resume/retry/export use the same schema that the run started with.

## Safety

The app does not hardcode or save the OpenAI API key. Evaluation cannot start unless both are true:

- an API key is pasted into the password field
- `I approve paid OpenAI API calls for this run` is checked

The preview flow makes no OpenAI API calls.

## Progress And Outputs

Each run is saved under `work/runs/<run_id>/` after every candidate, including:

- normalized candidate data
- per-candidate status
- successful rows
- failed rows
- raw structured model responses

Exports are saved under `outputs/` and are also available as CSV and Excel downloads in the app.

## Validation

The app validates every model response before saving a completed row:

- category score caps
- total score sum and 60-point maximum
- ranking band
- fixed output columns
- maximum three strongest evidence fields
- score rationale no longer than 75 words

Invalid responses are marked failed and can be retried from the app.
