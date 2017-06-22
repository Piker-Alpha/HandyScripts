#!/bin/sh
#
# Bash script to download macOS High Sierra update packages from sucatalog.gz and build the installer.pkg for it.
#
# version 1.2 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#
# 			- Creates a seedEnrollement.plist when missing.
# 			- Volume picker for seedEnrollement.plist added.
# 			- Added sudo to 'open installer.pkg' to remedy authorisation problems.
#

# CatalogURL for Developer Program Members
# https://swscan.apple.com/content/catalogs/others/index-10.13seed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz
#
# CatalogURL for Beta Program Members
# https://swscan.apple.com/content/catalogs/others/index-10.13beta-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz
#
# CatalogURL for Regular Software Updates
# https://swscan.apple.com/content/catalogs/others/index-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz

#
# Tip: In case you run into the ERROR_7E7AEE96CA error then you need to change the ProductVersion and 
# in /System/Library/CoreServices/SystemVersion.plist to 10.13
#

#
# You may need VolumeCheck() to return true (and thus skip checks)
#
export __OS_INSTALL=1

let index=0

#
# Collect available volume names.
#
targetVolumes=($(ls /Volumes | sort))

echo "\nAvailable target volumes:\n"

for volume in "${targetVolumes[@]}"
  do
    echo "[$index] $volume"
    let index++
done

echo ""

#
# Ask to select a target volume.
#
read -p "Select a target volume for the boot file: " volumeNumber

#
# Path to target volume.
#
targetVolume="/Volumes/${targetVolumes[$volumeNumber]}"

#
# Path to enrollment plist.
#
seedEnrollmentPlist="${targetVolume}/Users/Shared/.SeedEnrollment.plist"

#
# Write enrollement plist when missing.
#
if [ ! -e "${seedEnrollmentPlist}" ]
  then
    echo '<?xml version="1.0" encoding="UTF-8"?>'																	>  "${seedEnrollmentPlist}"
    echo '<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'	>> "${seedEnrollmentPlist}"
    echo '<plist version="1.0">'																					>> "${seedEnrollmentPlist}"
    echo '	<dict>'																									>> "${seedEnrollmentPlist}"
    echo '		<key>SeedProgram</key>'																				>> "${seedEnrollmentPlist}"
    echo '		<string>DeveloperSeed</string>'																		>> "${seedEnrollmentPlist}"
    echo '	</dict>'																								>> "${seedEnrollmentPlist}"
    echo '</plist>'																									>> "${seedEnrollmentPlist}"
fi

#
# Target key copied from sucatalog.gz
#
key="091-19061"

#
# tmpDirectory
#
tmpDirectory="/tmp"

#
# Name of target package
#
installerPackage="installer.pkg"

#
# URL copied from sucatalog.gz
#

url="https://swdist.apple.com/content/downloads/45/42/${key}/d6evxbyr9ft25w3ighkmny2phj4sctm0hy/"

#
# Target distribution language
#
distribution="${key}.English.dist"

#
# Package names copied from sucatalog.gz
#
packages={"FirmwareUpdate.pkg","FullBundleUpdate.pkg","EmbeddedOSFirmware.pkg","macOSUpd10.13.pkg","macOSUpd10.13.RecoveryHDUpdate.pkg"}
#
# On a hackintosh we can skip: FirmwareUpdate.pkg and EmbeddedOSFirmware.pkg
# but then you also need to remove them, manually, from the distribution file.
#
#packages={"FullBundleUpdate.pkg","macOSUpd10.13.pkg","macOSUpd10.13.RecoveryHDUpdate.pkg"}

if [ ! -d "${tmpDirectory}/${key}" ]
  then
    mkdir "${tmpDirectory}/${key}"
fi

#
# Get distribution file
#
curl "${url}${distribution}" -o "${tmpDirectory}/${key}/${distribution}"

#
# Change to working directory (otherwise it will fail to locate the packages).
#
cd "${tmpDirectory}/${key}"

#
# Get target packages
#
curl "${url}${packages}" -o "${tmpDirectory}/${key}/#1"

#
# Create installed package
#
productbuild --distribution "${tmpDirectory}/${key}/${distribution}" --package-path "${tmpDirectory}/${key}" "${installerPackage}"

#
# Launch the installer
#
if [ -e "${tmpDirectory}/${key}/${installerPackage}" ]
  then
    sudo open "${tmpDirectory}/${key}/${installerPackage}"
fi
