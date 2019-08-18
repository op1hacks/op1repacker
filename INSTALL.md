# Installation


## Mac OS X

### Step 1: Get the firmware file that you want to modify

First you need to have an official firmware update file, here's how to get one.

- **Recommended:** Get the latest OP-1 firmware update file from the TE website: https://teenage.engineering/downloads
- *Experimental:* If you want you can try older firmware files from the archive: https://github.com/op1hacks/op1-fw-archive

### Step 2: Get into the terminal

In this step we'll need to make sure  **python3**  is installed since Python 3 is the programming
language that **op1repacker** is written in. It might already be installed on your system but we'll
check and install it if it's not.

First we'll need to open the terminal:
- Open the Terminal App on your system (more info about Terminal here: https://macpaw.com/how-to/use-terminal-on-mac)
- Next lets see if python3 is installed.
  In the terminal type the following command and press enter:
```python3 --version```
  If the output looks something like `Python 3.X.X` then you have python3 and can continue to step #3. For example:
```Python 3.6.7```

If you get an error from the command above (something like `command not found: python3` you'll need to install Python 3 yourself. I would recommend checking out one of the following guides for installing it:
 - https://www.saintlad.com/install-python-3-on-mac/
 - https://docs.python-guide.org/starting/install3/osx/

Feel free to send message on the [OP-1 forum](https://op-forums.com/) or create an issue in the op1repacker GitHub repository if you need more info about installing python3 on Mac OS.

### Step 3: Install the op1repacker tool

- In the terminal run the following command:
```pip3 install op1repacker```
    - Alternatively try `pip install op1repacker` if that doesn't work. You might also have to add `sudo ` to the beginning of the command if it says something like permission denied.
- You should now have the latest version of the tool.
- To make sure the tool works run the following command:
```op1repacker -v```
If the installation worked you'll see a version number of the tool. For example:
```0.2.2```

### Step 4: Create your custom firmware
- In the terminal, go to the directory where your firmware file is. If the firmware file is in your home directory run the following command:
```cd ~```
- If the firmware is in some other directory you can navigate to it in the terminal this:
```cd /path/to/folder```

Now comes the fun part: actually modding the firmware. The commands below use the latest firmware `op1_235` as an example. Change the filename If you are using a different firmware version.

- First unpack the firmware file by running:
```op1repacker unpack op1_235.op1```
- Now you can mod the unpacked firmware. The available mods are described here: https://github.com/op1hacks/op1repacker#modify For example to enable all the available modifications run:
    > `op1repacker modify op1_235 --options iter presets-iter filter subtle-fx gfx-iter-lab gfx-tape-invert gfx-cwo-moose`

  You can of course leave any of the mods out if you don't want all of them.
- Now that the mods are done you can get your installable custom firmware file.
Repackage the unpacked firmware with this command:
```op1repacker repack op1_235```

Now your folder should have the file ```op1_235-repacked.op1```. Run the normal OP-1 firmware update and use this file and to get the mods installed on your OP-1.
**Enjoy!**


## Windows / Linux

No instructions yet, sorry.
