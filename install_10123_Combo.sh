#!/bin/sh
#
# Bash script to download macOS Sierra update packages from sucatalog.gz and build the installer PKG for it.
#
# version 1.1 - Copyright (c) 2016 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#

# CatalogURL for Developer Program Members
# https://swscan.apple.com/content/catalogs/others/index-10.12seed-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz
#
# CatalogURL for Beta Program Members
# https://swscan.apple.com/content/catalogs/others/index-10.12beta-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz
#
# CatalogURL for Regular Software Updates
# https://swscan.apple.com/content/catalogs/others/index-10.12-10.11-10.10-10.9-mountainlion-lion-snowleopard-leopard.merged-1.sucatalog.gz

#
# You may need VolumeCheck() to return true (and thus skip checks)
#
export OS_INSTALL=1

#
# Target key copied from sucatalog.gz
#
key="031-91606"

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

url="https://swdist.apple.com/content/downloads/59/13/${key}/drgqi6q29vcha66ymyrabpkwcsait0fn9p/"

#
# Target distribution language
#
distribution="${key}.English.dist"

#
# Package names copied from sucatalog.gz
#
packages={"FirmwareUpdate.pkg","FullBundleUpdate.pkg","EmbeddedOSFirmware.pkg","macOSUpdCombo10.12.3DeveloperBeta.pkg"}

if [ ! -d "${tmpDirectory}/${key}" ]
  then
    mkdir "${tmpDirectory}/${key}"
fi

#
# Get distribution file
#
curl "${url}${distribution}" -o "${tmpDirectory}/${key}/${distribution}"

#
# Get target packages
#
curl "${url}${packages}" -o "${tmpDirectory}/${key}/#1"

#
# Create installed package
#
productbuild --distribution "${tmpDirectory}/${key}/${distribution}" --package-path "${key}" "${installerPackage}"

#
# Launch the installer
#
if [ -e "${tmpDirectory}/${installerPackage}" ]
  then
    open "${tmpDirectory}/${installerPackage}"
fi
