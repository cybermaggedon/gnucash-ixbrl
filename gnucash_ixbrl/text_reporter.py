
from . format import NegativeParenFormatter
from . period import Period
import io

class TextReporter:

    def format_number(self, n):
        if abs(n.value) < 0.001:
            return "- "
        return self.fmt.format("{0:.2f}", n.value)

    def output(self, worksheet, out):

        self.out = out
        self.fmt = NegativeParenFormatter()

        ds = worksheet.get_structure()

        periods = ds.periods
        sections = ds.sections

        out.write(self.fmt.format("{0:40}  ", ""))
        for period in periods:
            out.write(self.fmt.format("{0:>10} ", period.name + " "))

        out.write("\n")

        for section in sections:
            section.update(self, None, periods)

            continue

            out.write("\n")

            if section.total == None and section.items == None:

                out.write(fmt.format("{0:40}: ", section.metadata.description))

                for period in periods:
                    out.write(fmt.format("{0:>10} ", " - "))

                out.write("\n")
                out.write("\n")

            elif section.items == None:

                out.write(fmt.format("{0:40}: ", section.metadata.description))

                for i in range(0, len(periods)):

                    s = format_number(section.total.values[i])
                    out.write("{0:>10} ".format(s))

                out.write("\n")

            else:

                out.write(fmt.format("{0}:\n", section.metadata.description))

                for item in section.items:
                    
                    out.write(

                        fmt.format("  {0:38}: ", item.metadata.description)
                    )

                    for i in range(0, len(periods)):

                        s = format_number(item.values[i])
                        out.write(fmt.format("{0:>10} ", s))

                    out.write("\n")

                out.write(fmt.format("{0:40}: ", "Total"))

                for i in range(0, len(periods)):

                    s = format_number(section.total.values[i])
                    out.write(fmt.format("{0:>10} ", s))

                out.write("\n")

    def add_heading(self, table, section, periods):
        self.out.write(self.fmt.format("{0}:\n", section.metadata.description))
        
    def add_item(self, table, section, periods):

        self.out.write(self.fmt.format("{0:40}: ", section.metadata.description))

        for i in range(0, len(periods)):
            s = self.format_number(section.value.values[i])
            self.out.write(self.fmt.format("{0:>10} ", s))

        self.out.write("\n")

    def add_totals(self, table, section, periods, super_total=False):

        self.out.write(self.fmt.format("{0:40}: ", "Total"))

        for i in range(0, len(periods)):
            s = self.format_number(section.total.values[i])
            self.out.write(self.fmt.format("{0:>10} ", s))

        self.out.write("\n")

    def add_single_line(self, table, section, periods, super_total=False):

        self.out.write(self.fmt.format("{0:40}: ", section.metadata.description))

        for i in range(0, len(periods)):
            s = self.format_number(section.total.values[i])
            self.out.write(self.fmt.format("{0:>10} ", s))

        self.out.write("\n")

    def add_break(self, table):
        self.out.write("\n")
