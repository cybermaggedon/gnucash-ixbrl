
from . datum import *

# Series is a 1-dimensional array of facts
class Series:
    def __init__(self, metadata, values, rank=0):
        self.metadata = metadata
        self.values = values
        self.rank = rank

# Base class for tabular data
class StructElt:
    def __init__(self):
        self.notes = None
    def set_notes(self, note):
        self.notes = note
    def has_notes(self):
        return self.notes is not None
    def get_notes(self):
        return self.notes

class Dataset:

    def __init__(self, periods, sections):
        self.periods = periods
        self.sections = sections

    def has_notes(self):
        for sec in self.sections:
            if sec.has_notes(): return True
        return False

class Heading(StructElt):

    def __init__(self, metadata):
        super().__init__()
        self.metadata = metadata

    def emit(self, reporter, grid, periods):
        reporter.add_heading(grid, self, periods)

class Totals(StructElt):

    def __init__(self, computation, results, super_total=False):
        super().__init__()
        self.id = None
        self.value = None
        self.metadata = computation.metadata
        self.super_total = super_total

        for result in results:
            comp_res = computation.get_output(result)
            comp_res.add_value(computation, result, self)

    def emit(self, reporter, grid, periods):
        reporter.add_totals(grid, self, periods, self.super_total)

class Break(StructElt):

    def __init__(self):
        super().__init__()

    def emit(self, reporter, grid, periods):
        reporter.add_break(grid)

class SingleLine(StructElt):

    def __init__(self, computation, results):
        super().__init__()
        self.id = None
        self.value = None
        self.metadata = computation.metadata

        for result in results:
            comp_res = computation.get_output(result)
            comp_res.add_value(computation, result, self)

    def emit(self, reporter, grid, periods):
        reporter.add_single_line(grid, self, periods)

class Item(StructElt):

    def __init__(self, computation, results):
        super().__init__()
        self.id = None
        self.value = None
        self.metadata = computation.metadata

        # FIXME, what's this???
        self.super_total = False

        for result in results:
            comp_res = computation.get_output(result)
            comp_res.add_value(computation, result, self)

    def emit(self, reporter, grid, periods):
        reporter.add_item(grid, self, periods)
