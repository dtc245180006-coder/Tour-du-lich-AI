"""Explicit database setup. --demo opts into demo users/data."""
import argparse
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.app.database import Base, engine, SessionLocal
from backend.app import models, auth
from backend.app.seed_data import init_db
from getpass import getpass

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--demo',action='store_true')
    parser.add_argument('--admin',help='Create an admin, password requested securely')
    args=parser.parse_args()
    Base.metadata.create_all(engine)
    if args.demo:
        init_db()
    if args.admin:
        password=getpass('Admin password (8+ characters): ')
        if len(password)<8:
            raise SystemExit('Password must have at least 8 characters.')
        with SessionLocal() as db:
            if db.query(models.User).filter_by(username=args.admin).first():
                raise SystemExit('Username already exists.')
            db.add(models.User(username=args.admin,full_name=args.admin,role='ADMIN',hashed_password=auth.hash_password(password)))
            db.commit()
    print('Database setup complete. Existing records were retained.')
