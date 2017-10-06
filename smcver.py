#!/usr/bin/env python
#
# Script (SMCver.py) to show the SMC version info (extracted from FirmwareUpdate.pkg).
#
# Version 1.1 - Copyright (c) 2017 by Dr. Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#		   - search scap files from 0xb0 onwards.
#		   - whitespace changes.
#		   - check for installSeed.py and download it when missing.
#		   - now highlights your board-id, model and smc-version.
#		   - license added.
#		   - shebang line changed.
#		   - match output style with that of EFIver.py
#
# License:
#		   -  BSD 3-Clause License
#
# Copyright (c) 2017 by Dr. Pike R. Alpha, All Rights Reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the name(s) of its
#   contributor(s) may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

import os
import glob
import objc
import json
import sys
import subprocess

from os.path import basename
from Foundation import NSBundle
from os.path import splitext

IOKitBundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [
			 ("IOServiceGetMatchingService", b"II@"),
			 ("IOServiceMatching", b"@*"),
			 ("IORegistryEntryCreateCFProperty", b"@I@@I")
			 ]

objc.loadBundleFunctions(IOKitBundle, globals(), functions)


VERSION = 1.1
INSTALLSEED = "installSeed.py"
FIRMWARE_PATH = "/tmp/FirmwareUpdate"
JSONS_PATH = "Scripts/Tools/SMCJSONs/*.json"

class attrdict(dict):
	__getattr__ = dict.__getitem__
	__setattr__ = dict.__setitem__


def getInstallSeed(scriptDirectory):
	URL = "https://raw.githubusercontent.com/Piker-Alpha/HandyScripts/master/installSeed.py"
	try:
		req = urllib2.urlopen(URL)
	except urllib2.URLError:
		print >> sys.stderr("\nERROR: opening of (%s) failed. Aborting ...\n" % URL)
	
	filename = basename(URL)
	filesize = req.info().getheader('Content-Length')
	targetFile = os.path.join(scriptDirectory, filename)

	if os.path.exists(targetFile):
		os.remove(targetFile)
	
	with open(targetFile, 'w') as f:
		print '\nDownloading: %s [%s bytes] ...' % (filename, filesize)
		while True:
			chunk = req.read(1024)
			if not chunk:
				break
			f.write(chunk)
		# get/set file mode (think chmod +x <filename>)
		mode = os.fstat(f.fileno()).st_mode
		mode |= stat.S_IXUSR
		os.fchmod(f.fileno(), stat.S_IMODE(mode))


def launchInstallSeed(unpackPath):
	scriptDirectory = os.path.dirname(os.path.abspath(__file__))
	helperScript = os.path.join(scriptDirectory, INSTALLSEED)
	# download installSeed if it isn't there
	if not os.path.exists(helperScript):
		getInstallSeed(scriptDirectory)
	#
	# installSeed -a update -f FirmwareUpdate.pkg -t / -c 0 -u /tmp/FirmwareUpdate
	#
	cmd = [os.path.join(scriptDirectory, INSTALLSEED)]
	cmd.extend(['-a', 'update'])
	cmd.extend(['-f', 'FirmwareUpdate.pkg'])
	cmd.extend(['-t', '/'])
	cmd.extend(['-c', '0'])
	cmd.extend(['-u', unpackPath])

	try:
		retcode = subprocess.call(cmd)
	except OSError, error:
		print >> sys.stderr, ("ERROR: launch of installSeed.py failed with %s." % error)


def getJSONFiles(path):
	return glob.glob(path)


def getModelIDFrom(boardID):
	ServerInformation = attrdict()
	ServerInformation_bundle = objc.loadBundle('ServerInformation', ServerInformation, bundle_path='/System/Library/PrivateFrameworks/ServerInformation.framework')
	return ServerInformation.ServerInformationComputerModelInfo.modelPropertiesForBoardIDs_([boardID])[0]


def getMyBoardID():
	return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("IOPlatformExpertDevice")), "board-id", None, 0)


def getMySMCVersion():
	return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("AppleSMC")), "smc-version", None, 0)


def showSystemData(linePrinted, boardID, modelID, smcVersion):
	if linePrinted == False:
		print '-----------------------------------------------------------'
	print '> %20s | %16s |  v%-11s <' % (boardID, modelID, smcVersion)
	print '-----------------------------------------------------------'
	return True


def shouldWarnAboutUpdate(mySMCVersion, smcVersion):
	if mySMCVersion < smcVersion:
		return True
	
	return False


def main():
	sys.stdout.write("\x1b[2J\x1b[H")

	if not os.path.exists(FIRMWARE_PATH):
		launchInstallSeed(FIRMWARE_PATH)

	print '-----------------------------------------------------------'
	print '  SMCver.py v%s Copyright (c) 2017 by Dr. Pike R. Alpha' % VERSION
	print '-----------------------------------------------------------'

	linePrinted = True
	warnAboutSMCVersion = False
	myBoardID = getMyBoardID()
	mySMCVersion = getMySMCVersion()
	jsonsPath = os.path.join(FIRMWARE_PATH, JSONS_PATH)
	jsonFiles = getJSONFiles(jsonsPath)

	for jsonFile in jsonFiles:
		boardID = splitext(basename(jsonFile))[0]
		modelID = getModelIDFrom(boardID)

		if boardID == modelID:
			modelID = "Unknown"

		with open(jsonFile, 'r') as jsonFile:
			jsonData = json.load(jsonFile)
			smcData = jsonData[boardID]
			if boardID == myBoardID:
				linePrinted = showSystemData(linePrinted, boardID, modelID, smcData['smc-version'])
				if shouldWarnAboutUpdate(mySMCVersion, smcData['smc-version']):
					warnAboutSMCVersion = True
			else:
				print '  %20s | %16s |  v%-11s' % (boardID, modelID, smcData['smc-version'])
				linePrinted = False

	if linePrinted == False:
		print '-----------------------------------------------------------'
	if warnAboutSMCVersion:
		print '> WARNING: Your SMC version (%8s) is not up-to-date! <' % mySMCVersion
		print '-----------------------------------------------------------'


if __name__ == "__main__":
	main()
