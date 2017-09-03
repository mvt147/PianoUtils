import json
from types import NoneType
from bs4 import Tag
from piano_utils.utils.parse_xml import Mapper, XmlToJson
from xml_json_converter import xml_to_json, json_to_xml


def pubmed_xml_to_json(xml_string):
    """
    Converts a PubMed XML string to a flattened JSON structure
    :param xml_string: PubMed XML string to flatten into JSON
    :return: JSON
    """
    return xml_to_json(xml_string, element_name="PubmedArticle")


def json_to_pubmed_xml(json_string):
    """
    Converts a flattened PubMed JSON string into a PubMed XML string
    :param json_string: flattened PubMed JSON string to convert to XML
    :return: XML
    """
    return json_to_xml(json_string, "PubmedArticleSet", "PubmedArticle")


def pubmed_xml_to_piano(xml_string):
    """
    Converts a PubMed XML string to a list of Piano dictionaries
    :param xml_string: Pubmed XML string to convert into a list of Piano dictionaries
    :return: list
    """
    parser = XmlToJson(PubMedMapper())
    return parser.xml_to_json(xml_string)


def pubmed_json_to_piano(json_string):
    """
    Converts a flattened PubMed JSON string into a Piano dictionary
    :param json_string: flattened PubMed JSON string to convert into a Piano dictionary
    :return: dict
    """
    def get_non_pubmed_dict(d):
        non_pubmed_dict = {}
        for k in d.keys():
            if not k.startswith(("MedlineCitation", "PubmedData")):
                non_pubmed_dict[k] = d.pop(k)
        return non_pubmed_dict

    json_dict = json.loads(json_string)
    non_pubmed_data = []
    if isinstance(json_dict, list):
        for article in json_dict:
            non_pubmed_data.append(get_non_pubmed_dict(article))
    else:
        non_pubmed_data.append(get_non_pubmed_dict(json_dict))

    piano_dict = pubmed_xml_to_piano(json_to_pubmed_xml(json.dumps(json_dict)))
    if non_pubmed_data:
        for idx, _ in enumerate(non_pubmed_data):
            piano_dict[idx].update(non_pubmed_data[idx])

    return piano_dict


class PubMedMapper(Mapper):

    def __init__(self):
        super(PubMedMapper, self).__init__()
        self.element_names = "PubmedArticle"

    def attach_article_ids(self, xml_items):
        return [(i, {"pmid": self.get_text_if_not_null(i.select_one('PMID'))}) for i in xml_items]

    def transform_to_piano(self, xml_soup_article):
        article = {}

        article['title'] = self.get_text_if_not_null(xml_soup_article.find('ArticleTitle'))
        article['doi'] = self.get_text_if_not_null(
            xml_soup_article.select_one('ArticleIdList > ArticleId[IdType="doi"]'))
        article['journal'] = self.get_text_if_not_null(xml_soup_article.select_one('Journal > Title'))
        article['published_date'] = self.get_text_if_not_null(xml_soup_article.select_one('PubDate > MedlineDate'))
        article['authors'] = [self.get_author(_xml) for _xml in xml_soup_article.select('AuthorList > Author')]
        article['abstract'] = self.get_abstract(xml_soup_article)
        article['keywords'] = ",".join(
            [self.get_single_mesh_heading(_xml) for _xml in xml_soup_article.select('MeshHeadingList > MeshHeading')])
        article['pmid'] = self.get_text_if_not_null(xml_soup_article.select_one('PMID'))
        if article['pmid']:
            article['external_id'] = "PUBMED:" + article['pmid']
        # article['pubmed_xml'] = self.get_text_if_not_null(xml_soup_article)

        article["author_address"] = self.get_text_if_not_null(
            xml_soup_article.select_one('AuthorList > Author > AffiliationInfo > Affiliation'))
        article["pages"] = self.get_text_if_not_null(
            xml_soup_article.select_one('Article > Pagination > MedlinePgn'))
        article["volume"] = self.get_text_if_not_null(
            xml_soup_article.select_one('Journal > JournalIssue > Volume'))
        article["number"] = self.get_text_if_not_null(
            xml_soup_article.select_one('Journal > JournalIssue > Issue'))

        pubdate_year = self.get_text_if_not_null(xml_soup_article.select_one('PubMedPubDate[PubStatus="pubmed"] > Year'))
        pubdate_month = self.get_text_if_not_null(xml_soup_article.select_one('PubMedPubDate[PubStatus="pubmed"] > Month'))
        pubdate_day = self.get_text_if_not_null(xml_soup_article.select_one('PubMedPubDate[PubStatus="pubmed"] > Day'))
        if pubdate_day and pubdate_month and pubdate_year:
            article["edition"] = pubdate_year + "/" + pubdate_month + "/" + pubdate_day

        article["isbn"] = self.get_text_if_not_null(xml_soup_article.select_one('Journal > ISSN'))
        article["language"] = self.get_text_if_not_null(xml_soup_article.select_one('Article > Language'))

        # article["pubmed_xml"] = xml_soup_article.PubmedArticle.wrap(xml_soup_article.new_tag("PubmedArticleSet"))

        return article

    def get_qualifier_name(self, qualifier_xml):
        """
        Gets as an input full xml qualifier: <QualifierName MajorTopicYN="Y" UI="Q000379">methods</QualifierName>
        :param qualifier_xml:
        :return:
        """
        if qualifier_xml is None:
            return None

        text_ = self.get_text_if_not_null(qualifier_xml)

        if isinstance(qualifier_xml, Tag) \
                and qualifier_xml.has_attr('MajorTopicYN') and qualifier_xml['MajorTopicYN'] == "Y":
            return '*' + text_
        else:
            return text_

    def get_single_mesh_heading(self, _xml):

        text_ = [self.get_text_if_not_null(_xml.select_one('DescriptorName'))] + \
                [self.get_qualifier_name(qualifier_xml)
                 if qualifier_xml is not NoneType else None
                 for qualifier_xml in _xml.find_all("QualifierName")]

        # skip all None
        text_ = filter(lambda t: t is not None, text_)

        str_mesh_heading = "/".join(text_)

        return str_mesh_heading

    def get_author(self, _xml):
        # extract elements
        text_ = [_xml.select_one('LastName'), _xml.select_one('ForeName')]

        # skip None values and join by comma
        return u", ".join(i.get_text() for i in filter(lambda t: not isinstance(t, NoneType), text_))

    def get_abstract(self, _xml):
        abstracts_soup = _xml.select('Abstract > AbstractText')
        if not abstracts_soup:
            return None
        abstracts = []
        for abstract in abstracts_soup:
            label = abstract.get("Label", "")
            if label:
                label += ": "
            text = self.get_text_if_not_null(abstract)
            if text:
                abstracts.append(label + text)
        return u"\n\n".join(abstracts) if abstracts else None
