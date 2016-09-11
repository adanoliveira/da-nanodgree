#!/usr/bin/python

import os
import pickle
import re
import sys

from parse_out_email_text import parseOutText

emails_by_address_path = "emails_by_address"
mail_dir_path = '/Users/Adan/Desktop'

"""
    Code to process the emails from enron employees to extract
    the features and get the documents ready for classification.

    The list of all the emails from enron employees are referenced in a folder
    with text files listing their path in the `enron_mail_20110402` email corpus.

    The data is stored in lists and packed away in pickle files at the end.
"""
def createTextData(email_list):
    from_data = []
    word_data = []
    person_emails = {}
    temp_counter = 0

    for email_address, poi in email_list:
        try:
            from_person  = open(os.path.join(emails_by_address_path, "from_"+email_address+".txt"), "r")
            word_data_from_person = []
            for path in from_person:
                temp_counter += 1
                if (temp_counter % 5000) == 0:
                    print "{} parsed emails".format(temp_counter)

                path = os.path.join(mail_dir_path , path[:-1])

                ### using parseOutText to extract the text from the opened email
                email = open(path, "r")
                text = parseOutText(email)

                ### append the text to word_data
                word_data.append(text)
                word_data_from_person.append(text)
                ### append a 0 to from_data if email is not from POI, and 1 if email is from a POI
                from_data.append(poi)

                email.close()
            person_emails[email_address] = word_data_from_person
        except:
            print "emails from %s not found" %email_address

        from_person.close()

    print "all emails processed"
    pickle.dump( word_data, open("enron_word_data.pkl", "w") )
    pickle.dump( from_data, open("enron_email_authors.pkl", "w") )
    pickle.dump( person_emails, open("emails_from_person.pkl", "w") )