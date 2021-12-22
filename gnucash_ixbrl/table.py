
# Table
#   Array of Column
#     array (span, fact, Columns | None)
#   Index
#     Index (span, fact, Index | Series
#     IndexColumn

class Notable:
    def __init__(self):
        self.notes = None
    def set_notes(self, note):
        self.notes = note
    def has_notes(self):
        return self.notes is not None
    def get_notes(self):
        return self.notes

class Cell:
    def __init__(self, metadata, value):
        self.metadata = metadata
        self.value = value

class Row:
    # values is an array of cell
    def __init__(self, values):
        self.values = values

class Index(Notable):
    # child is either a row, or an array of Index
    def __init__(self, metadata, child):
        self.metadata = metadata
        self.child = child

class Column:
    # children is either None or an array of Column
    def __init__(self, metadata, children=None):
        self.metadata = metadata
        self.children = children

class Table:
    def __init__(self, columns, ixs):
        self.columns = columns
        self.ixs = ixs
