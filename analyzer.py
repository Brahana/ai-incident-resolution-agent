
from pathlib import Path

def analyze_log(file_path):
    """Read a log file and extract error messages."""

    path = Path(file_path)

    if not path.exists():
        return {
            "status": "error",
            "message": f"Log file not found: {file_path}"
        }

    lines = path.read_text(encoding="utf-8").splitlines()

    errors = [
        line for line in lines
        if " ERROR " in line
    ]

    warnings = [
        line for line in lines
        if " WARNING " in line
    ]

    if not errors:
        summary = "No errors found in the log."
    else:
        summary = f"Found {len(errors)} error(s) in the log."

    return {
        "status": "success",
        "total_lines": len(lines),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "summary": summary,
        "errors": errors
    }


if __name__ == "__main__":
    result = analyze_log("sample_logs/batch_failure.log")

    for key, value in result.items():
        print(f"{key}: {value}")
