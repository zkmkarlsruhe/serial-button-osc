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
    "-c", "--char", dest="char", metavar="CHAR",
    default="3", help="serial char for button press, default: '3'")
args = parser.add_argument(
    "-v", "--verbose", action="store_true", dest="verbose",
    help="enable verbose printing")

##### SerialButton

import serial
import time

class SerialButton:

    def __init__(self, dev, char, rate=115200, verbose=True):
        self.serial = serial.Serial(dev, rate) # serial port
        self.char = ord(char) # button press event char byte value
        self.on_press = None  # button press callback: def button_pressed(button)
        self.interval = 0.1
        self.is_running = True
        self.verbose = verbose
        if self.verbose:
            print(f"serialbutton: created {dev} {rate}")

    # open serial port for reading
    def open(self):
        if not self.serial.is_open:
            self.serial.open()
            if self.verbose:
                print("serialbutton: open")

    # close serial port
    def close(self):
        if self.serial.is_open:
            self.serial.close()
            if self.verbose:
                print("serialbutton: close")

    # start synchronous run loop
    def start(self):
        self.is_running = True
        if self.verbose:
            print("serialbutton: start")
        while self.is_running:
            self.update()
            time.sleep(self.interval)
        self.is_running = False
        if self.verbose:
            print("serialbutton: stop")

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
                print(f"serialbutton: {recv}")
            for c in recv: # send once per message
                if c == self.char:
                    print(f"serialbutton: pressed")
                    if self.on_press: self.on_press(self)
                    break

##### button -> osc

from pythonosc.udp_client import SimpleUDPClient
from pythonosc import osc_message_builder

# send message on button press event
def button_pressed(button):
    message = osc_message_builder.OscMessageBuilder(address=args.message)
    sender.send(message.build())

##### signal

# signal handler for nice exit
def sigint_handler(signum, frame):
    button.stop()

##### main

if __name__ == '__main__':

    # parse
    args = parser.parse_args()

    # button
    try:
        button = SerialButton(dev=args.dev, char=args.char, rate=args.rate,
                              verbose=args.verbose)
    except Exception as e:
        print(e)
        exit(1)

    # osc sender
    sender = SimpleUDPClient(args.address, args.port)
    button.on_press = button_pressed

    # start
    signal.signal(signal.SIGINT, sigint_handler)
    try:
        button.open()
        button.start()
    finally:
        button.close()
