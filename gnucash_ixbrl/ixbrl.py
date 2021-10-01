
# Converts a worksheet into iXBRL.

from . format import NegativeParenFormatter
from datetime import datetime, date
from lxml import objectify

class IxbrlReporter:

    def get_elt(self, worksheet, par, taxonomy):

        self.par = par
        self.taxonomy = taxonomy

        return self.create_report(worksheet)

    def add_header(self, table, periods):

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        # Blank header cell
        blank = self.par.xhtml_maker.td("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

        # Header cells for period names
        for period in periods:

            elt = self.par.xhtml_maker.td(period.name)
            row.append(elt)
            elt.set("class", "period periodname cell")

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        # Blank header cell
        blank = self.par.xhtml_maker.td("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

        # Header cells for currencies
        for period in periods:

            elt = self.par.xhtml_maker.td("£")
            row.append(elt)
            elt.set("class", "period currency cell")

        # Empty row
        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        blank = self.par.xhtml_maker.td("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

    def maybe_tag(self, datum, section, pid):

        value = self.taxonomy.create_fact(datum)
        val = value.value

        if value.name:

            name = value.name
            context = value.context

            txt = "{0:,.2f}".format(abs(val))

            # Element always contains positive value.  For negative we
            # add parentheses
            elt = self.par.ix_maker.nonFraction(txt)
            elt.set("name", name)

            elt.set("contextRef", context)
            elt.set("format", "ixt2:numdotdecimal")
            elt.set("unitRef", "GBP")
            elt.set("decimals", "2")

            if abs(val) < 0.005: val = 0

            if abs(val) < 0.005:
                sign = False
            else:
                if val < 0:
                    sign = True
                else:
                    sign = False

                if value.reverse:
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

            return elt

        if abs(val) < 0.005: val = 0

        # Sign and negativity of value is not the same.
        if val < 0:

            txt = "{0:,.2f}".format(-val)

            span = self.par.xhtml_maker.span()
            span.append(self.par.xhtml_maker.span("( "))
            span.append(self.par.xhtml_maker.span(txt))
            span.append(self.par.xhtml_maker.span(" )"))
            return span

        return self.par.xhtml_maker.span("{0:,.2f}".format(val))

    def add_nil_section(self, table, section, periods):

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        div = self.par.xhtml_maker.td()
        div.set("class", "label header cell")

        if len(section.total.values) > 0 and section.total.values[0].id:
            desc = self.taxonomy.create_description_fact(
                section.total.values[0], section.header
            )
            div.append(desc.to_elt(self.par))
        else:
            div.append(self.par.xhtml_maker.span(section.header))

        row.append(div)

        for i in range(0, len(periods)):
            div = self.par.xhtml_maker.td()
            div.set(
                "class",
                "period total value nil rank%d cell" % section.total.rank
            )
            row.append(div)
            content = self.maybe_tag(0, section, i)
            div.append(content)

        # Empty row
        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        blank = self.par.xhtml_maker.td("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

    def add_total_section(self, table, section, periods):

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        div = self.par.xhtml_maker.td()
        div.set("class", "label header total cell")

        if len(section.total.values) > 0 and section.total.values[0].id:
            desc = self.taxonomy.create_description_fact(
                section.total.values[0], section.header
            )
            div.append(desc.to_elt(self.par))
        else:
            div.append(self.par.xhtml_maker.span(section.header))

        row.append(div)

        for i in range(0, len(periods)):
            div = self.par.xhtml_maker.td()
            row.append(div)
            value = section.total.values[i]
            if abs(value.value) < 0.001:
                div.set(
                    "class",
                    "period total value nil rank%d cell" % section.total.rank
                )
            elif value.value < 0:
                div.set(
                    "class",
                    "period total value negative rank%d cell" % section.total.rank
                )
            else:
                div.set(
                    "class",
                    "period total value rank%d cell" % section.total.rank
                )
            content = self.maybe_tag(value, section, i)
            div.append(content)

        # Empty row
        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        blank = self.par.xhtml_maker.td("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

    def add_breakdown_section(self, table, section, periods):

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        div = self.par.xhtml_maker.td()
        div.set("class", "label breakdown header cell")

        if len(section.total.values) > 0 and section.total.values[0].id:
            desc = self.taxonomy.create_description_fact(
                section.total.values[0], section.header
            )
            div.append(desc.to_elt(self.par))
        else:
            div.append(self.par.xhtml_maker.span(section.header))
        row.append(div)

        for item in section.items:

            row = self.par.xhtml_maker.tr({"class": "row"})
            table.append(row)

            div = self.par.xhtml_maker.td()
            div.set("class", "label breakdown item cell")

            if len(item.values) > 0 and item.values[0].id:
                desc = self.taxonomy.create_description_fact(
                    item.values[0], item.description
                )
                div.append(desc.to_elt(self.par))
            else:
                div.append(self.par.xhtml_maker.span(item.description))

            row.append(div)

            for i in range(0, len(periods)):

                value = item.values[i]

                div = self.par.xhtml_maker.td()
                if abs(value.value) < 0.001:
                    div.set("class",
                            "period value nil rank%d cell" % item.rank )
                elif value.value < 0:
                    div.set("class",
                            "period value negative rank%d cell" % item.rank)
                else:
                    div.set("class",
                            "period value rank%d cell" % item.rank)

                content = self.maybe_tag(value, item, i)

                div.append(content)
                row.append(div)

        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        div = self.par.xhtml_maker.td()
        div.set("class", "label breakdown total cell")
        row.append(div)
        div.append(self.par.xhtml_maker.span("Total"))

        for i in range(0, len(periods)):

            div = self.par.xhtml_maker.td()

            row.append(div)

            value = section.total.values[i]

            if abs(value.value) < 0.001:
                div.set("class",
                        "period value nil breakdown total rank%d cell" % section.total.rank)
            elif value.value < 0:
                div.set("class",
                        "period value negative breakdown total rank%d cell" % section.total.rank)
            else:
                div.set("class",
                        "period value breakdown total rank%d cell" % section.total.rank)

            content = self.maybe_tag(value, section, i)
            div.append(content)

        # Empty row
        row = self.par.xhtml_maker.tr({"class": "row"})
        table.append(row)

        blank = self.par.xhtml_maker.td("\u00a0")
        blank.set("class", "label cell")
        row.append(blank)

    def add_section(self, grid, section, periods):

        if section.total == None and section.items == None:

            self.add_nil_section(grid, section, periods)

        elif section.items == None:

            self.add_total_section(grid, section, periods)

        else:

            self.add_breakdown_section(grid, section, periods)

    def create_report(self, worksheet):

        ds = worksheet.get_dataset()
        periods = ds.periods
        sections = ds.sections

        grid = self.par.xhtml_maker.table()
        grid.set("class", "sheet table")

        self.add_header(grid, periods)

        for section in sections:

            self.add_section(grid, section, periods)

        return grid

