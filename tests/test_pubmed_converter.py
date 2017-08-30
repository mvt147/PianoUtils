import os
import json
import xmltodict
import xml.etree.ElementTree as Et
from unittest import TestCase
from copy import deepcopy
from pubmed_converter import xml_to_json, json_to_xml, xml_to_piano, json_to_piano


class TestPubMedConverter(TestCase):

    pmid = "26419243"
    title = "Post-concussion syndrome (PCS) in a youth population: defining the diagnostic value and cost-utility of brain imaging."
    pagination = "2305-9"
    authors = [
        {"ForeName": "Clinton D", "LastName": "Morgan"},
        {"ForeName": "Scott L", "LastName": "Zuckerman"},
        {"ForeName": "Lauren E", "LastName": "King"},
        {"ForeName": "Susan E", "LastName": "Beaird"},
        {"ForeName": "Allen K", "LastName": "Sills"},
        {"ForeName": "Gary S", "LastName": "Solomon"},
    ]
    keywords = ["Adolescent", "Brain/*diagnostic imaging/*pathology", "Child", "Child, Preschool", "Female",
                "Humans", "Image Processing, Computer-Assisted", "Magnetic Resonance Imaging", "Male",
                "Post-Concussion Syndrome/*diagnosis", "Retrospective Studies", "Tomography, X-Ray Computed"]

    pubmed_xml = open(os.path.join(os.path.dirname(__file__), 'single_pubmed_xml_article.xml')).read()

    pubmed_json = {
        "MedlineCitation_PMID_#text": pmid,
        "MedlineCitation_PMID_@Version": "1",
        "MedlineCitation_Article_ArticleTitle": title,
        "MedlineCitation_Article_Pagination_MedlinePgn": pagination,
        "PubmedData_PublicationStatus": "ppublish",
    }
    for idx, a in enumerate(authors):
        for k in a:
            key = "MedlineCitation_Article_AuthorList_Author_%s_%s" % (str(idx), k)
            pubmed_json[key] = a[k]
    for idx, keyword in enumerate(keywords):
        k = keyword.split("/*")
        pubmed_json["MedlineCitation_MeshHeadingList_MeshHeading_%s_DescriptorName_#text" % str(idx)] = k[0]
        for q_idx, qualifier in enumerate(k[1:]):
            pubmed_json["MedlineCitation_MeshHeadingList_MeshHeading_%s_QualifierName_%s_#text"
                        % (str(idx), str(q_idx))] = qualifier
            pubmed_json["MedlineCitation_MeshHeadingList_MeshHeading_%s_QualifierName_%s_@MajorTopicYN"
                        % (str(idx), str(q_idx))] = "Y"

    def test_xml_to_json(self):
        """
        test conversion from xml to json
        :return:
        """
        original_xml = deepcopy(self.pubmed_xml)

        # convert xml to json
        result = json.loads(xml_to_json(original_xml))

        # check is flattened
        for v in result.values():
            self.assertNotIsInstance(v, dict)
            self.assertNotIsInstance(v, list)

        for k, v in self.pubmed_json.iteritems():
            self.assertEquals(v, result[k])

    def test_json_to_xml(self):
        """
        test conversion from json to xml
        :return:
        """
        original_json = deepcopy(self.pubmed_json)

        # convert from json to xml
        result = json_to_xml(json.dumps(original_json))

        # get result xml tree (will fail if not well-formed xml)
        result_tree = Et.fromstring(result)
        medline_citation = result_tree[0].find("MedlineCitation")
        pubmed_data = result_tree[0].find("PubmedData")

        # check PMID
        self.assertEquals(self.pmid, medline_citation.find("PMID").text)
        self.assertEquals(original_json["MedlineCitation_PMID_@Version"],
                          medline_citation.find("PMID").attrib["Version"])

        # check title
        article = medline_citation.find("Article")
        self.assertEquals(self.title, article.find("ArticleTitle").text)

        # check authors
        authors = article.find("AuthorList")
        for idx, author in enumerate(authors.findall("Author")):
            for e in ["ForeName", "LastName"]:
                self.assertEquals(original_json["MedlineCitation_Article_AuthorList_Author_%s_%s" % (str(idx), e)],
                                  author.find(e).text)

        # check pagination
        pagination = article.find("Pagination")
        self.assertEquals(self.pagination,
                          pagination.find("MedlinePgn").text)

        # check publication status
        self.assertEquals(original_json["PubmedData_PublicationStatus"],
                          pubmed_data.find("PublicationStatus").text)

    def test_xml_to_json_to_xml(self):
        """
        test conversion from xml to json, then back from json to xml and ensure they are equal
        :return:
        """
        original_xml = deepcopy(self.pubmed_xml)

        # convert xml to json
        xml_as_json = json.loads(xml_to_json(deepcopy(original_xml)))

        # convert json back to xml
        json_as_xml = json_to_xml(json.dumps(xml_as_json))

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
        original_json = deepcopy(self.pubmed_json)

        # convert json to xml
        json_as_xml = json_to_xml(json.dumps(original_json))

        # convert xml back to json
        xml_as_json = json.loads(xml_to_json(json_as_xml))

        # compare results
        self.assertDictEqual(original_json, xml_as_json)

    def test_xml_to_piano(self):
        """
        test conversion from xml to piano
        :return:
        """
        original_xml = deepcopy(self.pubmed_xml)

        # convert xml to piano documents
        piano_docs = xml_to_piano(original_xml)

        print
        from pprint import pprint
        pprint(piano_docs)
        self.assertEquals(1, len(piano_docs))

        doc = piano_docs[0]

        # check pmid
        self.assertEquals(self.pmid, doc.get("pmid", ""))

        # check title
        self.assertEquals(self.title, doc.get("title", ""))

        # check authors
        self.assertEquals(["%s, %s" % (a["LastName"], a["ForeName"]) for a in self.authors],
                          doc.get("authors", []))

        # check pagination
        self.assertEquals(self.pagination, doc.get("pages", ""))

        # check keywords
        self.assertEquals(",".join(self.keywords), doc.get("keywords", ""))

    def test_json_to_piano(self):
        """
        test conversion from json to piano
        :return:
        """
        original_json = deepcopy(self.pubmed_json)

        # convert json to piano documents
        piano_docs = json_to_piano(json.dumps(original_json))

        print
        from pprint import pprint
        pprint(piano_docs)
        self.assertEquals(1, len(piano_docs))

        doc = piano_docs[0]

        # check pmid
        self.assertEquals(self.pmid, doc.get("pmid", ""))

        # check title
        self.assertEquals(self.title, doc.get("title", ""))

        # check authors
        self.assertEquals(["%s, %s" % (a["LastName"], a["ForeName"]) for a in self.authors],
                          doc.get("authors", []))

        # check pagination
        self.assertEquals(self.pagination, doc.get("pages", ""))

        # check keywords
        self.assertEquals(",".join(self.keywords), doc.get("keywords", ""))
