#!/usr/bin/python

import sys
import pickle
from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    raw_data_dict = pickle.load(data_file)

### Remove outliers and fix incorrect data
raw_data_dict.pop('TOTAL', None)

raw_data_dict['BELFER ROBERT']['expenses'] = 3285
raw_data_dict['BELFER ROBERT']['director_fees'] = 102500
raw_data_dict['BELFER ROBERT']['deferred_income'] = -102500
raw_data_dict['BELFER ROBERT']['total_payments'] = 3285
raw_data_dict['BELFER ROBERT']['restricted_stock'] = 44093
raw_data_dict['BELFER ROBERT']['restricted_stock_deferred'] = -44093
raw_data_dict['BELFER ROBERT']['deferral_payments'] = 'NaN'
raw_data_dict['BELFER ROBERT']['exercised_stock_options'] = 'NaN'
raw_data_dict['BELFER ROBERT']['total_stock_value'] = 'NaN'

raw_data_dict['BHATNAGAR SANJAY']['expenses'] = 137864
raw_data_dict['BHATNAGAR SANJAY']['total_payments'] = 137864
raw_data_dict['BHATNAGAR SANJAY']['exercised_stock_options'] = 15456290
raw_data_dict['BHATNAGAR SANJAY']['restricted_stock'] = 2604490
raw_data_dict['BHATNAGAR SANJAY']['restricted_stock_deferred'] = -2604490
raw_data_dict['BHATNAGAR SANJAY']['total_stock_value'] = 15456290
raw_data_dict['BHATNAGAR SANJAY']['director_fees'] = 'NaN'
raw_data_dict['BHATNAGAR SANJAY']['other'] = 'NaN'

### Create new features
#### 1. fraction of emails to and from POIs
for person, features in raw_data_dict.iteritems():
    raw_data_dict[person]['fraction_from_poi_to_this_person'] = 0
    raw_data_dict[person]['fraction_from_this_person_to_poi'] = 0
    if raw_data_dict[person]['to_messages'] > 0 and raw_data_dict[person]['from_poi_to_this_person'] != 'NaN':
        raw_data_dict[person]['fraction_from_poi_to_this_person'] = (float(raw_data_dict[person]['from_poi_to_this_person'])
                                                                     / float(raw_data_dict[person]['to_messages']))
    if raw_data_dict[person]['from_messages'] > 0 and raw_data_dict[person]['from_this_person_to_poi'] != 'NaN':
        raw_data_dict[person]['fraction_from_this_person_to_poi'] = (float(raw_data_dict[person]['from_this_person_to_poi'])
                                                                    / float(raw_data_dict[person]['from_messages']))
#### 2. fractions of total compensation
total_payments = ['salary','bonus', 'long_term_incentive', 'deferred_income',
                  'deferral_payments', 'loan_advances', 'other', 'expenses',
                  'director_fees']
total_stock_value = ['exercised_stock_options', 'restricted_stock',
                     'restricted_stock_deferred']

for person, features in raw_data_dict.iteritems():
    raw_data_dict[person]['aux_total_payments'] = (float(raw_data_dict[person]['total_payments'])
                                                    - float(raw_data_dict[person]['deferred_income']))
    raw_data_dict[person]['aux_total_stock_value'] = (float(raw_data_dict[person]['total_stock_value'])
                                                    - float(raw_data_dict[person]['restricted_stock_deferred']))

    for payment_feature in total_payments:
        if raw_data_dict[person]['aux_total_payments'] > 0 and  raw_data_dict[person][payment_feature] != 'NaN':
            raw_data_dict[person][payment_feature + '_fraction_from_payments'] = (float(raw_data_dict[person][payment_feature])
                                                                                / float(raw_data_dict[person]['aux_total_payments']))
        else:
            raw_data_dict[person][payment_feature + '_fraction_from_payments'] = 0

    for stock_feature in total_stock_value:
        if raw_data_dict[person]['aux_total_stock_value'] > 0 and  raw_data_dict[person][stock_feature] != 'NaN':
            raw_data_dict[person][stock_feature + '_fraction_from_stock'] = (float(raw_data_dict[person][stock_feature])
                                                                            / float(raw_data_dict[person]['aux_total_stock_value']))
        else:
            raw_data_dict[person][payment_feature + '_fraction_from_stock'] = 0

    if (float(raw_data_dict[person]['total_payments']) + float(raw_data_dict[person]['total_stock_value'])) > 0:
        raw_data_dict[person]['payments_fraction_from_compensation'] = (float(raw_data_dict[person]['total_payments'])
                                                                        / (float(raw_data_dict[person]['total_payments'])
                                                                           + float(raw_data_dict[person]['total_stock_value'])))
        raw_data_dict[person]['stock_fraction_from_compensation'] = (float(raw_data_dict[person]['total_stock_value']) /
                                                                    (float(raw_data_dict[person]['total_payments'])
                                                                     + float(raw_data_dict[person]['total_stock_value'])))
    else:
        raw_data_dict[person]['payments_fraction_from_compensation'] = 0
        raw_data_dict[person]['stock_fraction_from_compensation'] = 0

    raw_data_dict[person].pop('aux_total_payments', None)
    raw_data_dict[person].pop('aux_total_stock_value', None)

### Store to my_dataset for easy export below
my_dataset = raw_data_dict

### Select features
features_list = ['poi',
                 'exercised_stock_options',
                 'fraction_from_this_person_to_poi',
                 'bonus_fraction_from_payments']


### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Create classifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import MinMaxScaler

rf_clf = RandomForestClassifier(random_state=10,
                               class_weight='balanced',
                               min_samples_split=5,
                               n_estimators=15,
                               max_depth=2,
                               criterion='entropy')

preprocessed_features = FeatureUnion([
        ('scale', MinMaxScaler()),
    ])

estimators = [
    ('features', preprocessed_features),
    ('classify', rf_clf)
]
clf = Pipeline(estimators)

### Dump classifier and data
dump_classifier_and_data(clf, my_dataset, features_list)
