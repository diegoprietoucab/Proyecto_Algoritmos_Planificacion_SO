from plan.process.process_class import Process
from plan.process.process_state import ProcessState
import copy

"""Si dos procesos de la cola de listos tienen la misma ráfaga se selcciona el que llegó primero"""

def sjf(procesos: list[Process]):
    
    pendientes: list[Process] = copy.deepcopy(procesos)
    tiempo_actual: float = 0
    cola_listos: list[Process] = []
    terminados: int = 0
    total: int = len(pendientes)
    
    # Crear lista de eventos de llegada ordenados
    eventos_llegada: list[(float, Process)] = []
    for p in pendientes:
        eventos_llegada.append((p.llegada, p))
    eventos_llegada.sort(key=lambda x: x[0])

    llegadas_procesadas = 0

    print("\n------------------ SIMULADOR SJF ------------------n")
    while terminados < total:
        
        # Procesar todas las llegadas que ocurren en o antes del tiempo actual
        while llegadas_procesadas < len(eventos_llegada) and eventos_llegada[llegadas_procesadas][0] <= tiempo_actual:
            tiempo_llegada, proceso = eventos_llegada[llegadas_procesadas]
            if proceso.estado == ProcessState.NEW:
                proceso.estado = ProcessState.READY
                cola_listos.append(proceso)
                print(f"\nTiempo {tiempo_llegada}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1
        
        # Si no hay procesos listos, avanzar al siguiente evento de llegada
        if not cola_listos:
            if llegadas_procesadas < len(eventos_llegada):
                tiempo_actual = eventos_llegada[llegadas_procesadas][0]
                continue
            else:
                break
        
        # Mostrar cola de listos
        print("Cola de listos: [", end = "")
        for i in range(len(cola_listos)):
            print(f"P{cola_listos[i].pid}(r = {cola_listos[i].rafaga})",  end = "")
            if i < len(cola_listos) - 1:
                print(", ", end = "")
        print("]")
        
        # SJF: ordenar por ráfaga
        cola_listos.sort(key=lambda proceso: proceso.rafaga)
        proceso_actual = cola_listos.pop(0)
        
        print(f"Inicia proceso {proceso_actual.pid}")
        
        # Avanzar el tiempo
        tiempo_fin = tiempo_actual + proceso_actual.rafaga
        
        # Procesar llegadas que ocurren durante la ejecucion
        while llegadas_procesadas < len(eventos_llegada) and eventos_llegada[llegadas_procesadas][0] < tiempo_fin:
            tiempo_llegada, proceso = eventos_llegada[llegadas_procesadas]
            if proceso.estado == ProcessState.NEW:
                proceso.estado = ProcessState.READY
                cola_listos.append(proceso)
                print(f"\nTiempo {tiempo_llegada}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1
        
        tiempo_actual = tiempo_fin
        proceso_actual.estado = ProcessState.FINISHED
        print(f"\nTiempo {tiempo_actual}: Termina proceso {proceso_actual.pid}")
        
        terminados += 1

        print("\n---------------------- FIN SIMULACION ----------------------")