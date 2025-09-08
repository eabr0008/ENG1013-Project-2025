# Initial prototype of subsystem 2 milestone 2 code
# Created By : Eden Abrahams & Majd Abou Zaki
# Created Date: 05/09/2025
# version = 1.2
from pymata4 import pymata4
board = pymata4.Pymata4()
import time

#assigning the push buttons and lights to digital pin numbers on the arduino:

#pb pin numbers:
pb1 = 12
pb2 = 13

#tl4 pin numbers:
tl4G = 2
tl4Y = 3
tl4R = 4

#tl5 pin numbers:
tl5G = 5
tl5Y = 6
tl5R = 7

#ped pin numbers:
pl1G = 8
pl1R = 9
pl2G = 10
pl2R = 11


ledPinNums = [tl4G,tl4Y,tl4R,tl5G,tl5Y,tl5R,pl1G,pl1R,pl2G,pl2R]

#Common Durations:

#traffic lights:
durTl4Green = 20 #tl4 is green for 20 seconds
durTl4Yellow = 3 #tl4 is yellow for 3 seconds
durTl5Green = 10 #tl5 is green for 20 seconds
durTl5Yellow = 3 #tl5 is yellow for 3 seconds

#pedestrian lights:
pedDelayBeforeSequence = 2 #wait 2 seconds before pedestrian actions
durPedGreen = 3 #pedestrian lights should turn green for 3 seconds
durPedFlash = 2 #flashes red for 2 seconds
flashFreq = 3 #just chose a random frequency for flashing red

#initialisations for inputs
board.set_pin_mode_digital(pb1)
board.set_pin_mode_digital(pb2)

def turn_off():
    '''
    function makes each pin to output 0V (all off)
    args: None
    returns: None
    '''
    for pin in ledPinNums:
        board.digital_write(pin, 0)
#set the pins to digital output (for LEDs)
for pin in ledPinNums:
    board.set_pin_mode_digital_output(pin)

def make(light, state):
    '''
    makes a light turn on off by writing its state
    args: light,state
    returns: None
    '''
    board.digital_write(light, state)
turn_off()
#make tl4 green to start
make(tl4G, 1); make(tl4Y, 0); make(tl4R, 0)
make(tl5G, 0); make(tl5Y, 0); make(tl5R, 1)
make(pl1G, 0); make(pl1R, 1)
make(pl2G, 0); make(pl2R, 1)
