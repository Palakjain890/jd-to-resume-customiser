import importlib.util
import sys
import types
from pathlib import Path


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyColumn:
    def subheader(self, *args, **kwargs):
        return None

    def file_uploader(self, *args, **kwargs):
        return None

    def success(self, *args, **kwargs):
        return None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyExpander:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False
    
    def write(self, *args, **kwargs):
        return None


def test_app_imports_with_stubbed_streamlit(monkeypatch):
    streamlit = types.ModuleType("streamlit")
    streamlit.set_page_config = lambda *args, **kwargs: None
    streamlit.markdown = lambda *args, **kwargs: None
    streamlit.sidebar = DummyContext()
    streamlit.header = lambda *args, **kwargs: None
    streamlit.text_input = lambda *args, **kwargs: ""
    streamlit.button = lambda *args, **kwargs: False
    streamlit.file_uploader = lambda *args, **kwargs: None
    streamlit.divider = lambda *args, **kwargs: None
    streamlit.expander = lambda *args, **kwargs: DummyExpander()
    streamlit.stop = lambda *args, **kwargs: None
    streamlit.write = lambda *args, **kwargs: None

    def _columns(*args, **kwargs):
        if args and isinstance(args[0], (list, tuple)):
            count = len(args[0])
        elif args and isinstance(args[0], int):
            count = args[0]
        else:
            count = 2
        return tuple(DummyColumn() for _ in range(count))

    streamlit.columns = _columns
    streamlit.status = lambda *args, **kwargs: DummyContext()
    streamlit.warning = lambda *args, **kwargs: None
    streamlit.success = lambda *args, **kwargs: None
    streamlit.error = lambda *args, **kwargs: None
    streamlit.exception = lambda *args, **kwargs: None
    streamlit.subheader = lambda *args, **kwargs: None
    streamlit.download_button = lambda *args, **kwargs: None
    streamlit.spinner = lambda *args, **kwargs: DummyContext()

    monkeypatch.setitem(sys.modules, "streamlit", streamlit)

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("test_app_module", str(app_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert hasattr(module, "st")
