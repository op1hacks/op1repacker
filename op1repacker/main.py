#!/usr/bin/env python3
"""Unpack and repack OP1 firmware in order to create custom firmware."""

import os
import argparse
from shutil import copyfile

import op_db
import op_repack


__author__ = 'Richard Lewis'
__copyright__ = 'Copyright 2016, Richard Lewis'
__license__ = 'MIT'
__status__ = 'Development'
__version__ = '0.1.1'


description = """
Unpack and repack OP-1 firmware in order to create custom firmware.
Enable hidden features like the \'iter\' synth and \'filter\' effect.
Use at your own risk! Custom firmware will void your warranty and
may brick your OP-1.
"""


def main():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('action', choices=['unpack', 'modify', 'repack'],
                        help='action to perform on the firmware')
    parser.add_argument('path', type=str, nargs=1, help='file to unpack or directory repack')
    parser.add_argument('--options', nargs='+',
                        help='modifications to make on the unpacked firmware, valid values are \'iter\' \
                             \'filter\' \'subtle-fx\' and \'iter-gfx-lab\' to enable mods and the hidden features.')
    parser.add_argument('--debug', action='store_true', help='print debug messages')
    parser.add_argument('--version', action='version', version=__version__,
                        help='show program\'s version number and exit')
    args = parser.parse_args()

    repacker = op_repack.OP1Repack(debug=args.debug)

    # Path to the app location (NOT the firmware path)
    app_path = os.path.dirname(os.path.realpath(__file__))
    db_actions = ['iter', 'filter', 'subtle-fx']

    # Path to the firmware file or directory
    target_path = args.path[0]

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
            db = op_db.OP1DB()
            db.open(db_path)
            if 'iter' in args.options:
                print('Enabling "iter" synth...')
                if not db.enable_iter():
                    print('Failed to enable "iter". Maybe it\'s already enabled?')
            if 'filter' in args.options:
                print('Enabling "filter" effect...')
                if not db.enable_filter():
                    print('Failed to enable "filter". Maybe it\'s already enabled?')
            if 'subtle-fx' in args.options:
                print('Modifying FX defaults to be less intensive...')
                if not db.enable_subtle_fx_defaults():
                    print('Failed to modify default parameters for effects!')

            if db.commit():
                print('Database modifications succeeded!')
            else:
                print('Errors occured while modifying database!')

        # Custom GFX
        if 'iter-gfx-lab' in args.options:
            print('Enabling custom lab graphic for iter...')
            path_from = os.path.join(app_path, 'assets', 'display', 'iter-lab.svg')
            path_to = os.path.abspath(os.path.join(target_path, 'content', 'display', 'iter.svg'))
            copyfile(path_from, path_to)

        print('Done.')


if __name__ == '__main__':
    main()
