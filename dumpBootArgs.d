#!/usr/sbin/dtrace -C -s

/*
 * Copyright (c) 2014-2017 Pike R. Alpha
 *
 * Project: dumpBootArgs.sh (used for macosxbootloader project)
 *
 * Updates:
 *          Version 1.09 (Mavericks OS X 10.9)
 *          Version 1.10 (Yosemite OS X 10.10)
 *          Version 1.11 (El Capitan OS X 10.11)
 *          Version 1.12 (Sierra MacOS 10.12)
 *
 * Run command: sudo dumpBootArgs.sh
 *
 * Note: Run this script with SIP off/disabled or dtrace protection disabled.
 */

#pragma D option quiet

BEGIN
{
	self->boot_args = ((struct boot_args *)(`PE_state).bootArgs);

	printf("Revision..........................: 0x%x\n", self->boot_args->Revision);
	printf("Version...........................: 0x%x\n", self->boot_args->Version);
	printf("efiMode...........................: 0x%x\n", self->boot_args->efiMode);
	printf("debugMode.........................: 0x%x\n", self->boot_args->debugMode);
	printf("flags.............................: 0x%x\n", self->boot_args->flags);

	printf("CommandLine.......................: %s\n", self->boot_args->CommandLine);

	printf("MemoryMap.........................: 0x%x\n", self->boot_args->MemoryMap);
	printf("MemoryMapSize.....................: 0x%x\n", self->boot_args->MemoryMapSize);
	printf("MemoryMapDescriptorSize...........: 0x%x\n", self->boot_args->MemoryMapDescriptorSize);
	printf("MemoryMapDescriptorVersion........: 0x%x\n", self->boot_args->MemoryMapDescriptorVersion);

	printf("VideoV1.v_baseAddr................: 0x%x\n", self->boot_args->VideoV1.v_baseAddr);
	printf("VideoV1.v_display.................: 0x%x\n", self->boot_args->VideoV1.v_display);
	printf("VideoV1.v_rowBytes................: 0x%x\n", self->boot_args->VideoV1.v_rowBytes);
	printf("VideoV1.v_width...................: 0x%x\n", self->boot_args->VideoV1.v_width);
	printf("VideoV1.v_height..................: 0x%x\n", self->boot_args->VideoV1.v_height);
	printf("VideoV1.v_depth...................: 0x%x\n", self->boot_args->VideoV1.v_depth);

	printf("deviceTreeP.......................: 0x%x\n", self->boot_args->deviceTreeP);
	printf("deviceTreeLength..................: 0x%x\n", self->boot_args->deviceTreeLength);

	printf("kaddr.............................: 0x%x\n", self->boot_args->kaddr);
	printf("ksize.............................: 0x%x\n", self->boot_args->ksize);

	printf("efiRuntimeServicesPageStart.......: 0x%x\n", self->boot_args->efiRuntimeServicesPageStart);
	printf("efiRuntimeServicesPageCount.......: 0x%x\n", self->boot_args->efiRuntimeServicesPageCount);
	printf("efiRuntimeServicesVirtualPageStart: 0x%x\n", self->boot_args->efiRuntimeServicesVirtualPageStart);

	printf("efiSystemTable....................: 0x%x\n", self->boot_args->efiSystemTable);
	printf("kslide............................: 0x%x\n", self->boot_args->kslide);

	printf("performanceDataStart..............: 0x%x\n", self->boot_args->performanceDataStart);
	printf("performanceDataSize...............: 0x%x\n", self->boot_args->performanceDataSize);

	printf("keyStoreDataStart.................: 0x%x\n", self->boot_args->keyStoreDataStart);
	printf("keyStoreDataSize..................: 0x%x\n", self->boot_args->keyStoreDataSize);

	printf("bootMemStart......................: 0x%x\n", self->boot_args->bootMemStart);
	printf("bootMemSize.......................: 0x%x\n", self->boot_args->bootMemSize);

	printf("PhysicalMemorySize................: 0x%x\n", self->boot_args->PhysicalMemorySize);
	printf("FSBFrequency......................: 0x%x\n", self->boot_args->FSBFrequency);

	printf("pciConfigSpaceBaseAddress.........: 0x%x\n", self->boot_args->pciConfigSpaceBaseAddress);
	printf("pciConfigSpaceStartBusNumber......: 0x%x\n", self->boot_args->pciConfigSpaceStartBusNumber);
	printf("pciConfigSpaceEndBusNumber........: 0x%x\n", self->boot_args->pciConfigSpaceEndBusNumber);

	printf("csrActiveConfig...................: 0x%x\n", self->boot_args->csrActiveConfig);
	printf("csrCapabilities...................: 0x%x\n", self->boot_args->csrCapabilities);

	printf("boot_SMC_plimit...................: 0x%x\n", self->boot_args->boot_SMC_plimit);

	printf("bootProgressMeterStart............: 0x%x\n", self->boot_args->bootProgressMeterStart);
	printf("bootProgressMeterEnd..............: 0x%x\n", self->boot_args->bootProgressMeterEnd);

	printf("Video.v_display...................: 0x%x\n", self->boot_args->Video.v_display);
	printf("Video.v_rowBytes..................: 0x%x\n", self->boot_args->Video.v_rowBytes);
	printf("Video.v_width.....................: 0x%x\n", self->boot_args->Video.v_width);
	printf("Video.v_height....................: 0x%x\n", self->boot_args->Video.v_height);
	printf("Video.v_depth.....................: 0x%x\n", self->boot_args->Video.v_depth);
	printf("Video.v_resv[0]...................: 0x%x\n", self->boot_args->Video.v_resv[0]);
	printf("Video.v_resv[1]...................: 0x%x\n", self->boot_args->Video.v_resv[1]);
	printf("Video.v_resv[2]...................: 0x%x\n", self->boot_args->Video.v_resv[2]);
	printf("Video.v_resv[3]...................: 0x%x\n", self->boot_args->Video.v_resv[3]);
	printf("Video.v_resv[4]...................: 0x%x\n", self->boot_args->Video.v_resv[4]);
	printf("Video.v_resv[5]...................: 0x%x\n", self->boot_args->Video.v_resv[5]);
	printf("Video.v_resv[6]...................: 0x%x\n", self->boot_args->Video.v_resv[6]);

	printf("efiRuntimeServicesVirtualPageStart: 0x%x\n", self->boot_args->efiRuntimeServicesVirtualPageStart);
	exit(0);
}
