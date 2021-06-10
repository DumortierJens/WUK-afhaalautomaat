import serial

class NextionDisplay:

    __cmd_end = bytearray(3)
    for i in range(3):
        __cmd_end[i] = 0xFF


    def __init__(self, port, baud=9600):
        self.client = serial.Serial(port, baud)

        self.set_page(0)

        self.__cmd('wup=0') # Set wake up page
        self.__cmd('thup=1') # Wake up on touch
        self.__cmd('thsp=300') # Sleep on {x}s no touch

        self.wake_up()
        

    def __cmd(self, cmd):
        self.client.write(cmd.encode())
        self.client.write(self.__cmd_end)


    def set_page(self, value):
        self.__cmd(f'page {value}')
    

    def set_text(self, name, value):
        self.__cmd(f'{name}.txt="{value}"')


    def set_value(self, name, value):
        self.__cmd(f'{name}.val="{value}"')


    def set_brightness(self, value):
        self.__cmd(f'dims={value}')


    def sleep(self):
        self.__cmd('sleep=1')


    def wake_up(self):
        self.__cmd('sleep=0')


    def read(self):
        try:
            if self.client.in_waiting:
                return self.client.read_until(self.__cmd_end)[:-3].decode("utf-8") 
        except Exception:
            pass


    def close(self):
        self.client.close()