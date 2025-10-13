# Subsystem 2 finalised code
# Created By : Eden Abrahams
# Last Edited Date: 13/10/2025
# version = 2.6
'''
Google search / ai overview was used to figure out line 68 and it's associated
error involving pymata not reading the ldr value immediately, small sleep was required.
Search: "ldr not reading values immediately"
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

#555 timer pin:
pin555 = 12

#LDR pin
pinLDR = 0


ledPinNums = [tl4G,tl4Y,tl4R,tl5G,tl5Y,tl5R,pl1G,pl1R,pl2G,pl2R]


#Common Durations:

#traffic lights:
durTl4Yellow = 3 #tl4 is yellow for 3 seconds
durTl5Yellow = 3 #tl5 is yellow for 3 seconds

#pedestrian lights:
pedDelayBeforeSequence = 2 #wait 2 seconds before pedestrian actions
durPedGreen = 3 #pedestrian lights should turn green for 3 seconds
durPedFlash = 2 #ped flashes red for 2 seconds 


#initialisations for inputs
#needs to be analogue due to bouncing / noise issues
board.set_pin_mode_analog_input(pb1)
board.set_pin_mode_analog_input(pb2)

#intialise 555 timer pin
board.set_pin_mode_digital_input(pin555)

#initialise LDR pin
board.set_pin_mode_analog_input(pinLDR)
time.sleep(0.1)

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
def set_cycle_durations(currentDay):
    '''
    set globally both greens for the entire traffic light cycle
    Parameters: currentDay (tells if day or night based on True or False Boolean)
    Returns: None
    '''
    global durTl4Green
    global durTl5Green
    if currentDay:
        durTl4Green = 20 # day timings
        durTl5Green = 10
    else:
        durTl4Green = 30 # night timings
        durTl5Green = 5

day = True # is it day or night cycle, start as day

pedPressed = False #is one of the pedestrian buttons pressed
pedPressTime = None #time at press
pedPrinted = False #has this been printed 
currentWayEnding = None   # "TL4" or "TL5" 

#30s inactivitive for pb's
pedInactiveDuration = 30
pedInactiveUntil = 0

#light thresholds
thresh1 = 600
thresh2 = 500

ldr0 = board.analog_read(pinLDR)[0]
ldr0 = 0 if ldr0 is None else ldr0
if ldr0 >= thresh1:
    day = True
elif ldr0 <= thresh2:
    day = False
else:
    day = True
set_cycle_durations(day)
try:
    while True:
        #read the ldr unsing analogue and set day or night based on reading
        ldr = board.analog_read(pinLDR)[0]
        if ldr >= thresh1:
            day = True
        elif ldr <= thresh2:
            day = False
        #at any point in time, the current time is defined
        #time so far elapsed is then established as current - start
        currentTime = time.time()
        elapsedTime = currentTime - startTime
        analogHigh = 1023
        # read buttons (active-high, 1023 means is pressed)
        pb1Pressed = board.analog_read(pb1)[0] == analogHigh #== means boolean therefore true when high
        pb2Pressed = board.analog_read(pb2)[0] == analogHigh

        #Ignore presses during the 30s, this is done before any action is taken on button presses
        if currentTime < pedInactiveUntil:
            pb1Pressed = False
            pb2Pressed = False

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
            #Start 30s when ped sequence runs
            pedInactiveUntil = currentTime + pedInactiveDuration #at start, time is 0 so thats fine,
            #when the time is 10s elapsed overall for example, the pedInactiveUntil becomes 40s (buttons ignored till that time value is reached)
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
                set_cycle_durations(day)
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
            clock = board.digital_read(pin555)[0]
            #if 1, then it will turn on, otherwise it will be off
            make(pl1R, 1 if clock else 0)
            make(pl2R, 1 if clock else 0)
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
                set_cycle_durations(day)
                continue
            #quick sleep so stuff doesn't overload
            quickSleep = 0.05
            time.sleep(quickSleep)
       
except KeyboardInterrupt:
    print("Shutting Down...")
    turn_off()
    make(pl1G, 0)
    make(pl2G, 0)
    make(pl1R, 0)
    make(pl2R, 0)
    board.shutdown()