# Initial prototype of subsystem 2 milestone 2 code
# Created By : Eden Abrahams & Majd Abou Zaki
# Last Edited Date: 10/09/2025
# version = 2.1
'''
Used chatGPT 5 in the lines 174,176,177, where it was quite difficult 
to find an elegent way to make the pedestrian light flash smoothly
https://chatgpt.com/s/t_68bf7de1f4f08191a590d628d14a0a68
'''
from pymata4 import pymata4
board = pymata4.Pymata4()
import time

#assigning the push buttons and lights to digital pin numbers on the arduino:

#pb pin numbers:
pb1 = 1
pb2 = 2

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
durTl5Green = 10 #tl5 is green for 10 seconds
durTl5Yellow = 3 #tl5 is yellow for 3 seconds

#pedestrian lights:
pedDelayBeforeSequence = 2 #wait 2 seconds before pedestrian actions
durPedGreen = 3 #pedestrian lights should turn green for 3 seconds
durPedFlash = 2 #ped flashes red for 2 seconds 
flashHz = 3 #flash 3 times per second

#initialisations for inputs
#needs to be analogue due to bouncing and noise issues
board.set_pin_mode_analog_input(pb1)
board.set_pin_mode_analog_input(pb2)

#set the pins to digital output (for LEDs)
for pin in ledPinNums:
    board.set_pin_mode_digital_output(pin)
def turn_off():
    '''
    function makes each pin to output 0V (all off)
    
    Parameters: None
    
    Returns: None
    '''
    for pin in ledPinNums:
        board.digital_write(pin, 0)


def make(light, state):
    '''
    makes a light turn on off by writing its state
    
    Parameters: 
        light (int): Pin number for light
        state (int): 1 = On, 0 = Off
    
    Returns: None
    '''
    board.digital_write(light, state)
turn_off()
#make tl4 green to start
make(tl4G, 1)
make(tl4Y, 0)
make(tl4R, 0)
make(tl5G, 0)
make(tl5Y, 0)
make(tl5R, 1)
make(pl1G, 0)
make(pl1R, 1)
make(pl2G, 0)
make(pl2R, 1)

state = "TL4_Green"
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
        analogHigh = 1023
        # read buttons (active-high, 1023 means is pressed)
        pb1Pressed = board.analog_read(pb1)[0] == analogHigh
        pb2Pressed = board.analog_read(pb2)[0] == analogHigh
        #reading the button presses and printing accordingly
        if (pb1Pressed or pb2Pressed) and not pedPressed:
            pedPressed = True 
            pedPressTime = currentTime
            #avoid multiple presses affecting prints and cycles via tracking of printed
            if pb1Pressed:
                print("PB1 was pressed")
                pedPrinted = True
            else:
                print("PB2 was pressed")
                pedPrinted = True
        if pedPressed and (currentTime - pedPressTime >= pedDelayBeforeSequence) and state not in ("Current_Stream_Yellow", "Ped_Green", "Ped_Flash_Red"):
            #final checks before initialising pedestrian actions
            #checked if button is pressed that elapsed time of 2 seconds has passed
            if state in ("TL5_Green", "TL5_Yellow"): #2.R1 if TL5 is not red, goes yellow, getting ready for peds
                currentWayEnding = "TL5"
                make(tl5G, 0)
                make(tl5Y, 1)
                make(tl5R, 0)
                make(tl4G, 0)
                make(tl4Y, 0)
                make(tl4R, 1)
            else:
                currentWayEnding = "TL4" #then now make TL4 yellow, getting ready for peds
                make(tl4G, 0)
                make(tl4Y, 1)
                make(tl4R, 0)
                make(tl5G, 0)
                make(tl5Y, 0)
                make(tl5R, 1)
            state = "Current_Stream_Yellow"
            startTime = currentTime
            pedPrinted = False
            continue
        
        #setting up a loop for when nothing is pressed
        if state == "TL4_Green":
            if elapsedTime >= durTl4Green: #if tl4 has been green for 20s
                make(tl4G, 0)
                make(tl4Y, 1)
                make(tl4R, 0)
                make(tl5G, 0)
                make(tl5Y, 0)
                make(tl5R, 1)
                state = "TL4_Yellow"
                startTime = currentTime
                continue
        elif state == "TL4_Yellow":
            if elapsedTime >= durTl4Yellow:
                make(tl4G, 0)
                make(tl4Y, 0)
                make(tl4R, 1)
                make(tl5G, 1)
                make(tl5Y, 0)
                make(tl5R, 0)
                state = "TL5_Green"
                startTime = currentTime
                continue
        elif state == "TL5_Green":
            if elapsedTime >= durTl5Green: #check if 3s have passed, make tl5 yellow
                make(tl5G, 0)
                make(tl5Y, 1)
                make(tl5R, 0)
                make(tl4G, 0)
                make(tl4Y, 0)
                make(tl4R, 1)
                state = "TL5_Yellow"
                startTime = currentTime
                continue
        elif state == "TL5_Yellow":
            if elapsedTime >= durTl5Yellow:
                make(tl5G, 0)
                make(tl5Y, 0)
                make(tl5R, 1)
                make(tl4G, 1)
                make(tl4Y, 0)
                make(tl4R, 0)
                startTime = currentTime
                state = "TL4_Green"
                continue
        #pedestrian actions now:
        #now that the current stream of traffic has turned yellow for 3s,
        #all traffic can turn red and peds can cross
        elif state == "Current_Stream_Yellow":
            if elapsedTime >= durTl5Yellow and currentWayEnding == "TL5": 
                make(tl5G, 0)
                make(tl5Y, 0)
                make(tl5R, 1)
                make(pl1G, 1)
                make(pl1R, 0)
                make(pl2G, 1)
                make(pl2R, 0)
                state = "Ped_Green"
                startTime = currentTime
                continue
            elif elapsedTime >= durTl4Yellow and currentWayEnding == "TL4": 
                make(tl4G, 0)
                make(tl4Y, 0)
                make(tl4R, 1)
                make(pl1G, 1)
                make(pl1R, 0)
                make(pl2G, 1)
                make(pl2R, 0)
                state = "Ped_Green"
                startTime = currentTime
                continue
        elif state == "Ped_Green":
            if elapsedTime >= durPedGreen:
                make(pl1G, 0)
                make(pl2G, 0)
                state = "Ped_Flash_Red"
                startTime = currentTime
                continue
        elif state == "Ped_Flash_Red":
            #to work out if LED should be one or off
            #multiplying by flashHz turns it into flashes per second
            #int() makes sure that is is only 1 or 0
            phase = int((elapsedTime) * flashHz) % 2
            #if phase is 1, then it will turn on, otherwise it will be off
            make(pl1R, 1 if phase else 0)
            make(pl2R, 1 if phase else 0)
            if elapsedTime >= durPedFlash:
                make(pl1R, 1)
                make(pl2R, 1)
                make(tl4G, 1)
                make(tl4Y, 0)
                make(tl4R, 0)
                make(tl5G, 0)
                make(tl5Y, 0)
                make(tl5R, 1)
                state = "TL4_Green"
                startTime = currentTime
                currentWayEnding = None
                pedPressed = False
                pedPressTime = None
                continue
            smallSleep = 0.1
            time.sleep(smallSleep)
       
except KeyboardInterrupt:
    print("Shutting Down...")
    turn_off()
    make(pl1G, 0)
    make(pl2G, 0)
    make(pl1R, 0)
    make(pl2R, 0)
    board.shutdown()