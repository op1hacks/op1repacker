# OP-1 Firmware Repacker

Tool for unpacking and repacking OP1 firmware. *This is a work in progress!*

 - Requires Python3
 - Tested on Linux and OS X

## Disclaimer

**Don't use this unless you know exactly what you are doing!**
I take no responsibility whatsoever for any damage that might result from using this software.
You will void your OP-1 waranty and in the worst case brick it using custom firmware.
Everything you do with this is at your own risk!


## Usage

### Unpack & Repack

    python3 main.py unpack [filename]   # Unpack an OP-1 firmware file.
    python3 main.py repack [directory]  # Repack a directory containing unpacked firmware.

The firmware is unpacked to a new folder in the same location as the firmware file is.
If you unpack the firmware file 'op1_218.op1' at '/home/user/op1/' you'll get a folder '/home/user/op1/op1_218/' containing the unpacked files.
The same logic works for repacking, the new firmware file is saved in the same location, but the name will be 'op1_218-repacked.op1'.
