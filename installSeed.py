#!/usr/bin/python

#
# Script (installSeed.py) to get the latest seed package.
#
# Version 1.7 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#          - comments added
#          - target directory check added (Pike R. Alpha, August 2017)
#          - filesize check added
#          - renamed script
#          - don't try to remove the .dist file if it isn't there.
#          - copy InstallESDDmg.pkg to /Applications/Install macOS High Sierra Beta.app/Content/SharedSupport/InstallESD.dmg
#          - set environment variable.
#          - use sudo and path for productbuild.
#

import os
import glob
import plistlib
import requests
import subprocess

from os.path import basename

os.environ['__OS_INSTALL'] = "1"

#
#
#
languageSelector = 'English'

#
# Setup seed program data.
#
seedProgramData = {
 "DeveloperSeed":"index-10.13seed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "PublicSeed":"index-10.13beta-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog",
 "CustomerSeed":"index-10.13customerseed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog"
}

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
catalogRaw = requests.get(catalogURL, headers='')
catalogData = catalogRaw.text.encode('UTF-8')

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
						
						request = requests.get(url, stream=True, headers='')
						file = open(filename, 'wb')

						for chunk in request.iter_content(4096):
							file.write(chunk)
						file.close()
				#
				#
				#
				if 'Distributions' in product:
					distributions = product['Distributions']
					
					if distributions[languageSelector]:
						distributionURL = distributions.get(languageSelector)
						#print distributionURL
						request = requests.get(distributionURL, stream=True, headers='')
						distributionID = key + '.' + languageSelector + '.dist'
						distributionFile = os.path.join(targetPath, distributionID)
						#print distributionFile
						
						if os.path.exists(distributionFile):
							os.remove(distributionFile)
						
						file = open(distributionFile, 'w')
						
						for chunk in request.iter_content(1024):
							file.write(chunk)
						file.close()
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
