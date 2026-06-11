from plan.process.process_class import Process
from plan.process.process_state import ProcessState
import copy

#Muestra la ejecución completa de procesos estrictamente en el orden de llegada

def fcfs(procesos: list[Process]) -> None:
    
    pendientes: list[Process] = copy.deepcopy(procesos)
    tiempo_actual: float = 0
    cola_listos: list[Process] = []
    terminados: int = 0
    numero_procesos: int = len(pendientes)

    #ordena procesos por orden de llegada
    pendientes.sort(key=lambda p: p.llegada)
    
    print("\n------------------ SIMULADOR FCFS ------------------\n")
    
    llegadas_procesadas = 0
    
    while terminados < numero_procesos:
        
        #No se han mostrado todas las llegadas y ya alguna ha sucedido para el tiempo actual
        while llegadas_procesadas < len(pendientes) and pendientes[llegadas_procesadas].llegada <= tiempo_actual:
            proceso = pendientes[llegadas_procesadas]
            proceso.estado = ProcessState.READY
            cola_listos.append(proceso)
            print(f"\nTiempo {proceso.llegada}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1
        
        if not cola_listos:    #tiempo de ocio (no hay nadie en cola)
            if llegadas_procesadas < len(pendientes):
                tiempo_actual = pendientes[llegadas_procesadas].llegada
                continue
            else:
                break      #se acabaron las llegadas pendientes (fin del algoritmo)

        cola_texto = ", ".join([f"P{p.pid}(r={p.rafaga})" for p in cola_listos])
        print(f"Cola de listos: [{cola_texto}]")
        proceso_actual = cola_listos.pop(0)    #obtiene el último elemento en llegar
        
        print(f"Inicia proceso {proceso_actual.pid}")
        
        proceso_actual.inicio = tiempo_actual
        tiempo_actual += proceso_actual.rafaga     #se incrementa el tiempo del sistema
        proceso_actual.fin = tiempo_actual
        proceso_actual.estado = ProcessState.FINISHED
        
        # Mostrar llegadas que ocurrieron DURANTE la ejecución
        while llegadas_procesadas < len(pendientes) and pendientes[llegadas_procesadas].llegada < tiempo_actual:
            proceso = pendientes[llegadas_procesadas]
            proceso.estado = ProcessState.READY
            cola_listos.append(proceso)
            print(f"\nTiempo {proceso.llegada}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1

        proceso_actual.fin = tiempo_actual
        print(f"\nTiempo {tiempo_actual}: Termina proceso {proceso_actual.pid}")
        
        terminados += 1
    
    print("---------------------- FIN SIMULACION ----------------------")