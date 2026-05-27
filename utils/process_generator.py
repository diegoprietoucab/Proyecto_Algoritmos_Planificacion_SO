from typing import Set
from plan.process.process_class import Process
import utils.validations as val


pids_existentes = set()

def crearProceso() -> Process:
    pid = val.leerPIDUnico("ID del proceso (número entero positivo):", pids_existentes)
    llegada = val.leerFloat("Tiempo de llegada (número positivo o cero):", "El tiempo de llegada", False)
    rafaga = val.leerFloat("Tiempo de ráfaga o uso de CPU (número positivo):", "El tiempo de ráfaga", True)
    prioridad = val.leerInt("Prioridad (número entero positivo o cero):", "La prioridad del proceso", False)
    return Process(pid, llegada, rafaga, prioridad)

def crearListaManual():
    procesos = []
    print("\nA continuación deberá llenar todos los datos que se solicitan\n")
    numero_procesos = val.leerInt("¿Cuántos procesos quiere registrar?:", "La cantidad de procesos", True)
    for i in range(numero_procesos):
        print(f"\n----------------------- Proceso{i + 1} -----------------------\n")
        proceso = crearProceso()
        pids_existentes.add(proceso.pid)
        procesos.append(proceso)
    return procesos