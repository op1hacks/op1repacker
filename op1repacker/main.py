#!/usr/bin/env python3
"""Unpack and repack OP1 firmware in order to create custom firmware."""

import os
import json
import argparse
from shutil import copyfile

from . import op1_analyze
from . import op1_db
from . import op1_gfx
from . import op1_patches
from . import op1_repack


__author__ = 'Richard Lewis'
__copyright__ = 'Copyright 2019, Richard Lewis'
__license__ = 'MIT'
__status__ = 'Development'
__version__ = '0.2.6'


description = """
Unpack and repack OP-1 firmware in order to create custom firmware.
Enable hidden features like the \'iter\' synth and \'filter\' effect.
Use at your own risk! Custom firmware will void your warranty and
may brick your OP-1.
"""

actions_help = """action to perform on the firmware
- unpack: unpack a firmware file
- repack: repackage unpacked firmware
- modify: modify unpacked firmware with changes specified by --options
- analyze: analyze version info and other things of an unpacked firmware directory

"""

options_help = """changes to make on the unpacked firmware to enable mods and hidden features
valid values are:
- iter
- presets-iter
- filter
- subtle-fx
- gfx-iter-lab
- gfx-cwo-moose
- gfx-tape-invert
"""


def main():
    parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('action', choices=['unpack', 'modify', 'repack', 'analyze'],
                        help=actions_help)
    parser.add_argument('path', type=str, nargs='+', help='firmware file or directory path')
    parser.add_argument('--options', nargs='+', help=options_help)
    parser.add_argument('--debug', action='store_true', help='print debug messages')
    parser.add_argument('--version', '-v', action='version', version=__version__,
                        help='show program\'s version number and exit')
    args = parser.parse_args()

    repacker = op1_repack.OP1Repack(debug=args.debug)

    # Path to the app location (NOT the firmware path)
    app_path = os.path.dirname(os.path.realpath(__file__))
    db_actions = ['iter', 'filter', 'subtle-fx', 'presets-iter']

    for target_path in args.path:
        if not os.path.exists(target_path):
            print('The specified path "{}" doesn\'t exist!'.format(target_path))
            return

        # Analyze
        if args.action == 'analyze':
            if not os.path.isdir(target_path):
                print('The path to analyze must be a directory! Unpack the firmware file first.')
                return
            print('Analyzing {}...'.format(target_path))
            data = op1_analyze.analyze_unpacked_fw(target_path)
            for key, value in data.items():
                label = key.upper().replace('_', ' ')
                print('    - ' + label + ': ' + value)
            print("Done.\n")

        # Repack
        if args.action == 'repack':
            if not os.path.isdir(target_path):
                print('The path to repack must be a directory!')
                return

            print('Repacking {}...'.format(target_path))
            if repacker.repack(target_path):
                print('Done!')
            else:
                print('Errors occured during repacking!')

        # Unpack
        elif args.action == 'unpack':
            if not os.path.isfile(target_path):
                print('The path to unpack must be a file!')
                return

            if not target_path.endswith('.op1'):
                print('That doesn\'t seem to be a firmware file. The extension must be ".op1".')

            print('Unpacking {}...'.format(target_path))
            if repacker.unpack(target_path):
                print('Done!')
            else:
                print('Errors occured during unpacking!')

        # Modify
        elif args.action == 'modify':
            if not os.path.isdir(target_path):
                print('The path to modify must be a directory!')
                return

            if not args.options:
                print('Please specify what modifications to make with --options argument.')
                return

            # Only open the database for changes if at least one DB mod is selected
            if set(db_actions) - (set(db_actions) - set(args.options)):
                db_path = os.path.abspath(os.path.join(target_path, 'content', 'op1_factory.db'))
                db = op1_db.OP1DB()
                db.open(db_path)

                print("Running database modifications:")

                if 'iter' in args.options:
                    print('- Enabling "iter" synth...')
                    if not db.enable_iter():
                        print('    Failed to enable "iter". Maybe it\'s already enabled?')

                if 'presets-iter' in args.options:
                    print('- Adding community presets for iter:')
                    if not db.synth_preset_folder_exists('iter'):
                        iter_preset_path = os.path.join(app_path, 'assets', 'presets', 'iter')
                        patches = op1_patches.load_patch_folder(iter_preset_path)

                        for patch in patches:
                            print('    - ' + patch['name'])
                            patch_data = json.dumps(patch)
                            db.insert_synth_preset(patch_data, 'iter')
                    else:
                        print('    Iter already has presets, not adding new ones.')

                if 'filter' in args.options:
                    print('- Enabling "filter" effect...')
                    if not db.enable_filter():
                        print('    Failed to enable "filter". Maybe it\'s already enabled?')

                if 'subtle-fx' in args.options:
                    print('- Modifying FX defaults to be less intensive...')
                    if not db.enable_subtle_fx_defaults():
                        print('    Failed to modify default parameters for effects!')

                # Commit changes to sqlite file
                if not db.commit():
                    print('Errors occured while modifying database!')

                print('')

            # Custom GFX
            gfx_mods = filter(lambda opt: opt.startswith('gfx-'), args.options)
            if gfx_mods:
                print("Running graphics modifications:")
            for mod in gfx_mods:
                if mod == 'gfx-iter-lab':
                    print('- Enabling custom lab graphic for iter...')
                    path_from = os.path.join(app_path, 'assets', 'display', 'iter-lab.svg')
                    path_to = os.path.abspath(os.path.join(target_path, 'content', 'display', 'iter.svg'))
                    copyfile(path_from, path_to)
                else:
                    patch_name = mod[4:]
                    patch_path = os.path.join(app_path, 'assets', 'display', patch_name + '.patch.json')
                    if not os.path.exists(patch_path):
                        print('    GFX patch "{}" doesn\'t exist!'.format(patch_name))
                        continue

                    print('- Applying GFX patch "{}"...'.format(patch_name))
                    result = op1_gfx.patch_image_file(target_path, patch_path)
                    if not result:
                        print('    Failed to apply patch! Maybe the patch is already applied?')

            print('')
            print('Done.')


if __name__ == '__main__':
    main()
