import jpegdec # for jpeg decoding
import math
from time import sleep

### Images and metadata ###
TRAIN_STATION_FILE = "train_station.jpg"
TRAIN_STATION_SIZE = 40 #pixels, in height and width
TRAIN_ICON_FILE = "train_icon.jpg"
TRAIN_ICON_SIZE = 24 # pixels, in height and width

### For ASCII visualizations ###
# Produced using https://ascii-generator.site

TRAIN_ASCII = [                
  "  :----------------------------:. ",
  "+@%############################%@+",
  "@@.   .....   ......   .....    @@",
  "@@.  *@@%@@# .@@%%@@. *@@%@@#   @@",
  "@@.  *@+ =@# .@@  @@. *@+ =@#   @@",
  "@@.  +@@@@@*  @@@@@@. +@@@@@*   @@",
  "@@.                             @@",
  "@@.                             @@",
  "%@+----------------------------+@%",
  " =%@@##@@@%#@@@****%@@##@@@%#@@%= ",
  "  %@-  *@#  -@%    %@-  *@#  -@%  ",
  "  :@@##@@@%#@@-    :@@##@@@%#@@-  ",
  "    :--. .--:        :--. .--:    ",
]

# number of columns in each row of the train ASCII
NUM_COLS_TRAIN_ASCII = 34 

# ASCII decimal lookup for each of the symbols in the ASCII art above
# From https://www.ascii-code.com
CHAR_CODE_LOOKUP = { 
    ' ': 32,
    '@': 64,
    '+': 43,
    '%': 37,
    '#': 35,
    '=': 61,
    '-': 45,
    '*': 42,
    '.': 46,
    ':': 58
}

'''
Class to contain all methods related to the display of train schedules
on the Pimoroni Pico Display Pack attached to the Pico W
'''
class TrainScheduleDisplay:
    def __init__(self, display, led):
        self.display = display
        self.display.set_backlight(0.5)
        
        self.black = self.display.create_pen(0, 0, 0)
        self.white = self.display.create_pen(255, 255, 255)
        
        self.display_width, self.display_height = self.display.get_bounds()
        self.led = led
        
    # Flashes the onboard LED on and off once
    def show_startup_light(self):
        self.turn_indicator_on()
        self.turn_indicator_off()

    # Displays an init message on the screen, including calling .update()
    def show_init_message(self):
        # define lines
        line1 = "Welcome to"
        line2 = "Trainspotter!"
        
        # set important properties
        buffer_between_lines = 6
        self.display.set_font("bitmap14_outline")
        font_height = 14
        scale_value = 2
        line_height = font_height * scale_value
        
        '''figure out the locations'''
        # height is 28 (bitmap 14 * scale 2)
        # measure width as follows:
        width1 = self.display.measure_text(line1, scale=scale_value)
        width2 = self.display.measure_text(line2, scale=scale_value)
        
        # compute coordinates
        x1 = (self.display_width-width1)//2 # // is integer floor division
        x2 = (self.display_width-width2)//2 
        
        y1 = (self.display_height - (2 * line_height + buffer_between_lines))//2
        y2 = y1 + line_height + buffer_between_lines
        
        
        ''' Render the text '''
        self.clear_display()
        self.display.set_pen(self.white)
        self.display.text(line1, x1, y1, wordwrap=self.display_width, scale=scale_value)
        self.display.text(line2, x2, y2, wordwrap=self.display_width, scale=scale_value)
        self.display.update()
        sleep(2)

    # Turns the onboard indicator LED on to a color of green
    def turn_indicator_on(self):
        for i in range(1,10):
            self.led.set_rgb(0, i, 0)
            sleep(0.05)

    # Turns off the onboard LED indicator
    def turn_indicator_off(self):
        for i in reversed(range(0,10)):
            self.led.set_rgb(0, i, 0)
            sleep(0.05)
            
    # Clears the contents of the display.
    # DOES NOT refresh the display; need to call .update() for that
    def clear_display(self):
        self.display.set_pen(self.black)
        self.display.clear()
    
    # Legibly renders a textual message of any kind
    # on the display. This includes actually calling .update()
    def render_message(self, message):
        self.clear_display()
        
        self.display.set_pen(self.white)
        
        scale_value = 3
        self.display.set_font("bitmap8")
        text_height = scale_value * 8 # bitmap 8 height times scale value
        
        # deduce how wide the text will be, use that to compute the number of lines to
        # help with y-centering. This is a rough proxy, bc the display splits text more intelligently
        # along whitespace than it does by pixels. That said, whitespace splitting is always less
        # efficient than pixel splitting, meaning it always results in at least as many lines as
        # if split purely along pixels. So when centering in y direction, the risk is simply that it
        # will bleed one line lower than we think it should (i.e. be closer to the bottom than to the top).
        # We account for this by doing a 1/3 vs 2/3 split: 1/3 of remaining vertical space at the top,
        # 2/3 at the bottom
        num_lines = 0
        msg_width = self.display.measure_text(message, scale=scale_value)
        num_lines = self.display_width//msg_width # integer division, rounds down
        if msg_width % self.display_width > 0: num_lines += 1 #accounts for putting the remainder on one more line
        
        # calculate y position
        msg_height = num_lines * text_height
        y = int((self.display_height-msg_height)/3)
        
        self.display.text(message, 0, y, wordwrap=self.display_width, scale=scale_value)
        self.display.update()
    
    
    # Intakes a dictionary mapping "destination":[sorted int list]
    # Cycles through each destination, and shows all the trains
    # and their ETAs one by one, each for 4 seconds
    def render_rows(self, rows):
        
        for destination in rows:
            arrival_times = rows[destination]
            self.render_row(destination, arrival_times)
            sleep(4)

    # Takes in string for row name, list of integers (sorted) for arrival times
    # row y position is top left corner of entire row (i.e. label, track, trains, & station)
    # row_height is the total height of all contents
    # Updates display with the contents of a single row. 
    def render_row(self, row_name, arrival_times):
        self.clear_display()

        self.add_row_label(row_name, 0)
        
        track_y_position = int(self.display_height/2)
        
        self.add_train_track(track_y_position) 
        self.add_train_station(track_y_position)
        self.add_trains(arrival_times, track_y_position)
        
        self.display.update()

    # Adds, but does not update display with, a train station icon
    def add_train_station(self,track_y_position):

        x = self.display_width-TRAIN_STATION_SIZE - 4 # 4 is for a bit of buffer from right side
        y = math.floor(track_y_position - TRAIN_STATION_SIZE/2)
        
         # Create a new JPEG decoder for our PicoGraphics
        j = jpegdec.JPEG(self.display)

        # Open the JPEG file
        j.open_file(TRAIN_STATION_FILE)

        # Decode the JPEG
        j.decode(x, y, jpegdec.JPEG_SCALE_FULL, dither=True)
        
    # Adds, but does not update display with, train icons representing arriving trains
    # Far left of screen is farthest away, far right of screen is nearest
    def add_trains(self,eta_list, track_y_position): 
        eta_max = max(eta_list)
        
        maximum_x_position = self.display_width - TRAIN_ICON_SIZE - TRAIN_STATION_SIZE - 4 # 4 is buffer from the station
        
        for eta in eta_list:
            # create the train icon
            
            # at eta_max, we want x to be 0
            # at the smallest eta, we want it to be far to the right
            # at 0, we want it to be all the way to the right
            x = int(
                (eta_max - eta)/eta_max * maximum_x_position
            )
            y = math.floor(track_y_position - TRAIN_ICON_SIZE/2)
            
             # Create a new JPEG decoder for our PicoGraphics
            j = jpegdec.JPEG(self.display)

            # Open the JPEG file
            j.open_file(TRAIN_ICON_FILE)

            # Decode the JPEG
            j.decode(x, y, jpegdec.JPEG_SCALE_FULL, dither=True)

            # create the label
            self.display.set_pen(self.white)
            self.display.set_font("bitmap8")

            eta_text = str(eta)
            text_width = self.display.measure_text(eta_text)
            text_x = int(x + (TRAIN_ICON_SIZE - text_width)/2)
            text_y = y + TRAIN_ICON_SIZE + 4 # buffer
            self.display.text(eta_text, text_x, text_y)
            
    # Adds, but does not update display with, a horizontal line at the specified y position
    # to represent a train track. Stops at the train station
    def add_train_track(self,y_position):
        self.display.set_pen(self.white)
        self.display.line(0, y_position, self.display_width - TRAIN_STATION_SIZE, y_position, 2) #2 is the thickness of the line
        
    # Adds, but does not update display with, a label at
    # the top left position of where the row will go
    def add_row_label(self,label, label_y_position):
        '''
        Vector (Hershey) fonts.
        These are aligned horizontally (x) to their left edge,
        but vertically (y) to their midline excluding descenders
        [i.e., aligned at top edge of lower case letter m].
        At scale=1...
            the top edge of upper case letters is 10 pixels above the specified y,
            text baseline is 10 pixels below the specified y, and
            descenders go down to 20 pixels below the specified y.
        '''
        
        scale_value = 1
        amount_above_baseline = 10 * scale_value
        buffer = 5
        
        self.display.set_pen(self.white)
        self.display.set_font("sans")
        self.display.set_thickness(2)

        self.display.text(label, 0, label_y_position + amount_above_baseline + 5, scale=scale_value)
        
    # Adds, but does not update display with, train in ASCII characters 
    def add_train_ascii(self,x, y):

        self.display.set_pen(self.white)
        self.display.set_font("bitmap8")
        font_height = 8
        
        for index, line in enumerate(TRAIN_ASCII):
            for pos, char in enumerate(line):
                self.display.character(CHAR_CODE_LOOKUP[char],
                                  int(pos * (self.display_width/NUM_COLS_TRAIN_ASCII)) + x,
                                  index * font_height + y,
                                  scale=1)
    
    # Animates an ASCII train across the display
    def animate_train_ascii(self):
        for i in range(-1 * self.display_width, self.display_width + 5, 10): #10 is pixels per step in the animation
           self.clear_display()
           self.add_train_ascii(i, 16)
           self.display.update()
           sleep(0.005)