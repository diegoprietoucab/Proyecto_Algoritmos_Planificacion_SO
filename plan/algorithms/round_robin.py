from plan.process.process_class import Process
from plan.process.process_state import ProcessState
import copy

"""
    1) Se consideran los tiempos de llegada de cada proceso
    2) Si un proceso termina antes de que su quantum expire, el siguiente inicia automáticamente con la totalidad de su quantum
    3) Si un proceso está sólo en la lista y ya expiró su quantum se le otorga un tiempo de gracia, que se mantiene hasta
        a) Que llegue otro proceso
        b) Que termine su ejecución
    Depende de lo que suceda primero

    El objetivo de nuestro algoritmo es reducir el tiempo de ocio y los cambios de contexto innecesarios
"""

def round_robin(procesos: list[Process], quantum: float):
    pendientes: list[Process] = copy.deepcopy(procesos)
    tiempo_actual: float = 0
    cola_listos: list[Process] = []
    terminados: int = 0
    total: int = len(pendientes)

    eventos_llegada = sorted(
        [(p.llegada, p) for p in pendientes],
        key=lambda x: x[0]
    )
    llegadas_procesadas = 0

    def encolar_llegadas(hasta: float):
        nonlocal llegadas_procesadas
        while (llegadas_procesadas < len(eventos_llegada) and
               eventos_llegada[llegadas_procesadas][0] <= hasta):
            t_llegada, proceso = eventos_llegada[llegadas_procesadas]
            if proceso.estado == ProcessState.NEW:
                proceso.estado = ProcessState.READY
                cola_listos.append(proceso)
                print(f"\nTiempo {t_llegada:.0f}: Llega proceso {proceso.pid}")
            llegadas_procesadas += 1

    print("\n---------------------- SIMULADOR ROUND ROBIN ----------------------")

    while terminados < total:

        encolar_llegadas(tiempo_actual)

        if not cola_listos:
            if llegadas_procesadas < len(eventos_llegada):
                tiempo_actual = eventos_llegada[llegadas_procesadas][0]
            continue

        cola_texto = ", ".join([f"P{p.pid}(r={p.tiempo_restante})" for p in cola_listos])
        print(f"Cola de listos: [{cola_texto}]")

        proceso_actual = cola_listos.pop(0)
        if proceso_actual.inicio is None:
            proceso_actual.inicio = tiempo_actual

        tiempo_quantum_expira = tiempo_actual + quantum
        quantum_expirado = False

        print(f"Inicia proceso {proceso_actual.pid}")  # ← solo se imprime una vez

        while True:
            proxima_llegada = (eventos_llegada[llegadas_procesadas][0]
                               if llegadas_procesadas < len(eventos_llegada)
                               else float('inf'))

            if not quantum_expirado:
                proximo_evento = min(
                    tiempo_quantum_expira,
                    proxima_llegada,
                    tiempo_actual + proceso_actual.tiempo_restante
                )
            else:
                proximo_evento = min(
                    proxima_llegada,
                    tiempo_actual + proceso_actual.tiempo_restante
                )

            tiempo_ejecutado = proximo_evento - tiempo_actual
            proceso_actual.tiempo_restante -= tiempo_ejecutado
            tiempo_actual = proximo_evento

            termina = proceso_actual.tiempo_restante <= 0
            expira_quantum = not quantum_expirado and tiempo_actual >= tiempo_quantum_expira

            encolar_llegadas(tiempo_actual)

            if termina:
                proceso_actual.estado = ProcessState.FINISHED
                proceso_actual.fin = tiempo_actual
                print(f"\nTiempo {tiempo_actual:.0f}: Termina proceso {proceso_actual.pid}")
                terminados += 1
                break

            if expira_quantum:
                if cola_listos:
                    proceso_actual.estado = ProcessState.READY
                    cola_listos.append(proceso_actual)
                    print(f"\nTiempo {tiempo_actual:.0f}: Proceso {proceso_actual.pid} se interrumpe")
                    break
                else:
                    quantum_expirado = True
                    continue

            if quantum_expirado and cola_listos:
                proceso_actual.estado = ProcessState.READY
                cola_listos.append(proceso_actual)
                print(f"\nTiempo {tiempo_actual:.0f}: Proceso {proceso_actual.pid} se interrumpe")
                break

    print("\n---------------------- FIN SIMULACION ----------------------")