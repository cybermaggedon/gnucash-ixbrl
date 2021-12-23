
# A worksheet with a bunch of computations shown.

from . period import Period
from . worksheet import Worksheet
from . table import (
    Cell, Row, Index, Column, Table, TotalIndex
)
from . computation import Metadata, Group, Sum

class WorksheetSection:
    def __init__(self, id, rank=0, total_rank=0, hide_total=False):
        self.id = id
        self.rank = rank
        self.total_rank = total_rank
        self.hide_total = hide_total

class SimpleWorksheet(Worksheet):

    def __init__(self, comps, periods, data):
        self.computations = comps
        self.periods = periods
        self.data = data

    @staticmethod
    def load(defn, data):

        periods = data.get_periods()

        comps = defn.get("computations")

        ws_elts = []

        for comp in comps:
            if isinstance(comp, str):
                ws_elts.append(WorksheetSection(comp))
            else:
                ws_elts.append(WorksheetSection(
                    comp.get("id"),
                    rank=comp.get("rank", 0),
                    total_rank=comp.get("total-rank", 0),
                    hide_total=comp.get("hide-total", False)
                ))

        mpr = SimpleWorksheet(ws_elts, periods, data)

        return mpr

    def get_single_line_ix(self, computation, results):

        cells = []

        for period, result in results:
            cells.append(
                Cell(
                    computation.metadata,
                    computation.get_output(result).value
                )
            )

        ix = Index(computation.metadata, Row(cells))
        ixs.append(ix)

    def get_structure(self):

        if len(self.periods) < 1:
            raise RuntimeError("No periods in worksheet?")

        computations = {
            v.id: self.data.get_computation(v.id)
            for v in self.computations
        }

        self.currency_label = self.data.get_config(
            "metadata.accounting.currency-label", "€"
        )

        results = [
            (period, self.data.perform_computations(period))
            for period in self.periods
        ]

        columns = []
        for period in self.periods:
            m = Metadata(None, period.name, None, {}, period, None)
            col = Column(m, None, self.currency_label)
            columns.append(col)

#        columns = [
#            Column(Metadata(None, "FIXME", None, {}, None, None),
#                   columns, self.currency_label)
#        ]

        ixs = []

        for cix in range(0, len(self.computations)):

            comp_def = self.computations[cix]
            cid = comp_def.id
            computation = computations[cid]

            if isinstance(computation, Group):

                item_ixs = []
                for item in computation.inputs:
                    
                    cells = []
                    for period, result in results:
                        cells.append(
                            Cell(
                                item.metadata,
                                item.get_output(result).value
                            )
                        )
                    ix = Index(item.metadata, Row(cells))
                    item_ixs.append(ix)

                # Total
                cells = []
                for period, result in results:
                    cells.append(
                        Cell(
                            computation.metadata,
                            computation.get_output(result).value
                        )
                    )
                ix = TotalIndex(computation.metadata, Row(cells))
                item_ixs.append(ix)

                ix = Index(computation.metadata, item_ixs)
                ixs.append(ix)

            elif isinstance(computation, Sum):

                # Total
                cells = []
                for period, result in results:
                    cells.append(
                        Cell(
                            computation.metadata,
                            computation.get_output(result).value
                        )
                    )
                ix = Index(computation.metadata, Row(cells))
                ixs.append(ix)

            else:
                raise RuntimeError("Type %s not implemented" %
                                   str(type(computation)))

        tbl = Table(columns, ixs)

        return tbl
