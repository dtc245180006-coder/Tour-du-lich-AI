import pytest
from fastapi import HTTPException
from pydantic import ValidationError
from backend.tests.test_booking_logic import db
from backend.app import crud, models, schemas


def guide(db):
    g = models.TourGuide(full_name='Lifecycle Guide', phone='0901234999', status='AVAILABLE')
    db.add(g); db.commit()
    return g


def booking(db, paid=0):
    dep = db.query(models.Departure).first()
    return crud.create_booking(db, schemas.BookingCreate(departure_id=dep.id,
        customer_name='Lifecycle', customer_phone='0901234777', num_people=1, initial_payment=paid))


@pytest.mark.parametrize('status', ['RUNNING', 'ON_TOUR', 'COMPLETED'])
def test_update_cannot_skip_lifecycle(db, status):
    dep = db.query(models.Departure).first()
    with pytest.raises(HTTPException):
        crud.update_departure(db, dep.id, schemas.DepartureUpdate(status=status))
    db.refresh(dep)
    assert dep.status == 'OPEN'


@pytest.mark.parametrize('status', ['COMPLETED', 'CANCELLED'])
def test_terminal_trip_cannot_reopen(db, status):
    dep = db.query(models.Departure).first(); dep.status=status; db.commit()
    with pytest.raises(HTTPException):
        crud.update_departure(db, dep.id, schemas.DepartureUpdate(status='OPEN'))
    db.refresh(dep)
    assert dep.status == status


def test_complete_marks_booking_and_blocks_refund(db):
    b = booking(db, 3_000_000)
    g = guide(db)
    crud.assign_guide_to_departure(db, b.departure_id, g.id)
    assert g.status == 'AVAILABLE'
    crud.start_departure(db, b.departure_id)
    assert g.status == 'ON_TOUR'
    crud.complete_departure(db, b.departure_id)
    db.refresh(b); db.refresh(g)
    assert b.status == 'COMPLETED'
    assert g.status == 'AVAILABLE'
    before = b.departure.available_slots
    with pytest.raises(HTTPException):
        crud.cancel_booking(db, b.id, schemas.BookingCancel(reason='Late cancellation'))
    assert db.query(models.Payment).filter_by(payment_type='REFUND').count() == 0
    db.refresh(b.departure)
    assert b.departure.available_slots == before


def test_legacy_booking_of_completed_trip_cannot_refund(db):
    b = booking(db, 3_000_000)
    b.departure.status = 'COMPLETED'; db.commit()
    with pytest.raises(HTTPException):
        crud.cancel_booking(db, b.id, schemas.BookingCancel(reason='Legacy'))
    assert db.query(models.Payment).filter_by(payment_type='REFUND').count() == 0


def test_start_requires_settled_bookings(db):
    b = booking(db)
    g = guide(db)
    crud.assign_guide_to_departure(db, b.departure_id, g.id)
    with pytest.raises(HTTPException):
        crud.start_departure(db, b.departure_id)
    db.refresh(b.departure)
    assert b.departure.status == 'OPEN'


def test_change_tour_is_rejected_not_silently_ignored():
    with pytest.raises(ValidationError):
        schemas.DepartureUpdate(tour_id=999)


def test_future_assignment_and_removal_keep_guide_available(db):
    dep = db.query(models.Departure).first()
    g = guide(db)
    crud.assign_guide_to_departure(db, dep.id, g.id)
    db.refresh(g)
    assert g.status == 'AVAILABLE'
    crud.update_departure(db, dep.id, schemas.DepartureUpdate(guide_id=None))
    db.refresh(dep); db.refresh(g)
    assert dep.guide_id is None
    assert g.status == 'AVAILABLE'
