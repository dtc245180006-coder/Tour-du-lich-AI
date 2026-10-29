from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app import crud, models, schemas
from backend.app.database import Base


@pytest.mark.parametrize('payload', [
    {'total_slots': 0}, {'total_slots': 2, 'available_slots': 3},
    {'price_override': -1}, {'status': 'INVALID'},
])
def test_departure_rejects_invalid_capacity(payload):
    with pytest.raises(ValidationError):
        schemas.DepartureCreate(tour_id=1, departure_date=date.today(),
                                return_date=date.today() + timedelta(days=1), **payload)


def test_concurrent_booking_preserves_capacity(tmp_path):
    engine = create_engine('sqlite:///' + (tmp_path / 'race.db').as_posix(), connect_args={'timeout': 20})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)
    with factory() as db:
        tour = models.Tour(code='RACE', title='Race', destination='Test', base_price=100000)
        db.add(tour); db.flush()
        dep = models.Departure(tour_id=tour.id, departure_date=date.today()+timedelta(days=20),
                               return_date=date.today()+timedelta(days=21), total_slots=3, available_slots=3)
        db.add(dep); db.commit(); departure_id = dep.id
    def book(index):
        with factory() as db:
            try:
                crud.create_booking(db, schemas.BookingCreate(departure_id=departure_id,
                    customer_name='Race', customer_phone=f'09000000{index:02}', num_people=1))
                return True
            except HTTPException as exc:
                assert exc.status_code == 400
                return False
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(book, range(6)))
    with factory() as db:
        assert sum(results) == 3
        assert db.get(models.Departure, departure_id).available_slots == 0
        assert db.query(models.Booking).count() == 3
    engine.dispose()


def test_repeated_payment_is_idempotent(tmp_path):
    engine = create_engine('sqlite:///' + (tmp_path / 'payments.db').as_posix())
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)
    with factory() as db:
        tour = models.Tour(code='PAY', title='Pay', destination='Test', base_price=100000)
        db.add(tour); db.flush()
        dep = models.Departure(tour_id=tour.id, departure_date=date.today()+timedelta(days=20),
                               return_date=date.today()+timedelta(days=21), total_slots=3, available_slots=3)
        db.add(dep); db.commit()
        booking = crud.create_booking(db, schemas.BookingCreate(departure_id=dep.id,
            customer_name='Test', customer_phone='0901234567', num_people=1))
        payload = schemas.PaymentCreate(booking_id=booking.id, amount=100000, transaction_code='same-request')
        first = crud.add_payment(db, payload)
        second = crud.add_payment(db, payload)
        assert first.id == second.id
        assert booking.paid_amount == 100000
        assert db.query(models.Payment).count() == 1
    engine.dispose()


def test_concurrent_cancellation_does_not_double_refund(tmp_path):
    engine = create_engine('sqlite:///' + (tmp_path / 'cancel.db').as_posix(), connect_args={'timeout': 20})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False)
    with factory() as db:
        tour = models.Tour(code='CANCEL', title='Cancel', destination='Test', base_price=100001)
        db.add(tour); db.flush()
        dep = models.Departure(tour_id=tour.id, departure_date=date.today()+timedelta(days=20),
                               return_date=date.today()+timedelta(days=21), total_slots=3, available_slots=3)
        db.add(dep); db.commit(); departure_id=dep.id
        booking = crud.create_booking(db, schemas.BookingCreate(departure_id=dep.id,
            customer_name='Test', customer_phone='0901234567', num_people=1, initial_payment=100001))
        booking_id=booking.id
    def cancel(_):
        with factory() as db:
            try:
                crud.cancel_booking(db, booking_id, schemas.BookingCancel(reason='Test'))
                return True
            except HTTPException as exc:
                assert exc.status_code == 400
                return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(cancel,range(2)))
    with factory() as db:
        assert sum(results)==1
        assert db.get(models.Departure,departure_id).available_slots==3
        assert db.query(models.Payment).filter_by(payment_type='REFUND').count()==1
        assert db.get(models.Booking,booking_id).refund_amount==100001
    engine.dispose()
