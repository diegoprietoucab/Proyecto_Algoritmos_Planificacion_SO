from plan.process.process_class import Process

def imprimir_metricas_procesos(procesos: list[Process], nombre_algoritmo: str) -> None:
    """
    Imprime una tabla con las métricas individuales de cada proceso 
    tras finalizar la ejecución de un algoritmo específico.
    """
    print(f"\n--- MÉTRICAS POR PROCESO ({nombre_algoritmo.upper()}) ---")
    print()
    # Usamos anchos fijos <12 para alinear el ancho de las columnas y quantumue
    # no se deforme con los datos.
    print(f"{'PID':<5} | {'T. Retorno':<12} | {'T. Espera':<12} | {'T. Respuesta':<12}")
    print("-" * 50)
    
    for p in procesos:
        # Formateamos a 2 decimales (.2f) para quantumue se vea mucho más ordenado
        print(f"{p.pid:<5}   {p.tiempo_retorno:<12.2f}   {p.tiempo_espera:<12.2f}   {p.tiempo_respuesta:<12.2f}")
    print()
    
    # Leyenda para el usuario
    print("* Leyenda:")
    print("  - T. Retorno: Tiempo total desde que el proceso llega hasta que finaliza.")
    print("  - T. Espera: Tiempo total que el proceso pasa en la cola de listos (sin CPU).")
    print("  - T. Respuesta: Tiempo desde que el proceso llega hasta que usa la CPU por 1ra vez.\n")


def imprimir_tabla_comparativa(historial: list[dict]) -> None:
    """
    Imprime una tabla comparando el rendimiento global de los algoritmos ejecutados.
    El historial es una lista de diccionarios quantumue recibe el nombre del algoritmo y 
    sus métricas de uso del sistema.
    """
    if len(historial) < 2:
        print("\nERROR. No hay suficientes datos para comparar. Por favor ejecute al menos dos algoritmos primero.")
        return

    print("\n--- TABLA COMPARATIVA DE ALGORITMOS ---")
    print()
    print(f"{'Algoritmo':<25} | {'T. Retorno Prom':<16} | {'T. Espera Prom':<16} | {'Uso CPU (%)':<12}")
    print("-" * 84)

    mejor_algoritmo = ""
    mejor_tiempo_espera = float('inf')

    for registro in historial:
        nombre = registro["algoritmo"]
        metricas = registro["metricas"]
        
        t_retorno = metricas["tiempo_retorno_promedio"]
        t_espera = metricas["tiempo_espera_promedio"]
        uso_cpu = metricas["porcentaje_cpu_usada"]

        # Lógica para determinar el más eficiente (menor tiempo de espera promedio)
        if t_espera < mejor_tiempo_espera:
            mejor_tiempo_espera = t_espera
            mejor_algoritmo = nombre

        print(f"{nombre:<30}   {t_retorno:<16.2f}   {t_espera:<16.2f}   {uso_cpu:<12.2f}")
    
    print()
    
    # Leyenda para el usuario
    print("* Leyenda:")
    print("  - Promedios: Media de los tiempos calculados entre todos los procesos simulados.")
    print("  - Uso CPU (%): Porcentaje del tiempo total en que la CPU estuvo ejecutando ráfagas.\n")
    
    # Conclusión automática basada en las métricas comparadas
    print(f"*** ALGORITMO MÁS EFICIENTE PARA EL CASO DE PRUEBA ***")
    print(f"El algoritmo más eficiente para este caso de prueba es: {mejor_algoritmo}")
    print(f"Justificación: Presenta el menor Tiempo de Espera Promedio ({mejor_tiempo_espera:.2f}),")
    print(f"lo que significa que los procesos pasan menos tiempo retenidos en la cola de listos.")
    print("-" * 84)
    print()