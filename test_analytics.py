import pandas as pd

from src.analytics import source_performance, summary_metrics


def sample_frame():
    return pd.DataFrame([
        {"id": 1, "status": "Applied", "match_score": 70, "source": "LinkedIn"},
        {"id": 2, "status": "Interview", "match_score": 80, "source": "Referral"},
        {"id": 3, "status": "Rejected", "match_score": 60, "source": "LinkedIn"},
    ])


def test_summary_metrics():
    result = summary_metrics(sample_frame())
    assert result["total"] == 3
    assert result["active"] == 2
    assert result["interviews"] == 1
    assert result["avg_match"] == 70.0


def test_source_performance():
    result = source_performance(sample_frame())
    referral = result[result["source"] == "Referral"].iloc[0]
    assert referral["response_rate"] == 100.0
