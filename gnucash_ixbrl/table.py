
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

    def row_count(self):
        if isinstance(self.child, Row):
            return 1
        else:
            c = 0
            for ix in self.child:
                c += ix.row_count()
            return c

    def ix_count(self):
        if isinstance(self.child, Row): return 1
        
        return 1 + max([ix.ix_count() for ix in self.child])

class VerticalSpacer:
    def __init__(self):
        pass
    def row_count(self):
        return 1
    def ix_count(self):
        return 0

class TotalIndex(Index):
    pass

class Column:
    # children is either None or an array of Column
    def __init__(self, metadata, children=None):
        self.metadata = metadata
        self.children = children
    def column_count(self):
        if self.children:
            c = 0
            for col in self.children:
                c += col.column_count()
            return c
        else:
            return 1

class Table:
    def __init__(self, columns, ixs):
        self.columns = columns
        self.ixs = ixs

    def column_count(self):
        c = 0
        for col in self.columns:
            c += col.column_count()
        return c

    def row_count(self):
        c = 0
        for ix in self.ixs:
            c += ix.row_count()
        return c

    def ix_count(self):
        return max([ix.ix_count() for ix in self.ixs])
