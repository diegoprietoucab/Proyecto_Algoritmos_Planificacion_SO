import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from plan.process.process_class import Process
from utils.file_handler import leerProcesosJSON
from UI.gui.theme import COLORS, FONTS

PRESETS: dict[str, str] = {
    'Básicos':            'data/basicos.json',
    'Variados':           'data/variados.json',
    'Personales':         'data/personal.json',
    'Prueba Round Robin': 'data/prueba_rr.json',
}


class ProcessPanel(tk.Frame):
    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent, bg=COLORS['base'])
        self.app = app
        self._build()

    # Layout

    def _build(self) -> None:
        # Title row
        hdr = tk.Frame(self, bg=COLORS['base'])
        hdr.pack(fill='x', padx=30, pady=(24, 0))
        tk.Label(hdr, text="📋  Gestión de Procesos",
                 bg=COLORS['base'], fg=COLORS['text'], font=FONTS['title']).pack(side='left')
        tk.Frame(self, bg=COLORS['surface1'], height=1).pack(fill='x', padx=30, pady=(8, 16))

        # Two-column body
        body = tk.Frame(self, bg=COLORS['base'])
        body.pack(fill='both', expand=True, padx=30)
        body.columnconfigure(0, weight=3, minsize=300)
        body.columnconfigure(1, weight=5)
        body.rowconfigure(0, weight=1)

        self._build_left(body)
        self._build_right(body)

        # Status bar
        self._status_var = tk.StringVar(value="Sin procesos cargados")
        tk.Label(self, textvariable=self._status_var,
                 bg=COLORS['base'], fg=COLORS['subtext0'], font=FONTS['small']
                 ).pack(anchor='w', padx=30, pady=(8, 12))

    def _build_left(self, parent: tk.Frame) -> None:
        left = tk.Frame(parent, bg=COLORS['surface0'])
        left.grid(row=0, column=0, sticky='nsew', padx=(0, 14))

        tk.Label(left, text="Cargar Procesos",
                 bg=COLORS['surface0'], fg=COLORS['blue'], font=FONTS['heading']
                 ).pack(anchor='w', padx=16, pady=(14, 8))

        #  Preset file
        sec1 = self._section(left, "Desde archivo predefinido")
        self._preset_var = tk.StringVar(value='Básicos')
        ttk.Combobox(sec1, textvariable=self._preset_var,
                     values=list(PRESETS.keys()), state='readonly', width=28
                     ).pack(padx=10, pady=(6, 0), anchor='w')

        row1 = tk.Frame(sec1, bg=COLORS['surface0'])
        row1.pack(padx=10, pady=8, anchor='w')
        ttk.Button(row1, text="Cargar", style='Accent.TButton',
                   command=self._load_preset).pack(side='left')
        ttk.Button(row1, text="Examinar JSON…", style='TButton',
                   command=self._browse_file).pack(side='left', padx=(8, 0))

        #  Manual entry
        sec2 = self._section(left, "Crear manualmente")
        fields_frame = tk.Frame(sec2, bg=COLORS['surface0'])
        fields_frame.pack(padx=10, pady=(6, 4), anchor='w')

        labels = ['PID', 'Llegada', 'Ráfaga', 'Prioridad']
        self._fvars: dict[str, tk.StringVar] = {}
        for col, lbl in enumerate(labels):
            tk.Label(fields_frame, text=lbl, bg=COLORS['surface0'],
                     fg=COLORS['subtext0'], font=FONTS['small']
                     ).grid(row=0, column=col, padx=5, sticky='w')
            sv = tk.StringVar()
            self._fvars[lbl] = sv
            tk.Entry(fields_frame, textvariable=sv, width=8,
                     bg=COLORS['surface1'], fg=COLORS['text'],
                     insertbackground=COLORS['text'], relief='flat',
                     font=FONTS['body']
                     ).grid(row=1, column=col, padx=5, pady=3)

        ttk.Button(sec2, text="➕  Agregar proceso", style='TButton',
                   command=self._add_manual).pack(padx=10, pady=(0, 10), anchor='w')

        #  Danger zone
        ttk.Separator(left, orient='horizontal').pack(fill='x', padx=12, pady=6)
        ttk.Button(left, text="🗑  Limpiar todo", style='Danger.TButton',
                   command=self._clear_all).pack(padx=12, pady=(0, 14), anchor='w')

    def _build_right(self, parent: tk.Frame) -> None:
        right = tk.Frame(parent, bg=COLORS['surface0'])
        right.grid(row=0, column=1, sticky='nsew')
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        tk.Label(right, text="Procesos Cargados",
                 bg=COLORS['surface0'], fg=COLORS['blue'], font=FONTS['heading']
                 ).grid(row=0, column=0, sticky='w', padx=16, pady=(14, 8))

        tree_wrap = tk.Frame(right, bg=COLORS['surface0'])
        tree_wrap.grid(row=1, column=0, sticky='nsew', padx=16, pady=(0, 14))
        tree_wrap.rowconfigure(0, weight=1)
        tree_wrap.columnconfigure(0, weight=1)

        cols = ('PID', 'Llegada', 'Ráfaga', 'Prioridad')
        self._tree = ttk.Treeview(tree_wrap, columns=cols, show='headings')
        for c in cols:
            self._tree.heading(c, text=c)
            self._tree.column(c, anchor='center', width=120)
        self._tree.grid(row=0, column=0, sticky='nsew')

        sb = ttk.Scrollbar(tree_wrap, orient='vertical', command=self._tree.yview)
        sb.grid(row=0, column=1, sticky='ns')
        self._tree.configure(yscrollcommand=sb.set)

    # Helpers

    @staticmethod
    def _section(parent: tk.Frame, title: str) -> tk.Frame:
        lf = tk.LabelFrame(parent, text=f"  {title}  ",
                           bg=COLORS['surface0'], fg=COLORS['subtext1'],
                           font=FONTS['small'], bd=1, relief='groove',
                           highlightbackground=COLORS['surface1'])
        lf.pack(fill='x', padx=12, pady=(0, 10))
        return lf

    # Actions

    def _load_preset(self) -> None:
        path = PRESETS.get(self._preset_var.get(), '')
        self._load_file(path)

    def _browse_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de procesos",
            filetypes=[("JSON", "*.json"), ("Todos", "*.*")],
        )
        if path:
            self._load_file(path)

    def _load_file(self, path: str) -> None:
        try:
            procesos = leerProcesosJSON(path)
            self.app.set_procesos(procesos)
            self._status_var.set(f"✅  {len(procesos)} procesos cargados desde archivo")
        except Exception as exc:
            messagebox.showerror("Error al cargar", str(exc).strip())

    def _add_manual(self) -> None:
        try:
            pid      = int(self._fvars['PID'].get())
            llegada  = float(self._fvars['Llegada'].get())
            rafaga   = float(self._fvars['Ráfaga'].get())
            prior    = int(self._fvars['Prioridad'].get())
        except ValueError:
            messagebox.showerror("Datos inválidos", "Todos los campos deben ser numéricos.")
            return

        existing = {p.pid for p in self.app.procesos}
        if pid in existing:
            messagebox.showwarning("PID duplicado", f"Ya existe un proceso con PID {pid}.")
            return

        try:
            nuevo = Process(pid, llegada, rafaga, prior)
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Error", str(exc).strip())
            return

        self.app.procesos.append(nuevo)
        self.app.set_procesos(self.app.procesos)
        for sv in self._fvars.values():
            sv.set('')
        self._status_var.set(f"✅  {len(self.app.procesos)} proceso(s) en total")

    def _clear_all(self) -> None:
        if messagebox.askyesno("Confirmar", "¿Eliminar todos los procesos cargados?"):
            self.app.set_procesos([])
            self._status_var.set("Sin procesos cargados")

    # Called by app when processes change

    def on_update(self) -> None:
        self._tree.delete(*self._tree.get_children())
        for p in self.app.procesos:
            self._tree.insert('', 'end', values=(p.pid, p.llegada, p.rafaga, p.prioridad))
        n = len(self.app.procesos)
        if n:
            self._status_var.set(f"✅  {n} proceso(s) cargados")
        else:
            self._status_var.set("Sin procesos cargados")
