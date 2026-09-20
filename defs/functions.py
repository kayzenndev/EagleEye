def menu(opt):
    from defs import functions
    from defs import colorir

    functions.clear()
    print(colorir.negrito(colorir.verdeNeon(f'''
                                                     
 ▄▀▀▀▀▀▀█  ▄▀▀▀▀▀▄   ▄▀▀▀▀▀▄  █▀▀▄     ▄▀▀▀▀▀▀█       ▄▀▀▀▀▀▀█ █▀▀▀▄▀▀▀█  ▄▀▀▀▀▀▀█
█   ▄▄▄▄█ █       ▄ █       █ █  █    █   ▄▄▄▄█      █   ▄▄▄▄█ █   █   █ █   ▄▄▄▄█
█     ▄   █   ▄   █ █   █▀▀▀▄ █  █    █     ▄        █     ▄   ▄▀▄▄    █ █     ▄  
█   ▀▀▀▀█ █   █   █ █    ▀  █ █  ▀▀▀█ █   ▀▀▀▀█      █   ▀▀▀▀█ █       █ █   ▀▀▀▀█
 ▀▄▄▄▄▄▄█ █▄▄▄█ ▄▄█  ▀▄▄▄▀▄▄█ █▄▄▄▄▄█  ▀▄▄▄▄▄▄█       ▀▄▄▄▄▄▄█ █▄▄▄▄▄▄▀   ▀▄▄▄▄▄▄█

                                E A G L E  E Y E
                                    v1.0.0.0

[!] - Welcome to EagleEye - A facial recognition tool 


Options:

{opt}

''')))


#Limpar tela
def clear():
    from os import system
    system('cls')

#Time de 2s
def timer2():
    import time
    time.sleep(2)

#Time de 5s
def timer1():
    import time
    time.sleep(1)

def exit_animation():
    import time

    print('''
     ''')

    spinner = ["-", "\\", "||", "//"]
    i = 0

    while i < 12:
        print(f'\033[38;2;160;0;255m\r{spinner[i % len(spinner)]} Exiting... See you next time...\033[0m', end='', flush=True)
        i += 1
        time.sleep(0.2)

    clear()

def load_animation():
    import time

    print('''
         ''')

    spinner = ["-", "\\", "||", "//"]
    i = 0

    while i < 12:
        print(f'\033[38;2;160;0;255m\r{spinner[i % len(spinner)]} Loading... Please, wait...\033[0m', end='', flush=True)
        i += 1
        time.sleep(0.2)

    clear()
