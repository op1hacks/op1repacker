# OP-1 Firmware Repacker

Tool for unpacking and repacking OP1 firmware. *This is a work in progress!*

 - Requires Python3
 - Tested on Linux

## Disclaimer

*Don't use this unless you know exactly what you are doing!*
I take no responsibility whatsoever for any damage that might result from using this software.
You will void your OP-1 waranty and in the worst case brick it using custom firmware.
Everything you do with this is at your own risk!

## Usage

### Unpack & Repack

    python3 main.py unpack [filename]... # Unpack an OP-1 firmware file.
    python3 main.py repack [directory]   # Repack a directory containing unpacked firmware.

### Add & Remove Checksum

Warning: These commands don't check if the checksum already exists.
The first 4 bytes are just removed by 'remove_checksum' and a new checksum is added by 'add_checksum' even if it already exists.

    python3 main.py add_checksum [filename]... # Unpack an OP-1 firmware file.
    python3 main.py remove_checksum [directory]   # Repack a directory containing unpacked firmware.


