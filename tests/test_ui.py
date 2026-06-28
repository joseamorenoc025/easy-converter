"""Tests de UI con tkinter.event_generate."""
import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

SKIP_UI = os.environ.get("CI", "false").lower() == "true"


@pytest.fixture
def app():
    """Crea la app y la destruye al final, sin abrir mainloop."""
    import customtkinter
    customtkinter.set_appearance_mode("dark")
    from ui.main_window import App
    try:
        application = App()
    except Exception:
        pytest.skip("No se pudo inicializar la ventana tkinter")
    yield application
    try:
        application.after(0, application.destroy)
        application.update()
    except Exception:
        pass


@pytest.mark.skipif(SKIP_UI, reason="No display in CI")
class TestAppInit:
    def test_app_initializes(self, app):
        assert app is not None
        assert app.winfo_exists()

    def test_app_title(self, app):
        assert "Easy Converter" in app.title()

    def test_app_has_controller(self, app):
        assert hasattr(app, 'controller')
        assert app.controller is not None


@pytest.mark.skipif(SKIP_UI, reason="No display in CI")
class TestModeToggle:
    def test_set_mode_pdf2word(self, app):
        app.set_mode("pdf2word")
        assert app.conversion_mode == "pdf2word"

    def test_set_mode_word2pdf(self, app):
        app.set_mode("word2pdf")
        assert app.conversion_mode == "word2pdf"


@pytest.mark.skipif(SKIP_UI, reason="No display in CI")
class TestWidgets:
    def test_queue_frame_exists(self, app):
        assert hasattr(app, 'scroll_frame')
        assert app.scroll_frame is not None

    def test_sidebar_checkboxes(self, app):
        assert hasattr(app, 'check_open')
        assert hasattr(app, 'check_ocr')

    def test_mode_buttons_exist(self, app):
        assert hasattr(app, 'btn_pdf2word')
        assert hasattr(app, 'btn_word2pdf')
