
# Converts a worksheet into iXBRL.

from . format import NegativeParenFormatter
from datetime import datetime, date
from lxml import objectify
from . table import Row, TotalIndex

class IxbrlReporter:

    def __init__(self, hide_notes):
        self.hide_notes = hide_notes

    def add_empty_row(self, table):

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        blank = self.create_cell("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

    def create_table(self):
        grid = self.par.xhtml_maker.table()
        grid.set("class", "sheet table")
        return grid

    def add_row(self, table, elts):
        row = self.par.xhtml_maker.tr({"class": "row"})
        for elt in elts:
            row.append(elt)
        table.append(row)

    def create_cell(self, text=None):
        if text == None:
            return self.par.xhtml_maker.td()
        else:
            return self.par.xhtml_maker.td(text)

    def fmt(self, v):
        v = round(v, self.decimals)
        v = v / (10 ** self.scale)
        if self.decimals > 0:
            fmt = "{0:,.%df}" % self.decimals
        else:
            fmt = "{0:,.0f}"
        return fmt.format(v)

    def maybe_tag(self, datum, section):

        fact = self.taxonomy.create_fact(datum)
        val = fact.value

        if fact.name:

            name = fact.name
            context = fact.context

            txt = self.fmt(abs(val))

            # Element always contains positive value.  For negative we
            # add parentheses
            elt = self.par.ix_maker.nonFraction(txt)
            elt.set("name", name)

            elt.set("contextRef", context)
            elt.set("format", "ixt2:numdotdecimal")
            elt.set("unitRef", self.currency)
            elt.set("decimals", str(self.decimals))
            elt.set("scale", str(self.scale))

            if abs(val) < self.tiny: val = 0

            if abs(val) < self.tiny:
                sign = False
            else:
                if val < 0:
                    sign = True
                else:
                    sign = False

                if fact.reverse:
                    sign = not sign

            if sign:
                elt.set("sign", "-")

            # Sign and negativity of value is not the same.
            # FIXME: Can't remember what the above comment means.

            if val < 0:

                span = self.par.xhtml_maker.span()
                span.append(self.par.xhtml_maker.span("( "))
                span.append(elt)
                span.append(self.par.xhtml_maker.span(" )"))
                return span

            else:

                span = self.par.xhtml_maker.span()
                span.append(self.par.xhtml_maker.span(""))
                span.append(elt)
                span.append(self.par.xhtml_maker.span("\u00a0\u00a0"))
                return span

            return elt

        if abs(val) < self.tiny: val = 0

        # Sign and negativity of value is not the same.
        if val < 0:

            txt = self.fmt(-val)

            span = self.par.xhtml_maker.span()
            span.append(self.par.xhtml_maker.span("( "))
            span.append(self.par.xhtml_maker.span(txt))
            span.append(self.par.xhtml_maker.span(" )"))
            return span

        else:
            txt = self.fmt(val) + "\u00a0\u00a0"
            return self.par.xhtml_maker.span(txt)

    def add_column_headers(self, grid, cols):

        row = []

        blank = self.create_cell("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

        for col, span in cols:

            txt = col.metadata.description
            cell = self.create_cell(txt)
            cell.set("class", "period periodname cell")
            cell.set("colspan", str(span))
            row.append(cell)

        self.add_row(grid, row)

    def add_currency_subheaders(self, grid, cols):

        row = []

        blank = self.create_cell("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

        for col, span in cols:

            if col.units:
                txt = col.units
            else:
                txt = "\u00a0"
            cell = self.create_cell(txt)
            cell.set("class", "period currency cell")
            cell.set("colspan", str(span))
            row.append(cell)

        self.add_row(grid, row)

    def add_header(self, t, grid):

        for lvl in range(0, t.header_levels()):

            cols = []

            def doit(col, l):
                if l == lvl:
                    cols.append((col, col.column_count()))

            t.column_recurse(doit)

            self.add_column_headers(grid, cols)
            self.add_currency_subheaders(grid, cols)

    def add_row_ix(self, grid, x):

        row = []

        if isinstance(x, TotalIndex):
            txt = "Total"
            elt = self.create_cell(txt)
            elt.set("class", "label breakdown total cell")
        else:
            txt = x.metadata.description
            elt = self.create_cell()
            elt.set("class", "label breakdown item cell")
            desc = self.taxonomy.create_description_fact(
                x.metadata, txt,
            )
            elt.append(desc.to_elt(self.par))

        row.append(elt)

        for cell in x.child.values:

            value = cell.value
            elt = self.create_cell()
            if isinstance(x, TotalIndex):
                if abs(value.value) < self.tiny:
                    elt.set("class", "period value breakdown total nil cell")
                elif value.value < 0:
                    elt.set("class", "period value breakdown total negative cell")
                else:
                    elt.set("class", "period value breakdown total cell")
            else:
                if abs(value.value) < self.tiny:
                    elt.set("class", "period value nil cell")
                elif value.value < 0:
                    elt.set("class", "period value negative cell")
                else:
                    elt.set("class", "period value cell")

            content = self.maybe_tag(value, value)
            elt.append(content)

            row.append(elt)

        self.add_row(grid, row)

    def add_single_line_ix(self, grid, x):

        row = []

        txt = x.metadata.description

        elt = self.create_cell()
        elt.set("class", "label header total cell")

        if x.metadata:
            desc = self.taxonomy.create_description_fact(
                x.metadata, x.metadata.description
            )
            elt.append(desc.to_elt(self.par))
        else:
            elt.append(
                self.par.xhtml_maker.span(x.metadata.description)
            )

        row.append(elt)

        for cell in x.child.values:

            value = cell.value
            elt = self.create_cell()

            if abs(value.value) < self.tiny:
                elt.set("class", "period value total nil cell")
            elif value.value < 0:
                elt.set("class", "period value total negative cell")
            else:
                elt.set("class", "period value total cell")

            content = self.maybe_tag(value, value)
            elt.append(content)

            row.append(elt)

        self.add_row(grid, row)

    def add_header_ix(self, grid, x):

        row = []

        elt = self.create_cell()
        elt.set("class", "label breakdown header cell")

        if x.metadata:
            desc = self.taxonomy.create_description_fact(
                x.metadata, x.metadata.description
            )
            elt.append(desc.to_elt(self.par))
        else:
            elt.append(
                self.par.xhtml_maker.span(x.metadata.description)
            )

        row.append(elt)

        self.add_row(grid, row)

    def add_body(self, t, grid):

        def doit(x, level=0):
            if isinstance(x.child, Row):
                self.add_row_ix(grid, x)
            else:

                if len(x.child) == 1 and type(x.child[0]) == TotalIndex:
                    self.add_empty_row(grid)
                    self.add_single_line_ix(grid, x.child[0])
                else:
                    self.add_empty_row(grid)
                    self.add_header_ix(grid, x)
                    for ix in x.child:
                        doit(ix, level + 1)
        for ix in t.ixs:
            doit(ix)

    def create_report(self, worksheet):

        grid = self.create_table()

        ds = worksheet.get_structure()

        self.add_header(ds, grid)
        self.add_body(ds, grid)

        return grid

        # Hide notes if the option is set, or there are no notes.
        self.hide_notes = self.hide_notes or not ds.has_notes()

        periods = ds.periods
        sections = ds.sections


        self.add_header(grid, periods)

        for section in sections:
            section.emit(self, grid, periods)

        return grid

    def get_elt(self, worksheet, par, taxonomy, data):

        self.par = par
        self.taxonomy = taxonomy
        self.data = data

        self.decimals = self.data.get_config("metadata.accounting.decimals", 2)
        self.scale = self.data.get_config("metadata.accounting.scale", 0)
        self.currency = self.data.get_config(
            "metadata.accounting.currency", "EUR"
        )
        self.tiny = (10 ** -self.decimals) / 2

        return self.create_report(worksheet)
