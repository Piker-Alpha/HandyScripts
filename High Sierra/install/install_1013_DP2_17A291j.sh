#!/bin/sh
#
# Bash script to download macOS High Sierra update packages from sucatalog.gz and build the installer.pkg for it.
#
# version 1.4 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#
# 			- Creates a seedEnrollement.plist when missing.
# 			- Volume picker for seedEnrollement.plist added.
# 			- Added sudo to 'open installer.pkg' to remedy authorisation problems.
# 			- Fix for volume names with a space in it. Thanks to:
# 			- https://pikeralpha.wordpress.com/2017/06/22/script-to-upgrade-macos-high-sierra-dp1-to-dp2/#comment-10216
# 			- Add file checks so that we only download the missing files.
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

#
# Personalization setting.
#
#export __OSIS_ENABLE_SECUREBOOT

let index=0

#
# Change additional shell optional behavior (expand unmatched names to a null string).
#
shopt -s nullglob

#
# Change to Volumes folder.
#
cd /Volumes

#
# Collect available target volume names.
#
targetVolumes=(*)

echo "\nAvailable target volumes:\n"

for volume in "${targetVolumes[@]}"
  do
    echo "[$index] ${volume}"
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
# Write enrollement plist when missing (seed program options: CustomerSeed, DeveloperSeed or PublicSeed).
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
# Target files copied from sucatalog.gz (think CatalogURL).
#
targetFiles={"FirmwareUpdate.pkg","FullBundleUpdate.pkg","EmbeddedOSFirmware.pkg","macOSUpd10.13.pkg","macOSUpd10.13.RecoveryHDUpdate.pkg"}
#
# On a hackintosh we can skip: FirmwareUpdate.pkg and EmbeddedOSFirmware.pkg
# but then you also need to remove them, manually, from the distribution file.
#
#targetFiles={"FullBundleUpdate.pkg","macOSUpd10.13.pkg","macOSUpd10.13.RecoveryHDUpdate.pkg"}

if [ ! -d "${tmpDirectory}/${key}" ]
  then
    mkdir "${tmpDirectory}/${key}"
fi

#
# Get distribution file
#
if [ ! -e "${tmpDirectory}/${key}/${distribution}" ];
  then
    curl "${url}${distribution}" -o "${tmpDirectory}/${key}/${distribution}"
  else
    echo "File: ${distribution} already there, skipping download."
fi

#
# Change to working directory (otherwise it will fail to locate the packages).
#
cd "${tmpDirectory}/${key}"

let index=1

printf "${targetFiles}"

exit 0

for filename in "$(${targetFiles[@]})"
  do
    echo "[$index] $filename"
    let index++
done

exit 0

#
# Get target packages
#
if [ ! -e "${tmpDirectory}/${key}/#1" ];
  then
    curl "${url}${packages}" -o "${tmpDirectory}/${key}/#1"
  else
    echo "File: #1 already there, skipping download."
fi

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
