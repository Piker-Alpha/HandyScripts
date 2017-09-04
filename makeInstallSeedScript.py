#!/usr/bin/python

#
# Script (makeInstallSeedScript.py) to create a bash script that downloads the latest seed.
#
# Version 1.2 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#          - comments added.
#          - initial refactoring done.
#          - download template file when missing.
#

import os
import plistlib
import requests
import fileinput

#
# Script version info.
#
scriptVersion=1.2

#
# GitHub branch to pull data from (master or Beta).
#
gitHubBranch="master"

#
# Github download URL.
#
gitHubContentURL="https://raw.githubusercontent.com/Piker-Alpha/HandyScripts"

#
# We should show a list with supported languages.
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

def downloadTemplate(fileName):
	global gitHubContentURL
	global gitHubBranch
	gitHubContentURL = os.path.join(gitHubContentURL, gitHubBranch)
	templateURL = os.path.join(gitHubContentURL, fileName)
	request = requests.get(templateURL, stream=True, headers='')
	file = open(fileName, 'w')
	
	for chunk in request.iter_content(1024):
		file.write(chunk)
	file.close()

def downloadDistributionFile(product):
	if 'Distributions' in product:
		distributions = product['Distributions']
		
		if distributions[languageSelector]:
			distributionURL = distributions.get(languageSelector)
			request = requests.get(distributionURL, stream=True, headers='')
			distributionFile = os.path.join("/tmp", "distribution.xml")
			file = open(distributionFile, 'w')
			
			for chunk in request.iter_content(4096):
				file.write(chunk)
			file.close()

			return distributionURL

def getBuildID():
	import xml.etree.ElementTree as ET
	tree = ET.parse("/tmp/distribution.xml")
	root = tree.getroot()
	
	auxinfoKeys = root.findall("auxinfo/key")
	auxinfoStrings = root.findall("auxinfo/string")
	
	if auxinfoKeys is not None and auxinfoStrings is not None:
		if auxinfoKeys[0].text == 'BUILD':
			buildID = auxinfoStrings[0].text
		if auxinfoKeys[1].text == 'BUILD':
			buildID = auxinfoStrings[1].text
	
		return buildID

def writeScript(key, url):
	url_parts = url.split('/')
	version = url_parts[5] + '/' + url_parts[6]
	salt = url_parts[8]
	buildID = getBuildID()
	scriptName = "installSeed-" + buildID + ".sh"
	templateFileName = "installScriptTemplate.sh"
	
	if not os.path.exists(templateFileName):
		downloadTemplate(templateFileName)

	with open(templateFileName, "r") as file:
		filedata = file.read()
		filedata = filedata.replace("key=\"*\"", "key=\"" + key + "\"")
		filedata = filedata.replace("version=\"*\"", "version=\"" + version + "\"")
		filedata = filedata.replace("salt=\"*\"", "salt=\"" + salt + "\"")
		
		with open(scriptName, 'w') as file:
			file.write(filedata)

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
# Loop through the product available keys.
#
for key in products:
	if 'ExtendedMetaInfo' in products[key]:
		extendedMetaInfo = products[key]['ExtendedMetaInfo']
		
		if 'InstallAssistantPackageIdentifiers' in extendedMetaInfo:
			IAPackageIDs = extendedMetaInfo['InstallAssistantPackageIdentifiers']
			
			if IAPackageIDs['InstallInfo'] == 'com.apple.plist.InstallInfo' and IAPackageIDs['OSInstall'] == 'com.apple.mpkg.OSInstall':
				product = products[key]
				distributionURL = downloadDistributionFile(product)
				writeScript(key, distributionURL)
				break
