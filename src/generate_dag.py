import json
from pathlib import Path
from typing import Optional

from jil_parser import parse_jil_file
from invoke_bedrock import call_bedrock_claude


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PROMPT_DIR = BASE_DIR / "src" / "prompt_templates"
OUTPUT_DIR = BASE_DIR / "outputs"


def load_prompt_template(name: str) -> str:
    return (PROMPT_DIR / name).read_text()


def build_prompt_from_jil(jil_path: str) -> str:
    parsed = parse_jil_file(jil_path)
    template = load_prompt_template("autosys_to_airflow_glue_dag.txt")
    return template.replace("{{parsed_jil_json}}", json.dumps(parsed, indent=2))


def generate_dag_from_jil(jil_filename: str, output_filename: Optional[str] = None) -> Path:
    jil_path = str(DATA_DIR / jil_filename)
    prompt = build_prompt_from_jil(jil_path)
    dag_code = call_bedrock_claude(prompt)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if output_filename is None:
        output_filename = "autosys_chain_dag_generated.py"
    out_path = OUTPUT_DIR / output_filename
    out_path.write_text(dag_code)
    return out_path


if __name__ == "__main__":
    out = generate_dag_from_jil("sample_chain.jil")
    print(f"Generated DAG written to: {out}")
