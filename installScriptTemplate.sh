#!/bin/sh
#
# Bash script to download macOS High Sierra installation packages from sucatalog.gz and build the installer.pkg for it.
#
# version 2.1 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#
# 			- Creates a seedEnrollement.plist when missing.
# 			- Volume picker for seedEnrollement.plist added.
# 			- Added sudo to 'open installer.pkg' to remedy authorisation problems.
# 			- Fix for volume names with a space in it. Thanks to:
# 			- https://pikeralpha.wordpress.com/2017/06/22/script-to-upgrade-macos-high-sierra-dp1-to-dp2/#comment-10216)
# 			- Add file checks so that we only download the missing files.
# 			- Polished up comments.
# 			- Changed key, salt, target files and version (now v1.5).
# 			- Now calling the installer.app with -pkg -target instead of open to prevent failures.
# 			- Fixed path to distribution file.
# 			- Checks for missing files added.
# 			- Updated version number (now v1.6).
# 			- Removing unused (initialisation of a) variable.
# 			- Improved verbose output.
# 			- Updated version number (now v1.7).
# 			- Fix installer breakage.
# 			- Updated version number (now v1.8).
# 			- Opt out for firmware added.
# 			- Changed version number (now v1.9).
# 			- Opt in/out for APFS conversion added.
# 			- Changed version number (now v2.0).
# 			- Variables 'version' and 'salt' added.
# 			- Checks for newly added variables added.
# 			- Changed version number (now v2.1).
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
#  CatalogURL for Customer Seed Updates
# https://swscan.apple.com/content/catalogs/others/index-10.13customerseed-10.13-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz

#
# Tip: In case you run into the ERROR_7E7AEE96CA error then you need to change the ProductVersion and 
# in /System/Library/CoreServices/SystemVersion.plist to 10.13
#

#
# You may need VolumeCheck() to return true (and thus skip checks)
#
export __OS_INSTALL=1

#
# Skip firmware update (OSInstaller).
#
export __FIRMWARE_UPDATE_OPTOUT

#
# Do not convert target HFS volume to APFS (OSInstaller).
#
export __APFS_OPTOUT=1

#
# Convert target HFS volume to APFS (OSInstaller).
#
# Note: This appears to be the default now.
#
#export __APFS_OPTIN=1

#
# Personalization setting.
#
#export __OSIS_ENABLE_SECUREBOOT

#
# Initialisation of a variable.
#
let index=0

#
# Target key copied from sucatalog.gz (think CatalogURL).
#
key="*"

#
# ID copied from product URL.
#
version="*"

#
# Salt from product URL.
#
salt="*"

if [[ $key == "*" || $version == "*" || $salt == "*" ]];
  then
    echo 'Error: variables unitialised, please run makeInstallSeedScript.py'
    exit -1
fi

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
# Path to enrollment plist for 10.9.
#
if [ $(/usr/bin/sw_vers -productVersion | /usr/bin/cut -d '.' -f 1,2) == "10.9" ];
  then
    seedEnrollmentPlist="$3/Library/Application Support/App Store/.SeedEnrollment.plist"
fi

#
# Write enrollement plist when missing (seed program options: CustomerSeed, DeveloperSeed or PublicSeed).
#
if [ ! -e "${seedEnrollmentPlist}" ]
  then
    echo "Writing: .SeedEnrollment.plist ..."
    echo '<?xml version="1.0" encoding="UTF-8"?>'																	>  "${seedEnrollmentPlist}"
    echo '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">'	>> "${seedEnrollmentPlist}"
    echo '<plist version="1.0">'																					>> "${seedEnrollmentPlist}"
    echo '	<dict>'																									>> "${seedEnrollmentPlist}"
    echo '		<key>SeedProgram</key>'																				>> "${seedEnrollmentPlist}"
    echo '		<string>DeveloperSeed</string>'																		>> "${seedEnrollmentPlist}"
    echo '	</dict>'																								>> "${seedEnrollmentPlist}"
    echo '</plist>'																									>> "${seedEnrollmentPlist}"
fi

#
# Initialisation of a variable (our target folder).
#
tmpDirectory="/tmp"

#
# Name of target installer package.
#
installerPackage="installer.pkg"

#
# URL copied from sucatalog.gz (think CatalogURL).
#
url="https://swdist.apple.com/content/downloads/${version}/${key}/${salt}/"

#
# Target distribution language.
#
distribution="${key}.English.dist"

#
# Target files copied from sucatalog.gz (think CatalogURL).
#
targetFiles=(
AppleDiagnostics.dmg
AppleDiagnostics.chunklist
BaseSystem.dmg
BaseSystem.chunklist
InstallESDDmg.pkg
InstallESDDmg.chunklist
InstallAssistantAuto.pkg
RecoveryHDMetaDmg.pkg
InstallInfo.plist
OSInstall.mpkg
)

#
# Check target directory.
#
if [ ! -d "${tmpDirectory}/${key}" ]
  then
    mkdir "${tmpDirectory}/${key}"
fi

#
# Download distribution file.
#
if [ ! -e "${tmpDirectory}/${key}/${distribution}" ];
  then
    echo "Downloading: ${distribution} ..."
    curl "${url}${distribution}" -o "${tmpDirectory}/${key}/${distribution}"
    #
    # Remove root only restriction/allow us to install on any target volume.
    #
    cat "${tmpDirectory}/${key}/${distribution}" | sed -e 's|rootVolumeOnly="true"|allow-external-scripts="true"|' > "${tmpDirectory}/${key}/new.dist"

    if [ -e "${tmpDirectory}/${key}/new.dist" ]
      then
        mv "${tmpDirectory}/${key}/new.dist" "${tmpDirectory}/${key}/${distribution}"
    fi
  else
    echo "File: ${distribution} already there, skipping this download."
fi

#
# Change to working directory (otherwise it will fail to locate the packages).
#
cd "${tmpDirectory}/${key}"

#
# Download target files.
#
for filename in "${targetFiles[@]}"
  do
    if [ ! -e "${tmpDirectory}/${key}/${filename}" ];
      then
        echo "Downloading: ${filename} ..."
        curl "${url}${filename}" -o "${tmpDirectory}/${key}/${filename}"
      else
        echo "File: ${filename} already there, skipping this download."
    fi
  done

#
# Create installer package.
#
echo "Creating installer.pkg ..."
productbuild --distribution "${tmpDirectory}/${key}/${distribution}" --package-path "${tmpDirectory}/${key}" "${installerPackage}"

#
# Launch the installer.
#
if [ -e "${tmpDirectory}/${key}/${installerPackage}" ]
  then
    echo "Running installer ..."
    sudo /usr/sbin/installer -pkg "${tmpDirectory}/${key}/${installerPackage}" -target "${targetVolume}"
fi

#
# Do we have a SharedSupport folder?
#
# Note: This may fail when you install the package from another volume (giving the installer the wrong mount point).
#
if [ -d "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport" ]
  then
    #
    # Yes we do, but did copy_dmg (a script inside RecoveryHDMetaDmg.pkg) copy the files that Install macOS 10.13 Beta.app needs?
    #
    if [ ! -e "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/AppleDiagnostics.dmg" ]
      then
        #
        # Without this step we end up with installer.pkg as InstallDMG.dmg and InstallInfo.plist
        #
        echo "Copying: InstallESDDmg.pkg to the target location ..."
        sudo cp "${tmpDirectory}/${key}/InstallESDDmg.pkg" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/InstallESD.dmg"
        #
        # Without this step we end up without AppleDiagnostics.[dmg/chunklist].
        #
        echo "Copying: AppleDiagnostics.dmg to the target location ..."
        sudo cp "${tmpDirectory}/${key}/AppleDiagnostics.dmg" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
        echo "Copying: AppleDiagnostics.chunklist to the target location ..."
        sudo cp "${tmpDirectory}/${key}/AppleDiagnostics.chunklist" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
        #
        # Without this step we end up without BaseSystem.[dmg/chunklist].
        #
        echo "Copying: BaseSystem.dmg to the target location ..."
        sudo cp "${tmpDirectory}/${key}/BaseSystem.dmg" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
        echo "Copying: BaseSystem.chunklist to the target location ..."
        sudo cp "${tmpDirectory}/${key}/BaseSystem.chunklist" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
    fi
fi
