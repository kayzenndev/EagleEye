from defs import functions
from defs import colorir
from banco import criar_tabela_pessoas
from cadastro import cadastrar

def main():
    try:
        criar_tabela_pessoas()
        options = """
[01] - Register Biometrics
[02] - Identify Biometrics
[00] - Exit
    """
        functions.menu(options)

        stop = 1

        while stop == 1:

            per_inic = float(input(colorir.verdeNeon('Please, select an option >>> ')))

            if per_inic == 1:
                functions.load_animation()
                cadastrar()

            elif per_inic == 2:
                functions.load_animation()

            elif per_inic == 0:
                functions.exit_animation()
                stop = 0


    except ValueError:
        print('Valor inválido. Tente novamente!')


if __name__ == "__main__":
    main()
