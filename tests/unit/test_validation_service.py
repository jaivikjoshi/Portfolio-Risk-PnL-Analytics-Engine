from __future__ import annotations

from app.services.ingestion_service import ingest_csv_path, seed_sample_data
from app.services.validation_service import list_issues, run_validation


def test_invalid_trade_rows_create_validation_issues(db_session):
    seed_sample_data(db_session, force=True)
    result = ingest_csv_path(
        db_session,
        source_type="trades",
        path="data/bad_samples/invalid_trades.csv",
        force=True,
    )

    assert result.issues_count >= 2
    issues = list_issues(db_session, limit=20)
    assert any(issue.rule_code == "INVALID_ROW" for issue in issues)


def test_validation_detects_sell_exceeds_position(db_session):
    seed_sample_data(db_session, force=True)
    ingest_csv_path(
        db_session,
        source_type="trades",
        path="data/bad_samples/inconsistent_positions.csv",
        force=True,
    )

    result = run_validation(db_session)
    assert result["critical_count"] >= 1
    issues = list_issues(db_session, rule_code="SELL_EXCEEDS_POSITION", limit=20)
    assert issues

