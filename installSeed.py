#!/usr/bin/env python

#
# Script (installSeed.py) to get the latest seed package.
#
# Version 3.8 - Copyright (c) 2017 by Dr. Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#		   - comments added
#		   - target directory check added (Pike R. Alpha, August 2017)
#		   - filesize check added
#		   - renamed script
#		   - don't try to remove the .dist file if it isn't there.
#		   - copy InstallESDDmg.pkg to /Applications/Install macOS High Sierra Beta.app/Content/SharedSupport/InstallESD.dmg
#		   - set environment variable.
#		   - use sudo and path for productbuild.
#		   - internationalisation (i18n) support added (downloads the right dictionary).
#		   - initial refactoring done.
#		   - minor cleanups.
#		   - version number error fixed.
#		   - graceful exit with instructions to install pip/request module.
#		   - use urllib2 instead of requests (thanks to Per Olofsson aka MagerValp).
#		   - more refactoring work done.
#		   - improved output of macOS name and version.
#		   - swap line order (error in v2.3).
#		   - eliminated two global variables and fixed some whitespace errors.
#		   - improved output of downloads and streamlined use of arguments.
#		   - multithreaded package downloads.
#		   - undone the renaming of getPackages() from Brian's tree.
#		   - now showing a list of the queued downloads, and when they are finished.
#		   - show seed BuildID/Key and ask the user for consent before continuing.
#		   - checks added for user input.
#		   - copyright notice in output of script added.
#		   - minor cleanups.
#		   - whitespace, output (formatting) and indentation fixes.
#		   - initial support for seed updates and downloads of a single packet.
#		   - command line arguments added.
#		   - buildID checks added.
#		   - show confirmation text based on the current/seed buildID's.
#		   - unpack option -u [path] support added for downloaded files.
#		   - script will now stop/abort when Ctrl+C is pressed.
#		   - check for Beta seed added to copyFiles()
#		   - option -m added to select a target macOS version.
#		   - error handling for urllib2.urlopen() added.
#		   - fixed two typos.
#		   - white space only changes.
#		   - fixed NSLocale incompatibility issues (verified with El Capitan).
#		   - license added.
#		   - shebang line changed.
#		   - fall back to en_US if selectLanguage fails.
#		   - run pkgutil without sudo.
#		   - add the regular update CatalogURL.
#		   - read SystemVersion.plist from target volume.
#		   - read seed enrollment plist from target volume.
#		   - renamed targetPath to sourcePath.
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
import subprocess
import urllib2
import platform
import getopt
import signal

from os.path import basename
from Foundation import NSLocale
from multiprocessing import Pool
from xml.etree import ElementTree
from numbers import Number
from subprocess import Popen, PIPE

os.environ['__OS_INSTALL'] = "1"

#
# Script version info.
#
scriptVersion=3.8

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
# International Components for Unicode (http://www.localeplanet.com/icu/)
#
icuData = {
 "el":"el",			#Greek
 "vi":"vi",			#English (U.S. Virgin Islands)
 "ca":"cs",			#Aghem (Cameroon)
 "ar":"ar",			#Arabic
 "cs":"cs",			#Czech
 "id":"id",			#Indonesian
 "ru":"ru",			#Russian
 "no":"no",			#Norwegian
 "tr":"tr",			#Turkish
 "th":"th",			#Thai
 "he":"he",			#Hebrew
 "pt":"pt",			#Portuguese
 "pl":"pl",			#Polish
 "uk":"uk",			#Ukrainian
 "hr":"hr",			#Croatian
 "hu":"hu",			#Hungarian
 "hi":"hi",			#Hindi
 "fi":"fi",			#Finnish
 "da":"da",			#Danish
 "ro":"rp",			#Romanian
 "ko":"ko",			#Korean
 "sv":"sv",			#Swedish
 "sk":"sk",			#Slovak
 "ms":"ms",			#Malay
 "en":"English",	#English
 "ja":"Japanese",	#Japanese
 "nl":"Dutch",		#Dutch
 "fr":"French",		#French
 "it":"Italian",	#Italian
 "de":"German",		#German
 "es":"Spanish",	#Spanish
 "es_419":"es_419",	#Latin American Spanish
 "zh_TW":"zh_TW",	#Chinese (Traditional, Taiwan)
 "zh_CN":"zh_CN",	#Chinese (Simplified, China, Hong Kong, Macau and Singapore)
 "pt":"pt",			#Portuguese (Angola, Brazil, Guinea-Bissau and Mozambique)
 "pt_PT":"pt_PT"	#Portuguese (Portugal)
}

#
# The target directory.
#
tmpDirectory="tmp"

#
# Name of target installer package.
#
installerPackage="installer.pkg"


def getOSVersion():
	version = platform.mac_ver()
	return float('.'.join(version[0].split('.')[:2]))


def getOSNameByOSVersion(version):
	switcher = {
	10.0:	"Cheetah",
	10.1:	"Puma",
	10.2:	"Jaguar",
	10.3: 	"Panther",
	10.4:	"Tiger",
	10.5:	"Leopard",
	10.6:	"Snow Leopard",
	10.7:	"Lion",
	10.8:	"Mountain Lion",
	10.9:	"Mavericks",
	10.10:	"Yosemite",
	10.11:	"El Capitan",
	10.12:	"Sierra",
	10.13:	"High Sierra"
	}
	return switcher.get(version, "Unknown")


def getICUName(id):
	return icuData.get(id, icuData['en'])


def selectLanguage():
	macOSVersion = getOSVersion()
	
	if macOSVersion > 10.11:
		locale = NSLocale.currentLocale()
		languageCode = NSLocale.languageCode(locale)
		id = languageCode
		countryCode = NSLocale.countryCode(locale)
		localeIdentifier = NSLocale.localeIdentifier(locale)
	else:
		cmd = ["defaults", 'read', '.GlobalPreferences', 'AppleLocale']
		proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = proc.communicate()

		if proc.returncode:
			id = "en"
			localeIdentifier = "en_US"
		else:
			localeIdentifier = output
			id = languageCode = output.split('_')[0]
	#
	# Special cases for Apple's SU.
	#
	if languageCode == "pt" and localeIdentifier == "pt_PT":
		id = localeIdentifier
	elif languageCode == "es" and localeIdentifier == "es_419":
		id = localeIdentifier
	elif languageCode == "zh":
		if localeIdentifier == "zh_TW":
			id = localeIdentifier
		else:
			id = "zh_CN"

	return getICUName(id)


def getTargetVolume():
	index = 0
	targetVolumes = glob.glob("/Volumes/*")
	print '\nAvailable target volumes:\n'

	for volume in targetVolumes:
		print ('[ %i ] %s' % (index, basename(volume)))
		index+=1

	print ''

	while True:
		try:
			volumeNumber = int(raw_input('Select a target volume: '))
			if volumeNumber > (index-1):
				sys.stdout.write("\033[F\033[K")
			else:
				break;
		except:
			sys.stdout.write("\033[F\033[K")

	return targetVolumes[int(volumeNumber)]


def downloadDistributionFile(url, targetPath):
	try:
		req = urllib2.urlopen(url)
	except urllib2.URLError:
		print >> sys.stderr("\nERROR: opening of (%s) failed. Aborting ...\n" % url)

	filename = basename(url)
	filesize = req.info().getheader('Content-Length')
	distributionFile = os.path.join(targetPath, filename)

	if os.path.exists(distributionFile):
		os.remove(distributionFile)

	with open(distributionFile, 'w') as file:
		print '\nDownloading: %s [%s bytes] ...' % (filename, filesize)
		while True:
			chunk = req.read(1024)
			if not chunk:
				break
			file.write(chunk)

	return distributionFile


def getSystemVersionPlist(targetVolume, target):
	systemVersionPlist = plistlib.readPlist(os.path.join(targetVolume, "System/Library/CoreServices/SystemVersion.plist"))
	if target == None:
		return systemVersionPlist
	else:
		try:
			return systemVersionPlist[target]
		except IOError:
			return 'None'


def getSeedProgram(targetVolume):
	version = getOSVersion()
	name = getOSNameByOSVersion(version)
	systemVersionPlist = getSystemVersionPlist(targetVolume, None)
	currentBuildID = systemVersionPlist['ProductBuildVersion']
	print 'Currently running on macOS %s %s Build (%s) ' % (name, version, currentBuildID)

	try:
		if systemVersionPlist['ProductVersion'] == '10.9':
			seedEnrollmentPlist = plistlib.readPlist(os.path.join(targetVolume, "Library/Application Support/App Store/.SeedEnrollment.plist"))
		else:
			seedEnrollmentPlist = plistlib.readPlist(os.path.join(targetVolume, "Users/Shared/.SeedEnrollment.plist"))
	except IOError:
		return 'None'

	seedProgram = seedEnrollmentPlist['SeedProgram']
	print 'Seed Program Enrollment: ' + seedProgram
	return seedProgram


def getCatalogData(targetVolume):
	seedProgram = getSeedProgram(targetVolume)
	catalog = seedProgramData.get(seedProgram, seedProgramData['Regular'])
	catalogURL = "https://swscan.apple.com/content/catalogs/others/" + catalog
	try:
		catalogReq = urllib2.urlopen(catalogURL)
	except URLError:
		print >> sys.stderr, ("\nERROR: opening of (%s) failed. Aborting ...\n" % url)
		sys.exit(-1)

	return catalogReq.read()


def getProduct(productType, macOSVersion, targetVolume):
	catalogData = getCatalogData(targetVolume)
	root = plistlib.readPlistFromString(catalogData)
	products = root['Products']
	print 'Searching for macOS: %s' % macOSVersion

	if productType == "install":
		for key in products:
			if 'ExtendedMetaInfo' in products[key]:
				extendedMetaInfo = products[key]['ExtendedMetaInfo']

				if 'InstallAssistantPackageIdentifiers' in extendedMetaInfo:
					IAPackageIDs = extendedMetaInfo['InstallAssistantPackageIdentifiers']

					if IAPackageIDs['InstallInfo'] == 'com.apple.plist.InstallInfo' and IAPackageIDs['OSInstall'] == 'com.apple.mpkg.OSInstall':
						return (key, products[key])
	elif productType == "update":
		for key in products:
			if 'ExtendedMetaInfo' in products[key]:
				extendedMetaInfo = products[key]['ExtendedMetaInfo']
				if 'ProductType' in extendedMetaInfo:
					if extendedMetaInfo['ProductType'] == 'macOS' and extendedMetaInfo['ProductVersion'] == macOSVersion:
						return (key, products[key])


def downloadFiles(argumentData):
	url = argumentData[0]
	targetFilename = argumentData[1]
	try:
		fileReq = urllib2.urlopen(url)
	except:
		print >> sys.stderr, ("\nERROR: opening of (%s) failed. Aborting ...\n" % url)
		sys.exit(-1)

	filename = basename(url)
	filesize = argumentData[2]

	with open(targetFilename, 'wb') as file:
		while True:
			chunk = fileReq.read(4096)
			if not chunk:
				print 'Download of %s finished' % filename
				break
			file.write(chunk)


def isBetaSeed(distributionFile):
	tree = ElementTree.parse(distributionFile)
	root = tree.getroot()
	localization = root.find('localization')

	if not localization == None:
		localization_iter = localization.iter()
	
		for element in localization_iter:
			if element.tag == 'strings':
				strings = element.text.split(';')[0]
				break

		if 'beta' in strings.lower():
			return True

	return False


def getBuildID(distributionFile):
	tree = ElementTree.parse(distributionFile)
	root = tree.getroot()
	auxinfo = root.find('auxinfo')

	if not auxinfo == None:
		auxinfo_iter = auxinfo.iter()

		for element in auxinfo_iter:
			if element.tag == 'key' and element.text == 'BUILD':
				try:
					return auxinfo_iter.next().text
				except StopIteration:
					pass
	else:
		element = root.find('pkg-ref')
		id = element.get('id')

		if not id == None:
			return id.split('.')[-1]

	return 'Unknown'


def getPackages(productType, macOSVersion, targetPackageName, targetVolume, unpackPackage, askForConfirmation, languageSelector):
	list = []

	if targetVolume == '':
		targetVolume = getTargetVolume()

	data = getProduct(productType, macOSVersion, targetVolume)

	if data == None:
		print >> sys.stderr, ("\nERROR: target macOS version (%s) not found. Aborting ...\n" % macOSVersion)
		sys.exit(1)

	key = data[0]
	product = data[1]

	targetPath = os.path.join(targetVolume, tmpDirectory, key)

	if not os.path.isdir(targetPath):
		os.makedirs(targetPath)

	distributions = product['Distributions']

	if distributions[languageSelector]:
		distributionURL = distributions.get(languageSelector)
		distributionFile = downloadDistributionFile(distributionURL, targetPath)

	seedBuildID = getBuildID(distributionFile)
	print 'Found Install Package with BuildID (%s) and Key (%s)' % (seedBuildID , key)
	confirmationText = 'Are you sure that you want to continue [y/n] ? '
	currentBuildID = getSystemVersionPlist(targetVolume, 'ProductBuildVersion')

	if currentBuildID == seedBuildID:
		print '\nWarning: Seed BuildID is the same as macOS on this Mac!'
	elif seedBuildID < currentBuildID:
		print '\nWarning: Seed BuildID is older than macOS on this Mac!'
		confirmationText = 'Are you absolutely sure that you want to continue [y/n] ? '
	elif seedBuildID > currentBuildID:
		print 'Seed BuildID is newer than macOS on this Mac (Ok)'
		confirmationText = 'Do you want to continue [y/n] ? '

	if askForConfirmation == True:
		print ''
		while True:
			confirm = raw_input(confirmationText).lower()
			if confirm in ('n', 'y'):
				if confirm == 'n':
					print 'Aborting ...\n'
					sys.exit(0)
				elif confirm == 'y':
					break
			else:
				sys.stdout.write("\033[F\033[K")

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
		print '\nQueued Download(s):'
		for array in list:
			print '%s [%s bytes]' % (basename(array[1]), array[2])
		print ''
		p = Pool()
		p.map(downloadFiles, list)
		p.close()
	else:
		if targetPackageName != "*":
			print '\nWarning: target package > %s < not found!' % targetPackageName

	if not unpackPackage == '':
		if os.path.isdir(unpackPackage):
			print '\nError: Given target path already exists!'
			print '       Please remove it or use a different path!\n\nAborting ...\n'
			sys.exit(17)
		print 'Expanding %s to %s' %(targetPackageName, unpackPackage)
		subprocess.call(["pkgutil", "--expand", targetFilename, unpackPackage])
	
	return (key, distributionFile, targetVolume)


def copyFiles(distributionFile, key, targetVolume, applicationPath):
	sourcePath = os.path.join(targetVolume, tmpDirectory, key)
	sharedSupportPath = os.path.join(applicationPath, "Contents/SharedSupport")

	if os.path.isdir(sharedSupportPath):
		#
		# Yes we do, but did copy_dmg (a script inside RecoveryHDMetaDmg.pkg) copy the files that Install macOS 10.13 (Beta).app needs?
		#
		if not os.path.exists(sharedSupportPath + "/AppleDiagnostics.dmg"):
			#
			# Without this step we end up with installer.pkg as InstallDMG.dmg and InstallInfo.plist
			#
			print '\nCopying: InstallESDDmg.pkg to the target location ...'
			sourceFile = os.path.join(sourcePath, "InstallESDDmg.pkg")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath + "/InstallESD.dmg" ])
			#
			# Without this step we end up without AppleDiagnostics.[dmg/chunklist].
			#
			print 'Copying: AppleDiagnostics.dmg to the target location ...'
			sourceFile = os.path.join(sourcePath, "AppleDiagnostics.dmg")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])
			print 'Copying: AppleDiagnostics.chunklist to the target location ...'
			sourceFile = os.path.join(sourcePath, "AppleDiagnostics.chunklist")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])
			#
			# Without this step we end up without BaseSystem.[dmg/chunklist].
			#
			print 'Copying: BaseSystem.dmg to the target location ...'
			sourceFile = os.path.join(sourcePath, "BaseSystem.dmg")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])
			print 'Copying: BaseSystem.chunklist to the target location ...'
			sourceFile = os.path.join(sourcePath, "BaseSystem.chunklist")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])


def runInstaller(installerPkg, targetVolume):
	print '\nRunning installer ...'
	subprocess.call(["sudo", "/usr/sbin/installer", "-pkg", installerPkg, "-target", targetVolume])


def installPackage(distributionFile, key, targetVolume):
	targetPath = os.path.join(targetVolume, tmpDirectory, key)
	installerPkg = os.path.join(targetPath, installerPackage)
	print '\nCreating installer.pkg ...'
	subprocess.call(["sudo", "productbuild", "--distribution", distributionFile, "--package-path", targetPath, installerPkg])

	if os.path.exists(installerPkg):
		runInstaller(installerPkg, targetVolume)


def showUsage(error, arg):
	if  error == True and not arg == '':
		print 'Error: invalid argument \'%s\' used\n' % arg
	else:
		print 'Error: invalid argument(s) used\n'
	print 'Supported arguments:\n'
	print 'installSeed.py -a update'
	print 'installSeed.py -a update -f <packagename>'
	print 'installSeed.py -a update -f <packagename> -t <volume>'
	print 'installSeed.py -a update -f <packagename> -t <volume> -u [target path]'
	print 'installSeed.py -a update -f <packagename> -t <volume> -c [0/1] (0 skips confirmation)\n'
	print 'installSeed.py -a update -f <packagename> -t <volume> -c [0/1] (0 skips confirmation) -m [10.13.x]\n'
	print 'installSeed.py -a install'
	print 'installSeed.py -a install -f <packagename>'
	print 'installSeed.py -a install -f <packagename> -t <volume>'
	print 'installSeed.py -a install -f <packagename> -t <volume> -u [target path]'
	print 'installSeed.py -a install -f <packagename> -t <volume> -c [0/1] (0 skips confirmation)\n'
	print 'installSeed.py -a install -f <packagename> -t <volume> -c [0/1] (0 skips confirmation) -m [10.13.x]\n'
	sys.exit(2)


def main(argv):
	sys.stdout.write("\x1b[2J\x1b[H")
	print 'installSeed.py v%s Copyright (c) 2017 by Dr. Pike R. Alpha\n' % scriptVersion
	action = 'install'
	target = '*'
	volume = ''
	confirm = True;
	unpackPackage = ''
	languageSelector = selectLanguage()
	print 'languageSelector: %s' % languageSelector
	macOSVersion = '10.13.1'

	try:
		opts, args = getopt.getopt(argv,"h:a:f:t:c:u:m:",["help","action","file","target","confirmation","unpack","mac"])
	except getopt.GetoptError as error:
		print str(error)
		showUsage(True, '')

	for opt, arg in opts:
		if opt in ('-h', '--help'):
			showUsage(False, '')
		elif opt in ('-a', '-action'):
			if arg in ('update', 'install'):
				action = arg
			else:
				showUsage(True, arg)
		elif opt == '-f':
			target = arg
		elif opt == '-c':
			confirm = arg
		elif opt == '-t':
			volume = arg
		elif opt == '-u':
			if target != '*':
				unpackPackage = arg
			else:
				showUsage(True, arg)
		elif opt == '-m':
			macOSVersion = arg
		else:
			showUsage(True, arg)

	data = getPackages(action, macOSVersion, target, volume, unpackPackage, confirm, languageSelector)
	key = data[0]
	distributionFile = data[1]
	targetVolume = data[2]

 	if key == "":
 		print "Error: Aborting ..."
 	elif target == "*":
		if action == "install" and target == "*":
			installPackage(distributionFile, key, targetVolume)
			betaTag = ""

			if isBetaSeed(distributionFile):
				betaTag = " Beta"

			applicationPath = os.path.join(targetVolume, "Applications/Install macOS High Sierra" + betaTag + ".app")
			copyFiles(distributionFile, key, targetVolume, applicationPath)
		elif action == "update":
			print 'Support for -a update is not implemented in v%s' % scriptVersion


if __name__ == "__main__":
	# Allows installSeed.py to exit quickly when pressing Ctrl+C.
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	main(sys.argv[1:])
