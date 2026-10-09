from pathlib import Path

from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parents[1]


def test_all_pages_render_and_match_action_runs():
    db = ROOT / "data" / "careerpilot.db"
    db.unlink(missing_ok=True)

    try:
        app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=20).run()
        assert not app.exception

        for page_name in ["Applications", "Match Lab", "Analytics", "About"]:
            app.sidebar.radio[0].set_value(page_name).run()
            assert not app.exception

        app.sidebar.radio[0].set_value("Match Lab").run()
        analyze_button = next(button for button in app.button if button.label == "Analyze match")
        analyze_button.click().run()
        assert not app.exception
        assert any(metric.label == "Overall match" for metric in app.metric)
    finally:
        db.unlink(missing_ok=True)
