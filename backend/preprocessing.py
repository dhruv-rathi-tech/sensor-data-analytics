"""Backward-compatible entry point for the upgraded ETL pipeline."""
import sys
from pathlib import Path

# Ensure package root and backend directory are in sys.path
_current = Path(__file__).resolve().parent
_root = _current.parent
if str(_current) not in sys.path:
    sys.path.insert(0, str(_current))
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

try:
    from backend.etl.pipeline import run_pipeline
except ModuleNotFoundError:
    from etl.pipeline import run_pipeline

if __name__ == "__main__":
    result = run_pipeline()
    print("\nETL completed successfully")
    print(f"Valid records: {result['valid_records']}")
    print(f"Rejected records: {result['rejected_records']}")
    print(f"Data quality score: {result['quality_score_pct']}%")
