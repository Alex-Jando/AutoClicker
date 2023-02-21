import pynput.mouse, pynput.keyboard
import time
import threading

# def record_keys(key):

#     try:

#         if key.name == 'esc':

#             return False
        
#     except:

#         pass

#     with open('test.macro', 'a') as f:

#         if type(key) == pynput.keyboard.Key:

#             f.write(f'{time.perf_counter() - MACRO_BASELINE}-KI-{key.name}\n')

#         elif type(key) == pynput.keyboard.KeyCode:

#             f.write(f'{time.perf_counter() - MACRO_BASELINE}-KC-{key.char}\n')

# MACRO_BASELINE = time.perf_counter()

# with pynput.keyboard.Listener(on_release = record_keys) as l:

#     l.join()

KEYBOARD_CONTROLLER = pynput.keyboard.Controller()

def press_in(macro):

    time.sleep(float(macro[0]))

    if macro[1] == 'KC':

        KEYBOARD_CONTROLLER.press(macro[2])
        KEYBOARD_CONTROLLER.release(macro[2])

    elif macro[1] == 'KI':

        KEYBOARD_CONTROLLER.press(pynput.keyboard.Key[macro[2]])
        KEYBOARD_CONTROLLER.release(pynput.keyboard.Key[macro[2]])

with open('test.macro', 'r') as f:

    macros = [macro.split('-') for macro in f.read().strip().split('\n')]

for macro in macros:

    threading.Thread(target = press_in, args = (macro, )).start()