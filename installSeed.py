#!/usr/bin/python

#
# Script (installSeed.py) to get the latest seed package.
#
# Version 2.7 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
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
#

import os
import sys
import glob
import plistlib
import subprocess
import urllib2
import platform

from os.path import basename
from Foundation import NSLocale
from multiprocessing import Pool

os.environ['__OS_INSTALL'] = "1"

#
# Script version info.
#
scriptVersion=2.7

#
# Setup seed program data.
#
seedProgramData = {
 "DeveloperSeed":"index-10.13seed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "PublicSeed":"index-10.13beta-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "CustomerSeed":"index-10.13customerseed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
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
 "es_419":"es_419", #Latin American Spanish
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
	locale = NSLocale.currentLocale()
	languageCode = NSLocale.languageCode(locale)
	id = languageCode
	countryCode = NSLocale.countryCode(locale)
	localeIdentifier = NSLocale.localeIdentifier(locale)
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
	
	volumeNumber = raw_input('\nSelect a target volume for the boot file: ')
	return targetVolumes[int(volumeNumber)]

def downloadDistributionFile(url, targetPath):
	req = urllib2.urlopen(url)
	filename = basename(url)
	filesize = req.info().getheader('Content-Length')
	distributionFile = os.path.join(targetPath, filename)
	
	if os.path.exists(distributionFile):
		os.remove(distributionFile)

	with open(distributionFile, 'w') as file:
		print 'Downloading: %s [%s bytes] ...' % (filename, filesize)
		while True:
			chunk = req.read(1024)
			if not chunk:
				break
			file.write(chunk)

	return distributionFile

def getSeedProgram():
	version = getOSVersion()
	name = getOSNameByOSVersion(version)
	systemVersionPlist = plistlib.readPlist("/System/Library/CoreServices/SystemVersion.plist")
	buildID = systemVersionPlist['ProductBuildVersion']
	print 'Currently running on macOS %s %s Build (%s) ' % (name, version, buildID)
	
	try:
		if systemVersionPlist['ProductVersion'] == '10.9':
			seedEnrollmentPlist = plistlib.readPlist("/Library/Application Support/App Store/.SeedEnrollment.plist")
		else:
			seedEnrollmentPlist = plistlib.readPlist("/Users/Shared/.SeedEnrollment.plist")
	except IOError:
		return ''
	
	seedProgram = seedEnrollmentPlist['SeedProgram']
	print 'Seed Program Enrollment: ' + seedProgram
	return seedProgram

def getCatalogData():
	seedProgram = getSeedProgram()
	catalog = seedProgramData.get(seedProgram, seedProgramData['PublicSeed'])
	catalogURL = "https://swscan.apple.com/content/catalogs/others/" + catalog
	catalogReq = urllib2.urlopen(catalogURL)
	#print catalogReq.info().getheader('Content-Length')
	return catalogReq.read()

def getProduct():
	macOSVersion = '10.13'
	catalogData = getCatalogData()
	root = plistlib.readPlistFromString(catalogData)
	products = root['Products']
	
	for key in products:
		if 'ExtendedMetaInfo' in products[key]:
			extendedMetaInfo = products[key]['ExtendedMetaInfo']
				
			if 'InstallAssistantPackageIdentifiers' in extendedMetaInfo:
				IAPackageIDs = extendedMetaInfo['InstallAssistantPackageIdentifiers']
					
				if IAPackageIDs['InstallInfo'] == 'com.apple.plist.InstallInfo' and IAPackageIDs['OSInstall'] == 'com.apple.mpkg.OSInstall':
					return (key, products[key])

def downloadFile(argumentData):
	url = argumentData[0]
	targetFilename = argumentData[1]
	fileReq = urllib2.urlopen(url)
	filename = basename(url)
	filesize = argumentData[2]

	with open(targetFilename, 'wb') as file:
		#print 'Downloading: %s [%s bytes] ...' % (filename, filesize)
		while True:
			chunk = fileReq.read(4096)
			if not chunk:
				print 'Download of %s finished' % filename
				break
			file.write(chunk)

def getPackages(languageSelector):
	list = []
	data = getProduct()
	key = data[0]
	product = data[1]
	targetVolume = getTargetVolume()
	targetPath = os.path.join(targetVolume, tmpDirectory, key)

	if not os.path.isdir(targetPath):
		os.makedirs(targetPath)

	distributions = product['Distributions']

	if distributions[languageSelector]:
		distributionURL = distributions.get(languageSelector)
		distributionFile = downloadDistributionFile(distributionURL, targetPath)

	packages = product['Packages']

	for package in packages:
		url = package.get('URL')
		filename = basename(url)
		targetFilename = os.path.join(targetPath, filename)
		filesize = package.get('Size')
		args = [url, targetFilename, filesize]
		list.append(args)

	if not len(list) == 0:
		print '\nQueued Downloads:\n'
		for array in list:
			print '%s [%s bytes]' % (basename(array[1]), array[2])
		print ''

	p = Pool()
	p.map(downloadFile, list)
	p.close()

	return (key, distributionFile, targetVolume)

def copyFiles(targetVolume, key):
	targetPath = os.path.join(targetVolume, tmpDirectory, key)

	if os.path.isdir(targetVolume + "/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport"):
		#
		# Yes we do, but did copy_dmg (a script inside RecoveryHDMetaDmg.pkg) copy the files that Install macOS 10.13 Beta.app needs?
		#
		if not os.path.exists(targetVolume + "/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/AppleDiagnostics.dmg"):
			#
			# Without this step we end up with installer.pkg as InstallDMG.dmg and InstallInfo.plist
			#
			print 'Copying: InstallESDDmg.pkg to the target location ...'
			sourceFile = os.path.join(targetPath, "InstallESDDmg.pkg")
			#print sourceFile
			sharedSupportPath = os.path.join(targetVolume, "Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport")
			#print targetPath
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath + "/InstallESD.dmg" ])
			#
			# Without this step we end up without AppleDiagnostics.[dmg/chunklist].
			#
			print 'Copying: AppleDiagnostics.dmg to the target location ...'
			sourceFile = os.path.join(targetPath, "AppleDiagnostics.dmg")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])
			print 'Copying: AppleDiagnostics.chunklist to the target location ...'
			sourceFile = os.path.join(targetPath, "AppleDiagnostics.chunklist")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])
			#
			# Without this step we end up without BaseSystem.[dmg/chunklist].
			#
			print 'Copying: BaseSystem.dmg to the target location ...'
			sourceFile = os.path.join(targetPath, "BaseSystem.dmg")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])
			print 'Copying: BaseSystem.chunklist to the target location ...'
			sourceFile = os.path.join(targetPath, "BaseSystem.chunklist")
			subprocess.call(["sudo", "cp", sourceFile, sharedSupportPath])

def runInstaller(installerPkg, targetVolume):
	print 'Running installer ...'
	subprocess.call(["sudo", "/usr/sbin/installer", "-pkg", installerPkg, "-target", targetVolume])
	#/System/Library/CoreServices/Installer.app/Contents/MacOS/Installer

def installSeedPackage(distributionFile, key, targetVolume):
	targetPath = os.path.join(targetVolume, tmpDirectory, key)
	installerPkg = os.path.join(targetPath, installerPackage)
	print 'Creating installer.pkg ...'
	subprocess.call(["sudo", "productbuild", "--distribution", distributionFile, "--package-path", targetPath, installerPkg])
	
	if os.path.exists(installerPkg):
		runInstaller(installerPkg, targetVolume)

if __name__ == "__main__":
	languageSelector = selectLanguage()
	data = getPackages(languageSelector)
	key = data[0]
	distributionFile = data[1]
	targetVolume = data[2]

	if key == "":
		print 'Error: Aborting ...'
	else:
		installSeedPackage(distributionFile, key, targetVolume)
		copyFiles(targetVolume, key)

