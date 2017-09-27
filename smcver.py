#!/usr/bin/python

import os
import glob
import objc
import json
import sys
import subprocess

from os.path import basename
from os.path import splitext

VERSION = 1.0
INSTALLSEED = "installSeed.py"
FIRMWARE_PATH = "/tmp/FirmwareUpdate"
JSONS_PATH = "Scripts/Tools/SMCJSONs/*.json"

class attrdict(dict):
	__getattr__ = dict.__getitem__
	__setattr__ = dict.__setitem__

def launchInstallSeed(unpackPath):
	scriptDirectory = os.path.dirname(os.path.abspath(__file__))
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

def main():
	sys.stdout.write("\x1b[2J\x1b[H")

	if not os.path.exists(FIRMWARE_PATH):
		launchInstallSeed(FIRMWARE_PATH)

	print '--------------------------------------------------'
	print 'SMCver.py v%s Copyright (c) 2017 by Pike R. Alpha' % VERSION
	print '--------------------------------------------------'

	jsonsPath = os.path.join(FIRMWARE_PATH, JSONS_PATH)
	jsonFiles = getJSONFiles(jsonsPath)

	for jsonFile in jsonFiles:
		boardID = splitext(basename(jsonFile))[0]
		modelID = getModelIDFrom(boardID)

		with open(jsonFile, 'r') as jsonFile:
			jsonData = json.load(jsonFile)
			smcData = jsonData[boardID]
			print '%s | %14s | v%s' % (boardID, modelID, smcData['smc-version'])

	print '--------------------------------------------------'

if __name__ == "__main__":
	main()
