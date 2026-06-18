import time
from plan.process.process_class import Process
from plan.process.process_state import ProcessState

_DELAY_SECONDS: int = 3

_STATE_LABELS: dict[ProcessState, str] = {
    ProcessState.NEW:      "Nuevo",
    ProcessState.READY:    "Listo",
    ProcessState.RUNNING:  "Ejecutando",
    ProcessState.FINISHED: "Terminado",
    ProcessState.WAITING:  "Esperando",
}


def _estado(proceso: Process) -> str:
    return _STATE_LABELS.get(proceso.estado, str(proceso.estado))


def _cola_texto(cola: list[Process]) -> str:
    return "[" + ", ".join(f"P{p.pid}(r={p.rafaga})" for p in cola) + "]"


def fcfs_simulacion(procesos: list[Process]) -> None:
    """
    Runs a visual FCFS simulation printing a progressive event log.
    Each significant event is printed and then pauses _DELAY_SECONDS seconds,
    showing the state transition (Nuevo → Listo → Ejecutando → Terminado)
    inline with the event description.
    """
    pendientes: list[Process] = sorted(procesos, key=lambda p: p.llegada)
    tiempo_actual: float = 0.0
    cola_listos: list[Process] = []
    terminados: int = 0
    numero_procesos: int = len(pendientes)
    llegadas_procesadas: int = 0

    print("\n------------------ SIMULACIÓN FCFS (con estados) ------------------\n")

    # Show initial state of all processes
    print("Estado inicial de los procesos:")
    for p in procesos:
        print(f"  P{p.pid} → {_estado(p)}")
    print()
    time.sleep(_DELAY_SECONDS)

    while terminados < numero_procesos:

        # Admit every process whose arrival time <= current time → READY
        admitidos = False
        while (
            llegadas_procesadas < len(pendientes)
            and pendientes[llegadas_procesadas].llegada <= tiempo_actual
        ):
            proceso = pendientes[llegadas_procesadas]
            proceso.estado = ProcessState.READY
            cola_listos.append(proceso)
            llegadas_procesadas += 1
            print(f"Tiempo {proceso.llegada}: Llega P{proceso.pid}  →  Estado: {_estado(proceso)}")
            admitidos = True

        if admitidos:
            time.sleep(_DELAY_SECONDS)

        if not cola_listos:
            # CPU idle: jump to next arrival
            if llegadas_procesadas < len(pendientes):
                tiempo_actual = pendientes[llegadas_procesadas].llegada
                continue
            else:
                break

        # Show ready queue
        print(f"Cola de listos: {_cola_texto(cola_listos)}")
        time.sleep(_DELAY_SECONDS)

        # Pick first process → RUNNING
        proceso_actual = cola_listos.pop(0)
        proceso_actual.estado = ProcessState.RUNNING
        proceso_actual.inicio = tiempo_actual

        print(f"Inicia P{proceso_actual.pid}  →  Estado: {_estado(proceso_actual)}")
        time.sleep(_DELAY_SECONDS)

        # Advance time by full burst (FCFS is non-preemptive)
        tiempo_actual += proceso_actual.rafaga
        proceso_actual.fin = tiempo_actual
        proceso_actual.estado = ProcessState.FINISHED

        # Admit processes that arrived during execution
        while (
            llegadas_procesadas < len(pendientes)
            and pendientes[llegadas_procesadas].llegada < tiempo_actual
        ):
            proceso = pendientes[llegadas_procesadas]
            proceso.estado = ProcessState.READY
            cola_listos.append(proceso)
            llegadas_procesadas += 1
            print(f"Tiempo {proceso.llegada}: Llega P{proceso.pid}  →  Estado: {_estado(proceso)}")

        print(f"\nTiempo {tiempo_actual}: Termina P{proceso_actual.pid}  →  Estado: {_estado(proceso_actual)}\n")
        time.sleep(_DELAY_SECONDS)

        terminados += 1

    print("---------------------- FIN SIMULACIÓN ----------------------")
    print("\nPresione Enter para volver al menú...")
    input()
