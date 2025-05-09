class NotificationService:
    @staticmethod
    def send_notification(user, subject, message):
        # Simulate in-app + email sending
        print(f"\n📨 [NOTIFY] To: {user.email} | {subject}\n{message}\n")

