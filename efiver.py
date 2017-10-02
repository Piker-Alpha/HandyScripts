#!/usr/bin/python

#
# Script (efiver.py) to show the EFI ROM version (extracted from FirmwareUpdate.pkg).
#
# Version 1.7 - Copyright (c) 2017 by Dr. Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#		   - search scap files from 0xb0 onwards.
#		   - EFI ROM version check added.
#		   - now highlights your board-id, model and EFI ROM version.
#		   - now using a more reliable EFI ROM version check.
#		   - check for installSeed.py and download it when missing.
#		   - code refactored (no more code duplication).
#		   - the output of the scrit is now a lot quicker.
#		   - now reads the supported board-id's from the firmware payload files.
#		   - changed version number to v1.5
#		   - support for older version of efiupdater added.
#		   - now using the right patch for support of older versions of efiupdater.
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
import sys
import subprocess
import binascii
import objc
import stat
import urllib2
#import uuid

from os.path import basename
from Foundation import NSBundle
from subprocess import Popen, PIPE

IOKitBundle = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')

functions = [
 ("IOServiceGetMatchingService", b"II@"),
 ("IOServiceMatching", b"@*"),
 ("IORegistryEntryCreateCFProperty", b"@I@@I")
]

objc.loadBundleFunctions(IOKitBundle, globals(), functions)

VERSION = 1.7
IOREG = "/usr/sbin/ioreg"
EFIUPDATER = "/usr/libexec/efiupdater"
INSTALLSEED = "installSeed.py"
FIRMWARE_PATH = "/tmp/FirmwareUpdate"
PAYLOAD_PATH = "Scripts/Tools/EFIPayloads"

GLOB_SCAP_EXTENSION = "*.scap"
GLOB_FD_EXTENSION = "*.fd"

MATCHING_BOARD_IDS_GUID = "4a251f7857c4135d92751bf5d56e0724"

oldTypeFWModels = [
 "MB51","MB52","MB61","MB71","MBP41","MBP51","MBP52","MBP53",
 "MBP55","MBP61","MBP71","MBP81","MBP91","MBP101","MBP102",
 "MBA21","MBA31","MBA41","MBA51","IM81","IM91","IM101","IM111",
 "IM112","IM121","IM131","MM32","MM41","MM51","MM61","MP61"
]

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

#x = uuid.UUID(bytes_le='\x4A\x25\x1F\x78\x57\xC4\x13\x5D\x92\x75\x1B\xF5\xD5\x6E\x07\x24')
#print uuid.UUID(x.hex)

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
	cmd = [helperScript]
	cmd.extend(['-a', 'update'])
	cmd.extend(['-f', 'FirmwareUpdate.pkg'])
	cmd.extend(['-t', '/'])
	cmd.extend(['-c', '0'])
	cmd.extend(['-u', unpackPath])
	
	try:
		retcode = subprocess.call(cmd)
	except OSError, error:
		print >> sys.stderr, ("ERROR: launch of installSeed.py failed with %s." % error)

def getFirmwareFiles(path):
	return glob.glob(path)

def shouldPerformGUIDCheck(filename):
	for id in oldTypeFWModels:
		if filename.startswith(id):
			return False
	return True

def getBoardIDs(f, position):
	boardIDs = []
	count = 15
	# skip GUID + the the first four bytes of the structure.
	position+=20
	f.seek(position, 0)
	while count > 1:
		count-=1
		# skip eight bytes (the first time this is the structure, and after that a board-id).
		position+=8
		f.seek(position, 0)
		boardID = binascii.hexlify(f.read(8)).upper()
		if boardID == "FFFFFFFFFFFFFFFF":
			break;
		else:
			boardIDs.append("Mac-%s" % boardID)

	return boardIDs

def getEFIVersion(f, position):
	f.seek(position, 0)

	if position > 4096:
		while not f.read(8) == "$IBIOSI$":
			position-=4
			f.seek(position)
	else:
		while not f.read(8) == "$IBIOSI$":
			position+=4
			f.seek(position)

	return f.read(0x41)

def getEFIData(f, position):
	biosID = getEFIVersion(f, position)
	model = biosID.split('.')[0]
	modelID = getModelID(model)
	boardID = getBoardIDByModel(modelID)
	return (boardID, modelID, biosID)

def getModelNumberString(decimals):
	length = len(decimals)

	if length == 2:
		strData = decimals[0] + ',' + decimals[1]
	elif length == 3:
		strData = decimals[0] + decimals[1] + ',' + decimals[2]
	return strData

def getModelID(id):
	did = id.decode('utf-16')
	lid = did.lstrip()
	length = (len(lid) - 1)

	if lid.startswith('IM'):
		number = lid.strip('IM')
		return 'iMac%s' % getModelNumberString(number)
	elif lid.startswith('MBP'):
		number = lid.strip('MBP')
		return 'MacBookPro%s' % getModelNumberString(number)
	elif lid.startswith('MBA'):
		number = lid.strip('MBA')
		return 'MacBookAir%s' % getModelNumberString(number)
	elif lid.startswith('MB'):
		number = lid.strip('MB')
		return 'MacBook%s' % getModelNumberString(number)
	elif lid.startswith('MM'):
		number = lid.strip('MP')
		return 'Macmini%s' % getModelNumberString(number)
	elif lid.startswith('MP'):
		number = lid.strip('MP')
		return 'MacPro%s' % getModelNumberString(number)
	
	return 'Unknown'

def getBoardIDByModel(modelID):
	for x in boardIDModelIDs:
		if modelID == x[1]:
			return x[0]

	return 'Unknown'

def getModelByBoardID(boardID):
	for x in boardIDModelIDs:
		if boardID == x[0]:
			return x[1]

	return 'Unknown'

def getMyBoardID():
	return IORegistryEntryCreateCFProperty(IOServiceGetMatchingService(0, IOServiceMatching("IOPlatformExpertDevice")), "board-id", None, 0)

def getRawEFIVersion():
	cmd = [IOREG]
	cmd.extend(['-rw', '0'])
	cmd.extend(['-p' 'IODeviceTree'])
	cmd.extend(['-n' 'rom'])
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, err = proc.communicate()
	
	if proc.returncode:
		print "ERROR: ioreg -rw 0 -p IODeviceTree -n rom failed."
	else:
		lines = output.splitlines()
		for line in lines:
			# skip empty lines.
			if line.rstrip():
				# strip leading whitespace.
				strippedLine = line.lstrip()
				if strippedLine.startswith("\"version"):
					# spit line into two parts.
					data = strippedLine.split(' = ')
					return data[1].lstrip('<"').rstrip('">')

	return 'Unknown'

def getEFIVersionsFromEFIUpdater():
	cmd = [EFIUPDATER]
	proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, err = proc.communicate()
	lines = output.splitlines()

	if len(lines) == 2:
		rawString = "Raw EFI Version string: %s" % getRawEFIVersion()
		lines.insert(0, rawString)

	rawVersion = lines[0].split(': ')[1].strip(' ')
	currentVersion = lines[1].split(': ')[1].strip('[ ]')
	updateVersion = lines[2].split(': ')[1].strip('[ ]')

	return (rawVersion, currentVersion, updateVersion)

def getEFIDate(efiDate):
	return efiDate.strip('\x00')

def searchForGUID(f, filesize):
	position = 0x98
	f.seek(position, 0)
	if not binascii.hexlify(f.read(16)) == MATCHING_BOARD_IDS_GUID:
		position = 0x1048
		f.seek(position, 0)
		if not binascii.hexlify(f.read(16)) == MATCHING_BOARD_IDS_GUID:
			position = 0
			f.seek(position, 0)
		else:
			position = 0
			f.seek(position, 0)
			while not binascii.hexlify(f.read(16)) == MATCHING_BOARD_IDS_GUID:
				if position < (filesize-8):
					position+=4
					f.seek(position, 0)

	#print 'GUID found @ byte 0x%x' % position
	return position

def showSystemData(linePrinted, boardID, modelID, biosID):
	if linePrinted == False:
		print '---------------------------------------------------------------------------'
	print '> %20s | %14s |%s <' % (boardID, modelID, biosID)
	print '---------------------------------------------------------------------------'
	return True

def shouldWarnAboutUpdate(rawVersion, biosID):
	myBiosDate = rawVersion.split('.')[4]
	biosDate = biosID.split('.')[4].replace('\x00', '')
	if myBiosDate < biosDate:
		return True

	return False

def main():
	sys.stdout.write("\x1b[2J\x1b[H")

	if not os.path.exists(FIRMWARE_PATH):
		launchInstallSeed(FIRMWARE_PATH)

	print '---------------------------------------------------------------------------'
	print '         EFIver.py v%s Copyright (c) 2017 by Dr. Pike R. Alpha' % VERSION
	print '---------------------------------------------------------------------------'

	linePrinted = True
	warnAboutEFIVersion = False
	myBoardID = getMyBoardID()
	rawVersion, currentVersion, updateVersion = getEFIVersionsFromEFIUpdater()
	targetFileTypes = [GLOB_SCAP_EXTENSION, GLOB_FD_EXTENSION]

	for fileType in targetFileTypes:
		targetFiles = os.path.join(FIRMWARE_PATH, PAYLOAD_PATH, fileType)
		firmwareFiles = getFirmwareFiles(targetFiles)
		for firmwareFile in firmwareFiles:
			with open(firmwareFile, 'rb') as f:
				position = 0xb0
				if shouldPerformGUIDCheck(basename(firmwareFile)):
					filesize = os.stat(firmwareFile).st_size
					if fileType == GLOB_SCAP_EXTENSION:
						position = 0xb0
					else:
						position = filesize-44
					biosID = getEFIVersion(f, position)
					position = searchForGUID(f, position)
					boardIDs = getBoardIDs(f, position)
					for boardID in boardIDs:
						modelID = getModelByBoardID(boardID)
						if boardID == myBoardID:
							linePrinted = showSystemData(linePrinted, boardID, modelID, biosID)
							if shouldWarnAboutUpdate(rawVersion, biosID):
								warnAboutEFIVersion = True
						else:
							print '  %20s | %14s |%s' % (boardID, modelID, biosID)
							linePrinted = False
				else:
					boardID, modelID, biosID = getEFIData(f, 0xb0)
					if boardID == myBoardID:
						linePrinted = showSystemData(linePrinted, boardID, modelID, biosID)
						if shouldWarnAboutUpdate(rawVersion, biosID):
							warnAboutEFIVersion = True
					else:
						print '  %20s | %14s |%s' % (boardID, modelID, biosID)
						linePrinted = False

	if linePrinted == False:
		print '---------------------------------------------------------------------------'
	if warnAboutEFIVersion:
		print '> WARNING: Your EFI ROM %21s is not up-to-date!! <' % rawVersion
		print '---------------------------------------------------------------------------'

if __name__ == "__main__":
	main()
