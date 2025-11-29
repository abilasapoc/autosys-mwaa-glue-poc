import re
from pathlib import Path
from typing import List, Dict, Any


def parse_jil(jil_text: str) -> Dict[str, Any]:
    """Very lightweight JIL parser for POC purposes."""
    jobs: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}

    def flush_current():
        nonlocal current
        if current:
            jobs.append(current)
            current = {}

    for line in jil_text.splitlines():
        line = line.strip()
        if not line or line.startswith("/*") or line.startswith("#"):
            continue

        m_job = re.match(r"insert_job:\s*(\S+)", line, re.IGNORECASE)
        if m_job:
            flush_current()
            current = {
                "job_name": m_job.group(1),
                "raw_lines": []
            }
            continue

        if not current:
            continue

        current["raw_lines"].append(line)

        lower = line.lower()
        if lower.startswith("job_type:"):
            val = line.split(":", 1)[1].strip().lower()
            if val == "c":
                current["job_type"] = "command"
            elif val == "f":
                current["job_type"] = "file_watch"
            else:
                current["job_type"] = val

        elif lower.startswith("command:"):
            current["command"] = line.split(":", 1)[1].strip()

        elif lower.startswith("watch_file:"):
            current["watch_file"] = line.split(":", 1)[1].strip()

        elif lower.startswith("condition:"):
            current["condition"] = line.split(":", 1)[1].strip()

        elif lower.startswith("start_times:"):
            times = line.split(":", 1)[1].strip().strip('"')
            current["start_times"] = times

    flush_current()
    return {"jobs": jobs}


def parse_jil_file(path: str) -> Dict[str, Any]:
    return parse_jil(Path(path).read_text())


if __name__ == "__main__":
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python jil_parser.py <path_to_jil>")
        raise SystemExit(1)

    parsed = parse_jil_file(sys.argv[1])
    print(json.dumps(parsed, indent=2))
