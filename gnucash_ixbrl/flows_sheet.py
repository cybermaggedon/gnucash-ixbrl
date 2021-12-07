
# A worksheet with a bunch of computations shown.

from . worksheet import Worksheet
from . worksheet_structure import Dataset, Heading, Items, Totals, Break

class WorksheetSection:
    def __init__(self, comp, kind, rank=0, total_rank=0, hide_total=False):
        self.comp = comp
        self.kind = kind
        self.rank = rank
        self.total_rank = total_rank
        self.hide_total = hide_total

class FlowsWorksheet(Worksheet):

    def __init__(self, content, periods, data):
        self.content = content
        self.periods = periods
        self.data = data

    @staticmethod
    def load(defn, data):

        periods = data.get_periods()

        cont = defn.get("content")

        ws_elts = []

        for elt in cont:
            if isinstance(elt, str):
                ws_elts.append(WorksheetSection(elt))
            else:
                ws_elts.append(WorksheetSection(
                    elt.get("computation", None, mandatory=False),
                    elt.get("kind"),
                    rank=elt.get("rank", 0),
                    total_rank=elt.get("total-rank", 0),
                    hide_total=elt.get("hide-total", False)
                ))

        f = FlowsWorksheet(ws_elts, periods, data)

        return f

    def get_dataset(self):

        ds = Dataset(self.periods, [])

        computations = {}
        for v in self.content:
            if v.comp:
                computations[v.comp] = self.data.get_computation(v.comp)

        results = [
            self.data.perform_computations(period)
            for period in self.periods
        ]

        results = [
            {
                cid: computations[cid].get_output(results[i])
                for cid in computations
            }
            for i in range(0, len(self.periods))
        ]

        for cix in range(0, len(self.content)):

            comp_def = self.content[cix]

            if comp_def.kind == "break":
                sec = Break()
                ds.sections.append(sec)
                continue

            compid = comp_def.comp
            computation = computations[compid]

            if comp_def.kind == "heading":
                sec = Heading(computation.metadata)
                ds.sections.append(sec)
                continue

            if comp_def.kind == "items":
                sec = Items(computation, comp_def, results)
                ds.sections.append(sec)
                continue

            if comp_def.kind == "total":
                sec = Totals(computation, comp_def, results)
                ds.sections.append(sec)
                continue

            if comp_def.kind == "supertotal":
                sec = Totals(computation, comp_def, results, super_total=True)
                ds.sections.append(sec)
                continue

            raise RuntimeError(
                "Don't understand flows_sheet kind %s" % comp_def.kind
            )

        return ds

