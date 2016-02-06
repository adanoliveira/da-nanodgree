#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/Adan/anaconda/lib/python2.7/site-packages')
import data_cleaning_functions
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
import phonenumbers

def shape_element(element):
    #Parses each node or way element in the OSM XML file to produce a dictionary named "node", which will later be saved as a document of a JSON file (to be imported into MongoDB).
    #Street names, postcodes and phone numbers are cleansed before being saved in the dictionary.
    #Each dictionary is structured as the example below:
    # {
    # "id": "2406124091",
    # "type: "node",
    # "visible":"true",
    # "created": {
    #           "version":"2",
    #           "changeset":"17206049",
    #           "timestamp":"2013-08-03T16:43:42Z",
    #           "user":"linuxUser16",
    #           "uid":"1219059"
    #         },
    # "pos": [41.9757030, -87.6921867],
    # "address": {
    #           "housenumber": "5157",
    #           "postcode": "60625",
    #           "street": "North Lincoln Ave"
    #         },
    # "amenity": "restaurant",
    # "cuisine": "mexican",
    # "name": "La Cabana De Don Luis",
    # "phone": "1 (773)-271-5176"
    # }

    #Declaring the node dictionary
    node = {}

    #Filtering node and way elements
    if element.tag == "node" or element.tag == "way":

        #Parsing tag id attribute
        if "id" in element.attrib:
            node["id"] = element.attrib["id"]

        #Parsing tag tag type
        node["type"] = element.tag

        #Parsing tag visibility attribute
        if "visible" in element.attrib:
            node["visible"] = element.attrib["visible"]

        #Parsing tag creation attributes as a dictionary
        node["created"] = {
                            "version": element.attrib["version"],
                            "changeset": element.attrib["changeset"],
                            "timestamp": element.attrib["timestamp"],
                            "user": element.attrib["user"],
                            "uid": element.attrib["uid"]
                           }

        #Parsing lat and long attributes as a list
        if "lat" in element.attrib:
            node["pos"] = [
                            float(element.attrib["lat"]),
                            float(element.attrib["lon"])
                          ]
        #Creating address dictionary to be used later
        address = {}

        for tag in element.iter("tag"):
            #Parsing address attribute tags and auditing values before saving them in the address dictionary
            if ("addr:" in tag.attrib['k']) and (tag.attrib['k'].count(':') < 2):
                audited_value = data_cleaning_functions.audit_and_clean(tag) #calls audit_and_clean function defined in the data_cleaning_functions.py file
                address[tag.attrib['k'].split(':')[-1]] = audited_value
                node["address"] = address
            #Parsing other tags without problematic characters and auditing values before saving them
            elif tag.attrib['k'].count(':') < 2:
                audited_value = data_cleaning_functions.audit_and_clean(tag) #calls audit_and_clean function defined in the data_cleaning_functions.py file
                node[tag.attrib['k']] = audited_value

        #Parsing tag node_refs attribute
        node_refs = []
        for nd in element.iter("nd"):
            node_refs.append(nd.attrib['ref'])
            node["node_refs"] = node_refs

        #Returing node dictionary for way and node elements
        return node
    else:
        #Returing none object if element is a relation
        return None


def process_map(file_in, pretty = False):
    # Creates a JSON file and iterates through each of the OSM XML's element to generate node dictionaries using the shape_element function defined above.
    # It then saves each node into the JSON file.
    file_out = "{0}.json".format(file_in)
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")

#Running the process_map function to create a JSON file with parsed and cleansed data from OSM XML. This file will later be bulk imported into MongoDB.
process_map('sao-paulo_brazil.osm', True)
