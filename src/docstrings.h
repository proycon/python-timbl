#ifndef TIMBL_DOC_H
#define TIMBL_DOC_H

#include <Python.h>

PyDoc_STRVAR(SHOWOPTIONS_DOC, "self.showOptions(stream)\n\nPrint all options with their possible and current values to an output\nstream.\n\n:Parameters:\n  `stream`\n      a stream object, i.e. any object that has a `fileno` method\n      whose return value is a valid file descriptor\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(SHOWBESTNEIGHBORS_DOC, "self.showBestNeighbors(stream, distr)\n\nThis is an alias for ``showBestNeighbours``.");

PyDoc_STRVAR(ALGO_DOC, "self.algo()\n\nReturn the current algorithm.\n\n:return: the current algorithm\n:rtype: Algorithm");

PyDoc_STRVAR(CLASSIFY_DOC, "self.classify(instance)\n\nReturn the predicted class for a given test instance.\n\n:Parameters:\n  `instance` : str\n      a string representation of the test instance. The format of this\n      string is the same as used by the TiMBL command-line\n      application.\n\n:return: (boolean signalling success or failure, the predicted class)\n:rtype: (bool, str)");

PyDoc_STRVAR(BESTNEIGHBOURS_DOC, "self.bestNeighbours(distr)\n\nReturn the output of the showBestNeighbours method as a string.\n\n:return: the output of the showBestNeighbours method\n:rtype: str");

PyDoc_STRVAR(WRITEINSTANCEBASE_DOC, "self.writeInstanceBase(file)\n\nStore the current instance base to a file.\n\n:Parameters:\n  `file` : str\n      the output file to write the instance base to\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(SETOPTIONS_DOC, "self.setOptions(opts)\n\nChange the value of one or more options.\n\nSome options can only be set when initialising a TimblAPI\ninstance. Trying to change the value of those options with this method\nwill not succeed.\n\n:Parameters:\n  `opts` : str\n      an option string; this string follows the same format as is used\n      to pass option values to the TiMBL command-line application\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(WRITENAMESFILE_DOC, "self.writeNamesFile(file)\n\nWrite a C4.5-style names file.\n\n:Parameters:\n  `file` : str\n      the output file to write\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(REMOVE_DOC, "self.remove(file)\n\nRemove all instances in a file from the instance base.\n\n:Parameters:\n  `file` : str\n      the input file to read the instances from\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(VERSIONINFO_DOC, "self.versionInfo(full)\n\nReturn a string containing the version number, revision, revision\nstring, and optionally date and time of compilation of this TimblAPI\nimplementation\n\n:Parameters:\n  `full` : bool\n      if True, include the date and time of compilation in the\n      returned string\n\n:return: version info string\n:rtype: str");

PyDoc_STRVAR(CURRENTWEIGHTING_DOC, "self.currentWeighting()\n\nReturn the current weighting scheme.\n\n:return: the current weighting scheme\n:rtype: Weighting");

PyDoc_STRVAR(DECREMENT_DOC, "self.decrement(instance)\n\nRemove an instance from the instance base.\n\n:Parameters:\n  `instance` : str\n      a string representation of the instance to be removed. The\n      format of this string is the same as used by the TiMBL\n      command-line application.\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(EXPAND_DOC, "self.expand(file)\n\nAdd all instances in a file to the instance base.\n\n:Parameters:\n  `file` : str\n      the input file to read the instances from\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(EXPNAME_DOC, "self.expName()\n\nReturn the experiment name passed to the constructor of this TimblAPI\ninstance.\n\n:return: the name of the current experiment\n:rtype: str");

PyDoc_STRVAR(BESTNEIGHBORS_DOC, "self.bestNeighbors(distr)\n\nThis is an alias for ``bestNeighbours``.");

PyDoc_STRVAR(STARTSERVER_DOC, "self.startServer(port, maxConnections)\n\nStart a TiMBL server.\n\n:Parameters:\n  `port` : int\n      the TCP port on which to listen for connections\n\n  `maxConnections` : int\n      the maximum number of simultaneous connections\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(OPTIONS_DOC, "self.options()\n\nReturn the output of the showOptions method as a string.\n\n:return: the output of the showOptions method\n:rtype: str");

PyDoc_STRVAR(GETARRAYS_DOC, "self.getArrays(file)\n\nLoad probability arrays from a file.\n\n:Parameters:\n  `file` : str\n      the input file to load the arrays from\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(TIMBLAPI_DOC, "The TiMBL Application Programming Interface. All functionality exposed\nthrough the TiMBL C++ API can be accessed using methods of this class.");

PyDoc_STRVAR(SETTINGS_DOC, "self.settings()\n\nReturn the output of the showSettings method as a string.\n\n:return: the output of the showSettings method\n:rtype: str");

PyDoc_STRVAR(INIT_DOC, "TimblAPI(options, name)\n\nCreate a TiMBL experiment. The options argument is used to pass\nvarious options to TiMBL in exactly the same way as they would be\nwritten on the command-line. Some (but not all) option settings can\nlater on be changed using the setOptions method.\n\n:Parameters:\n  `options` : str\n      an option string used to initialise various TiMBL settings\n\n  `name` : str\n      a descriptive name given to the experiment. This name is printed\n      with any warning or error messages produced by TiMBL.");

PyDoc_STRVAR(TEST_DOC, "self.test(in, out, perc)\n\nTest the TiMBL model using the given test file.\n\n:Parameters:\n  `in` : str\n      the input file containing the test instances\n\n  `out` : str\n      the output file to write the output predictions to\n\n  `perc` : str\n      if not empty (\'\'), the file to write the classification accuracy to\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(SHOWSETTINGS_DOC, "self.showSettings(stream)\n\nPrint all options and their current values to an output stream.\n\n:Parameters:\n  `stream`\n      a stream object, i.e. any object that has a `fileno` method\n      whose return value is a valid file descriptor\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(LEARN_DOC, "self.learn(file)\n\nTrain TiMBL on the specified input file.\n\n:Parameters:\n  `file` : str\n      the input file containing the training instances.\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(CLASSIFY3_DOC, "self.classify3(instance)\n\nReturn the predicted class, the class distribution, and the distance\nof the nearest neighbour for a given test instance.\n\n:Parameters:\n  `instance` : str\n      a string representation of the test instance. The format of this\n      string is the same as used by the TiMBL command-line\n      application.\n\n:return: (boolean signalling success or failure, the predicted class,\n          class distribution, distance of the nearest neighbour)\n:rtype: (bool, str, str, float)");

PyDoc_STRVAR(GETWEIGHTS_DOC, "self.getWeights(file, weighting)\n\nLoad the feature weight table for the given weighting scheme from a file.\n\n:Parameters:\n  `file` : str\n      the input file to load the table from\n\n  `weighting` : Weighting\n      the feature weighting scheme for which to load the table\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(GETINSTANCEBASE_DOC, "self.getInstanceBase(file)\n\nLoad an instance base from a file.\n\n:Parameters:\n  `file` : str\n      the input file to load the instance base from\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(SHOWBESTNEIGHBOURS_DOC, "self.showBestNeighbours(stream, distr)\n\nPrint the nearest neighbour set for the most-recent classification to\nan output stream.\n\nFor this method to work successfully, either the +vn or the +vk\noptions must have been enabled. The output printed to the output\nstream is the same as produced by the TiMBL command-line application\nusing the same options.\n\n:Parameters:\n  `stream`\n      a stream object, i.e. any object that has a `fileno` method whose\n      return value is a valid file descriptor\n\n  `distr` : bool\n      if True, also print distributions\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(MODULE_DOC, "The Tilburg Memory-Based Learner (TiMBL) is an efficient\nimplementation of several memory-based learning algorithms. In\naddition to the TiMBL command-line application, TiMBL\'s functionality\nis also available for programmatic access via a C++ programming\ninterface, referred to as the TimblAPI. This module implements a\nPython language binding to this interface.\n\nThe main entry point for this module is the TimblAPI class. It\nprovides methods for all standard tasks that can be performed with\nTiMBL. The following brief example shows how a TiMBL classifier is\ntrained, and subsequently applied to an unseen test instance.\n\n>>> import timbl\n>>> mbl = timbl.TimblAPI(\'-a IB1\', \'\')\n>>> mbl.learn(\'dimin.data\')\n>>> mbl.classOf(\'- - - = t j e ?\')\n(True, \'T\')");

PyDoc_STRVAR(CLASSIFY2_DOC, "self.classify2(instance)\n\nReturn the predicted class and the distance of the nearest neighbour\nfor a given test instance.\n\n:Parameters:\n  `instance` : str\n      a string representation of the test instance. The format of this\n      string is the same as used by the TiMBL command-line\n      application.\n\n:return: (boolean signalling success or failure, the predicted class,\n          distance of the nearest neighbour)\n:rtype: (bool, str, float)");

PyDoc_STRVAR(INCREMENT_DOC, "self.increment(instance)\n\nAdd an instance to the instance base.\n\n:Parameters:\n  `instance` : str\n      a string representation of the instance to be added. The format\n      of this string is the same as used by the TiMBL command-line\n      application.\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(WRITEARRAYS_DOC, "self.writeArrays(file)\n\nStore the current probability arrays to a file.\n\n:Parameters:\n  `file` : str\n      the output file to write the arrays to\n\n:return: boolean signalling success or failure\n:rtype: bool");

PyDoc_STRVAR(SAVEWEIGHTS_DOC, "self.saveWeights(file)\n\nStore the current feature weight tables to a file.\n\n:Parameters:\n  `file` : str\n      the output file to write the tables to\n\n:return: boolean signalling success or failure\n:rtype: bool");

#endif
