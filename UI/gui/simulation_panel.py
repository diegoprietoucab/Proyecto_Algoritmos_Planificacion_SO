import copy
import tkinter as tk
from tkinter import ttk, messagebox

from plan.process.process_class import Process
from plan.process.process_class import ProcessState
from UI.gui.theme import COLORS, FONTS
from UI.simulation_display import formatear_llegada, formatear_ocio

_DELAY_MS = 1500
_STATE_LABEL = {
    ProcessState.NEW:      ('Nuevo',      COLORS['subtext0']),
    ProcessState.READY:    ('Listo',      COLORS['yellow']),
    ProcessState.RUNNING:  ('Ejecutando', COLORS['green']),
    ProcessState.FINISHED: ('Terminado',  COLORS['sapphire']),
}

_LOG_TAG = {
    'nuevo':      COLORS['subtext0'],
    'listo':      COLORS['yellow'],
    'ejecutando': COLORS['green'],
    'terminado':  COLORS['sapphire'],
    'fin':        COLORS['purple'],
    'info':       COLORS['blue'],
    'ocio':       COLORS['peach'],
}


class SimulationPanel(tk.Frame):
    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent, bg=COLORS['base'])
        self.app = app
        self._steps: list[dict] = []
        self._step_idx: int = 0
        self._after_id: str | None = None
        self._running: bool = False
        self._build()

    def _build(self) -> None:
        tk.Label(self, text="🔄  Simulación FCFS (con estados)",
                 bg=COLORS['base'], fg=COLORS['text'], font=FONTS['title']
                 ).pack(anchor='w', padx=30, pady=(24, 0))
        tk.Frame(self, bg=COLORS['surface1'], height=1).pack(fill='x', padx=30, pady=(8, 12))

        ctrl = tk.Frame(self, bg=COLORS['base'])
        ctrl.pack(fill='x', padx=30, pady=(0, 10))

        self._start_btn = ttk.Button(ctrl, text="▶  Iniciar simulación",
                                      style='Accent.TButton', command=self._start)
        self._start_btn.pack(side='left')

        self._stop_btn = ttk.Button(ctrl, text="⏹  Detener",
                                     style='Stop.TButton', command=self._stop,
                                     state='disabled')
        self._stop_btn.pack(side='left', padx=(8, 0))

        ttk.Button(ctrl, text="↺  Reiniciar", style='TButton',
                   command=self._reset).pack(side='left', padx=(8, 0))

        self._delay_label = tk.Label(ctrl, text="Pausa (s):",
                                      bg=COLORS['base'], fg=COLORS['subtext0'],
                                      font=FONTS['small'])
        self._delay_label.pack(side='right', padx=(0, 4))
        self._delay_var = tk.StringVar(value='3')
        tk.Entry(ctrl, textvariable=self._delay_var, width=4,
                 bg=COLORS['surface1'], fg=COLORS['text'],
                 insertbackground=COLORS['text'], relief='flat',
                 font=FONTS['body']).pack(side='right')

        body = tk.Frame(self, bg=COLORS['base'])
        body.pack(fill='both', expand=True, padx=30, pady=(0, 12))
        body.columnconfigure(0, weight=3)
        body.columnconfigure(1, weight=2)
        body.rowconfigure(0, weight=1)

        self._build_log(body)
        self._build_state_table(body)

        self._status_var = tk.StringVar(value="Cargue procesos e inicie la simulación")
        tk.Label(self, textvariable=self._status_var,
                 bg=COLORS['base'], fg=COLORS['subtext0'], font=FONTS['small']
                 ).pack(anchor='w', padx=30, pady=(0, 8))

    def _build_log(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=COLORS['surface0'])
        frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Registro de eventos",
                 bg=COLORS['surface0'], fg=COLORS['blue'], font=FONTS['heading']
                 ).grid(row=0, column=0, sticky='w', padx=12, pady=(10, 6))

        self._log = tk.Text(frame, state='disabled', wrap='word',
                             bg=COLORS['mantle'], fg=COLORS['text'],
                             font=FONTS['mono'], relief='flat')
        self._log.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))

        sb = ttk.Scrollbar(frame, orient='vertical', command=self._log.yview)
        sb.grid(row=1, column=1, sticky='ns', pady=(0, 10))
        self._log.configure(yscrollcommand=sb.set)

        for tag, color in _LOG_TAG.items():
            self._log.tag_configure(tag, foreground=color)

    def _build_state_table(self, parent: tk.Frame) -> None:
        frame = tk.Frame(parent, bg=COLORS['surface0'])
        frame.grid(row=0, column=1, sticky='nsew')
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text="Estado actual",
                 bg=COLORS['surface0'], fg=COLORS['blue'], font=FONTS['heading']
                 ).grid(row=0, column=0, sticky='w', padx=12, pady=(10, 6))

        cols = ('PID', 'Llegada', 'Ráfaga', 'Estado')
        self._state_tree = ttk.Treeview(frame, columns=cols, show='headings')
        widths = [60, 80, 70, 110]
        for c, w in zip(cols, widths):
            self._state_tree.heading(c, text=c)
            self._state_tree.column(c, anchor='center', width=w)
        self._state_tree.grid(row=1, column=0, sticky='nsew', padx=10, pady=(0, 10))

        sb = ttk.Scrollbar(frame, orient='vertical', command=self._state_tree.yview)
        sb.grid(row=1, column=1, sticky='ns', pady=(0, 10))
        self._state_tree.configure(yscrollcommand=sb.set)

        self._state_tree.tag_configure('nuevo',      foreground=COLORS['subtext0'])
        self._state_tree.tag_configure('listo',      foreground=COLORS['yellow'])
        self._state_tree.tag_configure('ejecutando', foreground=COLORS['green'],
                                       font=('Segoe UI', 10, 'bold'))
        self._state_tree.tag_configure('terminado',  foreground=COLORS['sapphire'])

    def _generate_steps(self, procesos: list[Process]) -> list[dict]:
        steps: list[dict] = []
        pending = sorted(copy.deepcopy(procesos), key=lambda p: p.llegada)
        state_map: dict[int, ProcessState] = {p.pid: ProcessState.NEW for p in pending}

        def snap(text: str, tag: str) -> None:
            steps.append({'text': text, 'tag': tag, 'state_map': dict(state_map)})

        snap(
            "Estado inicial de los procesos:\n" +
            "\n".join(f"  P{p.pid} → Nuevo" for p in pending) + "\n\n",
            'info',
        )

        cola: list[Process] = []
        terminados = 0
        llegadas_ok = 0
        t = 0.0

        while terminados < len(pending):
            admitted: list[Process] = []
            while llegadas_ok < len(pending) and pending[llegadas_ok].llegada <= t:
                p = pending[llegadas_ok]
                state_map[p.pid] = ProcessState.READY
                cola.append(p)
                admitted.append(p)
                llegadas_ok += 1

            if admitted:
                txt = ''.join(
                    formatear_llegada(p, p.llegada) + "\n"
                    for p in admitted
                )
                snap(txt, 'listo')

            if not cola:
                if llegadas_ok < len(pending):
                    siguiente = pending[llegadas_ok].llegada
                    if siguiente > t:
                        snap(formatear_ocio(t, siguiente - t) + "\n", 'ocio')
                    t = siguiente
                    continue
                break

            q_txt = ', '.join(f"P{p.pid}(r={p.rafaga})" for p in cola)
            snap(f"Cola de listos: [{q_txt}]\n", 'listo')

            proc = cola.pop(0)
            state_map[proc.pid] = ProcessState.RUNNING
            proc.inicio = t
            snap(f"Inicia P{proc.pid}  →  Estado: Ejecutando\n", 'ejecutando')

            t += proc.rafaga
            proc.fin = t
            state_map[proc.pid] = ProcessState.FINISHED

            during = ''
            while llegadas_ok < len(pending) and pending[llegadas_ok].llegada < t:
                p = pending[llegadas_ok]
                state_map[p.pid] = ProcessState.READY
                cola.append(p)
                during += f"Tiempo {p.llegada}: Llega P{p.pid}  →  Estado: Listo\n"
                llegadas_ok += 1

            fin_txt = (during or '') + f"\nTiempo {t}: Termina P{proc.pid}  →  Estado: Terminado\n\n"
            snap(fin_txt, 'terminado')
            terminados += 1

        snap("─────────── FIN DE LA SIMULACIÓN ───────────\n", 'fin')
        return steps


    def _start(self) -> None:
        if not self.app.procesos:
            messagebox.showwarning("Sin procesos",
                                   "Cargue procesos desde el panel de Gestión.")
            return
        self._reset_state()
        self._steps = self._generate_steps(self.app.procesos)
        self._step_idx = 0
        self._running = True
        self._start_btn.configure(state='disabled')
        self._stop_btn.configure(state='normal')
        self._status_var.set("▶  Simulación en curso…")
        self._tick()

    def _tick(self) -> None:
        if not self._running or self._step_idx >= len(self._steps):
            self._finish()
            return

        step = self._steps[self._step_idx]
        self._step_idx += 1

        self._append_log(step['text'], step['tag'])
        self._update_state_table(step['state_map'])

        delay = self._get_delay()
        self._after_id = self.after(delay, self._tick)

    def _finish(self) -> None:
        self._running = False
        self._start_btn.configure(state='normal')
        self._stop_btn.configure(state='disabled')
        self._status_var.set("✅  Simulación completada")

    def _stop(self) -> None:
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self._start_btn.configure(state='normal')
        self._stop_btn.configure(state='disabled')
        self._status_var.set("⏹  Simulación detenida")

    def _reset(self) -> None:
        self._stop()
        self._reset_state()
        self._status_var.set("Cargue procesos e inicie la simulación")

    def _reset_state(self) -> None:
        self._log.configure(state='normal')
        self._log.delete('1.0', tk.END)
        self._log.configure(state='disabled')
        self._state_tree.delete(*self._state_tree.get_children())

    def _append_log(self, text: str, tag: str) -> None:
        self._log.configure(state='normal')
        self._log.insert(tk.END, text, tag)
        self._log.see(tk.END)
        self._log.configure(state='disabled')

    def _update_state_table(self, state_map: dict[int, ProcessState]) -> None:
        self._state_tree.delete(*self._state_tree.get_children())
        for p in self.app.procesos:
            estado = state_map.get(p.pid, ProcessState.NEW)
            lbl, _ = _STATE_LABEL.get(estado, ('—', COLORS['text']))
            tag = lbl.lower()
            self._state_tree.insert('', 'end',
                                     values=(p.pid, p.llegada, p.rafaga, lbl),
                                     tags=(tag,))

    def _get_delay(self) -> int:
        try:
            return max(500, int(float(self._delay_var.get()) * 1000))
        except ValueError:
            return _DELAY_MS

    def on_update(self) -> None:
        pass
