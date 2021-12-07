
# The data model of a worksheet.  There are four kinds of thing which make
# up the output of a worksheet: Simple value, line-item breakdown,
# a total (without line-item breakdown), and a special nil value.

from . worksheet_structure import Series

class Result:
    def is_single_line(self):
        return True

class SimpleResult(Result):
    def __init__(self, defn, value):
        self.defn = defn
        self.value = value

class BreakdownResult(Result):
    def __init__(self, defn, value, items):
        self.defn = defn
        self.value = value
        self.items = items

    def add_total(self, computation, cdef, result, sec):

        if sec.metadata == None:
            sec.metadata = computation.metadata

        if sec.total == None:
            sec.total = Series(self.defn.metadata, [], rank=cdef.total_rank)

        sec.total.values.append(self.value.value)

    def add_items(self, computation, cdef, result, sec):

        if sec.items == None:
            sec.items = [
                Series(
                    computation.inputs[i].metadata, [],
                    rank=cdef.rank
                )
                for i in range(0, len(computation.inputs))
            ]

        for i in range(0, len(computation.inputs)):
            id = computation.inputs[i].metadata.id
            value = result[computation.metadata.id].items[i].value
            sec.items[i].values.append(value)

    def is_single_line(self):
        return False

class NilResult(Result):
    def __init__(self, defn, value):
        self.defn = defn
        self.value = value

    def add_total(self, computation, cdef, result, sec):

        if sec.metadata == None:
            sec.metadata = computation.metadata

        if sec.total == None:
            sec.total = Series(self.defn.metadata, [], rank=cdef.total_rank)

        sec.total.values.append(self.value.value)

    def add_items(self, computation, cdef, result, sec):
        pass

class TotalResult(Result):

    def __init__(self, defn, value, items):
        self.defn = defn
        self.value = value
        self.items = items

    def add_total(self, computation, cdef, result, sec):

        if sec.metadata == None:
            sec.metadata = computation.metadata

        if sec.total == None:
            sec.total = Series(self.defn.metadata, [], rank=cdef.total_rank)

        sec.total.values.append(self.value.value)

    def add_items(self, computation, cdef, result, sec):
        pass

