from streamlit.testing.v1 import AppTest


def access_app():
    return AppTest.from_string(
        "from app import _require_access\n"
        "import streamlit as st\n"
        "_require_access()\n"
        "st.success('Protected content')\n"
    )


def test_railway_without_password_blocks_access(monkeypatch):
    monkeypatch.setenv("RAILWAY_ENVIRONMENT_ID", "test")
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    app = access_app().run()
    assert not app.exception
    assert app.error
    assert not app.success


def test_password_required_and_persists_in_session(monkeypatch):
    monkeypatch.setenv("APP_PASSWORD", "test-only-password")
    app = access_app().run()
    assert not app.success
    app.text_input[0].set_value("incorrect")
    app.button[0].click().run()
    assert app.error
    assert not app.success
    app.text_input[0].set_value("test-only-password")
    app.button[0].click().run()
    assert not app.exception
    assert app.success[0].value == "Protected content"
    app.run()
    assert app.success


def test_local_without_password_keeps_existing_access(monkeypatch):
    monkeypatch.delenv("RAILWAY_ENVIRONMENT_ID", raising=False)
    monkeypatch.delenv("APP_PASSWORD", raising=False)
    app = access_app().run()
    assert not app.exception
    assert app.success
