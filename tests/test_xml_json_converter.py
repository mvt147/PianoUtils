import os
import json
import xmltodict
import xml.etree.ElementTree as Et
from unittest import TestCase
from copy import deepcopy
from piano_utils.xml_json_converter import xml_to_json, json_to_xml


class TestXmlJsonConverter(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        create/setup test data
        :return:
        """
        cls.simple_xml = open(os.path.join(os.path.dirname(__file__), 'simple_xml.xml')).read()

        cls.simple_json = {
            "note_to": "Tove",
            "note_from": "Jani",
            "note_heading": "Reminder",
            "note_body": "Don't forget me this weekend!",
        }

        cls.complex_xml = open(os.path.join(os.path.dirname(__file__), 'complex_xml.xml')).read()

        cls.catalog = [{
            "title": "Empire Burlesque",
            "artist": "Bob Dylan",
            "prices": ("10.90", "8.99"),
            "year": "1985",
        }, {
            "title": "Hide Your Heart",
            "artist": "Bonnie Tyler",
            "prices": ("9.90", "7.50"),
            "year": "1988",
        }, {
            "title": "One Night Only",
            "artist": "Bee Gees",
            "prices": ("10.90", "5.99"),
            "year": "1998",
        }]

        cls.complex_json = {}
        for idx, cd in enumerate(cls.catalog):
            for k in ["title", "artist", "prices", "year"]:
                key = "catalog_cd_%s_%s" % (str(idx), k)
                if k == "prices":
                    cls.complex_json[key + "_price_0_@type"] = "rrp"
                    cls.complex_json[key + "_price_0_#text"] = cd[k][0]
                    cls.complex_json[key + "_price_1_@type"] = "special"
                    cls.complex_json[key + "_price_1_#text"] = cd[k][1]
                else:
                    cls.complex_json[key] = cd[k]

        cls.complex_json = [cls.complex_json]

    def test_xml_to_json(self):
        """
        test conversion from xml to json
        :return:
        """
        original_xml = self.simple_xml

        xml_as_json = json.loads(xml_to_json(original_xml))

        self.assertDictEqual(self.simple_json, xml_as_json[0])

    def test_xml_to_json__with_multiple(self):
        """
        test conversion from xml to json with multiple tags
        :return:
        """
        original_xml = deepcopy(self.complex_xml)

        # convert xml to json
        result = json.loads(xml_to_json(original_xml))
        self.assertTrue(isinstance(result, list))

        # check is flattened
        for article in result:
            for v in article.values():
                self.assertNotIsInstance(v, dict)
                self.assertNotIsInstance(v, list)

        # check values
        for idx, json_value in enumerate(self.complex_json):
            for k, v in json_value.iteritems():
                self.assertEquals(v, result[idx][k])

    def test_json_to_xml(self):
        """
        test conversion from json to xml
        :return:
        """
        original_json = deepcopy(self.simple_json)

        json_as_xml = json_to_xml(json.dumps(original_json))

        xml_tree = Et.fromstring(json_as_xml)
        self.assertEquals("note", xml_tree.tag)
        self.assertEquals(original_json["note_to"], xml_tree.find("to").text)
        self.assertEquals(original_json["note_from"], xml_tree.find("from").text)
        self.assertEquals(original_json["note_heading"], xml_tree.find("heading").text)
        self.assertEquals(original_json["note_body"], xml_tree.find("body").text)

    def test_json_to_xml__with_multiple(self):
        """
        test conversion from json to xml with multiple tags
        :return:
        """
        original_json = deepcopy(self.complex_json)

        # convert from json to xml
        json_as_xml = json_to_xml(json.dumps(original_json[0]))

        for idx, json_value in enumerate(original_json):
            xml_tree = Et.fromstring(json_as_xml)
            cd = xml_tree[idx]
            self.assertEquals(self.catalog[idx]["title"], cd.find("title").text)
            self.assertEquals(self.catalog[idx]["artist"], cd.find("artist").text)
            self.assertEquals(self.catalog[idx]["year"], cd.find("year").text)
            prices = cd.find("prices")
            price_types = ["rrp", "special"]
            for p_idx, price in enumerate(prices.findall("price")):
                self.assertEquals(self.catalog[idx]["prices"][p_idx], price.text)
                self.assertEquals(price_types[p_idx], price.get("type", ""))

    def test_xml_to_json_to_xml(self):
        """
        test conversion from xml to json, and back from json to xml
        :return:
        """
        original_xml = deepcopy(self.simple_xml)

        # convert xml to json
        xml_as_json = json.loads(xml_to_json(deepcopy(original_xml)))

        # convert json back to xml
        json_as_xml = json_to_xml(json.dumps(xml_as_json[0]))

        # format result and expected result into dictionaries
        actual = json.loads(json.dumps(xmltodict.parse(json_as_xml)))
        expect = json.loads(json.dumps(xmltodict.parse(original_xml)))

        # compare dictionary values
        self.assertDictEqual(actual, expect)

    def test_xml_to_json_to_xml__with_multiple(self):
        """
        test conversion from xml to json, and back from json to xml with multiple tags
        :return:
        """
        original_xml = deepcopy(self.complex_xml)

        # convert xml to json
        xml_as_json = json.loads(xml_to_json(deepcopy(original_xml)))

        # convert json back to xml
        json_as_xml = json_to_xml(json.dumps(xml_as_json[0]))

        # format result and expected result into dictionaries
        result = json.loads(json.dumps(xmltodict.parse(json_as_xml)))
        expects = json.loads(json.dumps(xmltodict.parse(original_xml)))

        # compare dictionary values
        self.assertDictEqual(result, expects)

    def test_json_to_xml_to_json(self):
        """
        test conversion from json to xml, and back from xml to json
        :return:
        """
        original_json = deepcopy(self.simple_json)

        # convert json to xml
        json_as_xml = json_to_xml(json.dumps(original_json))

        # convert xml back to json
        xml_as_json = json.loads(xml_to_json(json_as_xml))

        # compare results
        self.assertDictEqual(original_json, xml_as_json[0])

    def test_json_to_xml_to_json__with_multiple(self):
        """
        test conversion from json to xml, and back from xml to json with multiple tags
        :return:
        """
        original_json = deepcopy(self.complex_json)

        # convert json to xml
        json_as_xml = json_to_xml(json.dumps(original_json[0]))

        # convert xml back to json
        xml_as_json = json.loads(xml_to_json(json_as_xml))

        # compare results
        self.assertEquals(len(original_json), len(xml_as_json))
        for idx, d in enumerate(original_json):
            self.assertDictEqual(d, xml_as_json[idx])
