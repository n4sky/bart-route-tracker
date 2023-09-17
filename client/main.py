##############################
###        IMPORTS         ###
##############################
import requests #mrequests as requests
import network
import json
from time import sleep
import machine
import _thread
# for background fetches of data while the existing trains are still cycling
# https://bytesnbits.co.uk/multi-thread-coding-on-the-raspberry-pi-pico-in-micropython

### Display-Related ###
from pimoroni import RGBLED
from picographics import PicoGraphics, DISPLAY_PICO_DISPLAY, PEN_P8 #P8 is standard 8-bit for each color, RGB332 is for sprites and such
from trainscheduledisplay import TrainScheduleDisplay

### WI-FI Secrets ###
import secrets

##############################
###       CONSTANTS        ###
##############################
DISPLAY = PicoGraphics(display=DISPLAY_PICO_DISPLAY, rotate=180, pen_type=PEN_P8)
LED = RGBLED(6, 7, 8)   # though the physical pin numbers are 9, 10, 11, the 
                        # GPIO pin numbers (see pico pinout) are 6, 7, 8
                                              
### API Requests ###
BASE_URL = "ENDPOINT_GOES_HERE"

           
##############################
###      GLOBAL VARS       ###
##############################

# Global variables for the current set of bart results
bart_results = {}
results_lock = _thread.allocate_lock()

# Class in trainscheduledisplay.py that contains all methods
# to display train data on screen
screen = TrainScheduleDisplay(DISPLAY, LED)

##############################
###       FUNCTIONS        ###
##############################


'''
Function connects Pico W to the internet and
displays a message when it does so successfully
'''
def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.WIFI_PASSWORD)
    
    waiting_count = 0
    while not wlan.isconnected():
        screen.turn_indicator_on()
        waiting_message = 'Waiting for connection'
        for i in range(waiting_count): waiting_message += "."
        
        screen.render_message(waiting_message)
        
        waiting_count += 1
        waiting_count = waiting_count % 4
        screen.turn_indicator_off()
        sleep(1)
    
    screen.render_message("Successfully connected to the internet!")
    print(str(wlan.ifconfig())) # show internet information
    sleep(2)

'''
Function intakes data from get_bart_arrival_times()
and modifies the global variable bart_results with the data
1) An empty dict (only expected at startup)
2) A dict with "Error" as a single key, mapped to a description string
2) A dict with ETAs for destinations e.g. "SFO/Millbrae" : ["1", "5"]

Note that if 2) is what's there, a valid value is "Leaving" in lieu of a minute string.
'''

def render_results():
    global bart_results, results_lock
    
    # render messages in perpetuity
    while(True):
        results_lock.acquire()
        results_to_show = bart_results.copy() # get a copy of the shared resource at the current time
        results_lock.release()
        
        # still haven't received Bart results
        if len(results_to_show) == 0:
            screen.render_message("Asking BART for train ETAs...")
        
        # bad bart results
        elif "Error" in results_to_show:
            screen.render_message("Error: {0}".format(results_to_show["Error"]))

        # good results
        else:
            # convert all ETAs in result lists to integers, then sort ascending
            for train in results_to_show:
                timelist = []
                for string_num in results_to_show[train]:
                    if string_num is "Leaving": timelist.append(0)
                    else: timelist.append(int(string_num))
                    
                results_to_show[train] = sorted(timelist)
            
            # render as a set of destinations
            screen.render_rows(results_to_show)

'''
Function requests data from the BART API 
and returns one of two objects:
1) A dict with "Error" as a single key, mapped to a description string
2) A dict with ETAs for destinations e.g. "SFO/Millbrae" : ["1", "5"]

Note that if 2) is returned, a valid value is "Leaving" in lieu of a minute string.
'''
def get_bart_arrival_times():
    global bart_results, results_lock
    
    while(True):
        screen.turn_indicator_on()
               
        data_to_show = {}
        try:
            data_to_show = requests.get(BASE_URL)
        except Exception as e:
            data_to_show["Error"] = "There was an issue calling the server from this device."
        
        #  print("resp: {}".format(response.text))
        screen.turn_indicator_off()
        
        results_lock.acquire() # use semaphore to ensure no concurrent read/writes
        bart_results = data_to_show.json()
        results_lock.release()
        
        sleep(20) #check the api every 20sec


'''
Function displays a start-up visual sequence on the display
'''
def display_init_sequence():
    screen.show_startup_light()
    screen.animate_train_ascii()
    screen.show_init_message()

'''
Main Function

Note on threading (originally from https://forums.raspberrypi.com/viewtopic.php?t=341783)

"I have concluded that thread1 appears to have trouble communicating with the wifi chip,
that is also why you can't toggle the onboard LED which is connected to a pin there, not on the pico itself.
I managed to work around this by using thread0 to do networking and thread1 for the rest."
'''
def main():
    # pleasing visuals
    display_init_sequence()
    
    # Connect to internet
    connect()
    
    # Set two threads:
    # one to poll BART API at regular intervals (thread 0)
    # one to constantly display the results in bart_results (thread 1)
    second_thread = _thread.start_new_thread(render_results, ())
    get_bart_arrival_times()
    

if __name__ == "__main__":
    main()