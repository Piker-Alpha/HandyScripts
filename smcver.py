#!/usr/bin/env python
#
# Script (SMCver.py) to show the SMC version info (extracted from FirmwareUpdate.pkg).
#
# Version 1.3 - Copyright (c) 2017 by Dr. Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#		   - search scap files from 0xb0 onwards.
#		   - whitespace changes.
#		   - check for installSeed.py and download it when missing.
#		   - now highlights your board-id, model and smc-version.
#		   - license added.
#		   - shebang line changed.
#		   - match output style with that of EFIver.py
#		   - no longer using ServerInformation.framework
#		   - fix incompatible issues with older versions of macOS.
#		   - script will now stop/abort when Ctrl+C is pressed.
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
import signal

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


VERSION = 1.3
INSTALLSEED = "installSeed.py"
FIRMWARE_PATH = "/tmp/FirmwareUpdate"
JSONS_PATH = "Scripts/Tools/SMCJSONs/*.json"

boardIDModelIDs = [
 ["Mac-F22C8AC8", "MacBook6,1"],
 ["Mac-F22C89C8", "MacBook7,1"],
 ["Mac-BE0E8AC46FE800CC", "MacBook8,1"],
 ["Mac-9AE82516C7C6B903", "MacBook9,1"],
 ["Mac-EE2EBD4B90B839A8", "MacBook10,1"],
 ["Mac-F22589C8", "MacBookPro6,1"],
 ["Mac-F22586C8", "MacBookPro6,2"],
 ["Mac-F222BEC8", "MacBookPro7,1"],
 ["Mac-94245B3640C91C81", "MacBookPro8,1"],
 ["Mac-94245A3940C91C80", "MacBookPro8,2"],
 ["Mac-942459F5819B171B", "MacBookPro8,3"],
 ["Mac-4B7AC7E43945597E", "MacBookPro9,1"],
 ["Mac-6F01561E16C75D06", "MacBookPro9,2"],
 ["Mac-C3EC7CD22292981F", "MacBookPro10,1"],
 ["Mac-AFD8A9D944EA4843", "MacBookPro10,2"],
 ["Mac-189A3D4F975D5FFC", "MacBookPro11,1"],
 ["Mac-3CBD00234E554E41", "MacBookPro11,2"],
 ["Mac-2BD1B31983FE1663", "MacBookPro11,3"],
 ["Mac-06F11FD93F0323C5", "MacBookPro11,4"],
 ["Mac-06F11F11946D27C5", "MacBookPro11,5"],
 ["Mac-E43C1C25D4880AD6", "MacBookPro12,1"],
 ["Mac-473D31EABEB93F9B", "MacBookPro13,1"],
 ["Mac-66E35819EE2D0D05", "MacBookPro13,2"],
 ["Mac-A5C67F76ED83108C", "MacBookPro13,3"],
 ["Mac-B4831CEBD52A0C4C","MacBookPro14,1"],
 ["Mac-CAD6701F7CEA0921","MacBookPro14,2"],
 ["Mac-551B86E5744E2388","MacBookPro14,3"],
 ["Mac-942452F5819B1C1B", "MacBookAir3,1"],
 ["Mac-942C5DF58193131B", "MacBookAir3,2"],
 ["Mac-C08A6BB70A942AC2", "MacBookAir4,1"],
 ["Mac-742912EFDBEE19B3", "MacBookAir4,2"],
 ["Mac-66F35F19FE2A0D05", "MacBookAir5,1"],
 ["Mac-2E6FAB96566FE58C", "MacBookAir5,2"],
 ["Mac-35C1E88140C3E6CF", "MacBookAir6,1"],
 ["Mac-7DF21CB3ED6977E5", "MacBookAir6,2"],
 ["Mac-9F18E312C5C2BF0B", "MacBookAir7,1"],
 ["Mac-937CB26E2E02BB01", "MacBookAir7,2"],
 ["Mac-F2268CC8", "iMac10,1"],
 ["Mac-F2268DAE", "iMac11,1"],
 ["Mac-F2238AC8", "iMac11,2"],
 ["Mac-F2238BAE", "iMac11,3"],
 ["Mac-942B5BF58194151B", "iMac12,1"],
 ["Mac-942B59F58194171B", "iMac12,2"],
 ["Mac-00BE6ED71E35EB86", "iMac13,1"],
 ["Mac-FC02E91DDD3FA6A4", "iMac13,2"],
 ["Mac-7DF2A3B5E5D671ED", "iMac13,3"],
 ["Mac-031B6874CF7F642A", "iMac14,1"],
 ["Mac-27ADBB7B4CEE8E61", "iMac14,2"],
 ["Mac-77EB7D7DAF985301", "iMac14,3"],
 ["Mac-81E3E92DD6088272", "iMac14,4"],
 ["Mac-FA842E06C61E91C5", "iMac15,1"],
 ["Mac-42FD25EABCABB274", "iMac15,1"],
 ["Mac-A369DDC4E67F1C45", "iMac16,1"],
 ["Mac-FFE5EF870D7BA81A", "iMac16,2"],
 ["Mac-DB15BD556843C820", "iMac17,1"],
 ["Mac-65CE76090165799A", "iMac17,1"],
 ["Mac-B809C3757DA9BB8D", "iMac17,1"],
 ["Mac-4B682C642B45593E", "iMac18,1"],
 ["Mac-77F17D7DA9285301", "iMac18,2"],
 ["Mac-BE088AF8C5EB4FA2", "iMac18,3"],
 ["Mac-F2208EC8", "Macmini4,1"],
 ["Mac-8ED6AF5B48C039E1", "Macmini5,1"],
 ["Mac-4BC72D62AD45599E", "Macmini5,2"],
 ["Mac-7BA5B2794B2CDB12", "Macmini5,3"],
 ["Mac-031AEE4D24BFF0B1", "Macmini6,1"],
 ["Mac-F65AE981FFA204ED", "Macmini6,2"],
 ["Mac-35C5E08120C7EEAF", "Macmini7,1"],
 ["Mac-F221BEC8", "MacPro4,1"],
 ["Mac-F221DCC8", "MacPro5,1"],
 ["Mac-F60DEB81FF30ACF6", "MacPro6,1"]
]

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


def getModelByBoardID(boardID):
	for x in boardIDModelIDs:
		if boardID == x[0]:
			return x[1]

	return 'Unknown'


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
		modelID = getModelByBoardID(boardID)

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
	# Allows installSeed.py to exit quickly when pressing Ctrl+C.
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	main()
