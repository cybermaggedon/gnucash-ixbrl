
from . datum import *

class Dataset:
    pass

class Section:
    def __init__(self):
        self.id = None
        self.metadata = None
        self.items = None
        self.total = None

    def add_data(self, computation, comp_def, results):

        self.metadata = computation.metadata

        for result in results:
            comp_res = computation.get_output(result)
            comp_res.add_data(computation, comp_def, result, self)

class Series:
    def __init__(self, metadata, values, rank=0):
        self.metadata = metadata
        self.values = values
        self.rank = rank
