# Autosys JIL → Airflow (MWAA) → AWS Glue POC

This POC demonstrates a realistic enterprise-style modernization pattern:

- **Input**: Autosys JIL file describing jobs, dependencies, and simple schedule.
- **Processing**:
  - A lightweight JIL parser converts the JIL into structured JSON.
  - Amazon Bedrock (Claude 3.5 Sonnet) is invoked with a prompt template.
  - The LLM generates an Airflow DAG that orchestrates AWS Glue jobs.
- **Output**:
  - A fully-formed Airflow DAG Python file placed under `outputs/`, ready to upload to an MWAA environment.

The DAG uses:

- `GlueJobOperator` for Glue ETL jobs
- `S3KeySensor` for file-watcher style jobs
- `SnsPublishOperator` for failure alerts
- Parallel branches and `TriggerRule.ALL_DONE` to support "continue even on failure" scenarios

## Repo Layout

- `data/sample_chain.jil`  
  Example Autosys JIL with:
  - One file watcher
  - Multiple command jobs
  - Parallel branches
  - A job that should wait for 2 upstream jobs but continue regardless of their success/failure

- `src/jil_parser.py`  
  Tiny JIL parser used to convert the raw JIL file into JSON that can be passed into the LLM.

- `src/invoke_bedrock.py`  
  Thin wrapper around Amazon Bedrock Runtime API using Claude 3.5 Sonnet.

- `src/prompt_templates/autosys_to_airflow_glue_dag.txt`  
  Prompt instructing the LLM to generate a production-style Airflow DAG for MWAA + Glue, with SNS alerts and proper operators.

- `src/generate_dag.py`  
  Entry point script:
  - Reads `sample_chain.jil`
  - Builds the prompt
  - Calls Bedrock
  - Writes the generated DAG Python file into `outputs/autosys_chain_dag_generated.py`

- `outputs/example_parallel_chain_dag.py`  
  A **hand-authored** example DAG that illustrates:
  - 1 file watcher sensor
  - 10 Glue jobs
  - JOB1 & JOB2 in parallel → JOB3 waits for both
  - JOB4/5/6 in parallel
  - JOB7 waiting for JOB5 + JOB6 with `TriggerRule.ALL_DONE` (continues even on failure)
  - JOB8 waiting on JOB7
  - JOB9 and JOB10 in parallel after JOB8
  - SNS failure callback and sensible `default_args`

## How to Run Locally

1. Create and activate a virtualenv (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # on macOS/Linux
   # .venv\Scripts\activate  # on Windows
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure your AWS credentials are configured and that you have access to Amazon Bedrock with the Claude 3.5 Sonnet model.

4. Generate the Airflow DAG from the JIL:

   ```bash
   cd src
   python generate_dag.py
   ```

5. The generated DAG will be written to:

   ```text
   ../outputs/autosys_chain_dag_generated.py
   ```

   You can inspect it locally, or upload it to MWAA.

## Deploying to MWAA (High-Level)

1. Create an MWAA environment in your AWS account.
2. Note the S3 bucket configured as the "DAGs" folder for MWAA.
3. Upload either:
   - `outputs/autosys_chain_dag_generated.py` (from Bedrock), or
   - `outputs/example_parallel_chain_dag.py` (manual example)

   into:

   ```text
   s3://<your-mwaa-bucket>/dags/
   ```

4. Open the Airflow UI from the MWAA console and you should see the DAG appear.

5. Configure:
   - An SNS topic (e.g. `airflow-alerts`)
   - Correct IAM permissions so MWAA can:
     - Start Glue jobs
     - Publish to SNS
     - Read from S3 for sensors

## Notes

- This POC is intentionally focused on **realistic patterns** rather than toy examples:
  - Parallel Glue jobs
  - Fan-in/fan-out dependencies
  - File watcher semantics
  - Failure alerting via SNS + email
- You can extend the prompt to support more complex JIL condition syntax, calendars, and time windows.

