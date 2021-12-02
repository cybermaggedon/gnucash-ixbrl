
# A Composite element is used to wrap several elements into a single document.

from . basicelement import BasicElement
from . notes import NoteExpansion
from . datum import StringDatum
from . worksheetelement import WorksheetElement
from . note_parse import *

from lxml import objectify, etree

def expand_string(value, data):

    # If it's just a string, (no expand: prefix) return a StringElt
    if not value.startswith("expand:"):
        return StringElt(value, data)

    # This is expand: without note:, return a template elt
    if not value.startswith("expand:note:"):
        return TemplateElt(value[7:], data)

    # The rest of this is the expand:note case.

    value = value[12:]

    stack = []
    tkstack = []
    content = []

    exp = NoteParser.parse(value)
    for tk in exp:
        if isinstance(tk, TextToken):
            content.append(StringElt(tk.text, data))
        elif isinstance(tk, MetadataToken):
            content.append(
                MetadataElt(tk.name, tk.prefix, tk.suffix, tk.null, data)
            )
        elif isinstance(tk, ComputationToken):
            content.append(
                ComputationElt(tk.name, tk.period)
            )
        elif isinstance(tk, TagOpen):
            if tk.kind != "string":
                raise RuntimeError("Only string tags, currently")
            tkstack.append(tk)
            stack.append(content)
            content = []
        elif isinstance(tk, TagClose):
            ftk = tkstack[-1]
            tkstack.pop()
            elt = FactElt(ftk.name, ftk.context, {}, content, data)
            content = stack[-1]
            stack.pop()
            content.append(elt)
    
    return TagElt("span", {}, content, data)

class Elt:
    @staticmethod
    def load(root, data):

        if isinstance(root, str):
            return expand_string(root, data)
#            return StringElt.load(root, data)

        if "tag" in root:
            return TagElt.load(root, data)

        if "fact" in root:
            return FactElt.load(root, data)

        if "element" in root:
            return ElementElt.load(root, data)

        if "worksheet" in root:
            return WorksheetElt.load(root, data)

        if "ifdef" in root:
            return IfdefElt.load(root, data)

        raise RuntimeError("Can't handle ", root)

class TagElt(Elt):
    def __init__(self, tag, attrs, content, data):
        self.tag = tag
        self.attrs = attrs
        self.content = content
        self.data = data

    @staticmethod
    def load(root, data):
        tag = root.get("tag")
        attrs = root.get("attributes", {}, mandatory=False)
        content = root.get("content", [], mandatory=False)

        if isinstance(content, str):
            content = [Elt.load(content, data)]
        elif isinstance(content, list):
            content = [Elt.load(v, data) for v in content]
        elif isinstance(content, dict):
            content = [Elt.load(content, data)]
        else:
            raise RuntimeError(
                "Can't handle content being type %s" % str(type(content))
            )

        return TagElt(tag, attrs, content, data)

    def to_html(self, par, taxonomy):

        elt = par.xhtml_maker(self.tag, self.attrs)

        for c in self.content:
            elt.append(c.to_html(par, taxonomy))

        return elt

class IfdefElt(Elt):
    def __init__(self, key, content, data):
        self.key = key
        self.content = content
        self.data = data

    @staticmethod
    def load(root, data):
        key = root.get("ifdef")
        content = root.get("content")
        content = Elt.load(content, data)
        return IfdefElt(key, content, data)

    def to_html(self, par, taxonomy):

        try:
            self.data.get_config(ifdef)
        except:
            return par.xhtml_maker.span()

        return self.content.to_html(par, taxonomy)

class TemplateElt(Elt):
    def __init__(self, value, data):
        self.value = value
        self.data = data

    def to_html(self, par, taxonomy):
        note = taxonomy.get_note(self.value)

        # FIXME: Logic error?
        note = "expand:note:" + note
        return expand_string(note, self.data).to_html(par, taxonomy)
#        return par.xhtml_maker.span("FIXME: " + note)

class MetadataElt(Elt):
    def __init__(self, name, prefix, suffix, null, data):
        self.name = name
        self.prefix = prefix
        self.suffix = suffix
        self.null = null
        self.data = data

    def to_html(self, par, taxonomy):

        elt = par.xhtml_maker.span()

        fact = taxonomy.get_metadata_by_id(self.data, self.name)
        if fact:
            if self.prefix != "":
                elt.append(par.xhtml_maker.span(self.prefix))
            elt.append(fact.to_elt(par))
            if self.suffix != "":
                elt.append(par.xhtml_maker.span(self.suffix))
            return elt

        val = self.data.get_config(self.name, mandatory=False)
        if val:
            if self.prefix != "":
                elt.append(par.xhtml_maker.span(self.prefix))
            elt.append(par.xhtml_maker.span(str(val)))
            if self.suffix != "":
                elt.append(par.xhtml_maker.span(self.suffix))
            return elt

        return par.xhtml_maker.span(self.null)

class StringElt(Elt):
    def __init__(self, value, data):
        self.value = value
        self.data = data

    @staticmethod
    def load(value, data):

        if not value.startswith("expand:"):
            return StringElt(value, data)

        if not value.startswith("expand:note:"):
            return TemplateElt(value[7:], data)

        value = value[12:]

        stack = []
        tkstack = []
        content = []

        exp = NoteParser.parse(value)
        for tk in exp:
            if isinstance(tk, TextToken):
                content.append(StringElt(tk.text, data))
            elif isinstance(tk, MetadataToken):
                content.append(
                    MetadataElt(tk.name, tk.prefix, tk.suffix, tk.null, data)
                )
            elif isinstance(tk, ComputationToken):
                content.append(
                    ComputationElt(tk.name, tk.period)
                )
            elif isinstance(tk, TagOpen):
                if tk.kind != "string":
                    raise RuntimeError("Only string tags, currently")
                tkstack.append(tk)
                stack.append(content)
                content = []
            elif isinstance(tk, TagClose):
                ftk = tkstack[-1]
                tkstack.pop()
                elt = FactElt(ftk.name, ftk.context, {}, content, data)
                content = stack[-1]
                stack.pop()
                content.append(elt)

        return TagElt("span", {}, content, data)

    def to_html(self, par, taxonomy):
        return par.xhtml_maker.span(self.value)

class FactElt(Elt):
    def __init__(self, fact, ctxt, attrs, content, data):
        self.fact = fact
        self.ctxt = ctxt
        self.attrs = attrs
        self.content = content
        self.data = data
    @staticmethod
    def load(root, data):
        fact = root.get("fact")
        attrs = root.get("attributes", {}, mandatory=False)
        content = root.get("content", [], mandatory=False)

        if isinstance(content, str):
            content = [Elt.load(content, data)]
        elif isinstance(content, list):
            content = [Elt.load(v, data) for v in content]
        elif isinstance(content, dict):
            content = [Elt.load(content, data)]
        else:
            raise RuntimeError(
                "Can't handle content being type %s" % str(type(content))
            )

        ctxt = root.get("context")
        return FactElt(fact, ctxt, attrs, content, data)

    def to_html(self, par, taxonomy):

        if self.ctxt == None:
            period = self.data.get_report_period()
            ctxt = self.data.business_context.with_period(period)
        else:
            ctxt = taxonomy.get_context(self.ctxt, self.data)
        datum = StringDatum(self.fact, [], ctxt)
        fact = taxonomy.create_fact(datum)
        elt = fact.to_elt(par)

        for child in self.content:
            elt.append(child.to_html(par, taxonomy))

        return elt

class ElementElt(Elt):
    def __init__(self, elt, data):
        self.elt = elt
        self.data = data
    @staticmethod
    def load(root, data):
        element = root.get("element")

        if isinstance(element, str):
            return ElementElt(data.get_element(element), data)
        elif isinstance(element, dict):
            return ElementElt(data.get_element(element), data)
        else:        
            raise RuntimeError(
                "Can't handle element being type %s" % str(type(content))
            )

    def to_html(self, par, taxonomy):

        content = self.elt.to_ixbrl_elt(par, taxonomy)
        
        cntr = par.xhtml_maker.div()
        for c in content:
            cntr.append(c)

        return cntr

class WorksheetElt(Elt):

    def __init__(self, ws, data):
        self.wse = ws
        self.data = data

    @staticmethod
    def load(root, data):
        wse = WorksheetElement.load(root, data)
        return WorksheetElt(wse, data)

    def to_html(self, par, taxonomy):

        # Assumption about WorksheetElement: Returns single element in list
        return self.wse.to_ixbrl_elt(par, taxonomy)[0]


class HtmlElement(BasicElement):
    def __init__(self, id, root, data):
        super().__init__(id, data)
        self.root = root

    @staticmethod
    def load(elt_def, data):

        id = elt_def.get("id", mandatory=False)
        root = elt_def.get("root")
        root = Elt.load(root, data)

        c = HtmlElement(id, root, data)

        return c

    def html_to_text(self, root, out):

        if root.tag == "{http://www.w3.org/1999/xhtml}span":
            if root.text: out.write(root.text)
        else:
            if root.text: out.write(root.text + "\n")

        for child in root.getchildren():
            self.html_to_text(child, out)

    def write_text(self, root, out, taxonomy):

        content = root.get("content", mandatory=False)

        if not content:
            content = []
            
        if isinstance(content, str):

            content = self.expand_text(content, self, taxonomy)

            if isinstance(content, str):
                out.write(content + "\n")
            else:
                for elt in content:
                    self.html_to_text(elt, out)

            return

        for child in content:

            if isinstance(child, str):
                child = self.expand_text(child, self, taxonomy)

                if isinstance(child, str):
                    out.write(child + "\n")
                else:
                    for child2 in child:
                        self.html_to_text(child2, out)

            elif isinstance(child, dict):
                self.write_text(child, out, taxonomy)
            else:
                raise RuntimeError(
                    "HTMLElement can't work with content of type %s" %
                    str(type(child))
                )

    def to_text(self, taxonomy, out):

        self.init_html(taxonomy)
        self.write_text(self.root, out, taxonomy)

    def expand_text(self, text, par, taxonomy):

        if not text.startswith("expand:"): return text

        ne = NoteExpansion(self.data)
        return ne.expand(text[7:], par, taxonomy)

    def to_html(self, root, par, taxonomy):

        return root.to_html(par, taxonomy)

        # FIXME: Too many logic paths through this functiona, refactor?
        ifdef = root.get("ifdef", mandatory=False)
        if ifdef:
            try:
                self.data.get_config(ifdef)
            except:
                # Tag does not exist.
                return par.xhtml_maker.span()

            # No exception, the config element exists
            content = root.get("content")
            return self.to_html(content, par, taxonomy)

        iftrue = root.get("iftrue", mandatory=False)
        if iftrue:
            if self.data.get_config_bool(iftrue, False, mandatory=False):
                # No exception, the config element exists
                content = root.get("content")
                return self.to_html(content, par, taxonomy)
            else:
                # Tag is not true.
                return par.xhtml_maker.span()

        iffalse = root.get("iffalse", mandatory=False)
        if iffalse:
            if not self.data.get_config_bool(iffalse, False, mandatory=False):
                # No exception, the config element exists
                content = root.get("content")
                return self.to_html(content, par, taxonomy)
            else:
                # Tag is not true.
                return par.xhtml_maker.span()

        tag = root.get("tag", mandatory=False)
        fact = root.get("fact", mandatory=False)

        worksheet = root.get("worksheet", mandatory=False)
        if worksheet:

            wse = WorksheetElement.load(root, self.data)
            return wse.to_ixbrl_elt(par, taxonomy)[0]

            # Assumption about WorksheetElement: Returns single element in list
            return wse.to_ixbrl_elt(par, taxonomy)[0]

        element = root.get("element", mandatory=False)
        if element:

            if isinstance(element, str):
            
                elt = self.data.get_element(element)

                cntr = par.xhtml_maker.div()

                # Assumption about Element: Returns single element in list
                for child in elt.to_ixbrl_elt(par, taxonomy):
                    cntr.append(child)

                return cntr

            else:
                elt = self.data.get_element(element)
                
                cntr = par.xhtml_maker.div()

                # Assumption about Element: Returns single element in list
                for child in elt.to_ixbrl_elt(par, taxonomy):
                    cntr.append(child)

                return cntr


        if not tag and not fact:
            raise RuntimeError(
                "HTML elements must have tag, fact, etc. property"
            )

        attrs = root.get("attributes", mandatory=False)
        content = root.get("content", mandatory=False)

        if not attrs:
            attrs = {}

        if not content:
            content = []

        if fact:
            context_id = root.get("context")
            ctxt = taxonomy.get_context(context_id, self.data)

        if isinstance(content, int):
            content = str(content)
        if isinstance(content, bool):
            content = str(content)
        if isinstance(content, float):
            content = str(content)

        # The content element is a string
        if isinstance(content, str):

            content = self.expand_text(content, par, taxonomy)

            if isinstance(content, str):

                # Expands to a string
                if fact:
                    datum = StringDatum(fact, content, ctxt)
                    fact = taxonomy.create_fact(datum)
                    return fact.to_elt(par)
                else:
                    return par.xhtml_maker(tag, attrs, content)

            else:

                # Expands to a list of elements
                elt = par.xhtml_maker(tag, attrs)
                for child in content:
                    elt.append(child)
                return elt

        # The content element is an array of elts.

        # If fact, parent elt is a fact tag
        if fact:
            datum = StringDatum(fact, [], ctxt)
            fact = taxonomy.create_fact(datum)
            elt = fact.to_elt(par)
        else:
            elt = par.xhtml_maker(tag, attrs)
        
        for child in content:
            if isinstance(child, str):
                child = self.expand_text(child, par, taxonomy)
                if isinstance(child, str):
                    elt.append(par.xhtml_maker.span(child))
                else:
                    for child2 in child:
                        if isinstance(child2, str):
                            elt.append(par.xhtml_maker.span(child2))
                        else:
                            elt.append(child2)
            elif isinstance(child, dict):
                elt.append(self.to_html(child, par, taxonomy))
            else:
                raise RuntimeError(
                    "HTMLElement can't work with content of type %s" %
                    str(type(child))
                )

        return elt

    def to_ixbrl_elt(self, par, taxonomy):

        root = self.root

        return [self.to_html(root, par, taxonomy)]
