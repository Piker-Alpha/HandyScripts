#!/bin/sh
#
# Bash script to download macOS High Sierra installation packages from sucatalog.gz and build the installer PKG for it.
#
# version 1.0 - Copyright (c) 2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
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
# You may need VolumeCheck() to return true (and thus skip checks).
#
export OS_INSTALL=1

#
# Target key copied from sucatalog.gz
#
key="091-15725"

#
# tmpDirectory
#
tmpDirectory="/tmp"

#
# Name of target package.
#
installerPackage="installer.pkg"

#
# URL copied from sucatalog.gz
#

url="https://swdist.apple.com/content/downloads/53/35/${key}/rr81nop9bl0ftqu4ulf1vfu92ch5nt6za6/"

#
# Target distribution language.
#
distribution="${key}.English.dist"

#
# Package names copied from sucatalog.gz
#
packages={"BaseSystem.chunklist","OSInstall.mpkg","AppleDiagnostics.chunklist","InstallInfo.plist","AppleDiagnostics.dmg","RecoveryHDMetaDmg.pkg","InstallOSAuto.pkg","InstallESDDmg.chunklist","BaseSystem.dmg","InstallESDDmg.pkm","InstallESDDmg.pkg","InstallOSAuto.pkm","RecoveryHDMetaDmg.pkm"}

if [ ! -d "${tmpDirectory}/${key}" ]
  then
    mkdir "${tmpDirectory}/${key}"
fi

#
# Get distribution file.
#
curl "${url}${distribution}" -o "${tmpDirectory}/${key}/${distribution}"

#
# Get target packages
#
curl "${url}${packages}" -o "${tmpDirectory}/${key}/#1"

#
# Change to working directory (otherwise it will fail to locate the packages).
#
cd "${tmpDirectory}/${key}"

#
# Create installed package.
#
productbuild --distribution "${tmpDirectory}/${key}/${distribution}" --package-path "${key}" "${installerPackage}"

#
# Launch the installer.
#
if [ -e "${tmpDirectory}/${installerPackage}" ]
  then
    open "${tmpDirectory}/${installerPackage}"
fi
