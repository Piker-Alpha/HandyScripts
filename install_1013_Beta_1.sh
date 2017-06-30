#!/bin/sh
#
# Bash script to download macOS High Sierra installation packages from sucatalog.gz and build the installer PKG for it.
#
# Version 1.6 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
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
# 			- Checks added to see if copy_dmg (a script inside RecoveryHDMetaDmg.pkg) completed.
# 			- Now calling the installer.app with -pkg -target instead of open to prevent failures.
# 			- Fixed path to distribution file.
# 			- Checks for missing files added.
# 			- Updated version number (now v1.6).
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
# Skip VolumeCheck() and SeedProgram3() for High Sierra.
#
export __OSINSTALL_ENVIRONMENT=1

#
# Personalization setting.
#
#export __OSIS_ENABLE_SECUREBOOT

#
# Initialisation of a variable.
#
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
#
#
#sudo chmod 777 "${targetVolume}/.PKInstallSandboxManager"

#
# Target key copied from sucatalog.gz (think CatalogURL).
#
key="091-21165"

#
# Initialisation of a variable (our target folder).
#
tmpDirectory="/tmp"

#
# Name of target installer package.
#
installerPackage="installer.pkg"

#
# URL copied from sucatalog.gz
#
url="https://swdist.apple.com/content/downloads/12/09/${key}/vumiq9mhdyn2lr8lg1oc1w2n8wxoinwjsh/"

#
# Target distribution language.
#
distribution="${key}.English.dist"

#
# Target files copied from sucatalog.gz (think CatalogURL).
#
targetFiles=(
RecoveryHDMetaDmg.pkg
BaseSystem.dmg
BaseSystem.chunklist
InstallESDDmg.pkg
InstallESDDmg.chunklist
AppleDiagnostics.dmg
AppleDiagnostics.chunklist
InstallInfo.plist
OSInstall.mpkg
InstallAssistantAuto.pkg
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
    echo "File: ${distribution} already there, skipping download."
fi

#
# Change to working directory (otherwise it will fail to locate the packages).
#
cd "${tmpDirectory}/${key}"

#
# Reset index variable.
#
let index=0

#
# Download target files.
#
for filename in "${targetFiles[@]}"
  do
    if [ ! -e "${tmpDirectory}/${key}/${filename}" ];
      then
        curl "${url}${filename}" -o "${tmpDirectory}/${key}/${filename}"
      else
        echo "File: ${filename} already there, skipping download."
    fi

    let index++
  done

#
# OSX_10_13_IncompatibleAppList.pkg
#
key2="091-05077"

#
#
#
url="http://swcdn.apple.com/content/downloads/62/30/${key2}/8243xxpqrcv69hakbdhxdlw1iiffa9yi18/"

#
#
#
filename="OSX_10_13_IncompatibleAppList.pkg"

#
#
#
if [ ! -e "${tmpDirectory}/${key}/${filename}" ];
  then
    curl "${url}${filename}" -o "${tmpDirectory}/${key}/${filename}"
  else
    echo "File: ${filename} already there, skipping download."
fi

#
# GatekeeperConfigData.pkg
#
key2="091-20697"

#
#
#
url="http://swcdn.apple.com/content/downloads/06/57/${key2}/dizlysxx81f4bc5v5jceelvzf8yu0yeh3l/"

#
#
#
filename="GatekeeperConfigData.pkg"

#
#
#
if [ ! -e "${tmpDirectory}/${key}/${filename}" ];
  then
    curl "${url}${filename}" -o "${tmpDirectory}/${key}/${filename}"
  else
    echo "File: ${filename} already there, skipping download."
fi

#
# Create installer package.
#
productbuild --distribution "${tmpDirectory}/${key}/${distribution}" --package-path "${tmpDirectory}/${key}" "${installerPackage}"

#
# Launch the installer.
#
if [ -e "${tmpDirectory}/${key}/${installerPackage}" ]
  then
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
        # Without this we might have end up with only InstallDMG.dmg and InstallInfo.plist
        #
        sudo cp "${tmpDirectory}/${key}/AppleDiagnostics.dmg" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
        sudo cp "${tmpDirectory}/${key}/AppleDiagnostics.chunklist" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
        sudo cp "${tmpDirectory}/${key}/BaseSystem.dmg" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
        sudo cp "${tmpDirectory}/${key}/BaseSystem.chunklist" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
    fi
    #
    # Is OSInstall.mpkg copied from "/tmp/${key}"?
    #
    if [ ! -e "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/OSInstall.mpkg" ]
      then
        #
        # No. Copy it (or you end up with a broken installer).
        #
        sudo cp "${tmpDirectory}/${key}/OSInstall.mpkg" "${targetVolume}/Applications/Install macOS High Sierra Beta.app/Contents/SharedSupport/"
    fi
fi

#
# Restore file.
#
#sudo chmod 755 "${targetVolume}/.PKInstallSandboxManager"
