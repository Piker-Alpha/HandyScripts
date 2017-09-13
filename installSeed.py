#!/usr/bin/python

#
# Script (installSeed.py) to get the latest seed package.
#
# Version 2.1 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
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
#          - use urllib2 instead of requests (thanks to Per Olofsson aka MagerValp).
#

import os
import sys
import glob
import plistlib
import subprocess
import urllib2

from os.path import basename
from Foundation import NSLocale

os.environ['__OS_INSTALL'] = "1"

#
# Script version info.
#
scriptVersion=2.1

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

def downloadDistributionFile(product):
	if 'Distributions' in product:
		distributions = product['Distributions']
		
		languageSelector = selectLanguage()
		
		if distributions[languageSelector]:
			distributionURL = distributions.get(languageSelector)
			req = urllib2.urlopen(distributionURL)
			distributionID = key + '.' + languageSelector + '.dist'
			distributionFile = os.path.join(targetPath, distributionID)
			print 'Downloading: ' + distributionID + ' ...'
			
			if os.path.exists(distributionFile):
				os.remove(distributionFile)
			
			file = open(distributionFile, 'w')
			
			while True:
				chunk = req.read(1024)
				if not chunk:
					break
				file.write(chunk)
			file.close()
				
		return distributionFile

#
# Name of target installer package.
#
installerPackage="installer.pkg"

#
# Initialisation of a variable.
#
index = 0

#
# Collect available target volume names.
#
targetVolumes = glob.glob("/Volumes/*")

print '\nAvailable target volumes:\n'

for volume in targetVolumes:
	print ('[ %i ] %s' % (index, basename(volume)))
	index+=1

#
# Ask to select a target volume.
#
volumeNumber = raw_input('\nSelect a target volume for the boot file: ')

#
# Path to target volume.
#
targetVolume = targetVolumes[int(volumeNumber)]
#print targetVolume

#
# Read ProductBuildVersion from SystemVersionplist.
#
systemVersionPlist = plistlib.readPlist("/System/Library/CoreServices/SystemVersion.plist")
buildID = systemVersionPlist['ProductBuildVersion']

#
# Read ProductVersion from SystemVersionplist.
#
if systemVersionPlist['ProductVersion'] == '10.9':
	#
	# Read enrollment plist for 10.9.
	#
	seedEnrollmentPlist = plistlib.readPlist("/Library/Application Support/App Store/.SeedEnrollment.plist")
else:
	#
	# Read enrollment plist for 10.10 and greater.
	#
	seedEnrollmentPlist = plistlib.readPlist("/Users/Shared/.SeedEnrollment.plist")

#
# Read SeedProgram from enrollment plist.
#
seedProgram = seedEnrollmentPlist['SeedProgram']
print 'Seed Program Enrollment: ' + seedProgram

#
# Get catalog path from seedProgramData.
#
catalog = seedProgramData.get(seedProgram, seedProgramData['PublicSeed'])
catalogURL = "https://swscan.apple.com/content/catalogs/others/" + catalog
#print catalogURL

#
# Get the software update catalog (sucatalog).
#
catalogReq = urllib2.urlopen(catalogURL)
catalogData = catalogReq.read()

#
# Get root.
#
root = plistlib.readPlistFromString(catalogData)
#
# Get available products.
#
products = root['Products']

#
# Loop through the product keys.
#
for key in products:
	if 'ExtendedMetaInfo' in products[key]:
		extendedMetaInfo = products[key]['ExtendedMetaInfo']
		
		if 'InstallAssistantPackageIdentifiers' in extendedMetaInfo:
			IAPackageIDs = extendedMetaInfo['InstallAssistantPackageIdentifiers']
			
			if IAPackageIDs['InstallInfo'] == 'com.apple.plist.InstallInfo' and IAPackageIDs['OSInstall'] == 'com.apple.mpkg.OSInstall':
				#print key
				targetPath = os.path.join(targetVolume, 'tmp', key)
				#print targetPath
				#
				# Check target directory.
				#
				if not os.path.isdir(targetPath):
					os.makedirs(targetPath)
			
				product = products[key]
				packages = product['Packages']
				#
				# Main package loop
				#
				for package in packages:
					url = package.get('URL')
					size = package.get('Size')
					packageName = basename(url)
					filename = os.path.join(targetPath, packageName)
					shouldDownload = False
					#
					# Check if file exists (already downloaded?).
					#
					if os.path.exists(filename):
						#
						# Check filesize (broken download).
						#
						if os.path.getsize(filename) == size:
							print 'File: %s already there, skipping this download.' % packageName
							shouldDownload = False
						else:
							print 'Error: Filesize incorrect, removing %s.' % packageName
							os.remove(filename)
							shouldDownload = True
					else:
						shouldDownload = True
					#
					# Should we download this file?
					#
					if shouldDownload == True:
						print 'Downloading: ' + packageName + ' ...'
						
						req = urllib2.urlopen(url)
						file = open(filename, 'wb')

						while True:
							chunk = req.read(4096)
							if not chunk:
								break
							file.write(chunk)
						file.close()
				#
				#
				#
				distributionFile = downloadDistributionFile(product)
				#
				# Create installer package.
				#
				print 'Creating %s ...' % installerPackage
				installerPkg = os.path.join(targetPath, installerPackage)
				#print installerPkg
				subprocess.call(["sudo", "/usr/bin/productbuild", "--distribution", distributionFile, "--package-path", targetPath, installerPkg])

				#
				# Launch the installer.
				#
				if os.path.exists(installerPkg):
					print 'Running installer ...'
					subprocess.call(["sudo", "/usr/sbin/installer", "-pkg", installerPkg, "-target", targetVolume])
					
				#
				# Do we have a SharedSupport folder?
				#
				# Note: This may fail when you install the package from another volume (giving the installer the wrong mount point).
				#
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
