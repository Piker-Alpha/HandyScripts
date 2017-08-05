#!/usr/bin/python

#
# Script (globResourceFiles.py) to get a list with boardID's and matching modelID from resource files.
#
# Version 1.1 - Copyright (c) 2016-2017 by Pike R. Alpha (PikeRAlpha@yahoo.com)
#
# Updates:
#          - improved output (Pike R. Alpha, August 2017)
#

import os
import glob
import objc

from os.path import basename
from os.path import splitext

class attrdict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

resourceFiles = glob.glob("/System/Library/Extensions/IOPlatformPluginFamily.kext/Contents/PlugIns/X86PlatformPlugin.kext/Contents/Resources/*.plist")

ServerInformation = attrdict()
ServerInformation_bundle = objc.loadBundle('ServerInformation', ServerInformation, bundle_path='/System/Library/PrivateFrameworks/ServerInformation.framework')

print('-------------------------------------\n%i Resource files (plists) found\n-------------------------------------' % len(resourceFiles))

unknownBoardIDs = []

for resourceFile in resourceFiles:
    boardID = splitext(basename(resourceFile))[0]

    for modelID in ServerInformation.ServerInformationComputerModelInfo.modelPropertiesForBoardIDs_([boardID]):
        if boardID not in modelID:
            print('%s - %s' % (boardID, modelID))
        else:
            unknownBoardIDs.append(boardID)

if len(unknownBoardIDs):
    print('---------------------------------------')
    for boardID in unknownBoardIDs:
        print('-- No match for %s --' % boardID)
    print('---------------------------------------\n')
