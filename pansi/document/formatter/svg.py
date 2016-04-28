from xml.sax.saxutils import escape
from .. import tree
from ...ansi import SGR

class SvgFormatter(object):

    def __init__(self, flatten=False, font_size=12):
        self.font_size = font_size
        self.flat = flatten

    @property
    def font_width(self):
        return self.font_size / 2.0

    def document(self, doc, output):
        width = doc.width * self.font_width
        height = doc.height * self.font_size

        output.write("<?xml version='1.0' encoding='UTF-8' ?>\n")
        output.write("<svg xmlns='http://www.w3.org/2000/svg' width='%s' height='%s'>\n" % (width, height))
        output.write("<rect style='fill:black;stroke:none;' width='%s' height='%s' x='0' y='0' />\n" % (width, height))

        if self.flat:
            self.layer(doc.flattened(), output)
        else:
            for layer in doc.layers:
                self.layer(layer, output)

        output.write("</svg>\n")


    def layer(self, layer, output):
        css = [
            "font-family:monospace",
            "font-size:%spx" % self.font_size,
            "font-weight:bold",
        ]
        open_rect = lambda: "<text y='0' x='0' style='%s' xml:space='preserve'>\n" % ";".join(css)

        if isinstance(layer, tree.Layer):
            css.append("fill:%s" % self.color(layer.color))
            css.append("letter-spacing:-%spx" % (self.font_width * 0.2))
            output.write(open_rect())
            y = 0
            for line in layer.text.split("\n"):
                y += 1
                output.write("<tspan x='{x}' y='{y}'>{line}</tspan>\n".format(
                    x=0,
                    y=y * self.font_size,
                    line=escape(line)
                ))
        elif isinstance(layer, tree.FreeColorLayer):
            output.write(open_rect())
            prev_color = None
            for pos, item in layer.matrix.iteritems():
                char, color = item
                if color is not tree.UnchangedColor and color != prev_color:
                    prev_color = color
                output.write("<tspan x='{x}' y='{y}' style='fill:{color};'>{char}</tspan>\n".format(
                    x=pos[0] * self.font_width,
                    y=pos[1] * self.font_size,
                    color=self.color(prev_color),
                    char=escape(char)
                ))
        else:
            raise TypeError("Expected layer type")

        output.write("</text>\n")

    def color(self, color):
        if color is None:
            return "inherit"
        return tree.hex_rgb(color.rgb)
