import os
import json
import struct


def load_patch_folder(path):
    patch_files = [name for name in os.listdir(path) if name.lower().endswith('aif')]

    patches = []

    for file_name in patch_files:
        patch_name = os.path.splitext(file_name)[0]
        patch_data = read_patch(os.path.join(path, file_name))
        # Set the patch data name based on the filename of the patch
        # TODO: option for normalizing patch names
        patch_data['name'] = patch_name
        patches.append(patch_data)

    return patches


def read_patch(patch_filename):
    f = open(patch_filename, 'rb')
    data = f.read()
    f.close()

    # Locate start of APPL chunk
    appl_pos = data.find(bytes('APPL', 'utf-8'))
    if appl_pos == -1:
        raise TypeError('Invalid file. No APPL data found.')
    appl_pos += 4

    appl_chunk = data[appl_pos:]
    appl_data_len = struct.unpack('>l', appl_chunk[:4])[0]

    appl_data_bin = appl_chunk[4:appl_data_len+4]
    appl_data = str(appl_data_bin, 'utf-8').strip()

    if appl_data.startswith('op-1'):
        appl_data = appl_data[4:]

    return json.loads(appl_data)
