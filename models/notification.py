from datetime import datetime, timedelta


class Notification:
    def __init__(self, user_name: str, message: str, timestamp: datetime = None):
        self.user_name = user_name
        self.message = message
        self.timestamp = timestamp or datetime.now()

    def __str__(self):
        return f"Notification(to={self.user_name}, message='{self.message}', at={self.timestamp})"
