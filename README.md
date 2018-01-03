# OP-1 Firmware Repacker

The tool for unpacking and repacking OP1 firmware. This allows you to access and
modify the files within the firmware as well as repackaging the files into a
valid installable firmware file. The tool also includes some mods that can
be automatically applied. Currently three mods are available: `iter`, `filter`
and `subtle-fx`. See below for more information.

 - Requires Python3
 - Tested on Linux, OS X and Windows 10


## Disclaimer

**Don't use this unless you know exactly what you are doing!**
I take no responsibility whatsoever for any damage that might result from using
this software. You will void your OP-1 waranty and in the worst case brick it
using custom firmware. Everything you do with this is at your own risk!


## Installation

To install op1repacker run the following command:

    sudo pip3 install op1repacker


## Usage

### Unpack & Repack

    op1repacker unpack [filename]   # Unpack an OP-1 firmware file.
    op1repacker repack [directory]  # Repack a directory containing unpacked firmware.

The firmware is unpacked to a new folder in the same location as the firmware
file is. If you unpack the firmware file `op1_218.op1` at `/home/user/op1/`
you'll get a folder `/home/user/op1/op1_218/` containing the unpacked files.
The same logic works for repacking, the new firmware file is saved in the same
location, but the name will be `op1_218-repacked.op1`.


### Modify

The firmware can be automatically modified with some predefined mods.
These have been tested on the firmware version 225.
Currently available mods are:

 - iter
 > Enable the hidden iter synth

 - filter
 > Enable the hidden filter effect

 - subtle-fx
 > Lower the default intensity of effects. This allows you to turn effects on
 > without affecting the sound too much. You can then turn them up as you like.
 > This helps with live performances and avoids a sudden change to the sound
 > when an effect is enabled.

 - iter-gfx-lab
 > Add custom lab themed visuals to the iter synth.


To enable a mod first unpack the firmware, then run the following command
(replace mod_name with the mod you want) and repack the firmware after that.

    op1repacker modify [directory] --options mod_name

For example to enable all mods run this command:

    op1repacker modify [directory] --options iter filter subtle-fx iter-gfx-lab

More modifications might be added later.


## Contributing

If you want to participate please submit issues and pull requests to GitHub.
Pull requests should be opened against the `dev` branch. I like to only push
tested new versions to master. You can also let me know of possible mods you
would like to see by openning a new issue and describing the mod. Keep in
mind that new features can't be added. Only changes to what's already in the
firmware are possible.

