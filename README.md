# piano_utils
Provides a set of utilities intended for use in the Piano system.

### Installation
```
pip install piano_utils
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
Let's say you wanted to convert the JSON above back into the original XML. Use ```json_to_xml```:
```python
# reverse entire file
json_string = xml_to_json(xml_string)
xml_string = json_to_xml(json_string)

# reverse when using subset of file
json_string = xml_to_json(xml_string, "cd")
xml_string = json_to_xml(json_string, "catalog", "cd")
```
