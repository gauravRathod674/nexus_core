from datetime import datetime, timedelta
from enum import Enum, auto

class ReservationStatus(Enum):
    PENDING   = auto()   # waiting in line
    ACTIVE    = auto()   # hold is live—user has X days to pick up
    EXPIRED   = auto()
    CANCELLED = auto()

class Reservation:
    def __init__(
        self,
        user_name: str,
        isbn: str,
        request_date: datetime,
        hold_days: int = 2
    ):
        self.user_name      = user_name
        self.isbn           = isbn
        self.request_date   = request_date
        self.hold_days      = hold_days
        self.expiry_date    = None      # only set when hold becomes ACTIVE
        self.status         = ReservationStatus.PENDING

    def activate_hold(self):
        """Turn a pending reservation into an active hold."""
        self.status      = ReservationStatus.ACTIVE
        self.expiry_date = datetime.now() + timedelta(days=self.hold_days)

    def is_hold_over(self) -> bool:
        """Has the active hold period passed?"""
        if self.status != ReservationStatus.ACTIVE:
            return False
        return datetime.now() > self.expiry_date

    def expire(self):
        """Mark this reservation expired (pending or active)."""
        self.status = ReservationStatus.EXPIRED

    def cancel(self):
        """Cancel this reservation (pending or active)."""
        self.status = ReservationStatus.CANCELLED

    def __str__(self):
        base = (
            f"Reservation(user={self.user_name}, isbn={self.isbn}, "
            f"status={self.status.name}"
        )
        if self.status == ReservationStatus.ACTIVE:
            return f"{base}, expires={self.expiry_date.date()})"
        return base + ")"
