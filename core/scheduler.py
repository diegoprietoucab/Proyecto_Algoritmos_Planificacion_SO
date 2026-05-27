#de momento sólo se permite creación de procesos 

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from utils.process_generator import crearListaManual


def menu() -> None:
    print("\nSeleccione una de las siguientes opciones: ")
    print("1. Leer procesos desde un archivo")
    print("2. Crear proceso personalizado")
    print("3. Salir\n")

def main() -> None:
    procesos = []
    while(True):
        menu()
        choice = input()
        match(choice):
            case "1":
                print('Holi')
            case "2":
                procesos = crearListaManual()
            case "3":
                break
            case _:
                print("\nERROR. Asegúrese de ingresar una opción válida")

main()