#!/usr/bin/env python3
"""Unpack and repack OP1 firmware in order to create custom firmware."""

import os
import argparse

import op_db
import op_repack

__author__ = 'Richard Lewis'
__copyright__ = 'Copyright 2016, Richard Lewis'
__license__ = 'MIT'
__status__ = 'Development'
__version__ = '0.1.0'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Unpack and repack OP-1 firmware in order to create custom firmware.\
                                                  Use at your own risk! Custom firmware will void your warranty and\
                                                  may brick your OP-1.')
    parser.add_argument('action', choices=['unpack', 'modify', 'repack'],
                        help='action that should be performed on the firmware')
    parser.add_argument('path', type=str, nargs=1, help='file or dir to unpack or repack')
    parser.add_argument('--options', nargs='+', help='list modifications to make on the firmware')
    parser.add_argument('--debug', action='store_true', help='print debug messages')
    parser.add_argument('--version', action='version', version=__version__)
    args = parser.parse_args()

    repacker = op_repack.OP1Repack(debug=args.debug)

    if args.action == 'repack':
        print('Repacking {}...'.format(args.path[0]))
        if repacker.repack(args.path[0]):
            print('Done!')
        else:
            print('Errors occured during repacking!')

    elif args.action == 'unpack':
        print('Unpacking {}...'.format(args.path[0]))
        if repacker.unpack(args.path[0]):
            print('Done!')
        else:
            print('Errors occured during unpacking!')

    elif args.action == 'modify':
        if args.options:
            db_path = os.path.abspath(os.path.join(args.path[0], 'content', 'op1_factory.db'))
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
            if db.commit():
                print('Done!')
            else:
                print('Errors occured!')
        else:
            print('Please specify what modifications to make with --options argument.')
