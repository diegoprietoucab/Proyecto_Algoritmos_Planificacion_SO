from typing import Optional
from plan.process.process_state import ProcessState
from dataclasses import dataclass, field

@dataclass
class Process:
    pid: int
    llegada: float
    rafaga: float
    prioridad: int = 0

    estado: ProcessState = field(default = ProcessState.NEW, init = False)
    tiempo_restante: float = field(init = False)
    inicio: Optional[float] = field(default = None, init = False)
    fin: Optional[float] = field(default = None, init = False)
    tiempo_espera: float = field(default = 0, init = False)
    tiempo_retorno: float = field(default = 0, init = False)
    tiempo_respuesta: float = field(default = 0, init = False)

    def __post_init__(self) -> None:
        if not isinstance(self.pid, int):
            raise TypeError("ERROR. El pid debe ser un número entero")
        
        if not isinstance(self.llegada, (int, float)):
            raise TypeError("ERROR. El tiempo de llegada debe ser un número")
        
        if not isinstance(self.rafaga, (int, float)):
            raise TypeError("ERROR. El tiempo de ráfaga debe ser un número")
        
        if not isinstance(self.prioridad, int):
            raise TypeError("ERROR. La prioridad debe ser un número entero")
        
        if (self.llegada < 0):
            raise ValueError(f"ERROR. El tiempo de llegada ({self.llegada}) no puede ser negativo")
        
        if (self.rafaga <= 0):
            raise ValueError(f"ERROR. El tiempo de ráfaga ({self.rafaga}) debe ser positivo")
        
        if (self.prioridad < 0):
            raise ValueError(f"ERROR. La prioridad ({self.prioridad}) no puede ser negativa")
        
        if (self.pid <= 0):
            raise ValueError(f"ERROR. El pid ({self.pid}) debe ser positivo")

        self.tiempo_restante = self.rafaga

    def reiniciar(self) -> None:
        self.estado = ProcessState.NEW
        self.tiempo_restante = self.rafaga
        self.inicio = None
        self.fin = None
        self.tiempo_espera = 0
        self.tiempo_retorno = 0
        self.tiempo_respuesta = 0