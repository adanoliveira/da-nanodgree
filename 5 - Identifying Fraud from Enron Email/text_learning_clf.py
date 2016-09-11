#!/usr/bin/python

import sys
from time import time
sys.path.append('/Users/Adan/anaconda/lib/python2.7/site-packages')
from sklearn import tree
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, confusion_matrix


#Creating classifying function
def classify(features_train, labels_train, algorithm):
    """ create classifier,
    fit the classifier on the training features and labels
    and return the fit classifier
    """
    if algorithm == 'DT':
        clf = tree.DecisionTreeClassifier()
    elif algorithm == 'MNB':
        clf = MultinomialNB()
    elif algorithm == 'GNB':
        clf = GaussianNB()
        
    return clf.fit(features_train, labels_train)

def testClassifier(classifier, features_test, labels_test):
    """ computes evaluation metrics from input classifier """

    pred = classifier.predict(features_test)
    print "-- Accuracy score: {0:.2f}".format(accuracy_score(labels_test, pred))
    print "-- Classification Report: \n{}".format(classification_report(labels_test, pred))
    print "-- Confusion Matrix: \n{}".format(confusion_matrix(labels_test, pred))
    
    return

def mostInformativeFeatures(vectorizer, clf, n=20):
    """ Prints the n most informative
    features based on their coeficients 
    in a MultinomialNB classifier 
    """
    most_rel_ftrs = []
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    top = coefs_with_fns[:-(n + 1):-1]
    print "coef:     \t feature_name:"
    for (coef, fn) in top:
        print "%.4f \t %-15s" % (coef, fn)
        most_rel_ftrs.append(fn)
    return most_rel_ftrs 