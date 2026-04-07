from harbor.config import get_settings, reset_settings_cache
from harbor.runtime import runtime_summary


def test_runtime_summary_contains_expected_keys() -> None:
    reset_settings_cache()
    settings = get_settings()

    summary = runtime_summary(settings)

    assert summary["app_name"] == "Harbor"
    assert summary["environment"] == "dev"
    assert summary["postgres_configured"] is False
    assert "artifact_root" in summary
    assert "report_root" in summary
