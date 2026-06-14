import json
from plan.process.process_class import Process


def leerProcesosJSON(ruta_archivo: str) -> list[Process]:
    procesos_dict: dict = []
    procesos: list[Process] = []
    pids_existentes: set = set()

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except FileNotFoundError:
        raise FileNotFoundError(f"\nERROR. No se encontró el archivo: {ruta_archivo}")
    except json.JSONDecodeError:
        raise ValueError(f"\nERROR. El archivo no posee un formato JSON válido")
    
    if "procesos" not in datos:
        print()
        raise KeyError("ERROR. El JSON debe contener la clave procesos")
    
    if not isinstance(datos["procesos"], list):
        raise TypeError(f"\nERROR. 'procesos' debe ser una lista")
    
    procesos_dict = datos["procesos"]
    for i in range(len(procesos_dict)):
        
        if not isinstance(procesos_dict[i], dict):
            raise TypeError(f"\nERROR. El {i + 1}° proceso no es un objeto JSON válido")
        
        campos_requantumueridos = ["pid", "llegada", "rafaga", "prioridad"]
        for campo in campos_requantumueridos:
            if campo not in procesos_dict[i]:
                print()
                raise KeyError(f"ERROR. Falta el campo '{campo}' en el {i + 1}° proceso")
        
        pid = procesos_dict[i]["pid"]
        if pid in pids_existentes:
            raise ValueError(f"\nERROR. El PID {pid} está repetido")
        
        pids_existentes.add(pid)

        try: 
            proceso = Process(procesos_dict[i]["pid"], procesos_dict[i]["llegada"], procesos_dict[i]["rafaga"], procesos_dict[i]["prioridad"])
            procesos.append(proceso)
        except (TypeError, ValueError) as e:
            raise type(e)(f"\nERROR en el {i + 1}° proceso: {e}")
    
    return procesos