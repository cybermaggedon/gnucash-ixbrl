
# A Composite element is used to wrap several elements into a single document.

from . basicelement import BasicElement

class HtmlElement(BasicElement):
    def __init__(self, id, root, data):
        super().__init__(id, data)
        self.root = root

    @staticmethod
    def load(elt_def, data):

        c = HtmlElement(
            elt_def.get("id"),
            elt_def.get("root"),
            data
        )
        return c

    def to_text(self, out):
        raise RuntimeError("Not implemented")

    def to_html(self, root, par, taxonomy):

        tag = root.get("tag")
        attrs = root.get("attributes", mandatory=False)
        content = root.get("content")

        if not attrs:
            attrs = {}
            
        if isinstance(content, str):
            return par.xhtml_maker(tag, attrs, str(content))

        elt = par.xhtml_maker(tag, attrs)

        for child in content:
            if isinstance(child, str):
                elt.append(par.xhtml_maker.span(child))
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

        return self.to_html(root, par, taxonomy)

#        raise RuntimeError("Not implemented")

#        elt = par.xhtml_maker.div({
#            "class": "composite",
#            "id": self.id + "-element"
#        })

#        for v in self.elements:

#            sub = v.to_ixbrl_elt(par, taxonomy)
#            elt.append(sub)
        
#        return elt
