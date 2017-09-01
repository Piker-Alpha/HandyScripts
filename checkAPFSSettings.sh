#!/bin/sh
#
# Bash script to check APFS conversion settings in macOS Install Data.
#
# version 1.5 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
# 			- Add comments.
# 			- Automatic target volume selection.
# 			- Check for PlistBuddy added (triggers xcode-select --install).
# 			- Fix targetFile(s).
# 			- Show targetVolume(s).
#
# Note:		run with 'sudo' or changes won't be made!

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
# Default target volume is root.
#
targetVolume="/"

#
# Collect available target volume names.
#
targetVolumes=(*)

#
# Loop through volumes.
#
for volume in "${targetVolumes[@]}"
  do
    #
    # Is there a macOS Install Data folder?
    #
    if [ -e "/Volumes/${targetVolumes[$index]}/macOS Install Data" ];
      then
        #
        # Yes. Use it as our target volume (there should only be one).
        #
        targetVolume="/Volumes/${volume}"
        printf "Target Volume: ${targetVolume}\n" 
        #
        # Done.
        #
        break
      fi
      #
      #
      #
      let index++
done

#
# Setup target path.
#
filePath="${targetVolume}/macOS Install Data"

#
# Path to PlistBuddy.
#
plistBuddy="/usr/libexec/PlistBuddy"

#
# Check for PlistBuddy (part of developer tools).
#
if [ ! -e "${plistBuddy}" ];
  then
    #
    # Install developer tools.
    #
    xcode-select --install
fi

#
# First target file to check.
#
targetFile="${targetVolume}/macOS Install Data/minstallconfig.xml"

#
# Check if file exists.
#
if [ -e "${targetFile}" ];
  then
    if [ $("${plistBuddy}" -c "Print:ConvertToAPFS" "${targetFile}") == "true" ];
      then
        echo 'ConvertToAPFS = true'
      else
        echo 'ConvertToAPFS = false'
    fi
fi

#
# Second target file to check.
#
targetFile="${targetVolume}/macOS Install Data/OSInstallAttr.plist"

#
# Check if file exists.
#
if [ -e "${targetFile}" ];
  then
    if [ $("${plistBuddy}" -c "Print:Do\ APFS\ Convert"  "${targetFile}") == "true" ];
      then
        echo 'Do APFS Convert = true'
      else
        echo 'Do APFS Convert = false'
    fi
fi

#
# Third target file to check.
#
targetFile="${targetVolume}/macOS Install Data/Locked Files/minstallconfig.xml"

#
# Check if file exists.
#
if [ -e "${targetFile}" ];
  then
    if [ $("${plistBuddy}" -c "Print:ConvertToAPFS" "${targetFile}") == "true" ];
      then
        echo 'ConvertToAPFS = true'
        "${plistBuddy}" -c "Set :ConvertToAPFS 0" "${targetFile}"
      else
        echo 'ConvertToAPFS = false'
    fi
fi

#
# Fourth and last target file to check.
#
targetFile="${targetVolume}/macOS Install Data/Locked Files/OSInstallAttr.plist"

#
# Check if file exists.
#
if [ -e "${targetFile}" ];
  then
    if [ $("${plistBuddy}" -c "Print :Do\ APFS\ Convert" "${targetFile}") == "true" ];
      then
        echo 'Do APFS Convert = true'
        "${plistBuddy}" -c "Set :Do\ APFS\ Convert 0" "${targetFile}"
      else
        echo 'Do APFS Convert = false'
    fi
fi
