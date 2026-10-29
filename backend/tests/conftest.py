"""Isolate application import/startup from the real database and cloud services."""
import os
import tempfile
from pathlib import Path

_test_dir = tempfile.TemporaryDirectory(prefix="vietjourney-tests-")
os.environ["DB_TYPE"] = "sqlite"
os.environ["DATABASE_URL"] = "sqlite:///" + (Path(_test_dir.name) / "startup.db").as_posix()
os.environ["GEMINI_API_KEY"] = ""
os.environ["OPENAI_API_KEY"] = ""


from backend.app import config
config.BASE_DIR = Path(_test_dir.name)
from backend.app.seed_data import init_db
init_db()

def pytest_sessionfinish(session, exitstatus):
    from backend.app.database import engine
    engine.dispose()
    _test_dir.cleanup()
