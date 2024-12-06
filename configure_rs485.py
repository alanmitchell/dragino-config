#!/usr/bin/env python3
"""This script configures a Dragino RS485-LN sensor to retrieve data from a few
different types of devices supporting the MODBUS RTU serial protocol:

    * Spire T-Mag BTU meter.
    * Spire EF-40 BTU meter.
    * Micro820 PLC
    * WattNode MODBUS Power Sensor, WND-WR-MB
    * Peacefair PZEM-016 electrical power sensor.

Run the configuration tool by using the following command:

    python configure_rs485.py <COM port>

"""

# These are the list of AT commands needed for each possible MODBUS device. There
# also is a list of AT commands that are common to all devices, and that list is
# in the code following this preliminary section.

# Testing determined that the register addresses in the TMag manual are 0-based
# so they can be used as-is with the RS485-LN.  Also determined that Function Code
# 4 needed to be used.
commands_tmag = [
    ('payver', 1), 
    ('command1', '01 04 10 10 00 02,1'),
    ('cmddl1', 1000),
    ('command2', '01 04 10 26 00 08,1'),
    ('cmddl2', 1000),
]

# EF40 needs function code 03.  Need to subtract 1 from the MODBUS addresses
# listed in the manual, as they are 1-based.
commands_ef40 = [
    ('payver', 2), 
    ('command1', '01 03 00 00 00 04,1'),
    ('cmddl1', 1000),
    ('command2', '01 03 00 10 00 04,1'),
    ('cmddl2', 1000),
    ('command3', '01 03 00 20 00 04,1'),
    ('cmddl3', 1000),
]

# PZEM-016 Electric Power Sensor.
commands_pzem = [
    ('payver', 9), 
    ('command1', '01 04 00 00 00 09,1'),
    ('cmddl1', 1000),
]

# Micro820 PLC
commands_micro820 = [
    ('payver', 99),
    ('baudr', 19200),
    ('command1', '01 01 00 00 00 0c,1'),
    ('cmddl1', 1000),
    ('command2', '01 03 00 00 00 28,1'),
    ('cmddl2', 1000),
]

# WattNode MODBUS Power Sensor
# Note that all DIP Switches on the sensor should be in the 0 position except
# for DIP Switch #1, which should be in the 1 position.
commands_wattnode = [
    ('payver', 3),
    ('command1', '01 03 03 f0 00 1a,1'),
    ('cmddl1', 1000),
    ('command2', '01 03 04 72 00 08,1'),
    ('cmddl2', 1000),
    ('command3', '01 03 04 8a 00 06,1'),
    ('cmddl3', 1000),
]

#---------------------
import sys
import port
from questionary import select, text

if len(sys.argv) != 2:
    print('You must provide the name of the Serial Port as a command line parameter.')
    print('For example:  configure_rs485 COM4')
    sys.exit()

com_port = sys.argv[1]

# Open the serial port to the Dragino
p = port.Port(com_port)

ask_for_inputs = True

while True:


    # Start by issuing a command to show the DEV EUI of
    # the Dragino RS485-LN device.
    print('\n---------------------------------')
    p.try_command('AT+DEUI=?')
    print('---------------------------------\n')

    if ask_for_inputs:
        # Pick type of MODBUS device. The values (not keys) in this dictionary must match
        # the suffixes on the "commands_" arrays above.
        choices = {
            'Spire T-Mag BTU Meter': 'tmag',
            'Spire EF40 BTU Meter': 'ef40',
            'Micro820 PLC': 'micro820',
            'WattNode MODBUS': 'wattnode',
            'Peacefair PZEM-016 Power Sensor': 'pzem',
        }
        dev_str = select(
            'Select MODBUS Device:',
            choices=[*choices],
            default=[*choices][0],
        ).ask()
        device = choices[dev_str]

        # Ask for minutes between Transmissions
        mins = text('Enter Minutes between LoRa Transmissions:', default='10').ask()
        tdc = int(float(mins) * 60000.)

        # select data rate
        if device in ('micro820', 'wattnode'):
            choices = {
                'Medium Distance (SF8)': 2,
                'In Building (SF7)': 3,
            }
        else:
            choices = {
                'Long Distance (SF9)': 1,
                'Medium Distance (SF8)': 2,
                'In Building (SF7)': 3,
            }
        dr_str = select(
            'Select Data Rate for Sensors:',
            choices = [*choices],
            default=[*choices][0],
        ).ask()
        dr = choices[dr_str]

    # --------------------
    # Start the configuration process

    # Get the list of commands for the chosen device.
    dev_cmds = locals()['commands_' + device]

    # Commands that are common to all devices
    common_cmds = [
        ('che', 2), 
        ('tdc', tdc), 
        ('mbfun', 1), 
        ('dr', dr), 
        ('adr', 0),
    ]

    p.set_timeout(2.0)

    # reset to factory defaults
    p.try_command('AT+FDR')

    p.set_timeout(0.5)
    # This erases all the MODBUS comannds, 1 - 10
    p.set_at('cmdear', '1,9')


    for cmd, val in common_cmds + dev_cmds:
        p.set_at(cmd, val)

    p.set_timeout(12.0)
    p.try_command('ATZ')
    p.set_timeout(3.0)
    print('--------------------------------------')

    keep = (
        'ADR', '+DR', '+TDC', '+VER', 'MBFUN', 'PAYVER', '+CHE', 'COMMAND', 'BAUDR', 'DEUI', 'APPEUI', 'APPKEY'
    )
    p.try_command('AT+CFG', filter=keep)

    choices = [
        'Configure another device the same way.',
        'Change inputs and configure another device',
        'Quit',
    ]
    next = select(
        'What do You want to Do Next?',
        choices=choices,
        default=choices[0]
    ).ask()
    if next == choices[0]:
        ask_for_inputs = False
    elif next == choices[1]:
        ask_for_inputs = True
    elif next == choices[2]:
        p.close_port()
        break

