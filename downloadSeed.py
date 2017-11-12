#!/usr/bin/env python

#
# Script (installSeed.py) to get the latest seed package.
#
# Version 1.0 - Copyright (c) 2017 by Dr. Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#		   -
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
import sys
import glob
import plistlib
import platform
import subprocess
import signal
import argparse

if sys.version_info[0] == 2:
	from urllib2 import urlopen, URLError
else:
	from urllib import urlopen, URLError

from os.path import basename
from multiprocessing import Pool
from xml.etree import ElementTree
from numbers import Number
from subprocess import Popen, PIPE

VERSION = "1.0"
IATOOL = "Contents/MacOS/InstallAssistant"

#
# Setup seed program data.
#
seedProgramData = {
 "DeveloperSeed":"index-10.13seed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "PublicSeed":"index-10.13beta-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "CustomerSeed":"index-10.13customerseed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "Regular":"index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
}

#
# The target directory.
#
tmpDirectory="/tmp"

def downloadDistributionFile(url, targetPath):
	try:
		req = urlopen(url)
	except URLError:
		print >> sys.stderr("\nERROR: opening of (%s) failed. Aborting ...\n" % url)

	filename = basename(url)
	filesize = req.info().getheader('Content-Length')
	distributionFile = os.path.join(targetPath, filename)

	if os.path.exists(distributionFile):
		os.remove(distributionFile)

	with open(distributionFile, 'w') as file:
		while True:
			chunk = req.read(1024)
			if not chunk:
				break
			file.write(chunk)

	return distributionFile


def getCatalogData(targetVolume, seedProgram):
	catalog = seedProgramData.get(seedProgram, seedProgramData['Regular'])
	catalogURL = "https://swscan.apple.com/content/catalogs/others/" + catalog
	try:
		catalogReq = urlopen(catalogURL)
	except URLError:
		print >> sys.stderr, ("\nERROR: opening of (%s) failed. Aborting ...\n" % url)
		sys.exit(-1)

	return catalogReq.read()


def getProduct(productType, macOSVersion, targetVolume, targetPackageName, seedProgram):
	packageData = []
	catalogData = getCatalogData(targetVolume, seedProgram)
	root = plistlib.readPlistFromString(catalogData)
	products = root['Products']
	if targetPackageName == "*":
		print "Searching for macOS: %s" % macOSVersion
	else:
		print "Searching for: %s for macOS %s" % (targetPackageName, macOSVersion)

	if productType == "install":
		for key in products:
			if 'ExtendedMetaInfo' in products[key]:
				extendedMetaInfo = products[key]['ExtendedMetaInfo']

				if 'InstallAssistantPackageIdentifiers' in extendedMetaInfo:
					IAPackageIDs = extendedMetaInfo['InstallAssistantPackageIdentifiers']

					if IAPackageIDs['InstallInfo'] == 'com.apple.plist.InstallInfo' and IAPackageIDs['OSInstall'] == 'com.apple.mpkg.OSInstall':
						packageData.extend([key, products[key]])
	elif productType == "update":
		for key in products:
			if 'ExtendedMetaInfo' in products[key]:
				extendedMetaInfo = products[key]['ExtendedMetaInfo']
				if 'ProductType' in extendedMetaInfo:
					if extendedMetaInfo['ProductType'] == 'macOS' and extendedMetaInfo['ProductVersion'] == macOSVersion:
						packageData.extend([key, products[key]])

	return packageData


def downloadFiles(argumentData):
	url = argumentData[0]
	targetFilename = argumentData[1]
	try:
		fileReq = urlopen(url)
	except:
		print >> sys.stderr, ("\nERROR: opening of (%s) failed. Aborting ...\n" % url)
		sys.exit(-1)

	filename = basename(url)
	filesize = argumentData[2]

	with open(targetFilename, 'wb') as file:
		while True:
			chunk = fileReq.read(4096)
			if not chunk:
				print "Download of %s finished" % filename
				break
			file.write(chunk)


def getBuildAndVersion(distributionFile, targetPackageName, unpackFolder):
	build  = 0
	version = 0
	tree = ElementTree.parse(distributionFile)
	root = tree.getroot()
	auxinfo = root.find('auxinfo')

	if not auxinfo == None:
		auxinfo_iter = auxinfo.iter()

		for element in auxinfo_iter:
			if element.tag == 'key' and element.text == 'BUILD':
				try:
					build = auxinfo_iter.next().text
				except StopIteration:
					pass
			elif element.tag == 'key' and element.text == 'VERSION':
				try:
					version = auxinfo_iter.next().text
				except StopIteration:
					pass
		return (version, build)
	else:
		for element in root.findall('pkg-ref'):
			id = element.get('id')
			parts = id.split('.')

			if targetPackageName == "FirmwareUpdate.pkg" and unpackFolder != "":
				if parts[-1] == "FirmwareUpdate":
					build = parts[-1]
					return (version, build)
			elif len(parts) > 4:
				build = parts[-1]
				return (version, build)

	return ('Unknown', 'Unknown')


def confirmWithText(confirmationText, shouldAbort):
	while True:
		confirm = raw_input(confirmationText).lower()
		if confirm in ('n', 'y'):
			if confirm == 'n':
				if shouldAbort:
					print "Aborting ...\n"
					sys.exit(0)
				else:
					return False
			elif confirm == 'y':
				return True
		else:
			sys.stdout.write("\033[F\033[K")
	return False


def expandPackage(packageName, targetFolder):
	if os.path.isdir(targetFolder):
		print "\nError: Given target path already exists!"
		print "       Please remove it or use a different path!\n\nAborting ...\n"
		sys.exit(17)
	print "Expanding %s to %s" %(basename(packageName), targetFolder)
	subprocess.call(['pkgutil', '--expand', packageName, targetFolder])
	sys.exit(0)


def getPackages(productType, macOSVersion, targetPackageName, targetVolume, unpackFolder, askForConfirmation, seedProgram, languageSelector):
	data = getProduct(productType, macOSVersion, targetVolume, targetPackageName, seedProgram)

	if data == None:
		print >> sys.stderr, ("\nERROR: target macOS version (%s) not found. Aborting ..." % macOSVersion)
		print >> sys.stderr, ("       - you may need to use the -m <version> argument\n")
		sys.exit(1)

	list = []
	buildIDs = []
	item = 0
	index = 0
	indent = ' - '
	selectorText = ''
	#currentBuildID = getSystemVersionPlist(targetVolume, 'ProductBuildVersion')
	packageCount = (len(data)/2)

	while(index < (packageCount*2)):
		key = data[index]
		product = data[index+1]
		index+=2
		targetPath = os.path.join(targetVolume, tmpDirectory, key)

		if not os.path.isdir(targetPath):
			os.makedirs(targetPath)

		distributions = product['Distributions']

		if distributions[languageSelector]:
			distributionURL = distributions.get(languageSelector)
			distributionFile = downloadDistributionFile(distributionURL, targetPath)

		seedVersion, seedBuildID = getBuildAndVersion(distributionFile, targetPackageName, unpackFolder)

		if productType == 'update' and seedVersion == 0:
			seedVersion = macOSVersion

		if seedVersion >= macOSVersion:
			buildIDs.append(seedBuildID)
		else:
			continue

		item+=1

		if packageCount > 1:
			selectorText = "[ %s ] " % item
			indent = '      - '

		print "\n%sFound update for macOS %s (%s) with key: %s" % (selectorText, seedVersion, seedBuildID, key)

#if currentBuildID == seedBuildID:
#			print "%swarning: seed build version is the same as macOS on this Mac!" % indent
#		elif currentBuildID > seedBuildID:
#			print "%swarning: seed build version is older than macOS on this Mac!" % indent
#		elif currentBuildID < seedBuildID:
#			print "%sseed build version is newer than macOS on this Mac (Ok)" % indent

	if len(buildIDs) == 0:
		print >> sys.stderr, ("\nERROR: target macOS version (%s) not found. Aborting ..." % macOSVersion)
		print >> sys.stderr, ("       - you may need to use the -m <version> argument\n")
		sys.exit(1)

	print ''
	while True:
		if item > 1:
			selection = raw_input("Select package to install [1-%s] " % packageCount)

			if selection.isdigit():
				number = int(selection)
				if number > 0 and number <= packageCount:
					number-=1
					break
				else:
					sys.stdout.write("\033[F\033[K")
			else:
				sys.stdout.write("\033[F\033[K")
		else:
			number = 0
			break

	seedBuildID = buildIDs[number]

#	if currentBuildID == seedBuildID:
#		confirmationText = "\nAre you sure that you want to continue [y/n] ? "
#	elif currentBuildID > seedBuildID:
#		confirmationText = "\nAre you absolutely sure that you want to continue [y/n] ? "
#	elif currentBuildID < seedBuildID:
#		confirmationText = "\nDo you want to continue [y/n] ? "

	if askForConfirmation == True:
		confirmWithText(confirmationText, True)

	# update key / use key from the selected item.
	key = data[(number*2)]
	# update targetPath / use path from the selected item.
	targetPath = os.path.join(targetVolume, tmpDirectory, key)
	product = data[((number*2)+1)]
	packages = product['Packages']

	for package in packages:
		url = package.get('URL')
		filename = basename(url)
		targetFilename = os.path.join(targetPath, filename)

		if filename == targetPackageName or targetPackageName == "*":
			filesize = package.get('Size')
			args = [url, targetFilename, filesize]
			list.append(args)

			if not targetPackageName == "*":
				break;

	if not len(list) == 0:
		print "\nQueued Download(s):"
		for array in list:
			print "%s [%s bytes]" % (basename(array[1]), array[2])
		print ''
		p = Pool()
		p.map(downloadFiles, list)
		p.close()
	else:
		if targetPackageName != "*":
			print "\nWarning: target package > %s < not found!" % targetPackageName

	if not unpackFolder == '':
		expandPackage(targetFilename, unpackFolder)
	
	return (key, distributionFile, targetVolume)


def main(argv):
	sys.stdout.write("\x1b[2J\x1b[H")

	if platform.system() == "Windows":
		tmpDirectory = tempfile.gettempdir()
	
	parser = argparse.ArgumentParser()
	parser.add_argument('-a', dest='action')
	parser.add_argument('-c', dest='confirm')
	parser.add_argument('-f', dest='targetPackage')
	parser.add_argument('-t', dest='volume')
	parser.add_argument('-u', dest='unpackFolder')
	parser.add_argument('-m', dest='macOSVersion')
	args = parser.parse_args()
	
	if args.macOSVersion == None:
		macOSVersion = "10.13"
	else:
		macOSVersion = args.macOSVersion

	print "------------------------------------------------------------"
	print "downloadSeed.py v%s Copyright (c) 2017 by Dr. Pike R. Alpha" % VERSION
	print "------------------------------------------------------------"

	seedProgram = "DeveloperSeed"
	languageSelector = "English"
	key, distributionFile, targetVolume = getPackages(args.action, args.macOSVersion, args.targetPackage, args.volume, args.unpackFolder, args.confirm, seedProgram, languageSelector)

 	if key == "":
 		print "Error: Aborting ..."


if __name__ == "__main__":
	# Allows downloadSeed.py to exit quickly when pressing Ctrl+C.
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	main(sys.argv[1:])
