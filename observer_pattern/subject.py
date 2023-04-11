
class Subject:
    def __init__(self):
        self.observers = []

    def add(self, observer):
        self.observers.append(observer)

    def remove(self, observer):
        try:
            self.observers.remove(observer)
        except:
            pass

    def notify(self):
        for observer in self.observers:
            observer.update(self)