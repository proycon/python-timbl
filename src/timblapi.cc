/*
 * Copyright (C) 2006-2015 Sander Canisius, Maarten van Gompel
 *
 * This file is part of python-timbl.
 *
 * python-timbl is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * python-timbl is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with python-timbl; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA
 * 02110-1301 USA
 *
 * Linking python-timbl statically or dynamically with other modules
 * is making a combined work based on python-timbl. Thus, the terms
 * and conditions of the GNU General Public License cover the whole
 * combination.
 *
 * In addition, as a special exception, the copyright holder of
 * python-timbl gives you permission to combine python-timbl with free
 * software programs or libraries that are released under the GNU LGPL
 * and with code included in the standard release of TiMBL under the
 * TiMBL license (or modified versions of such code, with unchanged
 * license). You may copy and distribute such a system following the
 * terms of the GNU GPL for python-timbl and the licenses of the other
 * code concerned, provided that you include the source code of that
 * other code when and as the GNU GPL requires distribution of source
 * code.
 *
 * Note that people who make modified versions of python-timbl are not
 * obligated to grant this special exception for their modified
 * versions; it is their choice whether to do so. The GNU General
 * Public License gives permission to release a modified version
 * without this exception; this exception also makes it possible to
 * release a modified version which carries forward this exception.
 *
#*/


#include "timblapi.h"
#include "timbl/GetOptClass.h"
#include "timbl/Instance.h"
#include "docstrings.h"

#include <unistd.h>

#include <iostream>
#include <sstream>
#include <string>
#include <unordered_map>

#ifndef __clang__
#include <ext/stdio_filebuf.h>
#endif

#include <boost/utility.hpp>
#include <boost/python.hpp>

using namespace boost::python;


tuple TimblApiWrapper::classify(const std::string& line)
{
	std::string cls;
	bool result = Classify(line, cls);
	return boost::python::make_tuple(result, cls);
}


tuple TimblApiWrapper::classify2(const std::string& line)
{
	std::string cls;
	double distance;
	bool result = Classify(line, cls, distance);
	return boost::python::make_tuple(result, cls, distance);
}


tuple TimblApiWrapper::classify3(const std::string& line, bool normalize, const unsigned char requireddepth)
{
	std::string cls;
	double distance;
    const Timbl::ValueDistribution * distrib;
    const Timbl::TargetValue * result  = Classify(line, distrib , distance);
    if (result != NULL) {
        if ((requireddepth > 0) && (matchDepth() < requireddepth)) {
            return boost::python::make_tuple(true, "", python::dict(), 999999);
        } else {
            const std::string cls = result->Name();
            return boost::python::make_tuple(true, cls, dist2dict(distrib, normalize), distance);
        }
    } else {
        return boost::python::make_tuple(false,"",python::dict(),999999);
    }
}


Timbl::TimblExperiment * TimblApiWrapper::getexperimentforthread() {
    pthread_t thisthread = pthread_self();
    Timbl::TimblExperiment * clonedexp = NULL;
    pthread_mutex_lock(&lock);
    for (std::vector<std::pair<pthread_t,Timbl::TimblExperiment *> >::const_iterator iter = experimentpool.begin(); iter != experimentpool.end(); iter++) {
        if (iter->first == thisthread) {
            if (debug) std::cerr << "(Experiment in pool for thread " << (size_t) thisthread << ", runningthreads=" << runningthreads << ")" << std::endl;
            clonedexp = iter->second;
            break;
        }
    }
    pthread_mutex_unlock(&lock);

    if (clonedexp == NULL) {
        clonedexp = detachedexp->clone();
        if (debug) std::cerr << "(Creating new experiment in pool for thread " << (size_t) thisthread << ", clonedexp=" << (size_t) clonedexp << ", experimentpool=" << (size_t) &experimentpool << ", runningthreads=" << runningthreads << ")" << std::endl;
        *clonedexp = *detachedexp; //ugly but needed
        if ( detachedexp->getOptParams() ){
            clonedexp->setOptParams( detachedexp->getOptParams()->Clone(0) );
        }
        if (clonedexp == NULL) {
            std::cerr << "(FATAL ERROR clonedexp=NULL)" << std::endl;
        } else {
            pthread_mutex_lock(&lock);
            experimentpool.push_back(std::pair<pthread_t,Timbl::TimblExperiment*>(thisthread,clonedexp));
            pthread_mutex_unlock(&lock);
        }
        if (debug) std::cerr << "(Experimentpool size = " << experimentpool.size() << ")" << std::endl;
    }
    return clonedexp;
}

tuple TimblApiWrapper::classify3safe(const std::string& line, bool normalize,const unsigned char requireddepth)
{
    runningthreads++;
    PyThreadState * m_thread_state = PyEval_SaveThread(); //release GIL

    Timbl::TimblExperiment * clonedexp = getexperimentforthread();

    const Timbl::ValueDistribution * distrib;
    double distance;
    const Timbl::TargetValue * result = clonedexp->Classify(line, distrib,distance);
    if (result != NULL) {
        if ((requireddepth > 0) && (clonedexp->matchDepth() < requireddepth)) {
            PyEval_RestoreThread(m_thread_state);
            m_thread_state = NULL;
            runningthreads--;
            return boost::python::make_tuple(true, "", python::dict(), 999999);
        } else {
            const std::string cls = result->Name();
            //const std::string diststring = distrib->DistToString();
            PyEval_RestoreThread(m_thread_state);
            m_thread_state = NULL;
            runningthreads--;
            return boost::python::make_tuple(true, cls, dist2dict(distrib, normalize), distance);
        }
    } else {
        PyEval_RestoreThread(m_thread_state);
        m_thread_state = NULL;
        runningthreads--;
        return boost::python::make_tuple(false,"",python::dict(),999999);
    }
}

std::string TimblApiWrapper::bestNeighbours()
{
	std::ostringstream buf;
	ShowBestNeighbors(buf);
	return buf.str();
}


bool TimblApiWrapper::showBestNeighbours(object& stream)
{
    #ifdef __clang__
    std::cerr << "showBestNeighbours is not implemented for clang" << std::endl;
    return false;
	#else
	int fd = extract<int>(stream.attr("fileno")());
	__gnu_cxx::stdio_filebuf<char> fdbuf(dup(fd), std::ios::out);
	std::ostream out(&fdbuf);
	return ShowBestNeighbors(out);
	#endif
}


std::string TimblApiWrapper::options()
{
	std::ostringstream buf;
	ShowOptions(buf);
	return buf.str();
}


bool TimblApiWrapper::showOptions(object& stream)
{
    #ifdef __clang__
    std::cerr << "showOptions is not implemented for clang" << std::endl;
    return false;
	#else
	int fd = extract<int>(stream.attr("fileno")());
	__gnu_cxx::stdio_filebuf<char> fdbuf(dup(fd), std::ios::out);
	std::ostream out(&fdbuf);
	return ShowOptions(out);
	#endif
}


std::string TimblApiWrapper::settings()
{
	std::ostringstream buf;
	ShowSettings(buf);
	return buf.str();
}


void TimblApiWrapper::initthreading() {
    initExperiment();
    detachedexp = grabAndDisconnectExp();
}


bool TimblApiWrapper::showSettings(object& stream)
{
    #ifdef __clang__
    std::cerr << "showSettings is not implemented for clang" << std::endl;
    return false;
	#else
	int fd = extract<int>(stream.attr("fileno")());
	__gnu_cxx::stdio_filebuf<char> fdbuf(dup(fd), std::ios::out);
	std::ostream out(&fdbuf);
	return ShowSettings(out);
	#endif
}


python::dict TimblApiWrapper::dist2dict(const Timbl::ValueDistribution * distribution, bool normalize, double minf) const {
    python::dict result;

    size_t freq;

    double maxfreq = 0;

    if (normalize) {
        Timbl::ValueDistribution::VDlist::const_iterator it = distribution->begin();
        while ( it != distribution->end() ){
            Timbl::Vfield *f = it->second;
            if (f->Freq() > maxfreq) maxfreq = f->Freq();
            ++it;
        }
    }

    Timbl::ValueDistribution::VDlist::const_iterator it = distribution->begin();
    while ( it != distribution->end() ){
        Timbl::Vfield *f = it->second;
        if (normalize) {
            freq = f->Freq() / maxfreq;
        } else {
            freq = f->Freq();
        }
        if ( freq >= minf ){
            result[f->Value()->Name()] = freq;
        }
        ++it;
    }

    return result;
}

/*std::string TimblApiWrapper::weights()
{
	std::ostringstream buf;
	ShowWeights(buf);
	return buf.str();
}


bool TimblApiWrapper::showWeights(object& stream)
{
	int fd = extract<int>(stream.attr("fileno")());
	#if __GLIBCXX__ < 20040419
	__gnu_cxx::stdio_filebuf<char> fdbuf(fd, std::ios::out, false,
																			 static_cast< size_t >(BUFSIZ));
	#else
	__gnu_cxx::stdio_filebuf<char> fdbuf(dup(fd), std::ios::out);
	#endif
	std::ostream out(&fdbuf);
	return ShowWeights(out);
}*/


BOOST_PYTHON_MODULE(timblapi)
{
	scope().attr("__doc__") = MODULE_DOC;

	class_<TimblApiWrapper, boost::noncopyable>("TimblAPI",
																							TIMBLAPI_DOC,
																							init<const std::string&,
																							const std::string&>(INIT_DOC))
		.def("learn", &TimblApiWrapper::Learn, LEARN_DOC)
		.def("test", &TimblApiWrapper::Test, TEST_DOC)

		.def("setOptions", &TimblApiWrapper::SetOptions, SETOPTIONS_DOC)
		.def("showOptions", &TimblApiWrapper::showOptions, SHOWOPTIONS_DOC)
		.def("showSettings", &TimblApiWrapper::showSettings, SHOWSETTINGS_DOC)
		.def("showStatistics", &TimblApiWrapper::ShowStatistics, SHOWSTATISTICS_DOC)

		.def("writeInstanceBase", &TimblApiWrapper::WriteInstanceBase,
				 WRITEINSTANCEBASE_DOC)
		.def("getInstanceBase", &TimblApiWrapper::GetInstanceBase,
				 GETINSTANCEBASE_DOC)

		.def("saveWeights", &TimblApiWrapper::SaveWeights, SAVEWEIGHTS_DOC)
		.def("getWeights", &TimblApiWrapper::GetWeights, GETWEIGHTS_DOC)

		.def("getAccuracy", &TimblApiWrapper::GetAccuracy, GETACCURACY_DOC)

		.def("writeArrays", &TimblApiWrapper::WriteArrays, WRITEARRAYS_DOC)
		.def("getArrays", &TimblApiWrapper::GetArrays, GETARRAYS_DOC)

		.def("classify", &TimblApiWrapper::classify, CLASSIFY_DOC)
		.def("classify2", &TimblApiWrapper::classify2, CLASSIFY2_DOC)
		.def("classify3", &TimblApiWrapper::classify3, CLASSIFY3_DOC)
		.def("classify3safe", &TimblApiWrapper::classify3safe, CLASSIFY3SAFE_DOC)

		.def("initthreading", &TimblApiWrapper::initthreading, INITTHREADING_DOC)
		.def("enableDebug", &TimblApiWrapper::enableDebug, ENABLEDEBUG_DOC)

		.def("showBestNeighbours", &TimblApiWrapper::showBestNeighbours,
				 SHOWBESTNEIGHBOURS_DOC)
		.def("showBestNeighbors", &TimblApiWrapper::showBestNeighbours,
				 SHOWBESTNEIGHBORS_DOC)


		.def("increment", &TimblApiWrapper::Increment, INCREMENT_DOC)
		.def("decrement", &TimblApiWrapper::Decrement, DECREMENT_DOC)
		.def("expand", &TimblApiWrapper::Expand, EXPAND_DOC)
		.def("remove", &TimblApiWrapper::Remove, REMOVE_DOC)

		.def("writeNamesFile", &TimblApiWrapper::WriteNamesFile,
				 WRITENAMESFILE_DOC)
		.def("algo", &TimblApiWrapper::Algo, ALGO_DOC)
		.def("expName", &TimblApiWrapper::ExpName, EXPNAME_DOC)
		.def("versionInfo", &TimblApiWrapper::VersionInfo, VERSIONINFO_DOC)
		.staticmethod("versionInfo")
		.def("currentWeighting", &TimblApiWrapper::CurrentWeighting,
				 CURRENTWEIGHTING_DOC)
		.def("valid", &TimblApiWrapper::Valid)
		//.def("showWeights", &TimblApiWrapper::showWeights)

		// EXTRA METHODS
		.def("bestNeighbours", &TimblApiWrapper::bestNeighbours,
				 BESTNEIGHBOURS_DOC)
		.def("bestNeighbors", &TimblApiWrapper::bestNeighbours,
				 BESTNEIGHBORS_DOC)
		.def("options", &TimblApiWrapper::options, OPTIONS_DOC)
		.def("settings", &TimblApiWrapper::settings, SETTINGS_DOC)
		//.def("weights", &TimblApiWrapper::weights)
	;

	enum_<Timbl::Algorithm>("Algorithm")
		.value("UNKNOWN_ALG", Timbl::UNKNOWN_ALG)
		.value("IB1", Timbl::IB1)
		.value("IB2", Timbl::IB2)
		.value("IGTREE", Timbl::IGTREE)
		.value("TRIBL", Timbl::TRIBL)
		.value("TRIBL2", Timbl::TRIBL2)
		.value("LOO", Timbl::LOO)
		.value("CV", Timbl::CV)
	;

	enum_<Timbl::Weighting>("Weighting")
		.value("UNKNOWN_W", Timbl::UNKNOWN_W)
		.value("UD", Timbl::UD)
		.value("NW", Timbl::NW)
		.value("GR", Timbl::GR)
		.value("IG", Timbl::IG)
		.value("X2", Timbl::X2)
		.value("SV", Timbl::SV)
	;

	//def("to_string", to_string);
}



