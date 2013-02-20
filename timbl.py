#! /usr/bin/env python
# -*- coding: utf8 -*-

# Object oriented Python interface wrapping the Timbl API
#   by Maarten van Gompel
#   Radboud University Nijmegen

# Licensed under GPL 

import timblapi
import codecs
import sys
import os

class TimblClassifier(object):
    def __init__(self, fileprefix, timbloptions, format = "Tabbed", dist=True, encoding = 'utf-8', overwrite = True,  flushthreshold=10000):
        if format.lower() == "tabbed":
            self.format = "Tabbed"
            self.delimiter = "\t"
        elif format.lower() == "columns":
            self.format = "Columns"
            self.delimiter = " "
        else:            
            raise ValueError("Only Tabbed and Columns are supported input format for the python wrapper, not " + format)
        self.timbloptions = timbloptions
        if isinstance(fileprefix, unicode):
            self.fileprefix = fileprefix.encode('utf-8')
        else:
            self.fileprefix = fileprefix

        self.encoding = encoding
        self.dist = dist
        
        self.flushthreshold = flushthreshold 
        self.instances = []
        self.api = None
        
        if os.path.exists(self.fileprefix + ".train") and overwrite:     
            self.flushed = 0
        else:
            self.flushed = 1
            
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
        if len(self.instances) == 0: return False
        
        if self.flushed:
            f = codecs.open(self.fileprefix + ".train",'a', self.encoding)
        else:
            f = codecs.open(self.fileprefix + ".train",'w', self.encoding)
        
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
            raise Exception("Training file not found. Did you forget to add instances with append()?")
        options = "-F " + self.format + " " +  self.timbloptions
        if self.dist:    
            options += " +v+db +v+di"
        print >>sys.stderr, "Calling Timbl API for training: " + options 
        self.api = timblapi.TimblAPI(options, "")
        trainfile = self.fileprefix + ".train"
        self.api.learn(trainfile)
        if save:
            self.save()

    def save(self):
        if not self.api:
            raise Exception("No API instantiated, did you train the classifier first?")    
        self.api.writeInstanceBase(self.fileprefix + ".ibase")
        self.api.saveWeights(self.fileprefix + ".wgt")            

    def classify(self, features):
        
        features = self.validatefeatures(features)
        
        if not self.api:
            self.load()
        testinstance = self.delimiter.join(features) + self.delimiter + "?"
        if isinstance(testinstance,unicode):
            testinstance = testinstance.encode('utf-8')
        if self.dist:
            result, cls, distribution, distance = self.api.classify3(testinstance)            
            return (cls, self._parsedistribution(distribution.split(' ')), distance)
        else:
            result, cls = self.api.classify(testinstance)
            return cls
        
    def getAccuracy(self):
        if not self.api:
            raise Exception("No API instantiated, did you train and test the classifier first?")   
        return self.api.getAccuracy()
                
    def load(self):
        if not os.path.exists(self.fileprefix + ".ibase"):
            raise Exception("Instance base not found, did you train and save the classifier first?")
        
        options = "-F " + self.format + " " +  self.timbloptions
        self.api = timblapi.TimblAPI(options, "") 
        print >>sys.stderr, "Calling Timbl API : " + options
        self.api.getInstanceBase(self.fileprefix + '.ibase')
        #if os.path.exists(self.fileprefix + ".wgt"):
        #    self.api.getWeights(self.fileprefix + '.wgt')
        
    def addinstance(self, testfile, features, classlabel="?"):        
        """Adds an instance to a specific file. Especially suitable for generating test files"""
        
        features = self.validatefeatures(features)
                
        if self.delimiter in classlabel: 
            raise ValueError("Class label contains delimiter: " + self.delimiter)

        
        f = codecs.open(testfile,'a', self.encoding)
        f.write(self.delimiter.join(features) + self.delimiter + classlabel + "\n")
        f.close()
        
    def test(self, testfile):        
        """Test on an existing testfile and return the accuracy"""
        if not self.api:
            self.load()
        if isinstance(testfile, unicode):
            testfile = testfile.encode('utf-8')
        self.api.test(testfile, self.fileprefix + '.out','')
        return self.api.getAccuracy()                        
            
    def readtestoutput(self):
        if not os.path.exists(self.fileprefix + ".out"):
            raise Exception("No test output available. Run test() first")
        f = codecs.open(self.fileprefix + '.out', 'r', self.encoding)
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
                print >>sys.stderr, "ERROR: timbl._parsedistribution -- Could not fetch score for class '" + label + "', expected float, but found '"+instance[i+1].rstrip(",")+"'. Instance= " + " ".join(instance)+ ".. Attempting to compensate..."
                i = i - 1
            i += 2
            
        if not dist:
            print >>sys.stderr, "ERROR: timbl._parsedistribution --  Did not find class distribution for ", instance

        return dist

        
    
        
        
        
