from serial import Serial
import time


class ArduinoProgram:
    GENERAL_FLASH = 1
    START_LOADING = 2
    STOP_LOADING = 3
    PMI_START_SHOOTING = 4
    PMI_SUCCESS = 5
    PMI_FAIL = 6


def run_arduino_program(function: ArduinoProgram):
    with Serial(port='COM3', baudrate=115200, timeout=0.1) as arduino:
        time.sleep(1.65)
        arduino.write(str(function).encode())


run_arduino_program(ArduinoProgram.PMI_START_SHOOTING)
# run_arduino_program(ArduinoProgram.PMI_SUCCESS)
# run_arduino_program(ArduinoProgram.PMI_FAIL)

# run_arduino_program(ArduinoProgram.START_LOADING)
# time.sleep(5)
# run_arduino_program(ArduinoProgram.STOP_LOADING)
