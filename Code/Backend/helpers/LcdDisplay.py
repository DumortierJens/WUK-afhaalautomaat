from RPi import GPIO
import time

class LcdDisplay:

    __inst_function_set = 0x20
    __inst_function_set__8bit = 0x10
    __inst_function_set__2lines = 0x08

    __inst_display_control = 0x08
    __inst_display_control__display_on = 0x04
    __inst_display_control__cursor_on = 0x02
    __inst_display_control__blink_on = 0x01

    __inst_clear_display = 0x01
    __inst_return_home = 0x02
    __instr_entry_mode_set = 0x06
    __inst_set_ddram = 0x80

    def __init__(self, pin_rs, pin_e, data_pins):
        self.E = pin_e
        self.RS = pin_rs
        self.DATA = data_pins

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.E, self.RS], GPIO.OUT)
        GPIO.setup(self.DATA, GPIO.OUT)

        self.__init_LCD()

    
    def __set_bits(self, value):
        for i in range(4):
            GPIO.output(self.DATA[i], value & (1 << i))
        

    def __send_4_bits(self, value):
        GPIO.output(self.E, 1)
        
        self.__set_bits(value)

        GPIO.output(self.E, 0)
        time.sleep(0.0000005)


    def __send(self, value, mode):
        # Set mode
        GPIO.output(self.RS, mode)
        time.sleep(0.0000001)

        # Send 2x 4 bits
        self.__send_4_bits((value & 0xF0) >> 4)
        self.__send_4_bits(value & 0x0F)

        time.sleep(0.00005)


    def send_instruction(self, value):
        self.__send(value, 0)


    def send_character(self, value):
        self.__send(value, 1)


    def __init_LCD(self):

        # Startup procedure
        time.sleep(0.05)
        self.__send_4_bits(0x03)
        time.sleep(0.005)
        self.__send_4_bits(0x03)
        time.sleep(0.0002)
        self.__send_4_bits(0x03)
        
        self.__send_4_bits(0x02) # Set 4 bit mode
        self.send_instruction(self.__inst_function_set | self.__inst_function_set__2lines) # Set function set
        self.send_instruction(self.__inst_display_control | self.__inst_display_control__display_on) # Set display control
        self.send_instruction(self.__instr_entry_mode_set) # Set entry mode
        self.clear() # Clear display


    def clear(self):
        self.send_instruction(self.__inst_clear_display)
        time.sleep(1)
    

    def set_cursor_position(self, line, column):
        instruction = self.__inst_set_ddram | column | (line << 6)
        self.send_instruction(instruction)  


    def write_message(self, message):
        for i in range(len(message)):
            character = ord(message[i])
            self.send_character(character)

            if i == 15:
                self.set_cursor_position(1, 0)


    def close(self):
        self.send_instruction(self.__inst_display_control) # Turn off lcd
        GPIO.cleanup(self.DATA)
        GPIO.cleanup([self.RS, self.E])
        

if __name__ == '__main__':
    # Lcd Display
    pin_lcd_rs = 20
    pin_lcd_e = 21
    pins_lcd_data = [6, 13, 19, 26]   

    lcd_display = LcdDisplay(pin_lcd_rs, pin_lcd_e, pins_lcd_data)  
    lcd_display.write_message('Test')

    time.sleep(2)

    lcd_display.close()