#de momento sólo se permite creación de procesos 

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    )
)

from utils.process_generator import cargaProcesos
from plan.algorithms.sjf import sjf
from plan.algorithms.round_robin import round_robin
from plan.algorithms.priority import prioridad_apropiativa
from plan.algorithms.fcfs import fcfs
from plan.process.process_class import Process
from utils.validations import leerFloat
import ui.interface as ui

def reiniciarTodos(procesos: list[Process]) -> list[Process]:
    for p in procesos:
        p.reiniciar()
    return procesos


def main() -> None:
    procesos: list[Process] = []
    procesos = cargaProcesos()
    ui.imprimir_tabla_inicial(procesos)
    
    # Menú de algoritmos
    while True:
        procesos = reiniciarTodos(procesos)
        ui.menuAlgoritmos()
        eleccion = input()
        match(eleccion):
            case "1":
                fcfs(procesos)
            case "2":
                sjf(procesos)
            case "3":
                print()
                round_robin(procesos, leerFloat("Ingrese el valor del quantum:", "el quantum", True))
            case "4":
                prioridad_apropiativa(procesos)
            case "5":
                print("Comparación en desarrollo...")
            case "6":
                procesos = cargaProcesos()
                ui.imprimir_tabla_inicial(procesos)
            case "7":
                print("\n¡Gracias por usar el simulador!")
                break
            case _:
                print("\nERROR. Opción no válida")

main()