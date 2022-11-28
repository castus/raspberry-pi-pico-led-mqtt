from machine import Pin, SoftI2C

from i2c_lcd import I2cLcd

class AbstractLogger:
    def clear(self):
        # Clears the LCD display and moves the cursor to the top left corner
        pass

    def display_on(self):
        # Turns on (i.e. unblanks) the LCD
        pass

    def display_off(self):
        # Turns off (i.e. blanks) the LCD
        pass

    def move_to(self, cursor_x, cursor_y):
        # Moves the cursor position to the indicated position. The cursor
        # position is zero based (i.e. cursor_x == 0 indicates first column).
        pass

    def putstr(self, string):
        # Write the indicated string to the LCD at the current cursor
        # position and advances the cursor position appropriately.
        pass


class LCDLogger(AbstractLogger):
    def __init__(self):
        i2c = SoftI2C(sda=Pin(8), scl=Pin(9), freq=400000)
        devices = i2c.scan()

        if len(devices) == 0:
          print("No i2c device !")
        else:
          print('i2c devices found:', len(devices))

          for device in devices:
            print("Decimal address: ", device,
                  " | Hexa address: ", hex(device))

        I2C_ADDR = i2c.scan()[0]
        self.lcd = I2cLcd(i2c, I2C_ADDR, 2, 16)

    def clear(self):
        self.lcd.clear()

    def display_on(self):
        self.lcd.display_on()

    def display_off(self):
        self.lcd.display_off()

    def move_to(self, cursor_x, cursor_y):
        self.lcd.move_to(cursor_x, cursor_y)

    def putstr(self, string):
        self.lcd.putstr(string)
        print(string)


class TerminalLogger(AbstractLogger):
    def clear(self):
        pass

    def display_on(self):
        pass

    def display_off(self):
        pass

    def move_to(self, cursor_x, cursor_y):
        pass

    def putstr(self, string):
        print(string)
