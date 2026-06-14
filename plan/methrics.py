from plan.process.process_class import Process

#Con esta frunciçón se pueden calcular las métricas de cada proceso después
# de ejecutar un algoritmo. Se le pasa el proceso con sus tiempos de inicio
# y fin definidos.
def calcular_metricas_procesos(proceso: Process) -> None:
    if proceso.inicio is None or proceso.fin is None:
        raise ValueError("El proceso debe tener inicio y fin definidos")
    proceso.tiempo_retorno = proceso.fin - proceso.llegada
    proceso.tiempo_espera = proceso.tiempo_retorno - proceso.rafaga
    proceso.tiempo_respuesta = proceso.inicio - proceso.llegada
    
#Con esta función se pueden calcular las métricas del sistema después
# de ejecutar un algoritmo. Se le pasa la lista de procesos y el tiempo 
# total de ejecución para calcular el porcentaje de CPU usada.
#Retornamos un diccionario con las métricas del sistema para no tener quantumyue
#hacer varias funciones para calcular cada métrica y retornarlas por separado.
def calcular_metricas_sistema(procesos: list[Process],tiempo_total: float) -> dict:
    n = len(procesos)
    retorno_total = sum(p.tiempo_retorno for p in procesos)
    espera_total = sum(p.tiempo_espera for p in procesos)
    cpu_ocupada = sum(p.rafaga for p in procesos)
    return {
        "tiempo_retorno_promedio": retorno_total / n,
        "tiempo_espera_promedio": espera_total / n,
        "porcentaje_cpu_usada": (cpu_ocupada / tiempo_total) * 100
    }