#! /usr/bin/env python
# -*- coding: utf8 -*-


from __future__ import print_function,  unicode_literals, division, absolute_import #Make Python 2.x act as much like Python 3 as possible

import timbl
import os

#We are building a very simple context-aware translator Word Sense Disambiguator for the word "bank", based on the occurrence of some keywords in the same sentence: 

# The features are binary and represent presence or absence of certain keywords. We choose: 
# - money
# - sit
# - river
#They have a value of 0 or 1   (but note that Timbl support string features just as well!) 

#The classes we predict are:
# - financial
# - furniture
# - geographic

#Build the classifier training
classifier = timbl.TimblClassifier("wsd-bank", "-a 0 -k 1" ) #wsd-bank will be the prefix of any files written for timbl
classifier.append( (1,0,0), 'financial') #append is used to add training instances
classifier.append( (0,1,0), 'furniture')
classifier.append( (0,0,1), 'geographic')

#Train the classifier
classifier.train()


#Save
classifier.save()

#We start anew and load the classifier again (of course we could have just skipped this and the save step and continued immediately)
classifier = timbl.TimblClassifier("wsd-bank", "-a 0 -k 1" ) #wsd-bank will be the prefix of any files written for timbl
classifier.load() #even if this is omitted it will still work, the first classify() call will invoke load() 

#Let's classify an instance:
classlabel, distribution, distance = classifier.classify( (1,0,0) )
if classlabel == "financial":
    print("Classified correctly! Our accuracy is " + str(classifier.getAccuracy()))


#Let's classify an ambiguous one:
winningclasslabel, distribution, distance = classifier.classify( (1,1,1) )
for classlabel, score in distribution.items():
    print(classlabel + ": " + str(score))

print("Distance: ", distance)


#We again start anew and build a test file
if os.path.exists("testfile"): #delete if it already exists
    os.unlink("testfile")


classifier = timbl.TimblClassifier("wsd-bank", "-a 0 -k 1" )
classifier.load()
classifier.addinstance("testfile", (1,0,0),'financial' ) #addinstance can be used to add instances to external files (use append() for training)
classifier.addinstance("testfile", (0,1,0),'furniture' )
classifier.addinstance("testfile", (0,0,1),'geograpic' )
classifier.addinstance("testfile", (1,1,0),'geograpic' ) #this one will be wrongly classified as financial & furniture 

classifier.test("testfile")

print("Accuracy: ", classifier.getAccuracy())


















