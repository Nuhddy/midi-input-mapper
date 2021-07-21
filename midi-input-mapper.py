#! /usr/bin/env python3

import rtmidi
import os
import yaml
import argparse
import sys


def get_args():
    p = argparse.ArgumentParser(description="Map MIDI input to commands")
    p.add_argument("-l", "--list",
                   action="store_true",
                   help="prints a list of available MIDI input devices")
    p.add_argument("-k", "--keycodes",
                   action="store_true",
                   help="continuously prints keycodes from MIDI input")
    p.add_argument("-p", "--port",
                   type=int,
                   help="device port to open")
    p.add_argument("-c", "--config",
                   default="~/.config/midi-device-mapper/config.yaml",
                   help="path to (yaml) config file" +
                   "(default: ~/.config/midi-device-mapper/config.yaml)")
    args = p.parse_args()
    return args


def read_config(file_path):
    try:
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
        return config
    except:
        print("Config file does not exist")
        sys.exit(1)


def list_ports():
    ports = range(midi_in.getPortCount())
    if ports:
        for i in ports:
            print(str(i) + ": " + midi_in.getPortName(i))
    else:
        print("No available MIDI input ports")
        sys.exit(1)


def choose_port():
    list_ports()
    d = int(input("Choose device: "))
    return d


def print_message(midi):
    if midi.isNoteOn():
        msg = ["ON", midi.getNoteNumber(), midi.getVelocity()]
    elif midi.isNoteOff():
        msg = ["OFF", midi.getNoteNumber(), midi.getVelocity()]
    elif midi.isController():
        msg = ["CTRL", midi.getControllerNumber(), midi.getControllerValue()]

    print("%-4s %3i %3i" % (msg[0], msg[1], msg[2]))


def print_keycodes(port):
    midi_in.openPort(port)
    while True:
        m = midi_in.getMessage(250)
        if m:
            print_message(m)


def eval_input(port):
    midi_in.openPort(port)
    while True:
        m = midi_in.getMessage(250)
        if m:
            note = m.getNoteNumber()
            if note in config:
                if m.isNoteOn():
                    cmd = config[note]
                    os.system(cmd)
                elif m.isController():
                    val = val_pct(m.getControllerValue())
                    cmd = " ".join((config[note], str(val)))
                    os.system(cmd)


def val_pct(val):
    res = round(float(val) / 127, 2)
    return res


if __name__ == "__main__":
    args = get_args()

    midi_in = rtmidi.RtMidiIn()

    if args.list:
        list_ports()
    else:
        if args.port:
            port = args.port
        else:
            port = choose_port()

        if args.keycodes:
            print_keycodes(port)
        else:
            config = read_config(args.config)
            eval_input(port)
