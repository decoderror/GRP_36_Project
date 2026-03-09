from abc import ABC, abstractmethod

class BaseEntity(ABC):
    @abstractmethod
    def update(self):
        pass

