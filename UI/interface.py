from plan.process.process_class import Process

def menuAlgoritmos() -> None:
    print("\nSeleccione una de las siguientes opciones: ")
    print("1. Ejecutar FCFS")
    print("2. Ejecutar SJF")
    print("3. Ejecutar Round Robin")
    print("4. Ejecutar Prioridades")
    print("5. Ver tabla comparativa")
    print("6. Cargar otros procesos")
    print("7. Ejecutar Simulación de Procesos (FCFS)")
    print("8. Salir\n")

def imprimir_tabla_inicial(procesos: list[Process]) -> None:
    """
    Imprime una tabla con los datos iniciales de los procesos
    """
    print("\n--- DATOS INICIALES DE LOS PROCESOS ---")
    print()
    print("PID | Llegada | Ráfaga | Prioridad")
    print("-----------------------------------")
    
    for p in procesos:
        print(f"{p.pid}     {p.llegada}        {p.rafaga}       {p.prioridad}")
    print()