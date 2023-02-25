import pynput.mouse, pynput.keyboard
import time
import threading

class Macro:

    @staticmethod
    class CompileError(Exception):

            pass

    @staticmethod
    class MacroError(Exception):

        pass

    @staticmethod
    def record(out_file, break_key):

        RECORD = True

        with open(out_file, 'w') as f:

            f.write('')

        def keyboard_recorder():

            nonlocal RECORD, MACRO_BASELINE

            def on_release(key):

                nonlocal RECORD, MACRO_BASELINE

                if key == break_key:

                    RECORD = False

                if not RECORD:

                    return False

                with open(out_file, 'a') as f:

                    if type(key) == pynput.keyboard.Key:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-EKI-{key.name}\n')

                    elif type(key) == pynput.keyboard.KeyCode:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-EKC-{key.char}\n')

                    MACRO_BASELINE = t

            def on_press(key):

                nonlocal RECORD, MACRO_BASELINE

                if key == break_key:

                    RECORD = False

                if not RECORD:

                    return False

                with open(out_file, 'a') as f:

                    if type(key) == pynput.keyboard.Key:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-SKI-{key.name}\n')

                    elif type(key) == pynput.keyboard.KeyCode:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-SKC-{key.char}\n')

                    MACRO_BASELINE = t

            with pynput.keyboard.Listener(on_release = on_release, on_press = on_press) as l:

                l.join()

        def mouse_recorder():

            nonlocal RECORD, MACRO_BASELINE

            def on_move(x, y):

                nonlocal RECORD, MACRO_BASELINE

                if not RECORD:

                    return False

                with open(out_file, 'a') as f:

                    f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-MPC-{x},{y}\n')

                    MACRO_BASELINE = t
            
            def on_click(_, __, button, is_pressed):

                nonlocal RECORD, MACRO_BASELINE

                if not RECORD:

                    return False

                with open(out_file, 'a') as f:

                    if is_pressed:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-SMC-{button.name}\n')

                    else:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-EMC-{button.name}\n')

                    MACRO_BASELINE = t
            
            def on_scroll(_, __, ___, is_up):

                nonlocal RECORD, MACRO_BASELINE

                if not RECORD:

                    return False

                with open(out_file, 'a') as f:

                    if is_up:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-UMS-{bool(is_up)}\n')

                    else:

                        f.write(f'{(t:=time.perf_counter()) - MACRO_BASELINE}-DMS-{bool(is_up)}\n')

                    MACRO_BASELINE = t

            with pynput.mouse.Listener(on_move = on_move, on_click = on_click, on_scroll = on_scroll) as l:

                l.join()

        MACRO_BASELINE = time.perf_counter()

        threading.Thread(target = mouse_recorder, daemon = True).start()
        threading.Thread(target = keyboard_recorder, daemon = True).start()

        while True:

            if not RECORD:

                return False

            time.sleep(0.01)

    @staticmethod
    def play(in_file, break_key, num_of_repeats = -1):

        MOUSE_CONTROLLER = pynput.mouse.Controller()

        KEYBOARD_CONTROLLER = pynput.keyboard.Controller()

        def do_macro(macro, line):

            try:

                time.sleep(float(macro[0]))

                if not RUNNING.is_set():

                    return False

                match macro[1]:

                    case 'SKC':

                        KEYBOARD_CONTROLLER.press(macro[2])

                    case 'EKC':

                        KEYBOARD_CONTROLLER.release(macro[2])

                    case 'SKI':

                        KEYBOARD_CONTROLLER.press(pynput.keyboard.Key[macro[2]])

                    case 'EKI':

                        KEYBOARD_CONTROLLER.release(pynput.keyboard.Key[macro[2]])
                    
                    case 'MPC':

                        MOUSE_CONTROLLER.position = (int(macro[2].split(',')[0]), int(macro[2].split(',')[1]))

                    case 'SMC':

                        MOUSE_CONTROLLER.press(pynput.mouse.Button[macro[2]])

                    case 'EMC':

                        MOUSE_CONTROLLER.release(pynput.mouse.Button[macro[2]])

                    case 'UMS':

                        MOUSE_CONTROLLER.scroll(0, -1)

                    case 'DMS':

                        MOUSE_CONTROLLER.scroll(0, 1)

            except:

                raise Macro.MacroError(f'Error in macro on line {line + 1}: {"-".join(macro)}')

            return True

        with open(in_file, 'r') as f:

            macros = [macro.split('-') for macro in f.read().strip().split('\n')]

        try:

            Macro._compile(macros)

        except Macro.CompileError as e:

            messagebox.showerror('Compile Error', str(e))

            return False

        RUNNING = threading.Event()

        RUNNING.set()

        threading.Thread(target = Macro._wait_for_break_key, args = (break_key, RUNNING), daemon = True).start()

        repeats = 0

        while RUNNING.is_set() and repeats < num_of_repeats:

            for line, macro in enumerate(macros):

                try:

                    if not do_macro(macro, line):

                        break

                except Macro.MacroError as e:

                    messagebox.showerror('Macro Error', str(e))

                    RUNNING.clear()

                    break

            repeats += 1

    @staticmethod
    def _compile(macros):

        for line, macro in enumerate(macros):

            if macro[1] not in ['SKC', 'EKC', 'SKI', 'EKI', 'MPC', 'SMC', 'EMC', 'UMS', 'DMS']:

                raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

            elif macro[1] == 'MPC':

                try:

                    x, y = macro[2].split(',')

                    int(x)

                    int(y)

                except:

                    raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

            elif macro[1] in ['SKC', 'EKC']:

                try:

                    pynput.keyboard.KeyCode.from_char(macro[2])

                except:

                    raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

            elif macro[1] in ['SKI', 'EKI'] and macro[2] not in pynput.keyboard.Key.__dict__:

                raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

            elif macro[1] in ['SMC', 'EMC'] and macro[2] not in pynput.mouse.Button.__dict__:

                raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

            elif macro[1] in ['UMS', 'DMS'] and macro[2] not in ['True', 'False']:

                raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

            else:

                try:

                    if not float(macro[0]) > 0:

                        raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

                except:

                    raise Macro.CompileError(f'Invalid macro in line {line + 1}: {"-".join(macro)}')

    @staticmethod
    def _wait_for_break_key(break_key, running):

        def on_press(key):

            if key == break_key:

                return False

            elif not running.is_set():

                return False

        with pynput.keyboard.Listener(on_press = on_press) as l:

            l.join()

        running.clear()

# time.sleep(2.5)

# print('Macro Recording Started')

# Macro.record('recording.macro', pynput.keyboard.Key.esc)

# print('Macro Recording Stopped')

# print('Macro saved to recording.macro')

Macro.play('recording.macro', pynput.keyboard.Key.esc, 1)