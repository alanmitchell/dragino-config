#!/usr/bin/env python3
"""This script configures a Dragino RS485-LN sensor to retrieve data from a few
different types of devices supporting the MODBUS RTU serial protocol:

    * Spire T-Mag BTU meter.
    * Spire EF-40 BTU meter.
    * Peacefair PZEM-016 electrical power sensor.

Make sure to copy config_example.py to config.py and edit config.py appropriately.
"""
import port
from questionary import select, text

print('\n---------------------------------')
p = port.Port()
p.try_command('AT+DEUI=?')
print('---------------------------------\n')

# Ask for minutes between Transmissions
mins = text('Enter Minutes between LoRa Transmissions:').ask()
tdc = int(float(mins) * 60000.)

# data rate
choices = {
    'Long Distance (SF9)': 1,
    'Medium Distance (SF8)': 2,
    'In Building (SF7)': 3,
}
dr_str = select(
    'Select Data Rate for Sensors:',
    choices = [*choices],
    default = list(choices.keys())[0]
).ask()
dr = choices[dr_str]

p.set_timeout(2.0)

# reset to factory defaults
p.try_command('AT+FDR')

p.set_timeout(0.5)
p.set_at('cmdear', '1,9')

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

commands_ef40 = [
    ('payver', 2), 
    ('command1', '01 03 00 00 00 04,1'),
    ('cmddl1', 1000),
    ('command2', '01 03 00 10 00 04,1'),
    ('cmddl2', 1000),
    ('command3', '01 03 00 20 00 04,1'),
    ('cmddl3', 1000),
]

commands_pzem = [
    ('payver', 9), 
    ('command1', '01 04 00 00 00 09,1'),
    ('cmddl1', 1000),
]

set_cmds = [
    ('che', 2), 
    ('tdc', tdc), 
    ('mbfun', 1), 
    ('dr', dr), 
    ('adr', 0),
    ('baudr', 9600)
    ] + commands_ef40

for cmd, val in set_cmds:
    p.set_at(cmd, val)

p.set_timeout(6.0)
p.try_command('ATZ')
p.set_timeout(1.5)
print('--------------------------------------')

keep = (
    'ADR', '+DR', '+TDC', '+VER', 'MBFUN', 'PAYVER', '+CHE', 'COMMAND', 'BAUDR',
)
p.try_command('AT+CFG', filter=keep)

p.close_port()
