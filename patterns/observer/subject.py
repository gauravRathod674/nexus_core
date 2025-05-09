class Subject:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def notify(self, event_type, user=None, item=None, due_date=None):
        for observer in self._observers:
            observer.update(event_type, user=user, item=item, due_date=due_date)
