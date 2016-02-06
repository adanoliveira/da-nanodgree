#!/usr/bin/env python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as ET
import pprint
import re
import pandas as pd
from collections import defaultdict



### Counts the number of occurrences of each tag type in the document
### Output is a dictionary with the keys being each tag type and the values being their count.
def count_tags(filename):
        tags = {}
        for event, elem in ET.iterparse(filename):
            if elem.tag in tags.keys():
                tags[elem.tag] += 1
            elif elem.tag not in tags.keys():
                tags[elem.tag] = 1
        return tags

macro_tags = count_tags('sao-paulo_brazil.osm')
pprint.pprint(tags)



### Counts the number of occurrences of each tag key name by it's structure.
### Output is a dictionary with the keys being each type name and the values being their count.
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    if element.tag == "tag":
        for tag in element.iter("tag"):
            if re.search(lower, tag.attrib['k']) is not None:
                keys['lower'] += 1
            elif re.search(lower_colon, tag.attrib['k']) is not None:
                keys['lower_colon'] += 1
            elif re.search(problemchars, tag.attrib['k']) is not None:
                keys['problemchars'] += 1
            else:
                keys['other'] += 1
    return keys


def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

keys = process_map('sao-paulo_brazil.osm')
pprint.pprint(keys)



### Counts the number of occurrences of each address key type used and creates a dataframe sorting them from the most used to the least used ones.
### Output is a Pandas DataFrame with a column listing the address key types and another column with their counts, in descending order.
def count_address_keys(filename):
        tags = {}
        for event, element in ET.iterparse(filename):
             if element.tag == "tag":
                    for tag in element.iter("tag"):
                        if "addr:" in tag.attrib['k']:
                            if tag.attrib['k'] in tags.keys():
                                tags[tag.attrib['k']] += 1
                            elif tag.attrib['k'] not in tags.keys():
                                tags[tag.attrib['k']] = 1
        return tags

tags = count_address_keys('sao-paulo_brazil.osm')
tags_df = pd.DataFrame(tags.items(), columns=['Tag', 'Count'])
tags_df.sort_values(by='Count', ascending=False).head(10)



### Counts the number of occurrences of each key type used and creates a dataframe sorting keys from the most used to the least used ones.
### Output is a Pandas DataFrame with a column listing the key types and another column with their counts, in descending order.
def count_keys(filename):
        tags = {}
        for event, element in ET.iterparse(filename):
             if element.tag == "tag":
                    for tag in element.iter("tag"):
                        if tag.attrib['k'] in tags.keys():
                            tags[tag.attrib['k']] += 1
                        elif tag.attrib['k'] not in tags.keys():
                            tags[tag.attrib['k']] = 1
        return tags

tags = count_keys('sao-paulo_brazil.osm')
tags_df = pd.DataFrame(tags.items(), columns=['Tag', 'Count'])
tags_df.sort_values(by='Count', ascending=False).head(100)



### Counts the number of map contributors for the region
### Output is an integer number
def process_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.tag == "node" or element.tag == "way" or element.tag == "relation":
                users.add(element.attrib["uid"])
    return users

users = process_map('sao-paulo_brazil.osm')
print len(users)


### Audits ways for unexpected types, listing the occurencies for each unexpected type in a set dictionary
### Output is a dictionary where the keys are the unexpected types and the values are sets of occurrences for each unexpected type
OSMFILE = "sao-paulo_brazil.osm"
street_type_re = re.compile(r'\S+\.?\b', re.IGNORECASE)

expected = ["Rua", "Avenida", "Alameda", "Quarteirão", "Quadra", "Lugar", "Viela", "Faixa", "Estrada",
            "Trilha", "Praça", "Passarela"]

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types


st_types = audit(OSMFILE)
pprint.pprint(dict(st_types))



### Audits postcodes by grouping them into different problematic scenarios (e.g. extra or missing characters), and listing examples for each case.
### Output is a dictionary of tuples with one element being the count of occurrences in each scenario and the other being a list of up to 20 examples.

OSMFILE = "sao-paulo_brazil.osm"
post_code_re = re.compile(r'\d{5}\-\d{3}', re.IGNORECASE)
correct = []
extra_chars = []
missing_chars = []
missing_hyphen = []
wrong_region = []

def audit_post_code(post_code_types, post_code):
    post_code = post_code.encode('ascii','ignore')
    if ("-" not in post_code) and (len(post_code) < 8):
        missing_chars.append(post_code)
        post_code_types["missing_chars"] =(len(missing_chars), missing_chars[:20])

    elif (("-" not in post_code) and (len(post_code) > 8) or (len(post_code) > 9)):
        extra_chars.append(post_code)
        post_code_types["extra_chars"] = (len(extra_chars), extra_chars[:20])

    elif "-" not in post_code:
        missing_hyphen.append(post_code)
        post_code_types["missing_hyphen"] = (len(missing_hyphen), missing_hyphen[:20])

    elif (post_code[0] != "0") and (post_code[0] != "1"):
        wrong_region.append(post_code)
        post_code_types["wrong_region"] = (len(wrong_region), wrong_region[:20])

    elif re.search(post_code_re, post_code) is not None:
        correct.append(post_code)
        post_code_types["correct"] = (len(correct), correct[:20])


def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    post_code_types = {"missing_chars":0, "extra_chars":0, "missing_hyphen":0, "wrong_region":0, "correct":0}
    counter = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_post_code(tag):
                    audit_post_code(post_code_types, tag.attrib['v'])
                    counter += 1
    return post_code_types


pc_types = audit(OSMFILE)
pprint.pprint(dict(pc_types))


### Audits phone numbers by grouping them into different problematic scenarios (e.g. extra or missing characters), and listing examples for each case.
### Output is a dictionary of tuples with one element being the count of occurrences in each scenario and the other being a list of up to 20 examples.

OSMFILE = "sao-paulo_brazil.osm"

other = []
extra_chars = []
missing_chars = []
missing_hyphen = []

def audit_phone_number(phone_number_types, phone_number):
    if ("-" not in phone_number) and (len(phone_number) < 8):
        missing_chars.append(phone_number)
        phone_number_types["missing_chars"] =(len(missing_chars), missing_chars[:20])

    elif ("-" not in phone_number) and (len(phone_number) > 8):
        extra_chars.append(phone_number)
        phone_number_types["extra_chars"] = (len(extra_chars), extra_chars[:20])

    elif "-" not in phone_number:
        missing_hyphen.append(phone_number)
        phone_number_types["missing_hyphen"] = (len(missing_hyphen), missing_hyphen[:20])

    else:
        other.append(phone_number)
        phone_number_types["other"] = (len(other), other[:20])


def is_phone_number(elem):
    return (elem.attrib['k'] == "phone")


def audit(osmfile):
    osm_file = open(osmfile, "r")
    phone_number_types = {"missing_chars":0, "extra_chars":0, "missing_hyphen":0, "other":0}
    counter = 0
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_phone_number(tag):
                    counter += 1
                    audit_phone_number(phone_number_types, tag.attrib['v'])
    return phone_number_types


pn_types = audit(OSMFILE)
pprint.pprint(pn_types)
