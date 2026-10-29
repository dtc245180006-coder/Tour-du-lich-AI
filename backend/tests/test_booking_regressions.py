import pytest
from fastapi import HTTPException
from backend.tests.test_booking_logic import db
from backend.app import crud, models, schemas


def request(db):
    return crud.create_guest_booking(db, schemas.GuestBookingCreate(
        departure_id=db.query(models.Departure).first().id,
        customer_name="Regression", customer_phone="0900000123", num_people=2))


def test_cancel_waiting_request_never_adds_seats(db):
    departure = db.query(models.Departure).first()
    before = departure.available_slots
    booking = request(db)
    crud.cancel_booking(db, booking.id, schemas.BookingCancel(reason="Test"))
    db.refresh(departure)
    assert departure.available_slots == before


def test_failed_initial_payment_rolls_back_seats_and_booking(db):
    departure = db.query(models.Departure).first()
    before = departure.available_slots
    with pytest.raises(HTTPException):
        crud.create_booking(db, schemas.BookingCreate(
            departure_id=departure.id, customer_name="Test", customer_phone="0900000123",
            num_people=1, initial_payment=999999999))
    db.refresh(departure)
    assert departure.available_slots == before
    assert db.query(models.Booking).count() == 0
    assert db.query(models.Customer).count() == 0


def test_confirmed_request_cannot_be_rejected_or_deleted(db):
    booking = request(db)
    crud.confirm_guest_booking(db, booking.id, None)
    with pytest.raises(HTTPException):
        crud.reject_guest_booking(db, booking.id, "Test")
    with pytest.raises(HTTPException):
        crud.delete_departure(db, booking.departure_id)
    assert db.query(models.Booking).count() == 1


def test_payment_cannot_revive_cancelled_booking(db):
    booking = request(db)
    crud.cancel_booking(db, booking.id, schemas.BookingCancel(reason="Test"))
    with pytest.raises(HTTPException):
        crud.add_payment(db, schemas.PaymentCreate(booking_id=booking.id, amount=1000))
    db.refresh(booking)
    assert booking.status == "CANCELLED"
    assert booking.paid_amount == 0


def test_closed_departure_cannot_be_confirmed(db):
    booking = request(db)
    booking.departure.status = "CANCELLED"
    db.commit()
    with pytest.raises(HTTPException):
        crud.confirm_guest_booking(db, booking.id, None)
    db.refresh(booking)
    assert booking.status == "WAITING_CONFIRM"
