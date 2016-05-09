#
# Copyright (C) 2016 Mattia Basaglia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from patsi.document.tree import *


class TestLayer(unittest.TestCase):
    def test_empty(self):
        l = Layer()
        self.assertEquals(l.text, "")
        self.assertEquals(l.color, None)
        self.assertEquals(l.width, 0)
        self.assertEquals(l.height, 0)

    def test_set_char(self):
        l = Layer("foo\nBar!\n")
        self.assertEquals(l.text, "foo\nBar!\n")
        self.assertEquals(l.color, None)
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)
        self.assertEquals(l.lines, ["foo", "Bar!"])
        self.assertEquals(l.lines[1][3], "!")
        l.set_char(1, 0, "X")
        self.assertEquals(l.lines[0][1], "X")
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)
        l.set_char(5, 5, "X")
        self.assertEquals(l.lines[5][5], "X")
        self.assertEquals(l.width, 6)
        self.assertEquals(l.height, 6)

    def test_empty_trailing_line(self):
        l = Layer("foo\nBar!\n\n")
        self.assertEquals(l.text, "foo\nBar!\n\n")
        self.assertEquals(l.height, 3)
        self.assertEquals(l.lines, ["foo", "Bar!", ""])

    def test_no_trailing_newline(self):
        l = Layer("foo\nBar!")
        self.assertEquals(l.text, "foo\nBar!\n")
        self.assertEquals(l.color, None)
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)
        self.assertEquals(l.lines, ["foo", "Bar!"])

    def test_color(self):
        l = Layer("foo\nBar!\n", RgbColor(1, 2, 3))
        self.assertEquals(l.text, "foo\nBar!\n")
        self.assertEquals(l.color, RgbColor(1, 2, 3))
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)


class TestFreeColorLayer(unittest.TestCase):
    def test_empty(self):
        l = FreeColorLayer()
        self.assertFalse(l.matrix)
        self.assertEquals(l.width, 0)
        self.assertEquals(l.height, 0)

    def test_set_char(self):
        l = FreeColorLayer()
        self.assertFalse((4, 5) in l.matrix)
        l.set_char(4, 5, "x", RgbColor(1, 2, 3))
        self.assertTrue((4, 5) in l.matrix)
        self.assertEquals(l.matrix[(4, 5)], ("x", RgbColor(1, 2, 3)))
        self.assertEquals(l.width, 5)
        self.assertEquals(l.height, 6)

        l.set_char(4, 5, "y", RgbColor(3, 2, 1))
        self.assertEquals(l.matrix[(4, 5)], ("y", RgbColor(3, 2, 1)))
        self.assertEquals(l.width, 5)
        self.assertEquals(l.height, 6)

        l.set_char(1, 1, "y")
        self.assertEquals(l.matrix[(1, 1)], ("y", None))
        self.assertEquals(l.width, 5)
        self.assertEquals(l.height, 6)

    def test_add_layer(self):
        l = FreeColorLayer()
        color_foo = RgbColor(0xf, 0, 0)
        l.add_layer(Layer("Foo", color_foo))
        self.assertEquals(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEquals(l.matrix[(1, 0)], ("o", color_foo))
        self.assertEquals(l.matrix[(2, 0)], ("o", color_foo))

        color_ubar = RgbColor(0xb, 0xa, 0x2)
        l.add_layer(Layer(" u\n b\n a\n r", color_ubar))
        self.assertEquals(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEquals(l.matrix[(1, 0)], ("u", color_ubar))
        self.assertEquals(l.matrix[(2, 0)], ("o", color_foo))
        self.assertEquals(l.matrix[(1, 1)], ("b", color_ubar))

        color_fun = RgbColor(0xf, 0xa, 0xf)
        l.add_layer(Layer("  n\n", color_fun))
        self.assertEquals(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEquals(l.matrix[(1, 0)], ("u", color_ubar))
        self.assertEquals(l.matrix[(2, 0)], ("n", color_fun))
        # TODO finish this


class TestDocument(unittest.TestCase):
    def test_ctor(self):
        doc = Document()
        self.assertEquals(doc.name, "")
        self.assertEquals(doc.layers, [])
        self.assertEquals(doc.metadata, {})

        doc = Document("foo")
        self.assertEquals(doc.name, "foo")
        self.assertEquals(doc.layers, [])
        self.assertEquals(doc.metadata, {})

        doc = Document("foo", [Layer()], {"foo": "bar"})
        self.assertEquals(doc.name, "foo")
        self.assertEquals(len(doc.layers), 1)
        self.assertEquals(doc.metadata, {"foo": "bar"})

    def test_flatten(self):
        doc = Document()
        layer = doc.flattened()
        self.assertIsInstance(layer, Layer)
        self.assertEquals(layer.text, "")

        doc.layers.append(Layer("Foo\n", RgbColor(1, 2, 3)))
        layer = doc.flattened()
        self.assertIsInstance(layer, Layer)
        self.assertEquals(layer.text, "Foo\n")
        self.assertEquals(layer.color, doc.layers[0].color)

        doc.layers.append(Layer("\nbar\n", RgbColor(3, 2, 1)))
        layer = doc.flattened()
        self.assertIsInstance(layer, FreeColorLayer)
        self.assertEquals(layer.matrix[(0, 0)], ("F", RgbColor(1, 2, 3)))
        self.assertEquals(layer.matrix[(0, 1)], ("b", RgbColor(3, 2, 1)))

        doc2 = doc.flattened_doc()
        self.assertEquals(len(doc2.layers), 1)
        self.assertIsInstance(doc2.layers[0], FreeColorLayer)
        self.assertEquals(doc2.layers[0].matrix, layer.matrix)

    def test_properties(self):
        doc = Document(layers=[Layer("Foo\n\nBar"), Layer("Hello")])
        self.assertEquals(doc.width, 5)
        self.assertEquals(doc.height, 3)



#TODO Test formatters

unittest.main()
