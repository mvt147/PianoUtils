# piano_utils
Provides a set of utilities intended for use in the Piano system. The utilities avaiable are:
* [xml_json_converter](#xml_json_converter)
* [pubmed_converter](#pubmed_converter)

### Installation
```
pip install git+git://github.com/mvt147/PianoUtils.git@v0.1
```

#### or in PyCharm
* Under the Tools dropdown, click Python Console
* Then use pip from within the console:
```
import pip
pip.main(['install','git+git://github.com/mvt147/PianoUtils.git@v0.1'])
```

# xml_json_converter
This utility is used for converting XML and JSON formats between one another. The JSON format is a flattened structure.
```python
from piano_utils.xml_json_converter import xml_to_json, json_to_xml
```

### xml_to_json
Let's say you have the following XML:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<catalog>
    <cd>
        <title>Empire Burlesque</title>
        <artist>Bob Dylan</artist>
        <prices>
            <price type="rrp">10.90</price>
            <price type="special">8.99</price>
        </prices>
        <year>1985</year>
    </cd>
    <cd>
        <title>Hide Your Heart</title>
        <artist>Bonnie Tyler</artist>
        <prices>
            <price type="rrp">9.90</price>
            <price type="special">7.50</price>
        </prices>
        <year>1988</year>
    </cd>
    <cd>
        <title>One Night Only</title>
        <artist>Bee Gees</artist>
        <prices>
            <price type="rrp">10.90</price>
            <price type="special">5.99</price>
        </prices>
        <year>1998</year>
    </cd>
</catalog>
```
which you want to convert to JSON. Just use ```xml_to_json```:
```python
xml_to_json(xml_string)
```

Result:
```json
[{
    "catalog_cd_0_artist": "Bob Dylan",
    "catalog_cd_0_prices_price_0_@type": "rrp",
    "catalog_cd_0_prices_price_0_#text": "10.90",
    "catalog_cd_0_prices_price_1_@type": "special",
    "catalog_cd_0_prices_price_1_#text": "8.99",
    "catalog_cd_0_title": "Empire Burlesque",
    "catalog_cd_0_year": "1985",
    "catalog_cd_1_artist": "Bonnie Tyler",
    "catalog_cd_1_prices_price_0_@type": "rrp",
    "catalog_cd_1_prices_price_0_#text": "9.90",
    "catalog_cd_1_prices_price_1_@type": "special",
    "catalog_cd_1_prices_price_1_#text": "7.50",
    "catalog_cd_1_title": "Hide Your Heart",
    "catalog_cd_1_year": "1988",
    "catalog_cd_2_artist": "Bee Gees",
    "catalog_cd_2_prices_price_0_@type": "rrp",
    "catalog_cd_2_prices_price_0_#text": "10.90",
    "catalog_cd_2_prices_price_1_@type": "special",
    "catalog_cd_2_prices_price_1_#text": "5.99",
    "catalog_cd_2_title": "One Night Only",
    "catalog_cd_2_year": "1998"
}]
```
You can also pass in which element (child descendant from the root) to split the output by:
```python
xml_to_json(xml_string, "cd")
```
Result:
```json
[{
    "artist": "Bob Dylan",
    "prices_price_0_@type": "rrp",
    "prices_price_0_#text": "10.90",
    "prices_price_1_@type": "special",
    "prices_price_1_#text": "8.99",
    "title": "Empire Burlesque",
    "year": "1985"
}, {
    "artist": "Bonnie Tyler",
    "prices_price_0_@type": "rrp",
    "prices_price_0_#text": "9.90",
    "prices_price_1_@type": "special",
    "prices_price_1_#text": "7.50",
    "title": "Hide Your Heart",
    "year": "1988"
}, {
    "artist": "Bee Gees",
    "prices_price_0_@type": "rrp",
    "prices_price_0_#text": "10.90",
    "prices_price_1_@type": "special",
    "prices_price_1_#text": "5.99",
    "title": "One Night Only",
    "year": "1998"
}]
```

### json_to_xml
To convert the JSON above back into the original XML. Use ```json_to_xml```:
```python
# reverse entire file
json_string = xml_to_json(xml_string)
xml_string = json_to_xml(json_string)

# reverse when using subset of file
json_string = xml_to_json(xml_string, "cd")
xml_string = json_to_xml(json_string, "catalog", "cd")
```
# pubmed_converter
This utility is used for converting PubMed XML, JSON, and Piano formats between each other. The JSON format is a flattened structure.
```python
from piano_utils.pubmed_converter import pubmed_xml_to_json, json_to_pubmed_xml, pubmed_xml_to_piano, pubmed_json_to_piano
```
### pubmed_xml_to_json
Let's say you had the following PubMed XML file (shortened):
```xml
<?xml version="1.0"?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2017//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_170101.dtd">
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation Status="MEDLINE" Owner="NLM">
            <PMID Version="1">26419243</PMID>
            <DateCreated>
                <Year>2015</Year>
                <Month>11</Month>
                <Day>12</Day>
            </DateCreated>
            <DateCompleted>
                <Year>2016</Year>
                <Month>08</Month>
                <Day>18</Day>
            </DateCompleted>
            <DateRevised>
                <Year>2016</Year>
                <Month>11</Month>
                <Day>26</Day>
            </DateRevised>
            ...
        </MedlineCitation>
        <PubmedData>
            ...
        </PubmedData>
    </PubmedArticle>
</PubmedArticleSet>
```
which you want to convert to JSON. Use ```pubmed_xml_to_json```:
```python
pubmed_xml_to_json(xml_string)
```
Result (truncated):
```json
[{
    "MedlineCitation_PMID_@Version": "1",
    "MedlineCitation_PMID_#text": "26419243",
    "MedlineCitation_DateCreated_Day": "12",
    "MedlineCitation_DateCreated_Month": "11",
    "MedlineCitation_DateCreated_Year": "2015"
}]
```
### pubmed_json_to_xml
To convert the JSON above back into the original PubMed XML. Use ```pubmed_json_to_xml```:
```python
json_string = pubmed_xml_to_json(xml_string)
xml_string = pubmed_json_to_xml(json_string)
```
### pubmed_xml_to_piano
To convert PubMed XML to the Piano format use ```pubmed_xml_to_piano```:
```python
pubmed_xml_to_piano(xml_string):
```
Result (truncated):
```python
[{
    'pmid': u'26419243',
    'authors': [u'Morgan, Clinton D',
                u'Zuckerman, Scott L',
                u'King, Lauren E',
                u'Beaird, Susan E',
                u'Sills, Allen K',
                u'Solomon, Gary S'],
    'title': u'Post-concussion syndrome (PCS) in a youth population: defining the diagnostic value and cost-utility of brain imaging.',
}]
```
### pubmed_json_to_piano
To convert PubMed JSON to the Piano format use ```pubmed_json_to_piano```:
```python
pubmed_json_to_piano(json_string)
```