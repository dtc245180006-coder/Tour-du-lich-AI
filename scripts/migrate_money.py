"""Audit existing money columns; --apply migrates MySQL after table backups.

SQLite has dynamic numeric storage: whole-VND values need no table rebuild.
Run the audit with the application stopped before deploying Money mappings.
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text
from backend.app.database import engine

COLUMNS = {'tours':['base_price'], 'departures':['price_override'],
           'bookings':['total_amount','deposit_amount','paid_amount','refund_amount'], 'payments':['amount']}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args=parser.parse_args()
    with engine.connect() as conn:
        for table, columns in COLUMNS.items():
            for column in columns:
                count=conn.execute(text(f'SELECT COUNT(*) FROM `{table}` WHERE `{column}` < 0 OR `{column}` != ROUND(`{column}`, 0)')).scalar()
                if count:
                    raise SystemExit(f'{table}.{column}: {count} giá trị không phải số nguyên VNĐ không âm. Cần đối chiếu trước khi chuyển đổi.')
        print('Audit passed: money values are nonnegative whole VND.')
    if not args.apply:
        print('No data changed. Use --apply to migrate MySQL after stopping the application.')
        return
    if engine.dialect.name != 'mysql':
        print('SQLite: no rebuild needed for whole-VND values. Money mapping uses Decimal/int.')
        return
    suffix=datetime.now().strftime('%Y%m%d%H%M%S')
    with engine.begin() as conn:
        for table in COLUMNS:
            backup=f'{table}_money_backup_{suffix}'
            conn.execute(text(f'CREATE TABLE `{backup}` LIKE `{table}`'))
            conn.execute(text(f'INSERT INTO `{backup}` SELECT * FROM `{table}`'))
    with engine.begin() as conn:
        for table, columns in COLUMNS.items():
            for column in columns:
                nullable='NULL' if column=='price_override' else 'NOT NULL DEFAULT 0'
                conn.execute(text(f'ALTER TABLE `{table}` MODIFY COLUMN `{column}` DECIMAL(18,0) {nullable}'))
    print(f'Migration complete. Backup tables use suffix {suffix}.')

if __name__=='__main__':
    main()
