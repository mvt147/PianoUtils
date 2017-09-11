import datetime
import xml.etree.ElementTree as ET
from abc import ABCMeta, abstractmethod

import sys
from bs4 import BeautifulSoup


class Mapper:
    __metaclass__ = ABCMeta

    element_names = None
    overwrite = None

    def __init__(self, overwrite=False):
        self.overwrite = overwrite

    @abstractmethod
    def attach_article_ids(self, xml_items):
        """
        Attach the article identifier (e.g. PubMed ID) to each xml item, forming a list of tuples
        :param xml_items: list of articles
        :return: list of tuples, i.e. [(article, ID), ...]
        """
        pass

    @abstractmethod
    def transform_to_piano(self, xml_soup_element):
        """
        Transform an XML element in BeautifulSoup format to an article
        dictionary containing piano attributes
        :param xml_soup_element: XML element in BeautifulSoup format
        :return:
        """
        pass

    def transform_raw(self, xml):
        """
        Transform raw XML content into list of articles
        :param xml: xml to parse
        :return: combine new and existing ids in one return list
        """

        xml_articles_tuples = self.parse_articles_from_xml(xml)

        return xml_articles_tuples

    @staticmethod
    def get_text_if_not_null(element):
        """
        Get text value of element if it exists
        :param element: xml element
        :return: text value, else None
        """
        text = element.get_text() if element is not None else None
        return text if text is not None else None

    def parse_articles_from_xml(self, xml_raw):
        """
        Split raw xml into separate articles (xml format)
        Can throw exception if xml is invalid or could not fine any articles, for e.g. could not find articles.
        :param xml_raw: raw xml format
        :return: list of tuples (beautifulXML, pmid)
        """
        sys.stderr.write("Started parsing XML %s\n" % datetime.datetime.now())

        xml_items = self.parallelize_parse(xml_raw)

        sys.stderr.write("Found: %d xml articles\n" % len(xml_items))

        if len(xml_items) == 0:
            raise ValueError('Could not find any articles')

        return self.attach_article_ids(xml_items)

    def parallelize_parse(self, xml_raw):
        """
        Wanted to run multiple parsers in parallel but it seems that sax processing is enough.
        :param xml_raw: raw xml format
        :return:
        """
        _list = []

        if isinstance(xml_raw, unicode):
            # encode in utf8 if raw xml is unicode
            xml_raw = xml_raw.encode("utf8")
        root = ET.fromstring(xml_raw)
        for element in root.iter(self.element_names):
            _item = BeautifulSoup(ET.tostring(element), "xml")
            _list.append(_item)

        return _list


class XmlToJson:

    mapper = None
    dao = None

    def __init__(self, mapper):
        self.mapper = mapper

    def xml_to_json(self, xml_content):
        sys.stderr.write("Start Import %s\n" % datetime.datetime.now())

        list_of_references = self.mapper.transform_raw(xml_content)
        ids = []
        len_list = len(list_of_references)

        result = {"number": len_list}

        articles = []

        sys.stderr.write("Processing %s number of records %s\n" % (len_list, datetime.datetime.now()))
        try:
            for idx, (xml_article, id_dict) in enumerate(list_of_references):
                sys.stderr.write("Processing: %d/%d\n" % (idx + 1, len_list))

                piano = self.mapper.transform_to_piano(xml_article)
                articles.append(piano)

        except Exception, e:
            result["status"] = 'failed'
            result["error"] = str(e)
            result["error_number"] = len(ids) + 1
            print(str(e))
        else:
            result["status"] = 'successful'

        sys.stderr.write("End Import %s\n" % datetime.datetime.now())

        return articles
