from plan.process.process_class import Process
from plan.process.process_state import ProcessState
import copy

"""
    1) Se consideran los tiempos de llegada de cada proceso
    2) Si un proceso termina antes de que su quantum expire, el siguiente inicia automáticamente con la totalidad de su quantum
    3) Si termina el quantum de un proceso justo cuando llega otro, primero se encola el proceso nuevo de penúltimo y el proceso detenido se reencola de último
    4) Si un proceso está sólo en la lista y ya expiró su quantum se le otorga un tiempo de gracia, que se mantiene hasta
        a) que llegue otro proceso
        b) que termine su ejecución
    Depende de lo que suceda primero

    El objetivo de nuestro algoritmo es reducir el tiempo de ocio y los cambios de contexto innecesarios
"""

def round_robin(procesos: list[Process], quantum: float) -> None:
    pendientes: list[Process] = procesos.copy()
    tiempo_actual: float = 0
    cola_listos: list[Process] = []
    terminados: int = 0
    numero_proecesos: int = len(pendientes)
    eventos_llegada: list[(float, Process)] = []
    llegadas_procesadas = 0

    for p in pendientes:
        eventos_llegada.append((p.llegada, p))
    eventos_llegada.sort(key=lambda x: x[0])        #tupla ordenada de tiempo de llegada y proceso por tiempo de llegada
    
    def encolar_llegadas(tiempo_actual: float) -> None:
        nonlocal llegadas_procesadas
        while (llegadas_procesadas < len(eventos_llegada) and                #no se han procesado todos los eventos
               eventos_llegada[llegadas_procesadas][0] <= tiempo_actual):    #tiempo de llegada del proceso es menor que el tiempo actual
            t_llegada, proceso = eventos_llegada[llegadas_procesadas]      
            if proceso.estado == ProcessState.NEW:
                proceso.estado = ProcessState.READY                 #se reconoce la llegada
                cola_listos.append(proceso)
                print(f"\nTiempo {t_llegada:.0f}: Llega proceso {proceso.pid}")    
            llegadas_procesadas += 1                                #se procesan todas las llegadas hasta el tiempo actual 

    print("\n---------------------- SIMULADOR ROUND ROBIN ----------------------")

    while terminados < numero_proecesos:

        encolar_llegadas(tiempo_actual)       #revisa al inicio de cada iteración las llegadas (necesario, para mostrar la llegada en t = 0 por ejemplo)

        if not cola_listos:
            if llegadas_procesadas < len(eventos_llegada):                  #la cola está vacía, pero aún vienen más eventos
                tiempo_actual = eventos_llegada[llegadas_procesadas][0]     #único posible caso de tiempo de ocio
            continue

        cola_texto = ", ".join([f"P{p.pid}(r={p.tiempo_restante})" for p in cola_listos])
        print(f"Cola de listos: [{cola_texto}]")

        proceso_actual = cola_listos.pop(0)
        if proceso_actual.inicio is None:
            proceso_actual.inicio = tiempo_actual

        tiempo_quantum_expira = tiempo_actual + quantum
        tiempo_gracia = False

        print(f"Inicia proceso {proceso_actual.pid}")  #solo se imprime una vez

        while True:
            proxima_llegada = (eventos_llegada[llegadas_procesadas][0]        #toma el tiempo de la llegada actual
                               if llegadas_procesadas < len(eventos_llegada)  #si quedan procesos pendientes
                               else float('inf'))                             #si no, es infinito (porque no llegan más)

            if not tiempo_gracia:
                proximo_evento = min(          #qué sucede primero?
                    tiempo_quantum_expira,     #se acaba el quantum
                    proxima_llegada,           #llega alguien
                    tiempo_actual + proceso_actual.tiempo_restante     #se acaba el proceso
                )
            else:
                proximo_evento = min(          #el proceso ya expiró su quantum, pero sigue usando su tiempo de gracia
                    proxima_llegada,           #hasta que llegue otro proceso
                    tiempo_actual + proceso_actual.tiempo_restante     #o hasta que termine su ejecución
                )

            tiempo_ejecutado = proximo_evento - tiempo_actual     #el procesos se estuvo ejecutando hasta que pasó el evento anterior
            proceso_actual.tiempo_restante -= tiempo_ejecutado    #se decrementa el tiempo restante
            tiempo_actual = proximo_evento

            encolar_llegadas(tiempo_actual)    #como cambió el tiempo actual se revisa si hubo una llegada
            #Observar que en la primera condición pudo haber empate entre llegada y fin del quantum
            #primero se encola el proceso nuevo por la función encolar_llegadas
            #luego es que se reencola de último el proceso detenido

            if proceso_actual.tiempo_restante <= 0:     #terminó el proceso
                proceso_actual.estado = ProcessState.FINISHED
                proceso_actual.fin = tiempo_actual
                print(f"\nTiempo {tiempo_actual:.0f}: Termina proceso {proceso_actual.pid}")
                terminados += 1
                break

            if not tiempo_gracia and tiempo_actual >= tiempo_quantum_expira:  #expiró el quantum y no está en tiempo de gracia
                if cola_listos:                                  
                    proceso_actual.estado = ProcessState.READY  #se marca ready de nuevo, no running
                    cola_listos.append(proceso_actual)          #se reincorpora el proceso al final de la cola
                    print(f"\nTiempo {tiempo_actual:.0f}: Proceso {proceso_actual.pid} se interrumpe")
                    break
                else:
                    tiempo_gracia = True    #se marca que acabó el quantum
                    continue                   #como no hay más nadie no se señala la interrupción y el mismo proceso ejecuta otro ciclo (tiempo de gracia)

            if tiempo_gracia and cola_listos:    #El proceso está en tiempo de gracia, pero justo hay alguien en cola
                proceso_actual.estado = ProcessState.READY      #se marca ready de nuevo, no running
                cola_listos.append(proceso_actual)   #se encola de úitimo
                print(f"\nTiempo {tiempo_actual:.0f}: Proceso {proceso_actual.pid} se interrumpe")
                break

    print("\n---------------------- FIN SIMULACION ----------------------")