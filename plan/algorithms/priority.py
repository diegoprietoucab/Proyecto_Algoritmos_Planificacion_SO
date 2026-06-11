''' 
    Se implementa un algoritmo de planificación por prioridades apropiativo
    Si mientras un proceso se ejecuta llega uno de menor prioridad, el primero se interrumpe
    Si dos procesos de la cola de listos empatan por prioridad, se ejecuta el de menor ráfaga
    La prioridad se evalúa en orden decreciente (1 es la más importante de todas)
'''

from plan.process.process_class import Process
from plan.process.process_state import ProcessState
import copy

def prioridad_apropiativa(procesos: list[Process]) -> None:
    pendientes: list[Process] = copy.deepcopy(procesos)
    tiempo_actual: float = 0
    cola_listos: list[Process] = []
    terminados: int = 0
    numero_procesos: int = len(pendientes)
    proceso_en_ejecucion: Process = None

    #tupla (llegada, Proceso) ordenada por llegada
    eventos_llegada: list[(float, Process)] = []
    for p in pendientes:
        eventos_llegada.append((p.llegada, p))
    eventos_llegada.sort(key=lambda x: x[0])

    llegadas_procesadas = 0

    #encola todas las llegadas hasta un momento dado para mostrar los mensajes y registrar los procesos en orden
    def encolar_llegadas(tiempo_actual: float):
        nonlocal llegadas_procesadas
        while (llegadas_procesadas < len(eventos_llegada) and               #no se han encolado todas las llegadas
               eventos_llegada[llegadas_procesadas][0] <= tiempo_actual):   #el evento ya llegó y no se ha registrado
            t, proceso = eventos_llegada[llegadas_procesadas]
            if proceso.estado == ProcessState.NEW:
                proceso.estado = ProcessState.READY
                cola_listos.append(proceso)
                print(f"\nTiempo {t}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1

    def seleccionar_proceso() -> Process:
        #Idealmente selecciona el de menor prioridad. 
        #Los criterios de desempate son el tiempo restante y el tiempo de llegada (en este orden)
        return min(cola_listos, key=lambda p: (p.prioridad, p.tiempo_restante, p.llegada))

    print("\n------------------ SIMULADOR PRIORIDAD APROPIATIVA ------------------\n")

    while terminados < numero_procesos:

        encolar_llegadas(tiempo_actual)

        if not cola_listos:   #tiempo de ocio, salta hasta la llegada del primer proceso
            if llegadas_procesadas < len(eventos_llegada):
                tiempo_actual = eventos_llegada[llegadas_procesadas][0]
            continue

        #Mostrar cola de listos solo si hay cambios o al inicio
        if proceso_en_ejecucion is None:
            cola_texto = ", ".join([f"P{p.pid}(p={p.prioridad}, r={p.tiempo_restante})" for p in cola_listos])
            print(f"Cola de listos: [{cola_texto}]")

        #Selecciona el mejor proceso si hay alguno en la cola de listos

        #Si no hay proceso en ejecución, seleccionar uno nuevo (no hay interrupción porque el último ya había terminado)
        if proceso_en_ejecucion is None:
            proceso_en_ejecucion = seleccionar_proceso()    #selecciona el mejor proceso según los criterios anteriores
            cola_listos.remove(proceso_en_ejecucion)        #no hace pop, ya que el proceso seleccionado es retornado directamente por la función
            proceso_en_ejecucion.estado = ProcessState.RUNNING
            
            if proceso_en_ejecucion.inicio is None:
                proceso_en_ejecucion.inicio = tiempo_actual
            
            print(f"Inicia proceso {proceso_en_ejecucion.pid}")

        candidato = seleccionar_proceso() if cola_listos else None    #Se busca un posible proceso candidato para interrumpir al primero
        if proceso_en_ejecucion and candidato and candidato.prioridad < proceso_en_ejecucion.prioridad:
            #Aquí no se evalúa tiempo restante ni tiempo de llegada para evitar interrupcipones innecesarias
            #Estos últimos dos son criterios de selección mas no de interrupción
            #Interrumpir proceso actual
            proceso_en_ejecucion.estado = ProcessState.READY
            cola_listos.append(proceso_en_ejecucion)     #se reencola el proceso que se estaba ejecutando
            print(f"\nTiempo {tiempo_actual}: Se interrumpe proceso {proceso_en_ejecucion.pid}")
            
            cola_texto = ", ".join([f"P{p.pid}(p={p.prioridad}, r={p.tiempo_restante})" for p in cola_listos])
            print(f"Cola de listos: [{cola_texto}]")
            
            #Ahora se ejecuta el otro proceso
            proceso_en_ejecucion = candidato
            cola_listos.remove(proceso_en_ejecucion)
            proceso_en_ejecucion.estado = ProcessState.RUNNING
            
            if proceso_en_ejecucion.inicio is None:
                proceso_en_ejecucion.inicio = tiempo_actual
            
            print(f"Inicia proceso {proceso_en_ejecucion.pid}")
            continue
        
        #¿Cuándo llega el siguiente proceso? (posible interrupción)
        proxima_llegada = (eventos_llegada[llegadas_procesadas][0]
                           if llegadas_procesadas < len(eventos_llegada)
                           else float('inf'))   #no hay más nadie en la lista de procesos, el tiempo de llegada es infinito (nunca)

        #Ejecutar hasta: próxima llegada o fin del proceso (lo que suceda primero)
        #Se retorna el tiempo total de ejecución (no el tiempo de sistema después de la ejecución)
        tiempo_ejecucion = min(
            proxima_llegada - tiempo_actual,
            proceso_en_ejecucion.tiempo_restante
        )

        #se acabó el proceso
        if tiempo_ejecucion <= 0:
            continue

        # Ejecutar
        proceso_en_ejecucion.tiempo_restante -= tiempo_ejecucion    #se decrementa el tiempo restante
        tiempo_actual += tiempo_ejecucion                           #se incrementa el tiempo del sistema

        encolar_llegadas(tiempo_actual)                             #como cambió el tiempo actual se revisa si llegaron procesos

        # Verificar si el proceso terminó
        if proceso_en_ejecucion.tiempo_restante <= 0:
            proceso_en_ejecucion.estado = ProcessState.FINISHED
            proceso_en_ejecucion.fin = tiempo_actual
            print(f"\nTiempo {tiempo_actual}: Termina proceso {proceso_en_ejecucion.pid}")
            proceso_en_ejecucion = None
            terminados += 1

    print("\n---------------------- FIN SIMULACION ----------------------")