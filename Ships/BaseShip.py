from abc import ABC, abstractmethod
from Ships.Orientation import orientation
class BaseShip(ABC):

    def __init__(self):
        super().__init__()
        self._orientation = None
        self._ShipPoint = None
        self.emp_turns = 0
        self.hit_cells = set()

    def get_cells(self):

        if self._ShipPoint is None or self._orientation is None:
            return[]
        
        x,y = self._ShipPoint
        cells = []

        for i in range(self.length):
            if self._orientation == orientation.Right:
                cells.append((x + i, y))
            elif self._orientation == orientation.Left:
                cells.append((x - i, y))
            elif self._orientation == orientation.Down:
                cells.append((x, y + i))
            elif self._orientation == orientation.Up:
                cells.append((x, y - i))
        
        return cells
    
    def __contains__(self, cell):
        return cell in self.get_cells()
        
    def __iter__(self):
        return iter(self.get_cells())
    @property
    @abstractmethod
    def length(self):
        "base class length"
        pass

    @property
    @abstractmethod
    def color(self):
        "base class color"
        pass

    @property
    @abstractmethod
    def count(self):
        "base class count"
        pass

    @property
    @abstractmethod
    def orientation(self):
        "base class count"
        pass

    @orientation.setter
    @abstractmethod
    def orientation(self):
        "base class count"
        pass

    @property
    @abstractmethod
    def ShipPoint(self):
        """Abstract getter for basepoint of ship"""
        pass

    @ShipPoint.setter
    @abstractmethod
    def ShipPoint(self):
        """Abstract setter for basepoint of ship"""
        pass

    @abstractmethod
    def specialAtk(self, x, y, board, game):
        "base implentatie bevat geen functionaliteit"
        pass

    @property
    def is_emp(self):
        return self.emp_turns > 0

    