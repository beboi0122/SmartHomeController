from abc import abstractmethod


class Observer:
    @abstractmethod
    def update(self, subject):
        raise NotImplementedError("Update class is not implemented")