import time
from pathlib import Path
from serial import Serial
import config


class Port:

    def __init__(self):
        self.p = Serial(config.port, timeout=1.0)
        print(self.read_all())

    def close_port(self):
        self.p.close()

    def set_timeout(self, timeout):
        self.p.timeout = timeout

    def read_all(self, filter=None):
        resp = ''
        while True:
            tstart = time.time()
            lin = self.p.readline().decode('utf-8').strip()
            if time.time() - tstart > self.p.timeout * 0.9 and len(lin) == 0:
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

    def try_command(self, cmd, filter=None):
        for _ in range(2):
            print('Sending:', cmd)
            w_cmd = bytes(f'{cmd}\r\n', 'utf-8')
            self.p.write(w_cmd)
            resp = self.read_all(filter=filter)
            if "Incorrect" in resp:
                # not logged in. do that and retry.
                self.p.write(bytes('123456\r\n', 'utf-8'))
                self.read_all()
            else:
                return resp

    def set_at(self, at_cmd, val):
        self.p.reset_input_buffer()
        resp = self.try_command(f'AT+{at_cmd.upper()}={val}')
        return resp
