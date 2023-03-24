#!/usr/bin/env python3

# Python script to control EIZO FlexScan displays using EIZO's
# USB HID  protocol.
# Copyright (C) 2023 Pavel Löbl
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; If not, see <http://www.gnu.org/licenses/>.

import hid
import sys
import argparse

#info = dev.get_feature_report(0x08, 25)
#
#serial = ''.join([chr(s) for s in info[1:9]])
#model = ''.join([chr(s) for s in info[9:15]])
#
#print("Path   : " + str(usb_path))
#print("Serial : " + str(serial))
#print("Model  : " + str(model))

EIZO_USAGE_PROFILE = [ 0x0, 0xff, 0x15, 0x0 ]
EIZO_USAGE_INPUT = [ 0x1, 0xff, 0x48, 0x0 ]
EIZO_USAGE_ECOVIEW_SENSOR = [ 0x1, 0xff, 0x0c, 0x0 ]
EIZO_USAGE_IDENTIFY = [ 0x1, 0xff, 0x45, 0x0 ]
EIZO_USAGE_BRIGHTNESS = [ 0x82, 0x00, 0x10, 0x0 ]

eizo_inputs = {
    "dvi" : 0x200,
    "displayport" : 0x300,
    "hdmi" : 0x400,
    }

eizo_color_profiles = {
    "user1" : 0x16,
    "user2" : 0x17,
    "srgb"  : 0x4,
    "paper" : 0x22,
    "movie" : 0x2,
    "dicom" : 0x8,
    }

eizo_supported_ids = [
    { 'vid' : 0x056d, 'pid' : 0x4027 }
    ]

def detect_all():
    for h in hid.enumerate():
        for s in eizo_supported_ids:
            if h['vendor_id'] == s['vid'] and h['product_id'] == s['pid']:
                print('Bus: {:s} ID: {:04x}:{:04x}'.format(h['path'].decode('ascii'), h['vendor_id'], h['product_id']))

def eizo_string_to_value(key, mapping):
    for k,v in mapping.items():
        if k == key:
            return v
    return None

def eizo_value_to_string(hex_val, mapping):
    for k,v in mapping.items():
        if v == hex_val:
            return k
    return "unknown " + hex(hex_val)

def dump_hex(array):
    return
    #print(", ".join([hex(i) for i in array]))

def set_eizo_feature(dev, usage, value):
    buffer = [0x2] + usage
    buffer += counter + [value]

    dump_hex(buffer)
    dev.send_feature_report(buffer)


def get_eizo_feature(dev, usage):
    buffer = [0x3] + usage
    buffer += counter

    dump_hex(buffer)
    dev.send_feature_report(buffer)

    state = dev.get_feature_report(0x3, 40)
    return state

    # verify
    # state = dev.get_feature_report(7, 8)

    #for i in range(7):
    #    if tmp[i] != buf[i]:
    #        raise Exception
    #val = tmp[8] * 256 + tmp[7]

# counter
#counter = dev.get_feature_report(0x6, 3)[1:][::-1]
#counter = dev.get_feature_report(0x6, 3)[1:]
counter = [ 0, 0]

parser = argparse.ArgumentParser(description='Description of your program')
parser.add_argument('--get-input', help='Description for foo argument', action='store_true')
parser.add_argument('--get-profile', help='Description for bar argument', action='store_true')
parser.add_argument('--set-brightness', help='Description for bar argument', type=int)
parser.add_argument('--get-brightness', help='Description for bar argument', action='store_true')
parser.add_argument('--inc-brightness', help='Description for bar argument', type=int)
parser.add_argument('--dec-brightness', help='Description for bar argument', type=int)
parser.add_argument('--identify', help='Description for bar argument', action='store_true')
parser.add_argument('--path', help='usb path to device', nargs='+')
parser.add_argument('--detect', help='Detect all known devices.', action='store_true')
args = vars(parser.parse_args())

if args['detect']:
    detect_all()
    sys.exit(0)

usb_path = bytes(args['path'][0], 'ascii')

dev = hid.device()
dev.open_path(usb_path)
dev.set_nonblocking(1)

def get_input(dev):
    source = get_eizo_feature(dev, EIZO_USAGE_INPUT)
    #print(source)
    return source[8] << 8 | source[7]

def get_profile(dev):
    profile = get_eizo_feature(dev, EIZO_USAGE_PROFILE)
    #print(profile)
    return profile[7]

if args['get_input']:
    print(eizo_value_to_string(get_input(dev), eizo_inputs))
elif args['get_profile']:
    print(eizo_value_to_string(get_profile(dev), eizo_color_profiles))
elif args['set_brightness']:
    a = args['set_brightness']
    set_eizo_feature(dev, EIZO_USAGE_BRIGHTNESS, a*2)
elif args['get_brightness']:
    ret = get_eizo_feature(dev, EIZO_USAGE_BRIGHTNESS)
    print(ret[7])
elif args['inc_brightness']:
    inc = args['inc_brightness']
    ret = get_eizo_feature(dev, EIZO_USAGE_BRIGHTNESS)[7]
    set_eizo_feature(dev, EIZO_USAGE_BRIGHTNESS, ret + inc*2)
elif args['dec_brightness']:
    inc = args['dec_brightness']
    ret = get_eizo_feature(dev, EIZO_USAGE_BRIGHTNESS)[7]
    set_eizo_feature(dev, EIZO_USAGE_BRIGHTNESS, ret - inc*2)
elif args['identify']:
    set_eizo_feature(dev, EIZO_USAGE_IDENTIFY, 0)
else:
    ret = get_eizo_feature(dev, EIZO_USAGE_ECOVIEW_SENSOR)
    val = ret[8] << 8 | ret[7]
    print(ret)
    print(val)
    parser.print_usage()

sys.exit(0)
