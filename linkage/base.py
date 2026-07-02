from abc import ABC, abstractmethod

class BaseLinker(ABC):
    def __init__(self, name):
        self.name = name
        self.enabled = True

    @abstractmethod
    def find_window(self):
        pass

    @abstractmethod
    def link(self, stock_code):
        pass

    def is_running(self):
        return self.find_window() is not None
