
from . table import *

class DebugReporter:
    def output(self, ws, out):
        ds = ws.get_structure()
        self.handle(ds, out)

    def handle(self, thing, out, indent=0):

        if isinstance(thing, Table):

            out.write("  " * indent)
            print("Table:")

            for col in thing.columns:
                self.handle(col, out, indent + 1)

            for ix in thing.ixs:
                self.handle(ix, out, indent + 1)

        if isinstance(thing, Column):

            out.write("  " * indent)
            print("Column:", thing.metadata.description)

            if thing.children:
                for col in thing.children:
                    self.handle(col, out, indent + 1)

        if isinstance(thing, Index):

            out.write("  " * indent)
            print("Index:", thing.metadata.description)

            if isinstance(thing.child, Row):
                self.handle(thing.child, out, indent + 1)
            else:
                for ix in thing.child:
                    self.handle(ix, out, indent + 1)

        if isinstance(thing, Row):

            out.write("  " * indent)
            print("Row:")

            for value in thing.values:
                self.handle(value, out, indent + 1)

        if isinstance(thing, Cell):

            out.write("  " * indent)
            print("Cell:", round(thing.value.value, 2))
