import hardware_setup  # Create a display instance
from gui.core.ugui import Screen, ssd

from gui.widgets import Label, Button, CloseButton
# from gui.core.writer import Writer  # Monochrome display
from gui.core.writer import CWriter
# Font for CWriter or Writer
import gui.fonts.arial10 as arial10
from gui.core.colors import *

#button to navigate trees
def fwdbutton(wri, row, col, cls_screen, text='Next'):
    def fwd(button):
        Screen.change(cls_screen)  # Callback

    Button(wri, row, col, callback = fwd,
           fgcolor = BLACK, bgcolor = GREEN,
           text = text, shape = RECTANGLE)
    
# wri = Writer(ssd, arial10, verbose=False)  # Monochrome display
wri = CWriter(ssd, arial10, GREEN, BLACK, verbose=False)

# This screen overlays BaseScreen.
class CalibrationScreen(Screen):

    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, 'New screen.')
        CloseButton(wri)
        col = 2
        row = 2
        Slider(wri, row, col, callback=self.slider_cb,
               bdcolor=RED, slotcolor=BLUE,
               legends=('0.0', '0.5', '1.0'), value=0.5)
        CloseButton(wri)
        
    def slider_cb(self, s):
        v = s.value()
        if v < 0.2:
            s.color(BLUE)
        elif v > 0.8:
            s.color(RED)
        else:
            s.color(GREEN)
        
# This screen overlays BaseScreen.
class BackScreen(Screen):

    def __init__(self):
        super().__init__()
        Label(wri, 2, 2, 'New screen.')
        CloseButton(wri)

#main menu
class GUI(Screen):

    def __init__(self):

        def my_callback(button, arg):
            print('Button pressed', arg)
            
        def manual_callback(button, arg):
            
            return
            

        super().__init__()


        #write basic menu
        col = 2
        row = 2
        Label(wri, row, col, 'Welcome to the Crop Dryer Control System')
        row = 50
        
        fwdbutton(wri, row, col, BackScreen, text='Manual Calibration')
        row += 60
        fwdbutton(wri, row, col, BackScreen, text='Automatic Control')
        row += 60
        fwdbutton(wri, row, col, BackScreen, text='View Sensor Data')
        CloseButton(wri)  # Quit the application

def run():
    print('Launching GUI')
    Screen.change(GUI)  # A class is passed here, not an instance.

run()