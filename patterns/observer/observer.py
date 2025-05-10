from patterns.observer.notification_service import NotificationService

class Observer:
    def update(self, event_type, user=None, item=None, due_date=None):
        raise NotImplementedError("Subclass must implement update() method.")


class UserObserver(Observer):
    def update(self, event_type, user=None, item=None, due_date=None):
        if event_type == 'reservation_available' and user and item:
            NotificationService.send_notification(
                user,
                "Reserved Book Now Available",
                f"The book '{item.title}' you reserved is now available for borrowing."
            )

        elif event_type == 'due_date_approaching' and user and item and due_date:
            NotificationService.send_notification(
                user,
                "Due Date Approaching",
                f"Reminder: The due date for '{item.title}' is on {due_date}. Please return or renew it in time."
            )
