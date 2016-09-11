#!/usr/bin/python

from nltk.stem.snowball import SnowballStemmer
import string

def parseOutText(f):
    """ given an opened email file f, parse out all text below the
        metadata block at the top, stem words
        and return a string that contains all the words
        in the email (space-separated)
        
        example use case:
        f = open("email_file_name.txt", "r")
        text = parseOutText(f)
        
        """
    f.seek(0)  ### go back to beginning of file (annoying)
    all_text = f.read()

    ### split off metadata
    content = all_text.split("X-FileName:")
    words = ""
    if len(content) > 1:
        ### remove punctuation
        text_string = content[1].translate(string.maketrans("", ""), string.punctuation)

        ### split the text string into individual words, stemming each word,
        ### and appending the stemmed word to words
        words = text_string.strip().split()
        stemmer = SnowballStemmer("english")
        stemmed_text_string = ""
 
        for word in words:
            stemmed_text_string += stemmer.stem(word) + " "

    return stemmed_text_string.strip()