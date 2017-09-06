#!/usr/bin/python

#
# Script (makeInstallSeedScript.py) to create a bash script that downloads the latest seed.
#
# Version 1.5 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#          - comments added.
#          - initial refactoring done.
#          - download template file when missing.
#          - internationalisation (i18n) support added (downloads the right dictionary).
#          - indentation and comment errors fixed, superfluous code removed.
#          - graceful exit with instructions to install pip/request module.
#

import os
import sys
import plistlib
import fileinput

try:
	import requests
except ImportError:
	from os.path import isfile
	
	if not isfile("/usr/local/bin/pip"):
		sys.exit("""Run 'sudo easy_install pip' to install the Python Package Manager.""")
	else:
		sys.exit("""Run 'sudo pip install requests' to install a required module.""")

from Foundation import NSLocale

#
# Script version info.
#
scriptVersion=1.5

#
# GitHub branch to pull data from (master or Beta).
#
gitHubBranch="master"

#
# Github download URL.
#
gitHubContentURL="https://raw.githubusercontent.com/Piker-Alpha/HandyScripts"

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
 "el":"el",         #Greek
 "vi":"vi",         #English (U.S. Virgin Islands)
 "ca":"cs",         #Aghem (Cameroon)
 "ar":"ar",         #Arabic
 "cs":"cs",         #Czech
 "id":"id",         #Indonesian
 "ru":"ru",         #Russian
 "no":"no",         #Norwegian
 "tr":"tr",         #Turkish
 "th":"th",         #Thai
 "he":"he",         #Hebrew
 "pt":"pt",         #Portuguese
 "pl":"pl",         #Polish
 "uk":"uk",         #Ukrainian
 "hr":"hr",         #Croatian
 "hu":"hu",         #Hungarian
 "hi":"hi",         #Hindi
 "fi":"fi",         #Finnish
 "da":"da",         #Danish
 "ro":"rp",         #Romanian
 "ko":"ko",         #Korean
 "sv":"sv",         #Swedish
 "sk":"sk",         #Slovak
 "ms":"ms",         #Malay
 "en":"English",    #English
 "ja":"Japanese",   #Japanese
 "nl":"Dutch",      #Dutch
 "fr":"French",     #French
 "it":"Italian",    #Italian
 "de":"German",     #German
 "es":"Spanish",    #Spanish
 "es_419":"es_419", #Latin American Spanish
 "zh_TW":"zh_TW",   #Chinese (Traditional, Taiwan)
 "zh_CN":"zh_CN",   #Chinese (Simplified, China, Hong Kong, Macau and Singapore)
 "pt":"pt",         #Portuguese (Angola, Brazil, Guinea-Bissau and Mozambique)
 "pt_PT":"pt_PT"    #Portuguese (Portugal)
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
	# Special cases for Apple SU.
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
		
		languageSelector = selectLanguage()
		
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
