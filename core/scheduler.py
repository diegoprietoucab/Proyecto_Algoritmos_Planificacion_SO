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
import UI.interface as ui
from plan.methrics import calcular_metricas_sistema, calcular_metricas_procesos
from UI.results_display import imprimir_metricas_procesos, imprimir_tabla_comparativa
from UI.simulation_display import fcfs_simulacion

def reiniciarTodos(procesos: list[Process]) -> list[Process]:
    for p in procesos:
        p.reiniciar()
    return procesos


def main() -> None:
    procesos: list[Process] = []
    procesos = cargaProcesos()
    ui.imprimir_tabla_inicial(procesos)
    
    # Memú de almacenamiento histórico para la tabla comparativa
    historial: list[dict] = []
    
    # Menú de algoritmos
    while True:
        procesos = reiniciarTodos(procesos)
        ui.menuAlgoritmos()
        eleccion = input()
        
        # Variables auxiliares para capturar la ejecución actual
        algoritmo_ejecutado = ""
        tiempo_total = 0.0
        
        match(eleccion):
            case "1":
                algoritmo_ejecutado = "FCFS"
                tiempo_total = fcfs(procesos)
            case "2":
                algoritmo_ejecutado = "SJF"
                tiempo_total = sjf(procesos)
            case "3":
                print()
                quantum = leerFloat("Ingrese el valor del quantum:", "el quantum", True)
                # Guardamos el valor del quantum en el nombre para poder comparar distintos quantums
                algoritmo_ejecutado = f"Round Robin (quantum={quantum})"
                tiempo_total = round_robin(procesos, quantum)
            case "4":
                algoritmo_ejecutado = "Prioridad"
                tiempo_total = prioridad_apropiativa(procesos)
            case "5":
                # Mostramos la tabla comparativa pasándole el historial acumulado
                imprimir_tabla_comparativa(historial)
            case "6":
                procesos = cargaProcesos()
                ui.imprimir_tabla_inicial(procesos)
                # Limpiamos el historial porquantumue cambiaron los procesos del caso de prueba
                historial.clear()
                print("\n[INFO] Nuevo caso de prueba cargado. Historial comparativo reiniciado.")
            case "7":
                procesos = reiniciarTodos(procesos)
                fcfs_simulacion(procesos)
                procesos = reiniciarTodos(procesos)
            case "8":
                print("\n¡Gracias por usar el simulador!")
                break
            case _:
                print("\nERROR. Opción no válida")
        
        if eleccion in ["1", "2", "3", "4"]:
            
            # Si las funciones de algoritmos actúan por referencia y no retornan el tiempo total,
            # lo calculamos dinámicamente buscando el tiempo de finalización más alto de los procesos.
            if tiempo_total is None or tiempo_total == 0:
                #max() tomará el valor más alto de todos los tiempos de fin, y si algún proceso no tiene
                #fin definido (None), lo ignorará gracias a default=0.0.
                tiempo_total = max((p.fin for p in procesos if p.fin is not None), default=0.0) 
            for p in procesos:
                #calculamos las métricas de cada proceso
                calcular_metricas_procesos(p)
            # Se muestra inmediatamente la tabla con las métricas individuales por proceso
            imprimir_metricas_procesos(procesos, algoritmo_ejecutado)
            
            # Se calculan las métricas resumidas del sistema (promedios, uso de CPU)
            metricas_sistema = calcular_metricas_sistema(procesos, tiempo_total)
            
            # Se guarda este registro en el historial para la opción de tabla comparativa
            historial.append({
                "algoritmo": algoritmo_ejecutado,
                "metricas": metricas_sistema
            })

main()