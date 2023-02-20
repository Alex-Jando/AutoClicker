VERSION = 0.1
TOGGLE_KEY = 'f1'
CLICKING = False

import tkinter
import random
import pynput.mouse, pynput.keyboard
from time import sleep
from threading import Thread

MOUSE_CONTROLLER = pynput.mouse.Controller()
MOUSE_BUTTONS = pynput.mouse.Button

def trim_delays(delays):

    while sum(delays) != 1000:
        
            for delay_index, delay in enumerate(delays):
            
                if sum(delays) == 1000:

                    break
            
                if delay == 1:
            
                    continue

                if sum(delays) > 1000:

                    delays[delay_index] -= 1

                elif sum(delays) < 1000:

                    delays[delay_index] += 1

    return delays

def get_delays(CPS):

    delays = [int(1000 / CPS)] * CPS

    apply_offset = lambda delay: random.randint(int(-1000 / CPS) + 1, int(1000 / CPS)) + delay

    delays = list(map(lambda delay: delay / 1000, trim_delays(list(map(apply_offset, delays)))))

    return delays

class Window:

    def __init__(self):

        self.root = tkinter.Tk()

        self.root.title('Auto Clicker')
        self.root.iconphoto(False, tkinter.PhotoImage(file = 'icon.png'))
        self.root.resizable(width = False, height = False)
        self.root.geometry('300x400')
        self.root.configure(bg = 'white')

        self.setup_screen()

        self.root.mainloop()

    def setup_screen(self):

        self.title_label = tkinter.Label(self.root, text = f'Auto Clicker v{VERSION}', font = ('Arial', 24), bg = 'white', fg = 'black')
        self.title_label.pack(pady = 15, side = 'top')

        self.options_frame = tkinter.Frame(self.root, bg = 'white')
        self.options_frame.pack(expand = True)

        self.cps_frame = tkinter.Frame(self.options_frame, bg = 'white')
        self.cps_frame.pack(pady = 15)
        self.cps_label = tkinter.Label(self.cps_frame, text = f'CPS: ', font = ('Arial', 14), bg = 'white', fg = 'black')
        self.cps_label.grid(column = 0, row = 0)

        def check_int(key):
            try:
                int(key)
                return True
            except:
                return False
            
        only_int = self.root.register(check_int)
        self.cps_entry = tkinter.Entry(self.cps_frame, font = ('Arial', 12), bg = 'white', fg = 'black', validatecommand = (only_int, '%S'), validate = 'key')
        self.cps_entry.insert(0, '10')
        self.cps_entry.grid(column = 1, row = 0)


        self.mouse_btn_frame = tkinter.Frame(self.options_frame, bg = 'white')
        self.mouse_btn_frame.pack(pady = 15)
        self.mouse_btn_label = tkinter.Label(self.mouse_btn_frame, text = f'MOUSE BUTTON: ', font = ('Arial', 14), bg = 'white', fg = 'black')
        self.mouse_btn_label.grid(column = 0, row = 0)
        self.mouse_btn = tkinter.StringVar(self.root)
        self.mouse_btn_menu = tkinter.OptionMenu(self.mouse_btn_frame, self.mouse_btn, 'Left', 'Right', 'Middle')
        self.mouse_btn_menu.configure(background = 'white', font = ('Arial', 12))
        self.mouse_btn.set('Left')
        self.mouse_btn_menu.grid(column = 1, row = 0)

        self.toggle_key_frame = tkinter.Frame(self.options_frame, bg = 'white')
        self.toggle_key_frame.pack(pady = 15)
        self.toggle_key_label = tkinter.Label(self.toggle_key_frame, text = f'Toggle Key ({TOGGLE_KEY}): ', font = ('Arial', 14), bg = 'white', fg = 'black')
        self.toggle_key_label.grid(column = 0, row = 0)
        self.toggle_key_btn = tkinter.Button(self.toggle_key_frame, text = 'Change', font = ('Arial', 12), bg = 'white', fg = 'black', command = self.set_toggle_key)
        self.toggle_key_btn.grid(column = 1, row = 0)

        self.start_stop_frame = tkinter.Frame(self.root, bg = 'white')
        self.start_stop_frame.pack(pady = 15, side = 'bottom')
        self.start_btn = tkinter.Button(self.start_stop_frame, text = 'Start', font = ('Arial', 14), bg = 'white', fg = 'black', command = self.start)
        self.start_btn.grid(column = 0, row = 0, padx = 15)
        self.stop_btn = tkinter.Button(self.start_stop_frame, text = 'Stop', font = ('Arial', 14), bg = 'white', fg = 'black', command = self.stop, state = tkinter.DISABLED)
        self.stop_btn.grid(column = 1, row = 0, padx = 15)

        Thread(target = self.check_toggle_key, daemon = True).start()

    def set_toggle_key(self):

        def get_toggle_key(key):

            global TOGGLE_KEY

            try:

                TOGGLE_KEY = key.char

            except:

                TOGGLE_KEY = key.name

            return False

        def _():

            self.cps_entry.configure(state = tkinter.DISABLED)
            self.mouse_btn_menu.configure(state = tkinter.DISABLED)
            self.toggle_key_btn.configure(state = tkinter.DISABLED)
            self.start_btn.configure(state = tkinter.DISABLED)
            self.stop_btn.configure(state = tkinter.DISABLED)

            with pynput.keyboard.Listener(on_release = get_toggle_key) as l:

                l.join()

            self.toggle_key_label.configure(text = f'Toggle Key ({TOGGLE_KEY.title()}): ')

            self.cps_entry.configure(state = tkinter.NORMAL)
            self.mouse_btn_menu.configure(state = tkinter.NORMAL)
            self.toggle_key_btn.configure(state = tkinter.NORMAL)
            self.start_btn.configure(state = tkinter.NORMAL)
            self.stop_btn.configure(state = tkinter.DISABLED)

        Thread(target = _, daemon = True).start()

    def start(self):

        self.stop_btn.configure(state = tkinter.NORMAL)
        self.start_btn.configure(state = tkinter.DISABLED)

        self.cps_entry.configure(state = tkinter.DISABLED)
        self.mouse_btn_menu.configure(state = tkinter.DISABLED)
        self.toggle_key_btn.configure(state = tkinter.DISABLED)

        def click(cps, btn):

            global CLICKING

            CLICKING = True

            button = None

            match btn:

                case 'Left':
                    button = MOUSE_BUTTONS.left
                case 'Right':
                    button = MOUSE_BUTTONS.right
                case 'Middle':
                    button = MOUSE_BUTTONS.middle

            while CLICKING:
 
                for delay in get_delays(cps):

                    MOUSE_CONTROLLER.click(button, 1)
                    
                    if not CLICKING:
                        break

                    sleep(delay)

        Thread(target = click, args = (int(self.cps_entry.get()), self.mouse_btn.get()), daemon = True).start()

    def stop(self):

        self.start_btn.configure(state = tkinter.NORMAL)
        self.stop_btn.configure(state = tkinter.DISABLED)

        self.cps_entry.configure(state = tkinter.NORMAL)
        self.mouse_btn_menu.configure(state = tkinter.NORMAL)
        self.toggle_key_btn.configure(state = tkinter.NORMAL)

        global CLICKING

        CLICKING = False

    def check_toggle_key(self):

        def wait_toggle_key(key):

            global CLICKING
            global TOGGLE_KEY

            try:

                if TOGGLE_KEY == key.char:

                    if CLICKING:

                        self.stop()

                    else:

                        self.start()
                
            except:

                if TOGGLE_KEY == key.name:

                    if CLICKING:

                        self.stop()

                    else:

                        self.start()

        with pynput.keyboard.Listener(on_release = wait_toggle_key) as l:

            l.join()

GUI = Window()