import tkinter as tk
from tkinter import ttk

from plan.process.process_class import Process
from UI.gui.theme import COLORS, FONTS, apply_theme
from UI.gui.process_panel import ProcessPanel
from UI.gui.result_panel import ResultPanel
from UI.gui.gantt_panel import GanttPanel
from UI.gui.comparative_panel import ComparativePanel
from UI.gui.simulation_panel import SimulationPanel

_NAV = [
    ('📋', 'Procesos',    'process'),
    ('⚙️', 'Ejecutar',    'result'),
    ('📊', 'Gantt',       'gantt'),
    ('📈', 'Comparativa', 'comparative'),
    ('🔄', 'Simulación',  'simulation'),
]


class MainApp(tk.Tk):
    procesos:       list[Process]
    historial:      list[dict]
    last_gantt_data: dict

    def __init__(self) -> None:
        super().__init__()
        self.title("Simulador de Algoritmos de Planificación")
        self.geometry("1200x720")
        self.minsize(900, 600)
        self.configure(bg=COLORS['base'])

        apply_theme(self)

        self.procesos        = []
        self.historial       = []
        self.last_gantt_data = {'segments': [], 'algorithm': ''}

        self._active_key: str = 'process'
        self._nav_btns:   dict[str, ttk.Button] = {}
        self._panels:     dict[str, tk.Frame]   = {}

        self._build()
        self._show('process')


    def _build(self) -> None:
        self.columnconfigure(0, weight=0, minsize=190)
        self.columnconfigure(1, weight=0, minsize=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_sidebar()
        tk.Frame(self, bg=COLORS['surface1'], width=1).grid(
            row=0, column=1, sticky='ns'
        )
        self._build_content()

    def _build_sidebar(self) -> None:
        side = tk.Frame(self, bg=COLORS['mantle'])
        side.grid(row=0, column=0, sticky='nsew')
        side.columnconfigure(0, weight=1)

        logo_frame = tk.Frame(side, bg=COLORS['mantle'])
        logo_frame.grid(row=0, column=0, sticky='ew', pady=(16, 8))
        tk.Label(logo_frame, text="🖥", bg=COLORS['mantle'],
                 fg=COLORS['blue'], font=('Segoe UI', 24)).pack()
        tk.Label(logo_frame, text="Planificación\nde Procesos",
                 bg=COLORS['mantle'], fg=COLORS['text'],
                 font=('Segoe UI', 10, 'bold'), justify='center').pack()

        tk.Frame(side, bg=COLORS['surface1'], height=1).grid(
            row=1, column=0, sticky='ew', padx=12, pady=8
        )

        for i, (icon, label, key) in enumerate(_NAV):
            btn = ttk.Button(
                side, text=f"  {icon}  {label}",
                style='Nav.TButton',
                command=lambda k=key: self._show(k),
            )
            btn.grid(row=i + 2, column=0, sticky='ew')
            self._nav_btns[key] = btn

        tk.Label(side, text="v1.0 — SO Project",
                 bg=COLORS['mantle'], fg=COLORS['overlay0'],
                 font=FONTS['small']).grid(row=99, column=0, sticky='s', pady=12)
        side.rowconfigure(99, weight=1)

    def _build_content(self) -> None:
        container = tk.Frame(self, bg=COLORS['base'])
        container.grid(row=0, column=2, sticky='nsew')
        container.rowconfigure(0, weight=1)
        container.columnconfigure(0, weight=1)
        self._container = container

        panel_classes = {
            'process':    ProcessPanel,
            'result':     ResultPanel,
            'gantt':      GanttPanel,
            'comparative': ComparativePanel,
            'simulation': SimulationPanel,
        }
        for key, cls in panel_classes.items():
            panel = cls(container, self)
            panel.grid(row=0, column=0, sticky='nsew')
            self._panels[key] = panel


    def _show(self, key: str) -> None:
        self._active_key = key

        self._panels[key].tkraise()

        for k, btn in self._nav_btns.items():
            btn.configure(style='NavOn.TButton' if k == key else 'Nav.TButton')


    def set_procesos(self, procesos: list[Process]) -> None:
        self.procesos = procesos
        for panel in self._panels.values():
            panel.on_update()

    def add_to_historial(self, algorithm: str, metricas: dict) -> None:
        self.historial.append({'algoritmo': algorithm, 'metricas': metricas})
        self._panels['comparative'].on_update()

    def set_gantt_data(self, segments: list, algorithm: str) -> None:
        self.last_gantt_data = {'segments': segments, 'algorithm': algorithm}
        self._panels['gantt'].on_update()
