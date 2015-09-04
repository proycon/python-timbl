#! /usr/bin/env python
# -*- coding: utf8 -*-

# Object oriented Python interface wrapping the Timbl API
#   by Maarten van Gompel
#   Radboud University Nijmegen

# Licensed under GPL

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import sys
if sys.version < '3':
    from codecs import getwriter
    stderr = getwriter('utf-8')(sys.stderr)
    stdout = getwriter('utf-8')(sys.stdout)
else:
    stderr = sys.stderr
    stdout = sys.stdout

import timblapi
import io
import os

class LoadException(Exception):
    pass

class ClassifyException(Exception):
    pass

def b(s):
    """Conversion to bytes"""
    if sys.version < '3':
        if isinstance(s, unicode): #pylint: disable=undefined-variable
            return s.encode('utf-8')
    else:
        return s
    #else:
    #    if isinstance(s, str):
    #        return s.encode('utf-8')

def u(s, encoding = 'utf-8', errors='strict'):
    #ensure s is properly unicode.. wrapper for python 2.6/2.7,
    if sys.version < '3':
        #ensure the object is unicode
        if isinstance(s, unicode): #pylint: disable=undefined-variable
            return s
        else:
            return unicode(s, encoding,errors=errors) #pylint: disable=undefined-variable
    else:
        #will work on byte arrays
        if isinstance(s, str):
            return s
        else:
            return str(s,encoding,errors=errors)


class TimblClassifier(object):
    def __init__(self, fileprefix, timbloptions, format = "Tabbed", dist=True, encoding = 'utf-8', overwrite = True,  flushthreshold=10000, threading=False, normalize=True, debug=False):
        if format.lower() == "tabbed":
            self.format = "Tabbed"
            self.delimiter = "\t"
        elif format.lower() == "columns":
            self.format = "Columns"
            self.delimiter = " "
        else:
            raise ValueError("Only Tabbed and Columns are supported input format for the python wrapper, not " + format)
        self.timbloptions = timbloptions
        self.fileprefix = fileprefix

        self.encoding = encoding
        self.dist = dist

        self.normalize= normalize

        self.flushthreshold = flushthreshold
        self.instances = []
        self.api = None
        self.debug = debug

        if os.path.exists(self.fileprefix + ".train") and overwrite:
            self.flushed = 0
        else:
            self.flushed = 1

        self.threading = threading

    def validatefeatures(self,features):
        """Returns features in validated form, or raises an Exception. Mostly for internal use"""
        validatedfeatures = []
        for feature in features:
            if isinstance(feature, int) or isinstance(feature, float):
                validatedfeatures.append( str(feature) )
            elif self.delimiter in feature:
                raise ValueError("Feature contains delimiter: " + feature)
            else:
                validatedfeatures.append(feature)
        return validatedfeatures

    def append(self, features, classlabel):
        if not isinstance(features, list) and not isinstance(features, tuple):
            raise ValueError("Expected list or tuple of features")

        features = self.validatefeatures(features)

        if self.delimiter in classlabel:
            raise ValueError("Class label contains delimiter: " + self.delimiter)

        self.instances.append(self.delimiter.join(features) + self.delimiter + classlabel)
        if len(self.instances) >= self.flushthreshold:
            self.flush()

    def flush(self):
        if self.debug: print("Flushing...",file=sys.stderr)
        if len(self.instances) == 0: return False

        if self.flushed:
            f = io.open(self.fileprefix + ".train",'a', encoding=self.encoding)
        else:
            f = io.open(self.fileprefix + ".train",'w', encoding=self.encoding)

        for instance in self.instances:
            f.write(instance +  "\n")

        self.flushed += len(self.instances)
        f.close()
        self.instances = []
        return True

    def __delete__(self):
        self.flush()

    def train(self, save=False):
        self.flush()
        if not os.path.exists(self.fileprefix + ".train"):
            raise LoadException("Training file '"+self.fileprefix+".train' not found. Did you forget to add instances with append()?")
        options = "-F " + self.format + " " +  self.timbloptions
        if self.dist:
            options += " +v+db +v+di"
        print("Calling Timbl API for training: " + options, file=stderr)
        if sys.version < '3':
            self.api = timblapi.TimblAPI(b(options), b"")
        else:
            self.api = timblapi.TimblAPI(options,"")
        if self.debug:
            print("Enabling debug for timblapi",file=stderr)
            self.api.enableDebug()

        trainfile = self.fileprefix + ".train"
        self.api.learn(b(trainfile))
        if save:
            self.save()
        if self.threading:
            self.api.initthreading()

    def save(self):
        if not self.api:
            raise Exception("No API instantiated, did you train the classifier first?")
        self.api.writeInstanceBase(b(self.fileprefix + ".ibase"))
        self.api.saveWeights(b(self.fileprefix + ".wgt"))

    def classify(self, features, allowtopdistribution=True):

        features = self.validatefeatures(features)

        if not self.api:
            self.load()
        testinstance = self.delimiter.join(features) + self.delimiter + "?"
        if self.dist:
            if self.threading:
                result, cls, distribution, distance = self.api.classify3safe(b(testinstance), self.normalize, int(not allowtopdistribution))
            else:
                result, cls, distribution, distance = self.api.classify3(b(testinstance), self.normalize, int(not allowtopdistribution))
            if result:
                cls = u(cls)
                return (cls, distribution, distance)
                #distribution = u(distribution)
                #if cls:
                #    return (cls, self._parsedistribution(distribution.split(' ')), distance)
                #else:
                #   return (cls, {}, distance)
            else:
                raise ClassifyException("Failed to classify: " + u(testinstance))
        else:
            result, cls = self.api.classify(testinstance)
            if result:
                cls = u(cls)
                return cls
            else:
                raise ClassifyException("Failed to classify: " + u(testinstance))

    def getAccuracy(self):
        if not self.api:
            raise Exception("No API instantiated, did you train and test the classifier first?")
        return self.api.getAccuracy()

    def load(self):
        if not os.path.exists(self.fileprefix + ".ibase"):
            raise LoadException("Instance base '"+self.fileprefix+".ibase' not found, did you train and save the classifier first?")

        options = "-F " + self.format + " " +  self.timbloptions
        if sys.version < '3':
            self.api = timblapi.TimblAPI(b(options), b"")
        else:
            self.api = timblapi.TimblAPI(options, "")
        if self.debug:
            print("Enabling debug for timblapi",file=stderr)
            self.api.enableDebug()
        print("Calling Timbl API : " + options,file=stderr)
        self.api.getInstanceBase(b(self.fileprefix + '.ibase'))
        #if os.path.exists(self.fileprefix + ".wgt"):
        #    self.api.getWeights(self.fileprefix + '.wgt')
        if self.threading:
            if self.debug: print("Invoking initthreading()",file=sys.stderr)
            self.api.initthreading()

    def addinstance(self, testfile, features, classlabel="?"):
        """Adds an instance to a specific file. Especially suitable for generating test files"""

        features = self.validatefeatures(features)

        if self.delimiter in classlabel:
            raise ValueError("Class label contains delimiter: " + self.delimiter)


        f = io.open(testfile,'a', encoding=self.encoding)
        f.write(self.delimiter.join(features) + self.delimiter + classlabel + "\n")
        f.close()

    def test(self, testfile):
        """Test on an existing testfile and return the accuracy"""
        if not self.api:
            self.load()
        if sys.version < '3':
            self.api.test(b(testfile), b(self.fileprefix + '.out'),b'')
        else:
            self.api.test(u(testfile), u(self.fileprefix + '.out'),'')
        return self.api.getAccuracy()


    def crossvalidate(self, foldsfile):
        """Train & Test using cross validation, testfile is a file that contains the filenames of all the folds!"""
        options = "-F " + self.format + " " +  self.timbloptions + " -t cross_validate"
        print("Instantiating Timbl API : " + options,file=stderr)
        if sys.version < '3':
            self.api = timblapi.TimblAPI(b(options), b"")
        else:
            self.api = timblapi.TimblAPI(options, "")
        if self.debug:
            print("Enabling debug for timblapi",file=stderr)
            self.api.enableDebug()
        print("Calling Timbl Test : " + options,file=stderr)
        if sys.version < '3':
            self.api.test(b(foldsfile),b'',b'')
        else:
            self.api.test(u(foldsfile),'','')
        a = self.api.getAccuracy()
        del self.api
        return a



    def leaveoneout(self):
        """Train & Test using leave one out"""
        traintestfile = self.fileprefix + '.train'
        options = "-F " + self.format + " " +  self.timbloptions + " -t leave_one_out"
        if sys.version < '3':
            self.api = timblapi.TimblAPI(b(options), b"")
        else:
            self.api = timblapi.TimblAPI(options, "")
        if self.debug:
            print("Enabling debug for timblapi",file=stderr)
            self.api.enableDebug()
        print("Calling Timbl API : " + options,file=stderr)
        if sys.version < '3':
            self.api.learn(b(traintestfile))
            self.api.test(b(traintestfile), b(self.fileprefix + '.out'),b'')
        else:
            self.api.learn(u(traintestfile))
            self.api.test(u(traintestfile), u(self.fileprefix + '.out'),'')
        return self.api.getAccuracy()

    def readtestoutput(self):
        if not os.path.exists(self.fileprefix + ".out"):
            raise LoadException("No test output available, expected '" + self.fileprefix + ".out' . Run test() first")
        f = io.open(self.fileprefix + '.out', 'r', encoding=self.encoding)
        for line in f:
            endfvec = None
            line = line.strip()
            if line and line[0] != '#': #ignore empty lines and comments
                segments = [ x for i, x in enumerate(line.split(' ')) ]
                #segments = [ x for x in line.split() if x != "^" and not (len(x) == 3 and x[0:2] == "n=") ]  #obtain segments, and filter null fields and "n=?" feature (in fixed-feature configuration)
                if not endfvec:
                    try:
                        # Modified by Ruben. There are some cases where one of the features is a {, and then
                        # the module is not able to obtain the distribution of scores and senses
                        # We have to look for the last { in the vector, and due to there is no rindex method
                        # we obtain the reverse and then apply index.
                        aux=list(reversed(segments)).index("{")
                        endfvec=len(segments)-aux-1
                        #endfvec = segments.index("{")
                    except ValueError:
                        endfvec = None

                if endfvec > 2: #only for +v+db
                    try:
                        enddistr = segments.index('}',endfvec)
                    except ValueError:
                        raise
                    distribution = self._parsedistribution(segments, endfvec, enddistr)
                    if len(segments) > enddistr + 1:
                        distance = float(segments[-1])
                    else:
                        distance = None
                else:
                    endfvec = len(segments)
                    distribution = None
                    distance = None

                #features, referenceclass, predictedclass, distribution, distance
                yield " ".join(segments[:endfvec - 2]).split(self.delimiter), segments[endfvec - 2], segments[endfvec - 1], distribution, distance
        f.close()

    def _parsedistribution(self, instance, start=0, end =None):
        dist = {}
        i = start + 1

        if not end:
            end = len(instance) - 1

        while i < end:  #instance[i] != "}":
            label = instance[i]
            if self.format == "Tabbed": label = label.replace('\\_',' ')
            try:
                score = float(instance[i+1].rstrip(","))
                dist[label] = score
            except:
                print("ERROR: timbl._parsedistribution -- Could not fetch score for class '" + label + "', expected float, but found '"+instance[i+1].rstrip(",")+"'. Instance= " + " ".join(instance)+ ".. Attempting to compensate...",file=stderr)
                i = i - 1
            i += 2

        if not dist:
            print("ERROR: timbl._parsedistribution --  Did not find class distribution for ", instance, file=stderr)

        return dist






