#!/usr/bin/env python3
"""Unpack and repack OP1 firmware in order to create custom firmware."""

import os
import sys
import lzma
import shutil
import struct
import tarfile
import logging
import binascii

__author__ = 'Richard Lewis'
__copyright__ = 'Copyright 2016, Richard Lewis'
__license__ = 'MIT'
__status__ = 'Development'


class OP1Repacker:
    """Unpack and repack OP1 firmware and other related utilities."""
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG,
                            format='[%(asctime)s] %(levelname)-8s %(message)s',
                            datefmt='%Y-%m-%d %H:%M',
                            )

        self.logger = logging.getLogger()
        # The folder in wich the unpacking and repacking is done
        self.root_path = None
        # The FW file to unpack or the FW directory to repack
        self.target_file = None
        # Temporary file suffix to use when unpacking
        self.temp_file_suffix = '.unpacking'
        # Suffix to add when to FW file when it's repacked
        self.repack_file_suffix = '-repacked.op1'

    def run(self):
        """Parse command line options and run repacker."""
        # Check that we have at least the operation and the target path
        if len(sys.argv) < 3:
            self.logger.warning('Please specify action and input path!')
            return False
        action = sys.argv[1].lower()
        input_path = sys.argv[2]

        actions = ['unpack', 'repack', 'add_crc', 'remove_crc']
        if action not in actions:
            self.logger.warning('Invalid action. Valid actions are: {}'.format(', '.join(actions)))
            return False

        if action == 'repack':
            path = os.path.abspath(input_path)
            self.root_path = os.path.dirname(path)
            self.target_file = os.path.basename(input_path)
            self.repack()
        elif action == 'unpack':
            path = os.path.abspath(input_path)
            self.root_path = os.path.dirname(path)
            self.target_file = os.path.basename(input_path)
            self.unpack()
        elif action == 'add_crc':
            self.add_crc(input_path)
            return True
        elif action == 'remove_crc':
            self.remove_crc(input_path)
            return True
        else:
            self.logger.warning('Invalid action or input file!')
            return False
        return True

    def create_temp_file(self):
        from_path = os.path.join(self.root_path, self.target_file)
        to_path = os.path.join(self.root_path, self.target_file + self.temp_file_suffix)
        shutil.copy(from_path, to_path)
        return to_path

    def unpack(self):
        # TODO: maybe do all this in memory without the temp file
        full_path = os.path.join(self.root_path, self.target_file)
        self.logger.info('Unpacking firmware file: {}'.format(full_path))
        temp_file_path = self.create_temp_file()
        self.remove_crc(temp_file_path)
        self.uncompress_lzma(temp_file_path)
        self.uncompress_tar(temp_file_path)
        os.remove(temp_file_path)
        self.logger.info('Unpacking complete!')

    def repack(self):
        # TODO: maybe do all this in memory without the temp file
        compress_from = os.path.join(self.root_path, self.target_file)
        compress_to = os.path.join(self.root_path, self.target_file + self.repack_file_suffix)
        self.logger.info('Repacking firmware from: {}'.format(compress_from))
        self.compress_tar(compress_from, compress_to)
        self.compress_lzma(compress_to)
        self.add_crc(compress_to)
        self.logger.info('Repacking complete!')

    def remove_crc(self, path):
        """Remove the first 4 bytes of the firmware which contain the CRC-32 checksum."""
        f = open(path, 'rb')
        data = f.read()
        f.close()

        checksum_data = data[:4]
        checksum = struct.unpack('<L', checksum_data)[0]
        self.logger.info('Removing checksum: {}'.format(checksum))

        f = open(path, 'wb')
        f.write(data[4:])
        f.close()

    def add_crc(self, path):
        """Generates and adds a CRC to the beginning of a file."""
        f = open(path, 'rb')
        data = f.read()
        f.close()

        # Calculate our CRC
        calced_crc = binascii.crc32(data)
        self.logger.info('Adding checksum {} to {}'.format(calced_crc, path))
        # Convert the intiger to binary with little endian
        bin_crc = struct.pack('<L', calced_crc)

        # Write the new CRC with the data back to the file
        f = open(path, 'wb')
        f.write(bin_crc + data)
        f.close()

    def uncompress_lzma(self, temp_file):
        self.logger.info('Uncompressing LZMA...')
        f = lzma.open(temp_file)
        data = f.read()
        f.close()
        f = open(temp_file, 'wb')
        f.write(data)
        f.close()

    def uncompress_tar(self, temp_file):
        target_path = os.path.join(self.root_path, os.path.splitext(self.target_file)[0])
        self.logger.info('Uncompressing TAR {}...'.format(temp_file))
        self.logger.info('Target: {}'.format(target_path))
        tar = tarfile.open(temp_file)
        tar.extractall(target_path)

    def compress_lzma(self, target):
        self.logger.info('Compressing {} with LZMA...'.format(target))
        f = open(target, 'rb')
        data = f.read()
        f.close()
        # Getting these LZMA parameters right was a huge pain in the ass. I do not recommend touching them.
        # The OP1 only accepts max 15mb firwmare files. But using agressive compression requires more ram to decompress.
        # When using the most agressive preset 9, the OP1 fails to allocate enough RAM to perform the decompression.
        # I found that these settings work pretty well. FW under 15mb and it installs fine.
        my_filters = [
            {'id': lzma.FILTER_LZMA1, 'preset': 9, 'lc': 3, 'lp': 1, 'pb': 2, 'dict_size': 2**23},
        ]
        f = lzma.open(target, 'wb', filters=my_filters, format=lzma.FORMAT_ALONE)
        f.write(data)
        f.close()

    def tarinfo_reset(self, tarinfo):
        """Resets user information for each file compressed into the TAR."""
        tarinfo.uid = tarinfo.gid = 0
        tarinfo.uname = tarinfo.gname = 'root'
        return tarinfo

    def compress_tar(self, path, target):
        """Compresses path into the target TAR file."""
        self.logger.info('Repacking to TAR from {} to: {}'.format(path, target))
        files = os.listdir(path)
        tar = tarfile.open(target, 'w')
        for file in files:
            file_path = os.path.join(path, file)
            self.logger.debug('Adding "{}" to archive.'.format(file_path))
            # Remove the subfolder name so that the archive won't contain the subfolder.
            name = file_path.replace(path+os.sep, '')
            tar.add(file_path, arcname=name, filter=self.tarinfo_reset)
        tar.close()


if __name__ == '__main__':
    app = OP1Repacker()
    app.run()
