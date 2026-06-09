from plan.process.process_class import Process
import utils.validations as val
from utils.file_handler import leerProcesosJSON

pids_existentes = set()

def menuCreacion() -> None:
    print("\nSeleccione una de las siguientes opciones: ")
    print("1. Leer procesos desde un archivo")
    print("2. Crear proceso personalizado\n")

def cargaProcesos() -> list[Process]:
    procesos: list[Process] = []
    while True:
        menuCreacion()
        eleccion: str = input()
        match(eleccion):
            case "1":
                procesos = crearListaPredefinida()
                break
            case "2":
                procesos = crearListaManual()
                break
            case _:
                print("\nERROR. Asegúrese de ingresar una opción válida")
                continue
    return procesos

def crearProceso() -> Process:
    pid = val.leerPIDUnico("ID del proceso (número entero positivo):", pids_existentes)
    llegada = val.leerFloat("Tiempo de llegada (número positivo o cero):", "El tiempo de llegada", False)
    rafaga = val.leerFloat("Tiempo de ráfaga o uso de CPU (número positivo):", "El tiempo de ráfaga", True)
    prioridad = val.leerInt("Prioridad (número entero positivo o cero):", "La prioridad del proceso", False)
    return Process(pid, llegada, rafaga, prioridad)

def crearListaManual() -> list[Process]:
    procesos = []
    print("\nA continuación deberá llenar todos los datos que se solicitan\n")
    numero_procesos = val.leerInt("¿Cuántos procesos quiere registrar?:", "La cantidad de procesos", True)
    for i in range(numero_procesos):
        print(f"\n----------------------- Proceso{i + 1} -----------------------\n")
        proceso = crearProceso()
        pids_existentes.add(proceso.pid)
        procesos.append(proceso)
    return procesos

def menu() -> None:
    print("\nSeleccione una de los siguientes conjuntos predefinidos:")
    print("1. Procesos básicos")
    print("2. Procesos variados")
    print("3. Procesos personales")
    print("4. Prueba de round robin\n")

def crearListaPredefinida() -> list[Process]:
    procesos = []
    while(True):
        menu()
        eleccion = input()
        match(eleccion):
            case "1":
                ruta = "data/basicos.json"
                break
            case "2":
                ruta = "data/variados.json"
                break
            case "3":
                ruta = "data/personal.json"
                break
            case "4":
                ruta = "data/prueba_rr.json"
                break
            case _:
                print("\nERROR. Asegúrese de ingresar una opción válida")
    try:
        procesos = leerProcesosJSON(ruta) 
    except(ValueError, TypeError, KeyError, FileNotFoundError) as error:
        print(error)

    return procesos