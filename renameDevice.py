from labjack import ljm

handle = ljm.openS("ANY", "ANY", 470020169)
ljm.eWriteNameString(handle, "DEVICE_NAME_DEFAULT", "AMY")
ljm.close(handle)