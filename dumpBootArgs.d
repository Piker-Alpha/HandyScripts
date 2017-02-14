#!/usr/sbin/dtrace -C -s

/*
 * Copyright (c) 2014-2017 Pike R. Alpha
 *
 * Project: dumpBootArgs.sh (used for macosxbootloader project)
 *
 * Updates:
 *          Version 1.09.0 (Mavericks OS X 10.9)
 *          Version 1.10.0 (Yosemite OS X 10.10)
 *          Version 1.11.0 (El Capitan OS X 10.11)
 *          Version 1.12.1 (Sierra MacOS 10.12)
 *
 * Run command: sudo dumpBootArgs.sh
 *
 * Note: Run this script with SIP off/disabled or dtrace protection disabled.
 */

#pragma D option quiet

BEGIN
{
	self->initialized = ((`PE_state).initialized);

	self->video = ((struct PE_Video)(`PE_state).video);

	self->boot_args = ((struct boot_args *)(`PE_state).bootArgs);

	printf("PE_state.initialized................................: 0x%x\n", self->initialized);

	printf("PE_state.bootArgs.Revision..........................: 0x%x\n", self->boot_args->Revision);
	printf("PE_state.bootArgs.Version...........................: 0x%x\n", self->boot_args->Version);
	printf("PE_state.bootArgs.efiMode...........................: 0x%x\n", self->boot_args->efiMode);
	printf("PE_state.bootArgs.debugMode.........................: 0x%x\n", self->boot_args->debugMode);
	printf("PE_state.bootArgs.flags.............................: 0x%x\n", self->boot_args->flags);
	printf("\n");
	printf("PE_state.bootArgs.CommandLine.......................: %s\n", self->boot_args->CommandLine);
	printf("\n");
	printf("PE_state.bootArgs.MemoryMap.........................: 0x%x\n", self->boot_args->MemoryMap);
	printf("PE_state.bootArgs.MemoryMapSize.....................: 0x%x\n", self->boot_args->MemoryMapSize);
	printf("PE_state.bootArgs.MemoryMapDescriptorSize...........: 0x%x\n", self->boot_args->MemoryMapDescriptorSize);
	printf("PE_state.bootArgs.MemoryMapDescriptorVersion........: 0x%x\n", self->boot_args->MemoryMapDescriptorVersion);
	printf("\n");
	printf("PE_state.bootArgs.VideoV1.v_baseAddr................: 0x%x\n", self->boot_args->VideoV1.v_baseAddr);
	printf("PE_state.bootArgs.VideoV1.v_display.................: 0x%x\n", self->boot_args->VideoV1.v_display);
	printf("PE_state.bootArgs.VideoV1.v_rowBytes................: 0x%x\n", self->boot_args->VideoV1.v_rowBytes);
	printf("PE_state.bootArgs.VideoV1.v_width...................: 0x%x\n", self->boot_args->VideoV1.v_width);
	printf("PE_state.bootArgs.VideoV1.v_height..................: 0x%x\n", self->boot_args->VideoV1.v_height);
	printf("PE_state.bootArgs.VideoV1.v_depth...................: 0x%x\n", self->boot_args->VideoV1.v_depth);
	printf("\n");
	printf("PE_state.bootArgs.deviceTreeP.......................: 0x%x\n", self->boot_args->deviceTreeP);
	printf("PE_state.bootArgs.deviceTreeLength..................: 0x%x\n", self->boot_args->deviceTreeLength);
	printf("\n");
	printf("PE_state.bootArgs.kaddr.............................: 0x%x\n", self->boot_args->kaddr);
	printf("PE_state.bootArgs.ksize.............................: 0x%x\n", self->boot_args->ksize);
	printf("\n");
	printf("PE_state.bootArgs.efiRuntimeServicesPageStart.......: 0x%x\n", self->boot_args->efiRuntimeServicesPageStart);
	printf("PE_state.bootArgs.efiRuntimeServicesPageCount.......: 0x%x\n", self->boot_args->efiRuntimeServicesPageCount);
	printf("PE_state.bootArgs.efiRuntimeServicesVirtualPageStart: 0x%x\n", self->boot_args->efiRuntimeServicesVirtualPageStart);
	printf("\n");
	printf("PE_state.bootArgs.efiSystemTable....................: 0x%x\n", self->boot_args->efiSystemTable);
	printf("PE_state.bootArgs.kslide............................: 0x%x\n", self->boot_args->kslide);
	printf("\n");
	printf("PE_state.bootArgs.performanceDataStart..............: 0x%x\n", self->boot_args->performanceDataStart);
	printf("PE_state.bootArgs.performanceDataSize...............: 0x%x\n", self->boot_args->performanceDataSize);
	printf("\n");
	printf("PE_state.bootArgs.keyStoreDataStart.................: 0x%x\n", self->boot_args->keyStoreDataStart);
	printf("PE_state.bootArgs.keyStoreDataSize..................: 0x%x\n", self->boot_args->keyStoreDataSize);
	printf("\n");
	printf("PE_state.bootArgs.bootMemStart......................: 0x%x\n", self->boot_args->bootMemStart);
	printf("PE_state.bootArgs.bootMemSize.......................: 0x%x\n", self->boot_args->bootMemSize);
	printf("\n");
	printf("PE_state.bootArgs.PhysicalMemorySize................: 0x%x\n", self->boot_args->PhysicalMemorySize);
	printf("PE_state.bootArgs.FSBFrequency......................: 0x%x\n", self->boot_args->FSBFrequency);
	printf("\n");
	printf("PE_state.bootArgs.pciConfigSpaceBaseAddress.........: 0x%x\n", self->boot_args->pciConfigSpaceBaseAddress);
	printf("PE_state.bootArgs.pciConfigSpaceStartBusNumber......: 0x%x\n", self->boot_args->pciConfigSpaceStartBusNumber);
	printf("PE_state.bootArgs.pciConfigSpaceEndBusNumber........: 0x%x\n", self->boot_args->pciConfigSpaceEndBusNumber);
	printf("\n");
	printf("PE_state.bootArgs.csrActiveConfig...................: 0x%x\n", self->boot_args->csrActiveConfig);
	printf("PE_state.bootArgs.csrCapabilities...................: 0x%x\n", self->boot_args->csrCapabilities);
	printf("\n");
	printf("PE_state.bootArgs.boot_SMC_plimit...................: 0x%x\n", self->boot_args->boot_SMC_plimit);
	printf("\n");
	printf("PE_state.bootArgs.bootProgressMeterStart............: 0x%x\n", self->boot_args->bootProgressMeterStart);
	printf("PE_state.bootArgs.bootProgressMeterEnd..............: 0x%x\n", self->boot_args->bootProgressMeterEnd);
	printf("\n");
	printf("PE_state.bootArgs.Video.v_display...................: 0x%x\n", self->boot_args->Video.v_display);
	printf("PE_state.bootArgs.Video.v_rowBytes..................: 0x%x\n", self->boot_args->Video.v_rowBytes);
	printf("PE_state.bootArgs.Video.v_width.....................: 0x%x\n", self->boot_args->Video.v_width);
	printf("PE_state.bootArgs.Video.v_height....................: 0x%x\n", self->boot_args->Video.v_height);
	printf("PE_state.bootArgs.Video.v_depth.....................: 0x%x\n", self->boot_args->Video.v_depth);
	printf("PE_state.bootArgs.Video.v_resv[0]...................: 0x%x\n", self->boot_args->Video.v_resv[0]);
	printf("PE_state.bootArgs.Video.v_resv[1]...................: 0x%x\n", self->boot_args->Video.v_resv[1]);
	printf("PE_state.bootArgs.Video.v_resv[2]...................: 0x%x\n", self->boot_args->Video.v_resv[2]);
	printf("PE_state.bootArgs.Video.v_resv[3]...................: 0x%x\n", self->boot_args->Video.v_resv[3]);
	printf("PE_state.bootArgs.Video.v_resv[4]...................: 0x%x\n", self->boot_args->Video.v_resv[4]);
	printf("PE_state.bootArgs.Video.v_resv[5]...................: 0x%x\n", self->boot_args->Video.v_resv[5]);
	printf("PE_state.bootArgs.Video.v_resv[6]...................: 0x%x\n", self->boot_args->Video.v_resv[6]);
	printf("\n");
	printf("PE_state.bootArgs.efiRuntimeServicesVirtualPageStart: 0x%x\n", self->boot_args->efiRuntimeServicesVirtualPageStart);
	printf("\n");
	printf("PE_state.video.v_baseAddr...........................: 0x%x\n", self->video.v_baseAddr);
	printf("PE_state.video.v_rowBytes...........................: 0x%x\n", self->video.v_rowBytes);
	printf("PE_state.video.v_width..............................: 0x%x\n", self->video.v_width);
	printf("PE_state.video.v_height.............................: 0x%x\n", self->video.v_height);
	printf("PE_state.video.v_depth..............................: 0x%x\n", self->video.v_depth);
	printf("PE_state.video.v_display............................: 0x%x\n", self->video.v_display);
	printf("PE_state.video.v_pixelFormat........................: %x\n", self->video.v_pixelFormat[1]);
	printf("PE_state.video.v_offset.............................: 0x%x\n", self->video.v_offset);
	printf("PE_state.video.v_length.............................: 0x%x\n", self->video.v_length);
	printf("PE_state.video.v_rotate.............................: 0x%x\n", self->video.v_rotate);
	printf("PE_state.video.v_scale..............................: 0x%x\n", self->video.v_scale);

	exit(0);
}
