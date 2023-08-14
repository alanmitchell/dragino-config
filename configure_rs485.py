#!/usr/bin/env python3
import time
from pathlib import Path
from serial import Serial
from questionary import select, text

# Port object for Dragino device
p = None

def open_dev():
    global p
    # Find USB COM port
    com_port = str(list(Path('/dev').glob('ttyUSB*'))[0])
    p = Serial(com_port, timeout=1.0)
    return read_all()

def close_dev():
    p.close()

def read_all(filter=None):
    resp = ''
    while True:
        tstart = time.time()
        lin = p.readline().decode('utf-8').strip()
        if time.time() - tstart > p.timeout*0.9 and len(lin) == 0:
            return resp
        if len(lin):
            if filter:
                do_print = False
                for substr in filter:
                    if substr in lin:
                        do_print = True
                        break
            else:
                do_print = True    
            if do_print:
                print(lin)
        if resp:
            resp += f'\n{lin}'
        else:
            resp = lin

def try_command(cmd, filter=None):
    for _ in range(2):
        print('Sending:', cmd)
        w_cmd = bytes(f'{cmd}\r\n', 'utf-8')
        p.write(w_cmd)
        resp = read_all(filter=filter)
        if "Incorrect" in resp:
            # not logged in. do that and retry.
            p.write(bytes('123456\r\n', 'utf-8'))
            read_all()
        else:
            return resp

def set_at(at_cmd, val):
    p.reset_input_buffer()
    resp = try_command(f'AT+{at_cmd.upper()}={val}')
    return resp

# Ask for minutes between Transmissions
mins = text('Enter Minutes between LoRa Transmissions:').ask()
tdc = int(float(mins) * 60000.)

print('\n---------------------------------')
open_dev()
try_command('AT+DEUI=?')
print('---------------------------------\n')

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

p.timeout = 2.0
# reset to factory defaults
try_command('AT+FDR')

p.timeout=0.5
set_at('cmdear', '1,9')

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
    set_at(cmd, val)

p.timeout = 6.0
try_command('ATZ')
p.timeout = 1.5
print('--------------------------------------')

keep = (
    'ADR', '+DR', '+TDC', '+VER', 'MBFUN', 'PAYVER', '+CHE', 'COMMAND', 'BAUDR',
)
try_command('AT+CFG', filter=keep)

close_dev()
