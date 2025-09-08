# Initial prototype of subsystem 2 milestone 2 code
# Created By : Eden Abrahams & Majd Abou Zaki
# Last Edited Date: 08/09/2025
# version = 1.4
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

#set the pins to digital output (for LEDs)
for pin in ledPinNums:
    board.set_pin_mode_digital_output(pin)

def turn_off():
    '''
    function makes each pin to output 0V (all off)
    args: None
    returns: None
    '''
    for pin in ledPinNums:
        board.digital_write(pin, 0)


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

lightState = "TL4_Green"
startTime = time.time()

pedPressed = False #is a pedestrian button pressed
pedPressTime = None #time at press
pedPrinted = False #has this been printed 
currentWayEnding = None   # "TL4" or "TL5" 


try:
    while True:
        #at any point in time, the current time is defined
        #time so far elapsed is then established as current - start
        currentTime = time.time()
        elapsedTime = currentTime - startTime
        #reading the button presses and printing accordingly
        if board.digital_read(pb1)[0] == 1 or board.digital_read(pb2)[0] == 1:
            if not pedPressed:
                pedPressed = True 
                pedPressTime = currentTime
                #avoid multiple presses affecting prints and cycles via tracking of printed
                if not pedPrinted:
                    if board.digital_read(pb1)[0] == 1:
                        print("PB1 was pressed")
                        pedPrinted = True
                    else:
                        print("PB2 was pressed")
                        pedPrinted = True
        if pedPressed and (currentTime - pedPressTime >= pedDelayBeforeSequence):
        #checked if button is pressed that elapsed time of 2 seconds has passed
            if lightState not in ("TL5_Red"): #2.R1 if TL5 is not red, goes yellow, getting ready for peds
                currentWayEnding = "TL5"
                make(tl5G, 0); make(tl5Y, 1); make(tl5R, 0)
                make(tl4G, 0); make(tl4Y, 0); make(tl4R, 1)
            else:
                currentWayEnding = "TL4" #then now make TL4 yellow, getting ready for peds
                make(tl4G, 0); make(tl4Y, 1); make(tl4R, 0)
                make(tl5G, 0); make(tl5Y, 0); make(tl5R, 1)
            state = "Current_Stream_Yellow"
            startTime = currentTime
            pedPrinted = False
        
        #setting up a loop for when nothing is pressed
        if lightState == "TL4_Green":
            if elapsedTime >= durTl4Green: #if tl4 has been green for 20s
                make(tl4G, 0); make(tl4Y, 1); make(tl4R, 0)
                state = "TL4_Yellow"
                startTime = currentTime
        elif state == "TL4_Yellow":
            if elapsedTime >= durTl4Yellow:
                make(tl4G, 0); make(tl4Y, 0); make(tl4R, 1)
                make(tl5G, 1); make(tl5Y, 0); make(tl5R, 0)
                state = "TL5_Green"
                startTime = currentTime
        elif state == "TL5_Green":
            if elapsedTime >= durTl4Yellow: #check if 3s have passed, make tl5 yellow
                make(tl5G, 0); make(tl5Y, 1); make(tl5R, 0)
                state = "TL5_Yellow"
                startTime = currentTime
        elif state == "TL5_Yellow":
            if elapsedTime >= durTl5Yellow:
                make(tl4G, 1); make(tl4Y, 0); make(tl4R, 0)
                make(tl5G, 0); make(tl5Y, 0); make(tl5R, 1)
                state = "TL4_Green"
                startTime = currentTime
        #pedestrian actions now:
        #now that the current stream of traffic has turned yellow for 3s,
        #all traffic can turn red and peds can cross
        elif state == "Current_Stream_Yellow":
            if currentTime >= durTl5Yellow and currentWayEnding == "TL5": 
                make(tl5G, 0); make(tl5Y, 0); make(tl5R, 1)
                make(pl1G, 1); make(pl1R, 0)
                make(pl2G, 1); make(pl2R, 0)
                state = "Ped_Green"
                startTime = currentTime
            elif currentTime >= durTl4Yellow and currentWayEnding == "TL4": 
                make(tl4G, 0); make(tl4Y, 0); make(tl4R, 1)
                make(pl1G, 1); make(pl1R, 0)
                make(pl2G, 1); make(pl2R, 0)
                state = "Ped_Green"
                startTime = currentTime
        elif state == "Ped_Green":
            if currentTime >= durPedGreen:
                make(pl1G, 0); make(pl2G, 0)
                state = "Ped_Flash_Red"
                startTime = currentTime
        elif state == "Ped_Flash_Red":
            #need to add a way to make it flash
            pedPressed = False; pedPressTime = None
            time.sleep(0.1)

            
            
except KeyboardInterrupt:
    turn_off()
    board.shutdown()

