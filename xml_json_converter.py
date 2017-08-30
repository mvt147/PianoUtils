import json
import xmltodict
import xml.etree.ElementTree as Et
from flatten_json import flatten, unflatten_list


def xml_to_json(xml_string, element_name=None):
    """
    Converts an XML string to a flattened JSON structure
    :param xml_string: XML string to flatten into JSON
    :param element_name: (optional) XML element name from which the child elements are converted
    :return: JSON
    """
    json_list = []
    if element_name:
        root = Et.fromstring(xml_string)
        for element in root.iter(element_name):
            xml_dict = xmltodict.parse(Et.tostring(element))
            json_list.append(flatten(xml_dict.get(element_name, {})))
    else:
        json_list.append(flatten(xmltodict.parse(xml_string)))

    return json.dumps(json_list)


def json_to_xml(json_string, root_name):
    """
    Converts a JSON string to an XML string
    :param json_string: JSON string to convert into XML
    :param root_name: root element name in the XML
    :return: XML
    """
    json_value = json.loads(json_string)
    if isinstance(json_value, list):
        json_dicts = []
        for json_string in json_value:
            json_dicts.append(unflatten_list(json_string))
        return xmltodict.unparse({root_name: json_dicts})
    elif isinstance(json_value, dict):
        return xmltodict.unparse({root_name: unflatten_list(json_value)})
