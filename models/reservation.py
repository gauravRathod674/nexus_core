from datetime import datetime, timedelta
from enum import Enum


class ReservationStatus(Enum):
    ACTIVE = "Active"
    EXPIRED = "Expired"
    CANCELLED = "Cancelled"


class Reservation:
    def __init__(self, user_name: str, isbn: str, reservation_date: datetime, duration_days: int = 2):
        self.user_name = user_name
        self.isbn = isbn
        self.reservation_date = reservation_date
        self.expiry_date = reservation_date + timedelta(days=duration_days)
        self.status = ReservationStatus.ACTIVE

    def is_expired(self) -> bool:
        return datetime.now() > self.expiry_date

    def expire(self):
        if self.status == ReservationStatus.ACTIVE:
            self.status = ReservationStatus.EXPIRED
            # Notify via observer (placeholder)
            # subject.notify("reservation_expired", {"user": self.user_name, "isbn": self.isbn})

    def cancel(self):
        if self.status == ReservationStatus.ACTIVE:
            self.status = ReservationStatus.CANCELLED

    def __str__(self):
        return (
            f"Reservation(user={self.user_name}, isbn={self.isbn}, "
            f"expires={self.expiry_date.date()}, status={self.status.name})"
        )
