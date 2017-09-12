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
        cls.pubmed_xml_non_ascii = open(os.path.join(os.path.dirname(__file__), 'single_pubmed_xml_article_non_ascii.xml')).read()
        cls.pubmed_xml_mulitple_non_ascii = open(
            os.path.join(os.path.dirname(__file__), 'multiple_pubmed_xml_articles_non_ascii.xml')).read()

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
        """
        test conversion from json to piano with non-pubmed json fields
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons[0])

        # add non-pubmed json fields
        _id = "59ac8d07e247e100189ae0ea"
        uuid = "af93cac5-b6f9-4c0c-9ba1-3c4a360f637"
        original_json["_id"] = _id
        original_json["uuid"] = uuid

        # convert json to piano
        piano_docs = pubmed_json_to_piano(json.dumps(original_json))
        self.assertEquals(1, len(piano_docs))
        self.check_piano(0, piano_docs[0])

        # check non-pubmed values
        self.assertEquals(_id, piano_docs[0]["_id"])
        self.assertEquals(uuid, piano_docs[0]["uuid"])

    def test_json_to_piano__with_multiple_non_pubmed_fields(self):
        """
        test conversion from json to piano with multiple articles with non-pubmed json fields
        :return:
        """
        original_json = deepcopy(self.pubmed_jsons)

        # add non-pubmed json fields
        for idx, j in enumerate(original_json):
            j["_id"] = "59ac8d07e247e100189ae0ea_" + str(idx)
            j["uuid"] = "af93cac5-b6f9-4c0c-9ba1-3c4a360f637_" + str(idx)

        # convert json to piano documents
        piano_docs = pubmed_json_to_piano(json.dumps(original_json))

        # check values
        self.assertEquals(2, len(piano_docs))
        self.check_piano(0, piano_docs[0])
        self.check_piano(1, piano_docs[1])

        # check non-pubmed values
        for idx, d in enumerate(piano_docs):
            self.assertEquals("59ac8d07e247e100189ae0ea_" + str(idx), d["_id"])
            self.assertEquals("af93cac5-b6f9-4c0c-9ba1-3c4a360f637_" + str(idx), d["uuid"])

    def test_xml_to_json_to_piano__with_non_ascii_char(self):
        """
        test conversion from xml to json, then json to piano where xml contents contains non-ascii character(s)
        :return:
        """
        original_xml = deepcopy(self.pubmed_xml_non_ascii)

        # convert xml to json
        json_string = pubmed_xml_to_json(original_xml)
        # convert json to piano
        piano = pubmed_json_to_piano(json_string)
        article = piano[0]

        # check values
        self.assertEquals("26138797", article["pmid"])
        self.assertEquals("The role of the cervical spine in post-concussion syndrome.", article["title"])

    def test_xml_to_json_to_piano__with_multiple_non_ascii_char(self):
        """
        test conversion from xml to json, then json to piano where xml contents contains non-ascii character(s)
        :return:
        """
        original_xml = deepcopy(self.pubmed_xml_mulitple_non_ascii)

        # convert xml to json
        json_string = pubmed_xml_to_json(original_xml)
        # convert json to piano
        piano = pubmed_json_to_piano(json_string)

        # check values
        self.assertEquals(3, len(piano))
        article = piano[2]
        self.assertEquals("26138797", article["pmid"])
        self.assertEquals("The role of the cervical spine in post-concussion syndrome.", article["title"])

    def test_json_to_piano__with_unsorted_json(self):
        unsorted_json = {
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_25_@RefType": "Cites",
    "PubmedData_History_PubMedPubDate_2_@PubStatus": "entrez",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_40_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_41_PMID_@Version": "1",
    "MedlineCitation_Article_@PubModel": "Print-Electronic",
    "MedlineCitation_Article_AuthorList_Author_4_LastName": "Mohamed",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_51_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_4_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_0_@UI": "Q000235",
    "MedlineCitation_Article_Abstract_AbstractText_2_@Label": "RESULTS",
    "MedlineCitation_OtherID_0_#text": "NIHMS531851",
    "MedlineCitation_Article_AuthorList_Author_9_Initials": "D",
    "MedlineCitation_KeywordList_Keyword_3_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_14_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_39_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_DescriptorName_@UI": "D011471",
    "MedlineCitation_Article_AuthorList_Author_10_LastName": "Chen",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_12_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_26_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_28_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_4_RefSource": "Cancer Metastasis Rev. 2013 Jun;32(1-2):109-22",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_37_RefSource": "Cancer Cell. 2010 Jul 13;18(1):11-22",
    "MedlineCitation_Article_GrantList_Grant_1_Acronym": "CA",
    "MedlineCitation_Article_AuthorList_Author_9_LastName": "Young",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_21_@RefType": "Cites",
    "MedlineCitation_Article_Journal_ISOAbbreviation": "Prostate",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_7_RefSource": "EMBO Rep. 2007 Sep;8(9):871-8",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_44_PMID_#text": "16729045",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_48_RefSource": "Prostate. 2008 Sep 15;68(13):1387-95",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_20_PMID_@Version": "1",
    "PubmedData_ArticleIdList_ArticleId_1_@IdType": "doi",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_21_RefSource": "Oncogene. 2008 Sep 11;27(40):5348-53",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_29_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_16_LastName": "Saxena",
    "MedlineCitation_MeshHeadingList_MeshHeading_5_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_53_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_2_DescriptorName_#text": "Cell Line, Tumor",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_41_RefSource": "Exp Cell Res. 2006 Apr 1;312(6):831-43",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_22_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_34_RefSource": "J Proteome Res. 2010 May 7;9(5):2109-16",
    "MedlineCitation_Article_ArticleDate_@DateType": "Electronic",
    "MedlineCitation_ChemicalList_Chemical_1_NameOfSubstance_#text": "ERG protein, human",
    "MedlineCitation_Article_Journal_JournalIssue_PubDate_Year": "2014",
    "PubmedData_History_PubMedPubDate_0_@PubStatus": "received",
    "PubmedData_History_PubMedPubDate_3_Day": "12",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_24_RefSource": "J Clin Oncol. 2011 Sep 20;29(27):3659-68",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_48_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_7_LastName": "Saxena",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_46_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_13_PMID_@Version": "1",
    "PubmedData_History_PubMedPubDate_4_@PubStatus": "medline",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_30_RefSource": "Nat Cell Biol. 2012 Oct;14(10):1024-35",
    "MedlineCitation_MeshHeadingList_MeshHeading_9_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_Article_AuthorList_Author_12_ForeName": "Gyorgy",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_28_RefSource": "Eur Urol. 2013 Oct;64(4):567-76",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_DescriptorName_#text": "Trans-Activators",
    "MedlineCitation_Article_AuthorList_Author_16_Initials": "S",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_QualifierName_1_@MajorTopicYN": "Y",
    "MedlineCitation_Article_AuthorList_Author_2_Initials": "X",
    "MedlineCitation_ChemicalList_Chemical_2_NameOfSubstance_#text": "Oncogene Proteins",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_36_@RefType": "Cites",
    "MedlineCitation_KeywordList_Keyword_4_#text": "proteomics",
    "MedlineCitation_MeshHeadingList_MeshHeading_0_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_2_PMID_#text": "18792917",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_33_RefSource": "Stat Appl Genet Mol Biol. 2004;3:Article3",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_19_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_53_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_7_Initials": "S",
    "MedlineCitation_Article_Abstract_AbstractText_0_#text": "Gene fusion between TMPRSS2 promoter and the ERG proto-oncogene is a major genomic alteration found in over half of prostate cancers (CaP), which leads to aberrant androgen dependent ERG expression. Despite extensive analysis for the biological functions of ERG in CaP, there is no systematic evaluation of the ERG responsive proteome (ERP). ERP has the potential to define new biomarkers and therapeutic targets for prostate tumors stratified by ERG expression.",
    "MedlineCitation_Article_AuthorList_Author_8_Initials": "S",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_22_RefSource": "FEBS Lett. 2012 Sep 21;586(19):3208-14",
    "MedlineCitation_Article_GrantList_Grant_0_GrantID": "R01 CA162383",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_50_RefSource": "Science. 2005 Oct 28;310(5748):644-8",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_14_PMID_#text": "20878952",
    "MedlineCitation_MeshHeadingList_MeshHeading_11_DescriptorName_@UI": "D000071230",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_3_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_42_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_13_@ValidYN": "Y",
    "MedlineCitation_Article_AuthorList_Author_9_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_30_PMID_#text": "23023224",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_6_PMID_#text": "18425750",
    "MedlineCitation_Article_Abstract_AbstractText_0_@Label": "BACKGROUND",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_43_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_35_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_47_RefSource": "Neoplasia. 2008 Feb;10(2):177-88",
    "PubmedData_History_PubMedPubDate_2_Day": "12",
    "MedlineCitation_Article_Abstract_AbstractText_1_@Label": "METHODS",
    "MedlineCitation_Article_AuthorList_Author_0_AffiliationInfo_Affiliation": "Center for Prostate Disease Research, Department of Surgery, Uniformed Services University of the Health Sciences, Rockville, Maryland.",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_13_PMID_#text": "7531324",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_5_PMID_#text": "18676740",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_19_RefSource": "Oncogene. 2005 May 26;24(23):3847-52",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_1_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_14_ForeName": "David G",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_49_PMID_#text": "22461644",
    "MedlineCitation_ChemicalList_Chemical_5_RegistryNumber": "0",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_QualifierName_0_@MajorTopicYN": "N",
    "MedlineCitation_PMID_#text": "24115221",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_11_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_51_PMID_#text": "19203193",
    "MedlineCitation_ChemicalList_Chemical_1_NameOfSubstance_@UI": "C072312",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_2_RefSource": "Prostate. 2009 Jan 1;69(1):49-61",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_Article_AuthorList_Author_16_ForeName": "Satya",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_47_PMID_#text": "18283340",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_3_RefSource": "Endocr Relat Cancer. 2013 Jun;20(3):R83-99",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_8_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_6_@ValidYN": "Y",
    "MedlineCitation_OtherID_1_#text": "PMC4075339",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_0_@MajorTopicYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_49_RefSource": "Sci Transl Med. 2012 Mar 28;4(127):127rv3",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_27_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_46_PMID_@Version": "1",
    "MedlineCitation_ChemicalList_Chemical_3_NameOfSubstance_@UI": "D020543",
    "MedlineCitation_Article_ArticleTitle": "Evaluation of ERG responsive proteome in prostate cancer.",
    "MedlineCitation_Article_GrantList_Grant_0_Agency": "NCI NIH HHS",
    "PubmedData_History_PubMedPubDate_2_Minute": "0",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_36_PMID_#text": "16951139",
    "MedlineCitation_Article_AuthorList_Author_15_ForeName": "Isabell A",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_40_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_4_DescriptorName_#text": "Humans",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_29_RefSource": "J Carcinog. 2011;10:37",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_27_PMID_#text": "22815903",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_16_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_11_DescriptorName_#text": "Transcriptional Regulator ERG",
    "MedlineCitation_Article_Language": "eng",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_17_RefSource": "Prostate Cancer Prostatic Dis. 2010 Sep;13(3):228-37",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_41_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_25_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_4_@ValidYN": "Y",
    "MedlineCitation_DateCompleted_Day": "03",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_35_PMID_#text": "20516122",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_31_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_24_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_10_ForeName": "Yongmei",
    "MedlineCitation_ChemicalList_Chemical_4_NameOfSubstance_#text": "Trans-Activators",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_27_RefSource": "PLoS One. 2012;7(7):e41039",
    "PubmedData_ArticleIdList_ArticleId_2_#text": "PMC4075339",
    "MedlineCitation_MedlineJournalInfo_NlmUniqueID": "8101368",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_1_#text": "metabolism",
    "MedlineCitation_MedlineJournalInfo_ISSNLinking": "0270-4137",
    "PubmedData_History_PubMedPubDate_4_Year": "2014",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_6_RefSource": "Electrophoresis. 2008 May;29(10):2215-23",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_15_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_QualifierName_0_#text": "biosynthesis",
    "MedlineCitation_Article_AuthorList_Author_10_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_32_PMID_#text": "23634237",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_28_@RefType": "Cites",
    "PubmedData_History_PubMedPubDate_3_Month": "10",
    "MedlineCitation_ChemicalList_Chemical_5_NameOfSubstance_#text": "Transcriptional Regulator ERG",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_QualifierName_1_@UI": "Q000235",
    "MedlineCitation_Article_AuthorList_Author_8_LastName": "Katta",
    "MedlineCitation_Article_AuthorList_@CompleteYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_16_@RefType": "Cites",
    "MedlineCitation_Article_GrantList_Grant_1_Country": "United States",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_1_PMID_#text": "12210485",
    "PubmedData_PublicationStatus": "ppublish",
    "MedlineCitation_Article_AuthorList_Author_5_Initials": "NB",
    "MedlineCitation_MeshHeadingList_MeshHeading_3_QualifierName_@MajorTopicYN": "N",
    "MedlineCitation_Article_Abstract_AbstractText_1_@NlmCategory": "METHODS",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_QualifierName_1_@MajorTopicYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_43_PMID_#text": "24565966",
    "MedlineCitation_Article_Abstract_AbstractText_3_#text": "This study delineates the global proteome for prostate tumors stratified by ERG expression status. The ERP data confirm the functions of ERG in inhibiting cell differentiation and activating cell growth, and identify potentially novel biomarkers and therapeutic targets.",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_9_PMID_#text": "19284784",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_QualifierName_0_#text": "biosynthesis",
    "MedlineCitation_Article_AuthorList_Author_15_@ValidYN": "Y",
    "MedlineCitation_MeshHeadingList_MeshHeading_3_QualifierName_@UI": "Q000235",
    "MedlineCitation_Article_AuthorList_Author_14_Initials": "DG",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_30_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_50_PMID_#text": "16254181",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_23_PMID_#text": "20479932",
    "MedlineCitation_Article_AuthorList_Author_14_LastName": "McLeod",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_0_PMID_#text": "19955085",
    "MedlineCitation_Article_Abstract_AbstractText_2_#text": "We identified 1,196 and 2,190 unique proteins stratified by ERG status from prostate tumors and VCaP cells, respectively. Comparative analysis of these two proteomes identified 330 concordantly regulated proteins characterizing enrichment of pathways modulating cytoskeletal and actin reorganization, cell migration, protein biosynthesis, and proteasome and ER-associated protein degradation. ERPs unique for ERG (+) tumors reveal enrichment for cell growth and survival pathways while proteasome and redox function pathways were enriched in ERPs unique for ERG (-) tumors. Meta-analysis of ERPs against CaP gene expression data revealed that Myosin VI and Monoamine oxidase A were positively and negatively correlated to ERG expression, respectively.",
    "MedlineCitation_MeshHeadingList_MeshHeading_5_DescriptorName_@UI": "D008297",
    "MedlineCitation_Article_AuthorList_Author_3_ForeName": "Fang",
    "MedlineCitation_Article_GrantList_@CompleteYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_40_PMID_#text": "16829574",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_52_RefSource": "Prostate. 2012 Nov;72(15):1622-7",
    "MedlineCitation_Article_Journal_JournalIssue_PubDate_Month": "Jan",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_30_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_9_DescriptorName_@UI": "D020543",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_37_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_52_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_44_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_32_RefSource": "Am J Transl Res. 2013 Apr 19;5(3):254-68",
    "MedlineCitation_MeshHeadingList_MeshHeading_0_DescriptorName_#text": "Aged",
    "MedlineCitation_Article_AuthorList_Author_1_ForeName": "Bungo",
    "MedlineCitation_Article_AuthorList_Author_17_Initials": "S",
    "MedlineCitation_ChemicalList_Chemical_5_NameOfSubstance_@UI": "D000071230",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_48_@RefType": "Cites",
    "MedlineCitation_Article_Journal_ISSN_#text": "1097-0045",
    "MedlineCitation_MeshHeadingList_MeshHeading_3_DescriptorName_@UI": "D053263",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_42_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_9_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_0_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_33_PMID_#text": "16646809",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_33_@RefType": "Cites",
    "MedlineCitation_Article_Journal_JournalIssue_@CitedMedium": "Internet",
    "MedlineCitation_ChemicalList_Chemical_2_NameOfSubstance_@UI": "D015513",
    "PubmedData_ArticleIdList_ArticleId_0_#text": "24115221",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_QualifierName_0_#text": "biosynthesis",
    "MedlineCitation_KeywordList_Keyword_0_@MajorTopicYN": "N",
    "MedlineCitation_Article_AuthorList_Author_8_ForeName": "Shilpa",
    "MedlineCitation_@Status": "MEDLINE",
    "MedlineCitation_MeshHeadingList_MeshHeading_6_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_37_PMID_#text": "20579941",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_14_RefSource": "Prostate. 2011 Apr;71(5):489-97",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_Article_Abstract_AbstractText_0_@NlmCategory": "BACKGROUND",
    "MedlineCitation_Article_AuthorList_Author_12_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_16_RefSource": "Oncogene. 2010 Jan 14;29(2):188-200",
    "MedlineCitation_Article_AuthorList_Author_11_LastName": "Sreenath",
    "MedlineCitation_DateRevised_Day": "20",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_18_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_35_RefSource": "Cancer Res. 2010 Jul 1;70(13):5207-12",
    "MedlineCitation_Article_AuthorList_Author_4_ForeName": "Ahmed A",
    "MedlineCitation_Article_AuthorList_Author_11_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_20_PMID_#text": "20204405",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_18_RefSource": "Cancer Biol Ther. 2011 Feb 15;11(4):410-7",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_46_PMID_#text": "17071605",
    "MedlineCitation_Article_ArticleDate_Year": "2013",
    "PubmedData_History_PubMedPubDate_1_Month": "08",
    "PubmedData_History_PubMedPubDate_1_Day": "27",
    "MedlineCitation_Article_AuthorList_Author_12_LastName": "Petrovics",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_0_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_26_PMID_#text": "23390522",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_13_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_Article_AuthorList_Author_1_@ValidYN": "Y",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_2_@UI": "Q000473",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_17_PMID_#text": "20585344",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_18_PMID_#text": "21178489",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_5_RefSource": "Clin Cancer Res. 2008 Aug 1;14(15):4719-25",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_11_RefSource": "Nat Cell Biol. 2000 Aug;2(8):540-7",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_52_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_14_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_42_PMID_#text": "17614365",
    "MedlineCitation_Article_AuthorList_Author_3_@ValidYN": "Y",
    "MedlineCitation_ChemicalList_Chemical_0_NameOfSubstance_#text": "Biomarkers, Tumor",
    "MedlineCitation_Article_AuthorList_Author_13_ForeName": "Albert",
    "PubmedData_History_PubMedPubDate_2_Year": "2013",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_8_PMID_#text": "10202537",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_4_@RefType": "Cites",
    "PubmedData_History_PubMedPubDate_3_Year": "2013",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_12_PMID_#text": "22950997",
    "MedlineCitation_Article_Journal_ISSN_@IssnType": "Electronic",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_1_@MajorTopicYN": "N",
    "MedlineCitation_MeshHeadingList_MeshHeading_2_DescriptorName_@UI": "D045744",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_9_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_7_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_2_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_46_RefSource": "Am J Pathol. 2006 Nov;169(5):1843-54",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_28_PMID_#text": "23759327",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_21_PMID_#text": "18542058",
    "MedlineCitation_ChemicalList_Chemical_4_NameOfSubstance_@UI": "D015534",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_44_RefSource": "Mol Syst Biol. 2005;1:2005.0010",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_52_PMID_#text": "22473857",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_9_RefSource": "J Proteome Res. 2009 May;8(5):2310-8",
    "PubmedData_History_PubMedPubDate_0_Month": "08",
    "MedlineCitation_Article_Abstract_AbstractText_3_@NlmCategory": "CONCLUSIONS",
    "PubmedData_ArticleIdList_ArticleId_3_#text": "NIHMS531851",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_10_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_0_DescriptorName_@UI": "D000368",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_2_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_2_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_31_RefSource": "BMC Med Genomics. 2010;3:8",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_DescriptorName_#text": "Biomarkers, Tumor",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_53_PMID_#text": "14729644",
    "MedlineCitation_Article_AuthorList_Author_1_LastName": "Furusato",
    "MedlineCitation_ChemicalList_Chemical_4_RegistryNumber": "0",
    "MedlineCitation_KeywordList_Keyword_1_@MajorTopicYN": "N",
    "MedlineCitation_Article_AuthorList_Author_3_Initials": "F",
    "MedlineCitation_Article_PublicationTypeList_PublicationType_2_#text": "Research Support, N.I.H., Extramural",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_36_PMID_@Version": "1",
    "PubmedData_History_PubMedPubDate_3_Minute": "0",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_23_@RefType": "Cites",
    "PubmedData_History_PubMedPubDate_4_Minute": "0",
    "MedlineCitation_Article_ELocationID_@EIdType": "doi",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_26_RefSource": "PLoS One. 2013;8(2):e55207",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_11_PMID_#text": "10934475",
    "MedlineCitation_Article_AuthorList_Author_11_Initials": "T",
    "MedlineCitation_Article_AuthorList_Author_7_@ValidYN": "Y",
    "MedlineCitation_Article_AuthorList_Author_17_LastName": "Srivastava",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_10_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_45_PMID_#text": "18725993",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_12_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_21_PMID_@Version": "1",
    "MedlineCitation_Article_PublicationTypeList_PublicationType_2_@UI": "D052061",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_7_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_23_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_20_RefSource": "J Cancer Res Clin Oncol. 2010 Nov;136(11):1761-71",
    "PubmedData_ArticleIdList_ArticleId_2_@IdType": "pmc",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_33_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_5_@ValidYN": "Y",
    "MedlineCitation_Article_Journal_Title": "The Prostate",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_40_RefSource": "Proc Natl Acad Sci U S A. 2006 Jul 18;103(29):10991-6",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_36_RefSource": "Cancer Res. 2006 Sep 1;66(17):8337-41",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_DescriptorName_@UI": "D014408",
    "MedlineCitation_MeshHeadingList_MeshHeading_6_DescriptorName_#text": "Middle Aged",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_DescriptorName_#text": "Prostatic Neoplasms",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_45_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_5_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_9_QualifierName_@MajorTopicYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_24_PMID_#text": "21859993",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_34_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_15_RefSource": "J Proteome Res. 2008 Aug;7(8):3329-38",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_45_RefSource": "J Clin Invest. 2008 Sep;118(9):3003-6",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_39_RefSource": "Methods Mol Biol. 2009;520:107-28",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_22_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_24_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_DescriptorName_@UI": "D015534",
    "MedlineCitation_PMID_@Version": "1",
    "MedlineCitation_OtherID_1_@Source": "NLM",
    "MedlineCitation_Article_ELocationID_#text": "10.1002/pros.22731",
    "MedlineCitation_Article_AuthorList_Author_12_Initials": "G",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_QualifierName_1_#text": "genetics",
    "MedlineCitation_Article_AuthorList_Author_16_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_7_PMID_#text": "17721441",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_DescriptorName_@UI": "D015513",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_25_PMID_#text": "21575865",
    "MedlineCitation_Article_ELocationID_@ValidYN": "Y",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_QualifierName_0_@UI": "Q000096",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_3_PMID_#text": "23456430",
    "MedlineCitation_Article_GrantList_Grant_0_Country": "United States",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_19_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_6_@RefType": "Cites",
    "MedlineCitation_DateCreated_Day": "09",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_44_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_0_ForeName": "Shyh-Han",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_QualifierName_1_@UI": "Q000235",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_22_PMID_#text": "22884421",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_QualifierName_0_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_8_RefSource": "Annu Rev Neurosci. 1999;22:197-217",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_32_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_43_@RefType": "Cites",
    "MedlineCitation_Article_PublicationTypeList_PublicationType_1_@UI": "D016428",
    "MedlineCitation_Article_ArticleDate_Day": "21",
    "MedlineCitation_DateRevised_Year": "2017",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_13_RefSource": "Prostate. 1995 Jan;26(1):12-8",
    "MedlineCitation_Article_Journal_JournalIssue_Volume": "74",
    "MedlineCitation_Article_AuthorList_Author_5_LastName": "Griner",
    "MedlineCitation_MeshHeadingList_MeshHeading_9_QualifierName_@UI": "Q000235",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_1_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_38_PMID_#text": "23335087",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_51_RefSource": "J Proteome Res. 2009 Mar;8(3):1327-37",
    "MedlineCitation_Article_Abstract_CopyrightInformation": "\u00a9 2013 Wiley Periodicals, Inc.",
    "MedlineCitation_MeshHeadingList_MeshHeading_9_DescriptorName_#text": "Proteome",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_23_RefSource": "PLoS One. 2010;5(5):e10547",
    "MedlineCitation_Article_AuthorList_Author_2_LastName": "Fang",
    "MedlineCitation_Article_AuthorList_Author_6_ForeName": "Kaneeka",
    "MedlineCitation_MeshHeadingList_MeshHeading_6_DescriptorName_@UI": "D008875",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_53_RefSource": "Cancer Res. 2004 Jan 1;64(1):347-55",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_50_PMID_@Version": "1",
    "MedlineCitation_ChemicalList_Chemical_0_RegistryNumber": "0",
    "MedlineCitation_ChemicalList_Chemical_3_NameOfSubstance_#text": "Proteome",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_43_RefSource": "Eur Urol. 2014 Jun;65(6):e102-3",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_17_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_7_ForeName": "Sadhvi",
    "MedlineCitation_Article_AuthorList_Author_0_Initials": "SH",
    "MedlineCitation_MeshHeadingList_MeshHeading_5_DescriptorName_#text": "Male",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_32_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_QualifierName_1_#text": "genetics",
    "MedlineCitation_MeshHeadingList_MeshHeading_3_QualifierName_#text": "genetics",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_1_RefSource": "Prostate. 2002 Sep 1;52(4):253-63",
    "MedlineCitation_MeshHeadingList_MeshHeading_11_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_34_PMID_#text": "20334419",
    "MedlineCitation_Article_Journal_JournalIssue_Issue": "1",
    "MedlineCitation_DateCompleted_Month": "02",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_49_@RefType": "Cites",
    "PubmedData_ArticleIdList_ArticleId_1_#text": "10.1002/pros.22731",
    "PubmedData_ArticleIdList_ArticleId_0_@IdType": "pubmed",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_31_@RefType": "Cites",
    "MedlineCitation_Article_Abstract_AbstractText_2_@NlmCategory": "RESULTS",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_18_PMID_@Version": "1",
    "MedlineCitation_ChemicalList_Chemical_3_RegistryNumber": "0",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_5_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_15_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_39_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_17_@ValidYN": "Y",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_QualifierName_1_#text": "genetics",
    "MedlineCitation_KeywordList_Keyword_2_#text": "actin and cytoskeletal reorganization",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_17_PMID_@Version": "1",
    "PubmedData_History_PubMedPubDate_1_Year": "2013",
    "MedlineCitation_MeshHeadingList_MeshHeading_3_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_ChemicalList_Chemical_2_RegistryNumber": "0",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_34_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_4_DescriptorName_@UI": "D006801",
    "PubmedData_History_PubMedPubDate_3_@PubStatus": "pubmed",
    "MedlineCitation_CitationSubset": "IM",
    "PubmedData_History_PubMedPubDate_3_Hour": "6",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_14_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_2_@ValidYN": "Y",
    "PubmedData_ArticleIdList_ArticleId_3_@IdType": "mid",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_20_@RefType": "Cites",
    "MedlineCitation_ChemicalList_Chemical_0_NameOfSubstance_@UI": "D014408",
    "MedlineCitation_Article_AuthorList_Author_9_ForeName": "Denise",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_3_@RefType": "Cites",
    "MedlineCitation_Article_GrantList_Grant_1_Agency": "NCI NIH HHS",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_10_RefSource": "BMC Med Genomics. 2009 Aug 20;2:55",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_QualifierName_1_@UI": "Q000235",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_41_PMID_#text": "16413016",
    "MedlineCitation_DateCompleted_Year": "2014",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_16_PMID_#text": "19855435",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_10_PMID_#text": "19691856",
    "MedlineCitation_MedlineJournalInfo_MedlineTA": "Prostate",
    "MedlineCitation_Article_PublicationTypeList_PublicationType_1_#text": "Journal Article",
    "MedlineCitation_Article_AuthorList_Author_2_ForeName": "Xueping",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_0_#text": "genetics",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_QualifierName_0_@UI": "Q000096",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_QualifierName_1_@MajorTopicYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_42_RefSource": "Anal Chem. 2007 Aug 1;79(15):5785-92",
    "MedlineCitation_Article_PublicationTypeList_PublicationType_0_#text": "Evaluation Studies",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_37_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_0_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_49_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_50_@RefType": "Cites",
    "MedlineCitation_Article_Abstract_AbstractText_3_@Label": "CONCLUSIONS",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_27_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_29_PMID_#text": "22279422",
    "MedlineCitation_OtherID_0_@Source": "NLM",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_35_PMID_@Version": "1",
    "MedlineCitation_Article_AuthorList_Author_0_LastName": "Tan",
    "MedlineCitation_ChemicalList_Chemical_1_RegistryNumber": "0",
    "PubmedData_History_PubMedPubDate_0_Year": "2013",
    "MedlineCitation_Article_AuthorList_Author_10_Initials": "Y",
    "MedlineCitation_KeywordList_Keyword_0_#text": "ERG",
    "MedlineCitation_Article_AuthorList_Author_6_LastName": "Sood",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_6_PMID_@Version": "1",
    "MedlineCitation_DateCreated_Month": "12",
    "PubmedData_History_PubMedPubDate_4_Month": "2",
    "PubmedData_History_PubMedPubDate_4_Day": "4",
    "MedlineCitation_KeywordList_Keyword_3_#text": "myosin VI",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_47_PMID_@Version": "1",
    "MedlineCitation_Article_PublicationTypeList_PublicationType_0_@UI": "D023362",
    "MedlineCitation_Article_Abstract_AbstractText_1_#text": "Global proteome analysis was performed by using ERG (+) and ERG (-) CaP cells isolated by ERG immunohistochemistry defined laser capture microdissection and by using TMPRSS2-ERG positive VCaP cells treated with ERG and control siRNA.",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_47_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_13_LastName": "Dobi",
    "MedlineCitation_Article_AuthorList_Author_4_Initials": "AA",
    "MedlineCitation_Article_AuthorList_Author_5_ForeName": "Nicholas B",
    "MedlineCitation_Article_AuthorList_Author_15_Initials": "IA",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_15_PMID_#text": "18578523",
    "MedlineCitation_Article_GrantList_Grant_0_Acronym": "CA",
    "MedlineCitation_MeshHeadingList_MeshHeading_1_QualifierName_0_@MajorTopicYN": "N",
    "MedlineCitation_MedlineJournalInfo_Country": "United States",
    "MedlineCitation_KeywordList_Keyword_1_#text": "MAOA",
    "MedlineCitation_DateRevised_Month": "02",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_38_RefSource": "CA Cancer J Clin. 2013 Jan;63(1):11-30",
    "MedlineCitation_Article_AuthorList_Author_1_Initials": "B",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_45_@RefType": "Cites",
    "PubmedData_History_PubMedPubDate_4_Hour": "6",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_19_PMID_#text": "15750627",
    "MedlineCitation_Article_AuthorList_Author_3_LastName": "He",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_25_RefSource": "Cancer Cell. 2011 May 17;19(5):664-78",
    "MedlineCitation_Article_GrantList_Grant_1_GrantID": "R01CA162383",
    "MedlineCitation_Article_Pagination_MedlinePgn": "70-89",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_26_@RefType": "Cites",
    "MedlineCitation_MeshHeadingList_MeshHeading_3_DescriptorName_#text": "Gene Regulatory Networks",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_38_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_51_@RefType": "Cites",
    "MedlineCitation_Article_AuthorList_Author_13_Initials": "A",
    "PubmedData_History_PubMedPubDate_2_Month": "10",
    "MedlineCitation_KeywordList_@Owner": "NOTNLM",
    "MedlineCitation_Article_AuthorList_Author_17_ForeName": "Shiv",
    "MedlineCitation_MeshHeadingList_MeshHeading_4_DescriptorName_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_48_PMID_#text": "18543251",
    "MedlineCitation_Article_AuthorList_Author_11_ForeName": "Taduru",
    "PubmedData_History_PubMedPubDate_0_Day": "04",
    "MedlineCitation_KeywordList_Keyword_4_@MajorTopicYN": "N",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_29_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_11_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_4_PMID_#text": "23114843",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_38_PMID_@Version": "1",
    "MedlineCitation_MeshHeadingList_MeshHeading_9_QualifierName_#text": "genetics",
    "MedlineCitation_DateCreated_Year": "2013",
    "MedlineCitation_KeywordList_Keyword_2_@MajorTopicYN": "N",
    "PubmedData_History_PubMedPubDate_2_Hour": "6",
    "MedlineCitation_Article_AuthorList_Author_8_@ValidYN": "Y",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_0_RefSource": "Mol Cell Proteomics. 2010 Feb;9(2):298-312",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_39_PMID_#text": "19381950",
    "MedlineCitation_@Owner": "NLM",
    "MedlineCitation_Article_AuthorList_Author_15_LastName": "Sesterhenn",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_12_RefSource": "Urology. 2012 Oct;80(4):749-53",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_1_@UI": "Q000378",
    "MedlineCitation_Article_AuthorList_Author_6_Initials": "K",
    "MedlineCitation_Article_ArticleDate_Month": "09",
    "MedlineCitation_MeshHeadingList_MeshHeading_7_DescriptorName_#text": "Oncogene Proteins",
    "PubmedData_History_PubMedPubDate_1_@PubStatus": "accepted",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_2_@RefType": "Cites",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_8_PMID_@Version": "1",
    "MedlineCitation_CommentsCorrectionsList_CommentsCorrections_31_PMID_#text": "20233430",
    "MedlineCitation_MeshHeadingList_MeshHeading_10_QualifierName_0_@UI": "Q000096",
    "MedlineCitation_MeshHeadingList_MeshHeading_8_QualifierName_2_#text": "pathology"
  }
        piano = pubmed_json_to_piano(json.dumps(unsorted_json))

        self.assertEquals(piano[0]["pmid"], "24115221")
