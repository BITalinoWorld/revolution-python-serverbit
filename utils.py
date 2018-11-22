"""

* Copyright (c) PLUX S.A., All Rights Reserved.
* (www.plux.info)
*
* This software is the proprietary information of PLUX S.A.
* Use is subject to license terms.
*
*
---------------------------------------------------------
.. module:: utils
   :synopsis: General functions

.. moduleauthor:: pgoncalves <pgoncalves@plux.info>
"""
import json
import os
import numpy
import math
import platform
import time
import string
import threading
import datetime

bitalino = 'bitalino'
bitalino_rev = 'bitalino_rev'
bioplux = 'bioplux'
bioplux_exp = 'bioplux_exp'
riot = 'riot'
bitalino_riot = 'bitalino_riot'
biosignalsplux = 'biosignalsplux'
motionplux_physio = 'motionplux_physio'
motionplux_champ = 'motionplux_champ'
motionplux = 'motionplux'
senseaid = 'senseaid'
rachimeter = 'rachimeter'
channeller = 'channeller'
virtual_plux = 'virtual_plux'
gestureplux = 'gestureplux'
musclebanplux = 'musclebanplux'
swifter = 'swifter'
ddme_oximeter = 'ddme_oximeter'
ddme_openbanplux = 'ddme_openbanplux'

class ExceptionCode():
    UNDEFINED_DEVICE_TYPE = 'Undefined device type.'
    NO_PARAMETER = "Not parameter found." 

def getPluxAPI():
    try:
        import WIN64.plux  as plux
        os.environ['PATH'] += ';.\\code\\modules\\WIN64'
    except Exception, e:
        try:
            import WIN32.plux as plux
            os.environ['PATH'] += ';.\\code\\modules\\WIN32'
        except Exception, e:
            try:
                import OSX.plux as plux
                os.environ['PATH'] += ';.\\code\\modules\\OSX'
            except Exception, e:
                try:
                    import LINUX_AMD64.plux as plux
                    os.environ['PATH'] += ';.\\code\\modules\\LINUX_AMD64'
                except Exception, e:
                    print "Unable to import PLUX API"
                    import plux
    return plux

def isBitalino(device_type_str):
    """
    :param device_type_str: string to compare
    :type device_type_str: str
    :returns: True or False
    
    Compares `device_type_str` with the software's designation of Bitalino devices (``'bitalino'``).
    """
    return True if device_type_str == bitalino else False

def isBitalinoRev(device_type_str):
    return True if device_type_str == bitalino_rev else False

def isRiot(device_type_str):
    return True if device_type_str == riot else False

def isVirtualplux(device_type_str):
    return True if device_type_str == virtual_plux else False

def isBitalinoRiot(device_type_str):
    return True if device_type_str == bitalino_riot else False

def isBioplux(device_type_str):
    """
    :param device_type_str: string to compare
    :type device_type_str: str
    :returns: True or False
    
    Compares `device_type_str` with the software's designation of Bioplux devices (``'bioplux'``).
    """
    return True if device_type_str == bioplux else False

def isBiosignalsplux(device_type_str):
    return True if device_type_str == biosignalsplux else False

def isBioplux_exp(device_type_str):
    return True if device_type_str == bioplux_exp else False

def isMotionplux_physio(device_type_str):
    return True if device_type_str == motionplux_physio else False

def isMotionplux_champ(device_type_str):
    return True if device_type_str == motionplux_champ else False

def isMotionplux(device_type_str):
    return True if device_type_str == motionplux else False

def isSenseaid(device_type_str):
    return True if device_type_str == senseaid else False

def isRachimeter(device_type_str):
    return True if device_type_str == rachimeter else False

def isChanneller(device_type_str):
    return True if device_type_str == channeller else False

def isGestureplux(device_type_str):
    return True if device_type_str == gestureplux else False

def isMusclebanplux(device_type_str):
    return True if device_type_str == musclebanplux else False

def isSwifter(device_type_str):
    return True if device_type_str == swifter else False

def isDdmeOximeter(device_type_str):
    return True if device_type_str == ddme_oximeter else False

def isDdmeOpenbanplux(device_type_str):
    return True if device_type_str == ddme_openbanplux else False

def getParameter(dict, prop):
    if prop in dict:
        return dict[prop]
    else:
        raise Exception(ExceptionCode().NO_PARAMETER + " Required: " + prop)
    
def getExtension(path):
    return os.path.splitext(path)[1].upper()

def file_to_json(filename):
    """
    :param filename: path to json file
    :type filename: str
    
    Opens the specified file and returns de json data as a structured object. Uses :meth:`decode_json`
    """
    with open(filename, 'r+') as json_file:
        return json.load(json_file, encoding="latin-1")

def json_to_file(json_data, dest_filename):
	"""
	:param json_data: json object to save
	:type json_data: dict
	:param dest_filename: path to destination file
	:type dest_filename: str

	Saves the json object to the specified file. 

	.. note:: File is created if it doesn't exist.
	"""
	with open(dest_filename, 'w+') as outfile:
		json.dump(json_data, outfile, encoding="latin-1")

def seconds_to_date(seconds):
    """
    :param seconds: number of seconds
    :type seconds: int
    
    Converts a number of `seconds` into a string format (ex.: `2h23m21s`)  
    """
    hours = int(seconds / 3600)
    minutes = (seconds / 60) % 60
    seconds = (seconds % 60)
    
    if (hours != 0):
        return '%sh%sm%ss'%(hours,minutes,seconds)
    elif (minutes != 0):
        return '%sm%ss'%(minutes,seconds)
    else:
        return '%ss'%(seconds)

def path_from_root(relative_path = ""):
    """
    :param relative_path: path from root
    :type relative_path: str
    :returns: absolute path of root_directory + relative_path
    
    Returns the absolute path of a `relative_path` starting from OpenSignals root directory:
    ::
        >>> print utils.path_from_root("static//images")
        >>> print utils.path_from_root("/static/images")
        >>> print utils.path_from_root("//static\\images")
        >>> print utils.path_from_root("\static/images")
        
        >>> print utils.path_from_root()
        >>> print utils.path_from_root("")
        
        C:\plux.svn\code\OpenSignals_reStructured\static\images
        C:\plux.svn\code\OpenSignals_reStructured\static\images
        C:\plux.svn\code\OpenSignals_reStructured\static\images
        C:\plux.svn\code\OpenSignals_reStructured\static\images
        
        C:\plux.svn\code\OpenSignals_reStructured
        C:\plux.svn\code\OpenSignals_reStructured
    """
    this_path = os.path.realpath(__file__)
    walk_back = 3
    while walk_back > 0:
        this_path = os.path.split(this_path)[0]
        walk_back -= 1
    if len(relative_path) == 0:
        return this_path
    else:
        while relative_path[0] == '/' or relative_path[0] == '\\':
            relative_path = relative_path[1:]
        return os.path.join(this_path, fixPath(relative_path))

def path_from_config(relative_path = ""):
    if platform.system() == "Windows":
        import ctypes.wintypes
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 1, buf)
        user_doc = os.path.join(buf.value, "OpenSignals (r)evolution") 
    elif platform.system() == "Darwin":
        from Carbon import Folder, Folders 
        folderref = Folder.FSFindFolder(Folders.kUserDomain,
                                        Folders.kDocumentsFolderType,
                                        False)
        user_doc = os.path.join(folderref.as_pathname(), "OpenSignals (r)evolution")
    elif platform.system() == "Linux":
        user_doc = os.path.join(os.path.expanduser('~'), "Documents", "OpenSignals (r)evolution")
    else:
        raise Exception("Unsupported Operating System.")
    if len(relative_path) == 0:
        return user_doc
    else:
        while relative_path[0] == '/' or relative_path[0] == '\\':
            relative_path = relative_path[1:]
        return os.path.join(user_doc, fixPath(relative_path))

def fixPath(path):
    return os.path.normcase(os.path.normpath(path).replace("\\","/"))

def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    return filename

def rename_file(filepath, directory, filename, saveTimestamp):
    former_path, former_format = ".".join(filepath.split(".")[:-1]), filepath.split(".")[-1]
    former_timestamp = "_" + "_".join(former_path.split("_")[-2:]) if saveTimestamp else ""
    return os.path.join(directory, filename) + former_timestamp + "." + former_format

def remove_file(filename):
    os.remove(filename)
    
def subSample(currentData, final_nrSamples):
    """
    :param currenData: data to sub sample
    :type currentData: `numpy.ndarray`
    
    Reduces the number of samples in `currentData` to the ``visRate`` times ``timestep``. 
    """
    (currentSamples, finalSamples) = (currentData.shape[0], final_nrSamples)
    (currentPosition, finalPosition) = (0, 0)
    finalData = numpy.zeros((finalSamples, currentData.shape[1]))
    if finalSamples != 0:
        step = float(currentSamples)/finalSamples
        
        while currentPosition <= currentSamples - 1:
            finalData[finalPosition] = currentData[int(math.floor(currentPosition))]
            (currentPosition, finalPosition) = (currentPosition + step, finalPosition + 1)

    return finalData


def upSample(currentData, final_nrSamples):
    """
    :param currenData: data to sub sample
    :type currentData: `numpy.ndarray`

    Increases the number of samples in `currentData` to the ``visRate`` times ``timestep``.
    """
    (currentSamples, finalSamples) = (len(currentData), final_nrSamples)
    (currentPosition, finalPosition) = (0, 0)
    finalData = []
    if finalSamples != 0:
        step = float(finalSamples) / currentSamples
        while finalPosition <= finalSamples - 1:
            value = currentData[int(math.floor(currentPosition))]
            for i in numpy.arange(step):
                finalData.append(value)
            (currentPosition, finalPosition) = (currentPosition + 1, finalPosition + step)

    return finalData

class Timer():
    def __init__(self):
        self.initialTime = None
        self.analysis = {}
        self.analysis['labels'] = []
        self.analysis['times'] = []
        
    def start(self):
        self.__init__()
        self.initialTime = time.time()
        
    def markTime(self, label = ["undefined"]):
        if self.initialTime is not None:
            self.analysis['times'].append(time.time() - self.initialTime)
            self.analysis['labels'].append(label)
        else:
            raise Exception("Please use .start() to set the initial time.")
        
    def addProp(self, name, value):
        self.analysis[name] = value
        
    def getProp(self, name):
        if name in self.analysis:
            return self.analysis[name]
        else:
            raise Exception("Please use .stop() to compute analysis.")
    
    def stop(self):
        self.analysis['totalTime'] = self.analysis['times'][-1]
        self.analysis['relTimes'] = [self.analysis['times'][0]]
        self.analysis['relTimes'].extend([self.analysis['times'][i] - self.analysis['times'][i-1] for i in range(1,len(self.analysis['times']))])
        if self.analysis['totalTime'] > 0:
            self.analysis['percTimes'] = [int((i/self.analysis['totalTime'])*100.0) for i in self.analysis['relTimes']]
        else:
            self.analysis['percTimes'] = [0 for i in self.analysis['relTimes']]
        
    def getLabels(self):
        return self.getProp('labels')
    
    def getTimes(self):
        return self.getProp('times')
    
    def getTotalTime(self):
        return self.getProp('totalTime')
    
    def getRelTimes(self):
        return self.getProp('relTimes')
    
    def getPercTimes(self):
        return self.getProp('percTimes')
    
    def getAnalysis(self):
        return self.analysis
