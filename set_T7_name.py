from labjack import ljm

# Open first found LabJack
handle = ljm.openS("T7", "ANY", "470019440")

info = ljm.getHandleInfo(handle)
print("Opened a LabJack with Device type: %i, Connection type: %i,\n"
      "Serial number: %i, IP address: %s, Port: %i,\nMax bytes per MB: %i" %
      (info[0], info[1], info[2], ljm.numberToIP(info[3]), info[4], info[5]))

# Call eWriteNameString to set the name string on the LabJack.
string = "SAM"
ljm.eWriteNameString(handle, "DEVICE_NAME_DEFAULT", string)

print("\nSet device name : %s" % string)

# Close handle
ljm.close(handle)