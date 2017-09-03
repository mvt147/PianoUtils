import os
import json
import xmltodict
import xml.etree.ElementTree as Et
from unittest import TestCase
from copy import deepcopy
from piano_utils.pubmed_converter import pubmed_xml_to_json, json_to_pubmed_xml, \
    pubmed_xml_to_piano, pubmed_json_to_piano


class TestPubMedConverter(TestCase):

    @classmethod
    def setUpClass(cls):
        """
        create/setup test data
        :return:
        """
        cls.pmids = ["26419243", "26138797"]
        cls.titles = [
            "Post-concussion syndrome (PCS) in a youth population: defining the diagnostic value and cost-utility of brain imaging.",
            "The role of the cervical spine in post-concussion syndrome."
        ]
        cls.paginations = ["2305-9", "274-84"]
        cls.authors = [[
            {"ForeName": "Clinton D", "LastName": "Morgan"},
            {"ForeName": "Scott L", "LastName": "Zuckerman"},
            {"ForeName": "Lauren E", "LastName": "King"},
            {"ForeName": "Susan E", "LastName": "Beaird"},
            {"ForeName": "Allen K", "LastName": "Sills"},
            {"ForeName": "Gary S", "LastName": "Solomon"},
        ], [
            {"ForeName": "Cameron M", "LastName": "Marshall"},
            {"ForeName": "Howard", "LastName": "Vernon"},
            {"ForeName": "John J", "LastName": "Leddy"},
            {"ForeName": "Bradley A", "LastName": "Baldwin"},
        ]]
        cls.keywords = [[
            {"Adolescent": {"MajorTopicYN": "N"}},
            {"Brain": {"MajorTopicYN": "N", "Qualifiers": [("diagnostic imaging", "Y"), ("pathology", "Y")]}},
            {"Child": {"MajorTopicYN": "N"}},
            {"Child, Preschool": {"MajorTopicYN": "N"}},
            {"Female": {"MajorTopicYN": "N"}},
            {"Humans": {"MajorTopicYN": "N"}},
            {"Image Processing, Computer-Assisted": {"MajorTopicYN": "N"}},
            {"Magnetic Resonance Imaging": {"MajorTopicYN": "N"}},
            {"Male": {"MajorTopicYN": "N"}},
            {"Post-Concussion Syndrome": {"MajorTopicYN": "N", "Qualifiers": [("diagnosis", "Y")]}},
            {"Retrospective Studies": {"MajorTopicYN": "N"}},
            {"Tomography, X-Ray Computed": {"MajorTopicYN": "N"}},
        ], [
            {"Adult": {"MajorTopicYN": "N"}},
            {"Brain Concussion": {"MajorTopicYN": "N", "Qualifiers": [("physiopathology", "N")]}},
            {"Cervical Vertebrae": {"MajorTopicYN": "N", "Qualifiers": [("physiopathology", "Y")]}},
            {"Female": {"MajorTopicYN": "N"}},
            {"Humans": {"MajorTopicYN": "N"}},
            {"Male": {"MajorTopicYN": "N"}},
            {"Middle Aged": {"MajorTopicYN": "N"}},
            {"Post-Concussion Syndrome": {"MajorTopicYN": "N", "Qualifiers": [("complications", "N"), ("physiopathology", "Y")]}},
            {"Whiplash Injuries": {"MajorTopicYN": "N", "Qualifiers": [("complications", "N"), ("physiopathology", "N")]}},
            {"Young Adult": {"MajorTopicYN": "N"}},
        ]]

        cls.pubmed_xmls = [
            open(os.path.join(os.path.dirname(__file__), 'single_pubmed_xml_article.xml')).read(),
            open(os.path.join(os.path.dirname(__file__), 'multiple_pubmed_xml_articles.xml')).read()
        ]

        cls.pubmed_jsons = []
        for article_idx, pmid in enumerate(cls.pmids):
            pubmed_json = {
                "MedlineCitation_PMID_#text": cls.pmids[article_idx],
                "MedlineCitation_PMID_@Version": "1",
                "MedlineCitation_Article_ArticleTitle": cls.titles[article_idx],
                "MedlineCitation_Article_Pagination_MedlinePgn": cls.paginations[article_idx],
                "PubmedData_PublicationStatus": "ppublish",
            }

            for idx, a in enumerate(cls.authors[article_idx]):
                for k in a:
                    key = "MedlineCitation_Article_AuthorList_Author_%s_%s" % (str(idx), k)
                    pubmed_json[key] = a[k]

            keywords = cls.keywords[article_idx]
            for idx, keyword in enumerate(keywords):
                keyword_name = keyword.keys()[0]
                pubmed_json["MedlineCitation_MeshHeadingList_MeshHeading_%s_DescriptorName_#text" % str(idx)] = keyword_name
                pubmed_json["MedlineCitation_MeshHeadingList_MeshHeading_%s_DescriptorName_@MajorTopicYN" % str(idx)] = "N"
                qualifiers = keyword[keyword_name].get("Qualifiers", [])
                for q_idx, qualifier in enumerate(qualifiers):
                    key = "MedlineCitation_MeshHeadingList_MeshHeading_%s_QualifierName_" % str(idx)
                    if len(qualifiers) > 1:
                        key += str(q_idx) + "_"
                    pubmed_json[key + "#text"] = qualifier[0]
                    pubmed_json[key + "@MajorTopicYN"] = qualifier[1]

            cls.pubmed_jsons.append(pubmed_json)

    def get_keywords_as_string(self, article_idx):
        keywords = self.keywords[article_idx]
        keyword_list = []
        for keyword in keywords:
            keyword_name = keyword.keys()[0]
            qualifiers = []
            for q in keyword[keyword_name].get("Qualifiers", []):
                qualifier = q[0]
                if q[1] == "Y":
                    qualifier = "*" + qualifier
                qualifiers.append(qualifier)
            keyword_list.append("/".join([keyword_name] + qualifiers))
        return ",".join(keyword_list)

    def test_xml_to_json(self):
        """
        test conversion from xml to json
        :return:
        """
        original_xml = deepcopy(self.pubmed_xmls[0])

        # convert xml to json
        result = json.loads(pubmed_xml_to_json(original_xml))
        self.assertTrue(isinstance(result, list))

        result = result[0]

        # check is flattened
        for v in result.values():
            self.assertNotIsInstance(v, dict)
            self.assertNotIsInstance(v, list)

        # check values
        for k, v in self.pubmed_jsons[0].iteritems():
            self.assertEquals(v, result[k])

    def test_xml_to_json__with_multiple(self):
        """
        test conversion from xml to json with multiple articles in xml
        :return:
        """
        original_xml = deepcopy(self.pubmed_xmls[1])

        # convert xml to json
        result = json.loads(pubmed_xml_to_json(original_xml))
        self.assertTrue(isinstance(result, list))

        # check is flattened
        for article in result:
            for v in article.values():
                self.assertNotIsInstance(v, dict)
                self.assertNotIsInstance(v, list)

        # check values
        for idx, pubmed_json in enumerate(self.pubmed_jsons):
            for k, v in pubmed_json.iteritems():
                self.assertEquals(v, result[idx][k])

    def check_xml(self, article_idx, xml_string):
        original_json = self.pubmed_jsons[article_idx]

        result_tree = Et.fromstring(xml_string)
        medline_citation = result_tree[article_idx].find("MedlineCitation")
        pubmed_data = result_tree[article_idx].find("PubmedData")

        # check PMID
        self.assertEquals(self.pmids[article_idx], medline_citation.find("PMID").text)
        self.assertEquals(original_json["MedlineCitation_PMID_@Version"],
                          medline_citation.find("PMID").attrib["Version"])

        # check title
        article = medline_citation.find("Article")
        self.assertEquals(self.titles[article_idx], article.find("ArticleTitle").text)

        # check authors
        authors = article.find("AuthorList")
        for idx, author in enumerate(authors.findall("Author")):
            for e in ["ForeName", "LastName"]:
                self.assertEquals(original_json["MedlineCitation_Article_AuthorList_Author_%s_%s" % (str(idx), e)],
                                  author.find(e).text)

        # check pagination
        pagination = article.find("Pagination")
        self.assertEquals(self.paginations[article_idx],
                          pagination.find("MedlinePgn").text)

        # check publication status
        self.assertEquals(original_json["PubmedData_PublicationStatus"],
                          pubmed_data.find("PublicationStatus").text)

    def test_json_to_xml(self):
        """
        test conversion from json to xml
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons[0])

        # convert from json to xml
        result = json_to_pubmed_xml(json.dumps(original_json))

        self.check_xml(0, result)

    def test_json_to_xml__with_multiple(self):
        """
        test conversion from json to xml with multiple articles
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons)

        # convert from json to xml
        result = json_to_pubmed_xml(json.dumps(original_json))

        for idx, _ in enumerate(original_json):
            self.check_xml(idx, result)

    def test_xml_to_json_to_xml(self):
        """
        test conversion from xml to json, then back from json to xml and ensure they are equal
        :return:
        """
        original_xml = deepcopy(self.pubmed_xmls[0])

        # convert xml to json
        xml_as_json = json.loads(pubmed_xml_to_json(deepcopy(original_xml)))

        # convert json back to xml
        json_as_xml = json_to_pubmed_xml(json.dumps(xml_as_json[0]))

        # format result and expected result into dictionaries
        result = json.loads(json.dumps(xmltodict.parse(json_as_xml)))
        expects = json.loads(json.dumps(xmltodict.parse(original_xml)))

        # compare dictionary values
        self.assertDictEqual(result, expects)

    def test_xml_to_json_to_xml__with_multiple(self):
        """
        test conversion from xml to json, then back from json to xml with multiple articles
        :return:
        """
        original_xml = deepcopy(self.pubmed_xmls[1])

        # convert xml to json
        xml_as_json = json.loads(pubmed_xml_to_json(deepcopy(original_xml)))

        # convert json back to xml
        json_as_xml = json_to_pubmed_xml(json.dumps(xml_as_json))

        # format result and expected result into dictionaries
        result = json.loads(json.dumps(xmltodict.parse(json_as_xml)))
        expects = json.loads(json.dumps(xmltodict.parse(original_xml)))

        # compare dictionary values
        self.assertDictEqual(result, expects)

    def test_json_to_xml_to_json(self):
        """
        test conversion from json to xml, then back from xml to json and ensure they are equal
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons[0])

        # convert json to xml
        json_as_xml = json_to_pubmed_xml(json.dumps(original_json))

        # convert xml back to json
        xml_as_json = json.loads(pubmed_xml_to_json(json_as_xml))

        # compare results
        self.assertDictEqual(original_json, xml_as_json[0])

    def test_json_to_xml_to_json__with_multiple(self):
        """
        test conversion from json to xml, then back from xml to json with multiple articles
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons)

        # convert json to xml
        json_as_xml = json_to_pubmed_xml(json.dumps(original_json))

        # convert xml back to json
        xml_as_json = json.loads(pubmed_xml_to_json(json_as_xml))

        # compare results
        self.assertEquals(len(original_json), len(xml_as_json))
        for idx, d in enumerate(original_json):
            self.assertDictEqual(d, xml_as_json[idx])

    def check_piano(self, article_idx, doc):
        """
        perform tests on a piano document against the test data
        :param article_idx: index of article in test data
        :param doc: piano document to check
        :return:
        """
        # check pmid
        self.assertEquals(self.pmids[article_idx], doc.get("pmid", ""))

        # check title
        self.assertEquals(self.titles[article_idx], doc.get("title", ""))

        # check authors
        self.assertEquals(["%s, %s" % (a["LastName"], a["ForeName"]) for a in self.authors[article_idx]],
                          doc.get("authors", []))

        # check pagination
        self.assertEquals(self.paginations[article_idx], doc.get("pages", ""))

        # check keywords
        self.assertEquals(self.get_keywords_as_string(article_idx), doc.get("keywords", ""))

    def test_xml_to_piano(self):
        """
        test conversion from xml to piano
        :return:
        """
        original_xml = deepcopy(self.pubmed_xmls[0])

        # convert xml to piano documents
        piano_docs = pubmed_xml_to_piano(original_xml)
        self.assertEquals(1, len(piano_docs))
        self.check_piano(0, piano_docs[0])

    def test_xml_to_piano__with_multiple(self):
        """
        test conversion from xml to piano with multiple articles
        :return:
        """
        original_xml = deepcopy(self.pubmed_xmls[1])

        # convert xml to piano documents
        piano_docs = pubmed_xml_to_piano(original_xml)
        self.assertEquals(3, len(piano_docs))
        self.check_piano(0, piano_docs[0])
        self.check_piano(1, piano_docs[1])

    def test_json_to_piano(self):
        """
        test conversion from json to piano
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons[0])

        # convert json to piano documents
        piano_docs = pubmed_json_to_piano(json.dumps(original_json))
        self.assertEquals(1, len(piano_docs))
        self.check_piano(0, piano_docs[0])

    def test_json_to_piano__with_multiple(self):
        """
        test conversion from json to piano with multiple articles
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons)

        # convert json to piano documents
        piano_docs = pubmed_json_to_piano(json.dumps(original_json))
        self.assertEquals(2, len(piano_docs))
        self.check_piano(0, piano_docs[0])
        self.check_piano(1, piano_docs[1])

    def test_json_to_piano__with_non_pubmed_fields(self):
        original_json = deepcopy(self.pubmed_jsons[0])

        _id = "59ac8d07e247e100189ae0ea"
        uuid = "af93cac5-b6f9-4c0c-9ba1-3c4a360f637"
        original_json["_id"] = _id
        original_json["uuid"] = uuid

        # convert json to piano documents
        piano_docs = pubmed_json_to_piano(json.dumps(original_json))
        self.assertEquals(1, len(piano_docs))
        self.check_piano(0, piano_docs[0])

        self.assertEquals(_id, piano_docs[0]["_id"])
        self.assertEquals(uuid, piano_docs[0]["uuid"])

    def test_json_to_piano__with_multiple_non_pubmed_fields(self):
        """
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons)

        for idx, j in enumerate(original_json):
            j["_id"] = "59ac8d07e247e100189ae0ea_" + str(idx)
            j["uuid"] = "af93cac5-b6f9-4c0c-9ba1-3c4a360f637_" + str(idx)

        # convert json to piano documents
        piano_docs = pubmed_json_to_piano(json.dumps(original_json))
        self.assertEquals(2, len(piano_docs))
        self.check_piano(0, piano_docs[0])
        self.check_piano(1, piano_docs[1])

        for idx, d in enumerate(piano_docs):
            self.assertEquals("59ac8d07e247e100189ae0ea_" + str(idx), d["_id"])
            self.assertEquals("af93cac5-b6f9-4c0c-9ba1-3c4a360f637_" + str(idx), d["uuid"])
