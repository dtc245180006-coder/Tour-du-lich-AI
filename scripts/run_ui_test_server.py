"""Start an isolated, seeded server for browser tests. Never uses the real DB."""
import os
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='vietjourney-ui-') as directory:
        os.environ['DB_TYPE'] = 'sqlite'
        os.environ['DATABASE_URL'] = 'sqlite:///' + (Path(directory) / 'ui.db').as_posix()
        os.environ['GEMINI_API_KEY'] = ''
        os.environ['OPENAI_API_KEY'] = ''
        from backend.app import config
        config.BASE_DIR = Path(directory)
        from backend.app.seed_data import init_db
        from backend.app.database import engine
        init_db()
        import uvicorn
        try:
            uvicorn.run('backend.app.main:app', host='127.0.0.1', port=8011)
        finally:
            engine.dispose()
