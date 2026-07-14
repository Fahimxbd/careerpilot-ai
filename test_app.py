from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_all_pages_render_and_match_action_runs():
    db = Path("data/careerpilot.db")
    db.unlink(missing_ok=True)

    try:
        app = AppTest.from_file("app.py", default_timeout=20).run()
        assert not app.exception

        for page_name in ["Applications", "Match Lab", "Analytics", "About"]:
            app.sidebar.radio[0].set_value(page_name).run()
            assert not app.exception

        app.sidebar.radio[0].set_value("Match Lab").run()
        app.button[0].click().run()
        assert not app.exception
        assert any(metric.label == "Overall match" for metric in app.metric)
    finally:
        db.unlink(missing_ok=True)
