#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
sys.path.append('/Users/Adan/anaconda/lib/python2.7/site-packages')
import data_cleaning_functions
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")

def is_post_code(elem):
    return (elem.attrib['k'] == "addr:postcode")

def is_phone_number(elem):
    return (elem.attrib['k'] == "phone")


def audit_and_clean(tag):
    # With a tag as an input, assigns the proper data cleaning function for each tag type and returns the audited value
    if is_street_name(tag):
        #running street auditing and cleaning function
        audited_value = audit_street_type(tag.attrib['v'])

    elif is_post_code(tag):
        #running postcode cleaning function
        audited_value = clean_post_code(tag.attrib['v'])

    elif is_phone_number(tag):
        #running phone number cleaning function
        audited_value = clean_phone_number(tag.attrib['v'])
    else:
        audited_value = tag.attrib['v']

    return audited_value

def audit_street_type(street_name):
    # Parses the street name and if it's of an incorrect type, runs it through the clean_street_name function, returning a cleansed street name.

    street_type_re = re.compile(r'\S+\.?\b', re.IGNORECASE) #defining the regex to match the street types

    #listing expected values
    expected = ["Rua", "Avenida", "Alameda", "Quarteirão", "Quadra", "Lugar", "Viela", "Faixa", "Estrada",
                "Trilha", "Praça", "Passarela", 'Acesso', 'Largo', 'Rodovia', 'Travessa']


    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type.encode('utf-8','ignore') not in expected:
            better_name = clean_street_name(street_name) #calling clean_street_name function if street_type not in the expected list
            street_name = better_name #replacing original name with the cleansed name
    return street_name

def clean_street_name(street_name):
    # Takes the original street name with a mapped incorrect type and returs a copy with the corresponding correct type.

    #mapping the correct type for each of incorrect types found in the audit phase
    st_types_mapping = { "Acost ": "Acostamento ",
                "Acost.": "Acostamento",
                "Al.": "Alameda",
                "Al ": "Alameda ",
                "Alfonso ": "Avenida Alfonso ",
                "Antonio ": "Rua Antonio ",
                "Av ": "Avenida ",
                "Av.": "Avenida",
                "Coronel ": "Rua Coronel ",
                "Corredor ": "Avanida Corredor ",
                "Doutor ": "Rua Doutor ",
                "Franklin ": "Rua Franklin ",
                "Garcia ": "Rua Garcia ",
                "Manoel ": "Rua Manoel ",
                "Oscar ": "Rua Oscar ",
                "R ": "Rua ",
                "R.": "Rua",
                "RUA ": "Rua ",
                "RUa ": "Rua ",
                "Tavares ": "Rua Tavares ",
                "Vicente ": "Rua Vicente ",
                "avenida ": "Avenida ",
                "estrada ": "Estrada ",
                "rua ": "Rua "}

    #replacing incorrect substrings according to previous map
    done = False
    for item in st_types_mapping.iteritems():
        if done == False:
            better_name = street_name.replace(item[0], item[1].decode('utf-8'))
            if better_name != street_name:
                done = True
    return better_name


def clean_post_code(post_code):
    # Takes the orignial postcode and if it's problematic, replaces it with a copy conforming to the correct schema ("00000-000")

    post_code = post_code.encode('ascii','ignore')

    #cleaning codes with missing characters
    if ("-" not in post_code) and (len(post_code) < 8):
        mis_char_mapping = { "09380": "09380-000",
                             "05410": "05410-000",
                             "12242": "12242-000"}
        done = False
        for item in mis_char_mapping.iteritems():
            if done == False:
                fixed_post_code = post_code.replace(item[0], item[1])
                if fixed_post_code != post_code:
                    done = True
        post_code = fixed_post_code

    #cleaning codes with extra characters
    elif ((("-" not in post_code) and (len(post_code) > 8)) or (len(post_code) > 9)):
        ex_char_mapping = {
                            "010196-200": "01019-020",
                            "12.216-540": "12216-540",
                            "13.308-911": "13308-911",
                            "02363000": "02363-000",
                            "04783 020": "04783-020",
                            "042010-000": "04201-000",
                            "03032.030": "03032-030",
                            "09380-310 ": "09380-310",
                            "02213-070 ": "02213-070",
                            "02121-020 ": "02121-020",
                            "02831-000 ": "02831-000",
                            "09991-060 ": "09991-060",
                            "08451000.": "08451-000",
                            "04266 - 060": "04266-060",
                            "093340-180": "09334-180",
                            "12.243-360": "12243-360",
                            "040701-000": "04071-000",
                            "Igreja Presbiteriana Vila Gustavo": "02205-000",
                            "09790 - 400": "09790-400",
                            "09171 - 430": "09171-430",
                            "08451000.": "08451-000",
                            "042010-000": "04201-000",
                            "09890 070": "09890-070",
                            "09790 - 400": "09790-400",
                            "024350000": "024350-000",
                            "09810": "09810-000",
                            "03032.030": "03032-030",
                            "13.214-660": "13214-660",
                            "04122-0000": "04122-000",
                            "09890-1 09890-080 00": "09890-080",
                            "CEP 05118-100": "05118-100",
                            "09832 400": "09832-400"
                          }
        done = False
        for item in ex_char_mapping.iteritems():
            if done == False:
                fixed_post_code = post_code.replace(item[0], item[1])
                if fixed_post_code != post_code:
                    done = True
        post_code = fixed_post_code

    #cleaning codes missing the hyphen
    elif "-" not in post_code:
        fixed_post_code = post_code[:5] + '-' + post_code[5:]

        post_code = fixed_post_code

    return post_code


def clean_phone_number(phone_number):
    # Takes a phone number and returns a parsed copy conforming to the international schema ("+00 00 0000-0000").

    import phonenumbers #importing phonenumbers module

    #defining list of problematic numbers mapped in the audit phase
    prob_phone = ["55 11 3884 4016 / 97680-0017", "+11 55 4356 5226", "+55 11 1 3135 4156","+55 11 11 2063 9494","+55 11 2901-3155 / 2769-2901","+55 11 3814-3819  -  3031-1065","+55 11 433 .7185","+55 11+55 11","+55 11193","+55 11190","+55 4104 3859","+55 4109 2485","+55 4343 6454","11 2959-3594 / 2977-2491","11 3091-3503 / 3091-3596","3862-2772 / 36730360","55+ (11) 3670-8000","+55 11 11 4128 2828","+55 11 11 4392 6611"]

    #treating phone numbers to be parsed later
    if ("-" not in phone_number) and (len(phone_number) <= 9) or (" " not in phone_number) and (len(phone_number) <= 9):
        phone_number = "+55 11" + phone_number

    elif ("-" in phone_number) and (len(phone_number) <= 10) or (" " not in phone_number) and (len(phone_number) <= 10):
        phone_number = "+55 11" + phone_number

    elif phone_number in prob_phone:
        prob_phone_mapping = { "+11 55 4356 5226": "+55 11 4356 5226",
                "+55 11 1 3135 4156": "+55 11 3135 4156",
                "+55 11 11 2063 9494": "+55 11 2063 9494",
                "+55 11 11 4128 2828": "+55 11 4128 2828",
                "+55 11 11 4392 6611": "+55 11 4392 6611",
                "+55 11 2901-3155 / 2769-2901": "+55 11 2901-3155 / +55 11 2769-2901",
                "+55 11 3814-3819  -  3031-1065": "+55 11 3814-3819  -  +55 11 3031-1065",
                "+55 11 433 .7185": "+55 11 43337185",
                "+55 11+55 11": "+55 11",
                "+55 11193": "+55 11",
                "+55 11190": "+55 11",
                "+55 4104 3859": "+55 11 4104 3859",
                "+55 4109 2485": "+55 11 4109 2485",
                "+55 4343 6454": "+55 11 4343 6454",
                "11 2959-3594 / 2977-2491": "11 2959-3594 / 11 2977-2491",
                "11 3091-3503 / 3091-3596": "11 3091-3503 / 11 3091-3596",
                "3862-2772 / 36730360": "11 3862-2772 / 11 36730360",
                "55+ (11) 3670-8000": "+55 (11) 3670-8000",
                "55 11 3884 4016 / 97680-0017": "55 11 3884 4016 / 11 97680-0017"}

        for item in prob_phone_mapping.iteritems():
                if phone_number == item[0]:
                    phone_number = item[1]

    #parsing phone numbers using functions from the phonenumbers module
    try:
        x = phonenumbers.parse(phone_number, "BR")
        parsed_phone_number = phonenumbers.format_number(x, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except:
        parsed_phone_number = []
        for match in phonenumbers.PhoneNumberMatcher(phone_number, "BR"):
            parsed_phone = phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            parsed_phone_number.append(parsed_phone) #if the original string contains more than a number, they are converted into a list.

    return parsed_phone_number
