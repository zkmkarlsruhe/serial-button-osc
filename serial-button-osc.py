#! /usr/bin/env python3
#
# Copyright (c) 2023 ZKM | Hertz-Lab
# Dan Wilcox <dan.wilcox@zkm.de>
#
# BSD Simplified License.
# For information on usage and redistribution, and for a DISCLAIMER OF ALL
# WARRANTIES, see the file, "LICENSE.txt," in this distribution.
#
# This code has been developed at ZKM | Hertz-Lab as part of „The Intelligent
# Museum“ generously funded by the German Federal Cultural Foundation.

import sys
import signal
import argparse

##### parser

def len_min_2(s):
    if len(s) > 1:
        return s
    raise argparse.ArgumentTypeError("value must have min len of 2")

parser = argparse.ArgumentParser(description="send an OSC message when a big red button is pressed")
parser.add_argument(
    "dev", type=str, nargs="?", metavar="DEV",
    default="/dev/ttyAMA0", help="serial port device, default: /dev/ttyAMA0")
parser.add_argument(
    "message", type=str, nargs="?", metavar="MESSAGE",
    default="/button", help="OSC message address, default: /button")
parser.add_argument(
    "-a", "--address", dest="address", metavar="ADDR",
    default="127.0.0.1", help="destination hostname or IP address, default: 127.0.0.1")
parser.add_argument(
    "-p", "--port", type=int, dest="port", metavar="PORT",
    default=6000, help="destination port to send to, default: 6000")
parser.add_argument(
    "-r", "--rate", type=int, dest="rate", metavar="RATE",
    default=115200, help="serial port baud rate, default: 115200")
parser.add_argument(
    "--button-char", dest="buttonchar", metavar="BUTTON_CHAR",
    default="3", help="serial char for button press, default: '3'")
parser.add_argument(
    "-s", "--switch", action="store_true", dest="switch",
    help="read button as a switch and send off/on int value as message arg")
parser.add_argument(
    "--switch-chars", dest="switchchars", metavar="SWITCH_CHARS",
    default="01", help="serial chars for switch values off/on, default: '01'",
    type=len_min_2) # restrict to min len of 2
args = parser.add_argument(
    "-v", "--verbose", action="store_true", dest="verbose",
    help="enable verbose printing")

##### Serial

import serial
import time

# serial byte reader base class
class SerialReader:

    def __init__(self, dev, rate=115200, verbose=False):
        self.serial = serial.Serial(dev, rate) # serial port
        self.interval = 0.1
        self.is_running = True
        self.verbose = verbose
        if self.verbose:
            print(f"serial: created {dev} {rate}")

    # open serial port for reading
    def open(self):
        if not self.serial.is_open:
            self.serial.open()
            if self.verbose:
                print("serial: open")

    # close serial port
    def close(self):
        if self.serial.is_open:
            self.serial.close()
            if self.verbose:
                print("serial: close")

    # start synchronous run loop
    def start(self):
        self.is_running = True
        if self.verbose:
            print("serial: start")
        while self.is_running:
            self.update()
            time.sleep(self.interval)
        self.is_running = False
        if self.verbose:
            print("serial: stop")

    # stop synchronous run loop
    def stop(self):
        self.is_running = False

    # read serial bytes, send message if self.char byte is found
    def update(self):
        count = self.serial.in_waiting
        if count > 0:
            recv = self.serial.read(count)
            self.serial.reset_input_buffer()
            if self.verbose:
                print(f"serial: {recv}")
            self.recv(recv)

    # process received bytes, implement in child class
    def recv(serial_bytes):
        pass

# single char button press
class SerialButton(SerialReader):

    def __init__(self, dev, char, rate, verbose):
        super().__init__(dev, rate, verbose)
        self.char = ord(char) # button press event char byte value
        self.on_press = None  # button press callback: def button_pressed(button)

    # read serial bytes, send message if self.char byte is found
    def recv(self, serial_bytes):
        for c in serial_bytes: # send once per message
            if c == self.char:
                if self.verbose:
                    print(f"button: pressed")
                if self.on_press: self.on_press(self)
                break

# switch value char switch
class SerialSwitch(SerialReader):

    def __init__(self, dev, chars, rate, verbose):
        super().__init__(dev, rate, verbose)
        self.chars = [ord(chars[0]), ord(chars[1])] # switch value event char byte values: [off, on]
        self.on_change = None # switch value change callback: def switch_changed(switch, value)

    # read serial bytes, send message if either byte in self.chars is found
    def recv(self, serial_bytes):
        for c in serial_bytes:
            value = -1
            if c == self.chars[0]:
                value = 0 # off
            elif c == self.chars[1]:
                value = 1 # on
            if value != -1:
                if self.verbose:
                    print(f"switch: {value}")
                if self.on_change: self.on_change(self, value)

##### button/switch -> osc

from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_message_builder

# send message on button press event
def button_pressed(button):
    message = osc_message_builder.OscMessageBuilder(address=args.message)
    sender.send(message.build())

# send message on switch value change event
def switch_changed(switch, value):
    message = osc_message_builder.OscMessageBuilder(address=args.message)
    message.add_arg(value)
    sender.send(message.build())

##### signal

# signal handler for nice exit
def sigint_handler(signum, frame):
    reader.stop()

##### main

if __name__ == '__main__':

    # parse
    args = parser.parse_args()

    # button/switch
    try:
        if args.switch:
            reader = SerialSwitch(dev=args.dev, chars=args.switchchars, rate=args.rate,
                                  verbose=args.verbose)
        else:
            reader = SerialButton(dev=args.dev, char=args.buttonchar, rate=args.rate,
                                  verbose=args.verbose)
    except Exception as e:
        print(e)
        exit(1)

    # osc sender
    sender = SimpleUDPClient(args.address, args.port)
    if args.switch:
        reader.on_change = switch_changed
    else:
        reader.on_press = button_pressed

    # start
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        reader.open()
        reader.start()
    finally:
        reader.close()
