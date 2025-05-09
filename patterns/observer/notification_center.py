from patterns.observer.subject import Subject
from patterns.observer.observer import UserObserver

class NotificationCenter:
    _subject = None

    @classmethod
    def get_subject(cls):
        if cls._subject is None:
            cls._subject = Subject()
            cls._subject.attach(UserObserver())
        return cls._subject
