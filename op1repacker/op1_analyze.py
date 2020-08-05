"""Analyze unpacked OP-1 firmware directories."""

import os
import re
import time

UNKNOWN_VALUE = 'UNKNOWN'


def analyze_boot_ldr(target):
    path = os.path.join(target, 'te-boot.ldr')
    f = open(path, 'rb')
    data = f.read()
    f.close()

    version_arr = re.findall(br'TE-BOOT .+?(\d*\.?\d+)', data)
    bootloader_version = version_arr[0].decode('utf-8').strip() if version_arr else UNKNOWN_VALUE

    return {
        'bootloader_version': bootloader_version,
    }


def analyze_main_ldr(target):
    path = os.path.join(target, 'OP1_vdk.ldr')
    f = open(path, 'rb')
    data = f.read()
    f.close()

    start_pos = data.find(b'Rev.')
    chunk = data[start_pos:]
    end_pos = chunk.find(b'\n')
    chunk = chunk[:end_pos].decode('utf-8')

    build_version_arr = re.findall(r'Rev.+?(.*?);', chunk)
    build_version = build_version_arr[0].strip() if build_version_arr else UNKNOWN_VALUE

    date_arr = re.findall(r'\d\d\d\d/\d\d/\d\d', chunk)
    time_arr = re.findall(r'\d\d:\d\d:\d\d', chunk)

    fw_version = re.findall(br'R\..\d\d\d\d?\d?', data)
    fw_version = UNKNOWN_VALUE if not fw_version else fw_version[0].decode('utf-8')

    return {
        'firmware_version': str(fw_version),
        'build_version': build_version,
        'build_date': date_arr[0] if date_arr else UNKNOWN_VALUE,
        'build_time': time_arr[0] if time_arr else UNKNOWN_VALUE,
    }


def analyze_fs(target):
    oldest = None
    newest = None
    for root, dirs, files in os.walk(target):
        for file in files:
            file_path = os.path.join(root, file)
            mtime = os.path.getmtime(file_path)
            if oldest is None or mtime < oldest:
                oldest = mtime
            if newest is None or mtime > newest:
                newest = mtime

    return {
        'oldest_file': time.strftime('%Y/%m/%d %H:%M', time.gmtime(oldest)),
        'newest_file': time.strftime('%Y/%m/%d %H:%M', time.gmtime(newest)),
    }


def analyze_unpacked_fw(target):
    main_ldr_info = analyze_main_ldr(target)
    boot_ldr_info = analyze_boot_ldr(target)
    fs_info = analyze_fs(target)

    return {
        **main_ldr_info,
        **boot_ldr_info,
        **fs_info,
    }
