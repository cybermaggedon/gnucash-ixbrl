#!/usr/bin/env python3

from lxml import etree as ET
from lxml.isoschematron import Schematron

tree = ET.parse("accts.html")

sch = Schematron(ET.parse("rules.xml"), store_report=True)

res = sch.validate(tree)
print(res)

report = sch.validation_report

print(report)
