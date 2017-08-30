import os
import json
import xmltodict
import xml.etree.ElementTree as Et
from unittest import TestCase
from copy import deepcopy
from pubmed_converter import pubmed_xml_to_json, json_to_pubmed_xml, pubmed_xml_to_piano, pubmed_json_to_piano


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
            "Adolescent", "Brain/*diagnostic imaging/*pathology", "Child", "Child, Preschool", "Female",
            "Humans", "Image Processing, Computer-Assisted", "Magnetic Resonance Imaging", "Male",
            "Post-Concussion Syndrome/*diagnosis", "Retrospective Studies", "Tomography, X-Ray Computed"
        ], [
           "Adult", "Brain Concussion/physiopathology", "Female", "Humans", "Male", "Middle Aged",
            "Post-Concussion Syndrome/complications/*physiopathology",
            "Whiplash Injuries/complications/physiopathology", "Young Adult"
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
            for idx, keyword in enumerate(cls.keywords[article_idx]):
                k = keyword.split("/*")
                pubmed_json["MedlineCitation_MeshHeadingList_MeshHeading_%s_DescriptorName_#text" % str(idx)] = k[0]
                pubmed_json[
                    "MedlineCitation_MeshHeadingList_MeshHeading_%s_DescriptorName_@MajorTopicYN" % str(idx)] = "N"
                for q_idx, qualifier in enumerate(k[1:]):
                    key = "MedlineCitation_MeshHeadingList_MeshHeading_%s_QualifierName_" % str(idx)
                    if len(k[1:]) > 1:
                        key += str(q_idx) + "_"
                    pubmed_json[key + "#text"] = qualifier
                    pubmed_json[key + "@MajorTopicYN"] = "Y"

            cls.pubmed_jsons.append(pubmed_json)

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

        for k, v in self.pubmed_jsons[0].iteritems():
            self.assertEquals(v, result[k])

    def test_json_to_xml(self):
        """
        test conversion from json to xml
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons[0])

        # convert from json to xml
        result = json_to_pubmed_xml(json.dumps(original_json))

        # get result xml tree (will fail if not well-formed xml)
        result_tree = Et.fromstring(result)
        medline_citation = result_tree[0].find("MedlineCitation")
        pubmed_data = result_tree[0].find("PubmedData")

        # check PMID
        self.assertEquals(self.pmids[0], medline_citation.find("PMID").text)
        self.assertEquals(original_json["MedlineCitation_PMID_@Version"],
                          medline_citation.find("PMID").attrib["Version"])

        # check title
        article = medline_citation.find("Article")
        self.assertEquals(self.titles[0], article.find("ArticleTitle").text)

        # check authors
        authors = article.find("AuthorList")
        for idx, author in enumerate(authors.findall("Author")):
            for e in ["ForeName", "LastName"]:
                self.assertEquals(original_json["MedlineCitation_Article_AuthorList_Author_%s_%s" % (str(idx), e)],
                                  author.find(e).text)

        # check pagination
        pagination = article.find("Pagination")
        self.assertEquals(self.paginations[0],
                          pagination.find("MedlinePgn").text)

        # check publication status
        self.assertEquals(original_json["PubmedData_PublicationStatus"],
                          pubmed_data.find("PublicationStatus").text)

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
        self.assertEquals(",".join(self.keywords[article_idx]), doc.get("keywords", ""))

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
