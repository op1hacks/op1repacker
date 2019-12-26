#!/usr/bin/env python3
"""Unpack and repack OP1 firmware in order to create custom firmware."""

import os
import stat
import lzma
import shutil
import struct
import tarfile
import logging
import binascii


class OP1Repack:
    """Unpack and repack OP-1 firmware and other related utilities."""
    # TODO:
    # - Do some checks to make sure the fw is ok when unpacking & repacking (how?)

    def __init__(self, debug=0):
        logging.basicConfig(level=logging.WARNING,
                            # format='[%(asctime)s] %(levelname)-8s %(message)s',
                            format=' %(levelname)-10s %(message)s',
                            datefmt='%Y-%m-%d %H:%M',
                            )

        self.logger = logging.getLogger()
        if debug:
            self.logger.setLevel(logging.DEBUG)
        # Temporary file suffix to use when unpacking
        self.temp_file_suffix = '.unpacking'
        # Suffix to add when to FW file when it's repacked
        self.repack_file_suffix = '-repacked.op1'

    def create_temp_file(self, from_path):
        """Create a temporary file for the unpacking procedure and return its path."""
        to_path = from_path + self.temp_file_suffix
        shutil.copy(from_path, to_path)
        return to_path

    def unpack(self, input_path):
        """Unpack OP-1 firmware."""
        # TODO: maybe do all this in memory without the temp file
        path = os.path.abspath(input_path)
        if not os.path.isfile(input_path):
            self.logger.error("Firmware file doesn't exist: {}".format(input_path))
            return False
        root_path = os.path.dirname(path)
        target_file = os.path.basename(input_path)
        full_path = os.path.join(root_path, target_file)
        target_path = os.path.join(root_path, os.path.splitext(target_file)[0])

        self.logger.debug('Unpacking firmware file: {}'.format(full_path))
        temp_file_path = self.create_temp_file(path)
        self.remove_crc(temp_file_path)
        self.uncompress_lzma(temp_file_path, temp_file_path)
        self.uncompress_tar(temp_file_path, target_path)
        os.remove(temp_file_path)
        # Don't mess with permissions on Windows
        if os.name != 'nt':
            self.set_permissions(target_path)
        self.logger.debug('Unpacking complete!')
        return True

    def repack(self, input_path):
        """Repack OP-1 firmware."""
        # TODO: maybe do all this in memory without the temp file
        path = os.path.abspath(input_path)
        if not os.path.isdir(path):
            self.logger.error("Given path isn't a directory: {}".format(input_path))
            return False
        root_path = os.path.dirname(path)
        target_file = os.path.basename(os.path.normpath(input_path))
        compress_from = os.path.join(root_path, target_file)
        compress_to = os.path.join(root_path, target_file + self.repack_file_suffix)
        self.logger.debug('Repacking firmware from: {}'.format(compress_from))
        self.compress_tar(compress_from, compress_to)
        self.compress_lzma(compress_to)
        self.add_crc(compress_to)
        self.logger.debug('Repacking complete!')
        return True

    def remove_crc(self, path):
        """Remove the first 4 bytes of the firmware which contain the CRC-32 checksum."""
        with open(path, 'rb') as f:
            data = f.read()

        checksum_data = data[:4]
        checksum = struct.unpack('<L', checksum_data)[0]
        self.logger.debug('Removing checksum: {}'.format(checksum))

        with open(path, 'wb') as f:
            f.write(data[4:])

    def add_crc(self, path):
        """Generates and adds a CRC to the beginning of a file."""
        with open(path, 'rb') as f:
            data = f.read()

        # Calculate our CRC
        calced_crc = binascii.crc32(data)
        self.logger.debug('Adding checksum {} to {}'.format(calced_crc, path))
        # Convert the integer to binary with little endian
        bin_crc = struct.pack('<L', calced_crc)

        # Write the new CRC with the data back to the file
        with open(path, 'wb') as f:
            f.write(bin_crc + data)

    def uncompress_lzma(self, target_file, target_path):
        """Uncompress LZMA target_file contents to target_path."""
        self.logger.debug('Uncompressing LZMA...')
        with lzma.open(target_file) as f:
            data = f.read()
        with open(target_path, 'wb') as f:
            f.write(data)

    def uncompress_tar(self, target_file, target_path):
        """Uncompress TAR target_file to target_path."""
        self.logger.debug('Uncompressing TAR to "{}"...'.format(target_path))
        tar = tarfile.open(target_file)
        tar.extractall(target_path)

    def compress_lzma(self, target):
        """Compress the contents of target with LZMA compression."""
        self.logger.debug('Compressing {} with LZMA...'.format(target))
        with open(target, 'rb') as f:
            data = f.read()
        # Getting these LZMA parameters right was a huge pain in the ass. I do not recommend touching them. The OP-1
        # only accepts max 15mb firwmare files. But using agressive compression requires more ram to decompress.
        # When using the most agressive preset 9, the OP-1 fails to allocate enough RAM to perform the decompression.
        # I found that these settings work pretty well. The resulting firmware is under 15mb and it installs fine.
        lzma_filters = [
            {'id': lzma.FILTER_LZMA1, 'preset': 9, 'lc': 3, 'lp': 1, 'pb': 2, 'dict_size': 2**23},
        ]
        f = lzma.open(target, 'wb', filters=lzma_filters, format=lzma.FORMAT_ALONE)
        f.write(data)
        f.close()

    def tarinfo_reset(self, tarinfo):
        """Resets user information for each file compressed into the TAR."""
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = 'root'
        return tarinfo

    def compress_tar(self, path, target):
        """Compresses path into the target TAR file."""
        self.logger.debug('Repacking to TAR from {} to: {}'.format(path, target))
        files = os.listdir(path)
        tar = tarfile.open(
            target,
            'w',
            format=tarfile.GNU_FORMAT
        )
        for file in files:
            if file.startswith('.'):
                continue
            file_path = os.path.join(path, file)
            self.logger.debug('Adding "{}" to archive.'.format(file_path))
            # Remove the subfolder name so that the archive won't contain the subfolder.
            name = file_path.replace(path+os.sep, '')
            tar.add(file_path, arcname=name, filter=self.tarinfo_reset)
        tar.close()

    def set_permissions(self, target):
        """Make the unpacked firmware folder readable."""
        # TODO: does this need to be done on Windows?
        self.logger.debug('Setting access permissions to "{}" ...'.format(target))
        self.add_dir_permissions(target, stat.S_IEXEC)

    def add_dir_permissions(self, target, flag):
        """Recursively adds 'flag' permission to all subfolders in target."""
        for root, dirs, files in os.walk(target):
            for directory in dirs:
                path = os.path.join(root, directory)
                st = os.stat(path)
                os.chmod(path, st.st_mode | flag)
                self.add_dir_permissions(path, flag)
