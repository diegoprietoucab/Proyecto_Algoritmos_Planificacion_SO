from plan.process.process_class import Process
from plan.process.process_state import ProcessState
import copy

#Si dos procesos de la cola de listos tienen la misma ráfaga se selcciona el que llegó primero
#Este algoritmo es no apropiativo por lo que todos los procesos se ejecutan en su totalidad en un solo ciclo

def sjf(procesos: list[Process]):
    
    pendientes: list[Process] = procesos.copy()
    tiempo_actual: float = 0
    cola_listos: list[Process] = []
    terminados: int = 0
    numero_procesos: int = len(pendientes)
    
    #tupla ordenada de tiempo de llegada y proceso por tiempo de llegada
    eventos_llegada: list[(float, Process)] = []
    for p in pendientes:
        eventos_llegada.append((p.llegada, p))
    eventos_llegada.sort(key=lambda x: x[0])

    llegadas_procesadas = 0

    print("\n------------------ SIMULADOR SJF ------------------n")
    while terminados < numero_procesos:

        
        # Procesar todas las llegadas que ocurren en o antes del tiempo actual
        while llegadas_procesadas < len(eventos_llegada) and eventos_llegada[llegadas_procesadas][0] <= tiempo_actual:
            tiempo_llegada, proceso = eventos_llegada[llegadas_procesadas]
            if proceso.estado == ProcessState.NEW:
                proceso.estado = ProcessState.READY
                cola_listos.append(proceso)
                print(f"\nTiempo {tiempo_llegada}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1
        
        # Si no hay procesos listos, avanzar al siguiente evento de llegada (tiempo de ocio)
        if not cola_listos:
            if llegadas_procesadas < len(eventos_llegada):
                tiempo_actual = eventos_llegada[llegadas_procesadas][0]
                continue
            else:
                break
        
        # Mostrar cola de listos
        cola_texto = ", ".join([f"P{p.pid}(r={p.tiempo_restante})" for p in cola_listos])
        print(f"Cola de listos: [{cola_texto}]")
        
        # SJF: ordenar por ráfaga
        cola_listos.sort(key=lambda proceso: proceso.rafaga)
        proceso_actual = cola_listos.pop(0)
        #primero se ordenó por tiempo de llegada (en eventos_llegada)
        #luego se ordenó por ráfaga en cola_listos (que hizo append de eventos_llegada)
        #por ello si dos eventos empatan en ráfaga se ejecuta el que llegó primero
        
        print(f"Inicia proceso {proceso_actual.pid}")
        proceso_actual.inicio = tiempo_actual
        
        # Avanzar el tiempo hasta que el proceso termine (no apropiativo)
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
        proceso_actual.fin = tiempo_actual
        
        terminados += 1

    print("\n---------------------- FIN SIMULACION ----------------------")