import tkinter as tk
from tkinter import ttk, messagebox

from UI.gui.theme import COLORS, FONTS, PROCESS_COLORS


class GanttPanel(tk.Frame):
    def __init__(self, parent: tk.Widget, app) -> None:
        super().__init__(parent, bg=COLORS['base'])
        self.app = app
        self._build()

    # Layout

    def _build(self) -> None:
        # Title
        tk.Label(self, text="📊  Diagrama de Gantt",
                 bg=COLORS['base'], fg=COLORS['text'], font=FONTS['title']
                 ).pack(anchor='w', padx=30, pady=(24, 0))
        tk.Frame(self, bg=COLORS['surface1'], height=1).pack(fill='x', padx=30, pady=(8, 0))

        # Toolbar row
        toolbar_row = tk.Frame(self, bg=COLORS['base'])
        toolbar_row.pack(fill='x', padx=30, pady=8)

        self._algo_label = tk.Label(toolbar_row, text="Sin datos — ejecute un algoritmo primero",
                                     bg=COLORS['base'], fg=COLORS['subtext0'], font=FONTS['body'])
        self._algo_label.pack(side='left')

        # Chart container
        self._chart_frame = tk.Frame(self, bg=COLORS['mantle'])
        self._chart_frame.pack(fill='both', expand=True, padx=30, pady=(0, 16))

        # Canvas with scrollbars
        self._canvas = tk.Canvas(self._chart_frame, bg=COLORS['surface0'], highlightthickness=0)
        
        sb_y = ttk.Scrollbar(self._chart_frame, orient='vertical', command=self._canvas.yview)
        sb_x = ttk.Scrollbar(self._chart_frame, orient='horizontal', command=self._canvas.xview)
        self._canvas.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        self._canvas.grid(row=0, column=0, sticky='nsew')
        sb_y.grid(row=0, column=1, sticky='ns')
        sb_x.grid(row=1, column=0, sticky='ew')

        self._chart_frame.rowconfigure(0, weight=1)
        self._chart_frame.columnconfigure(0, weight=1)

        # Placeholder
        self._placeholder = tk.Label(
            self._canvas,
            text="El diagrama de Gantt aparecerá aquí\ndespués de ejecutar un algoritmo.",
            bg=COLORS['surface0'], fg=COLORS['subtext0'], font=FONTS['body'],
        )
        self._placeholder.place(relx=0.5, rely=0.5, anchor='center')

    # Public

    def on_update(self) -> None:
        segments = self.app.last_gantt_data.get('segments', [])
        algo     = self.app.last_gantt_data.get('algorithm', '')
        if segments:
            self._render(segments, algo)

    # Rendering

    def _render(self, segments: list[tuple], algo: str) -> None:
        self._algo_label.configure(
            text=f"Algoritmo: {algo}", fg=COLORS['blue']
        )

        self._placeholder.place_forget()
        self._canvas.delete("all")

        # Collect unique PIDs in order of first appearance
        seen: dict[int, int] = {}
        for pid, _s, _e in segments:
            if pid not in seen:
                seen[pid] = len(seen)
        pids = list(seen.keys())
        n_rows = len(pids)

        if not segments:
            return

        total_time = max(end for _, _, end in segments)
        if total_time == 0:
            total_time = 1

        # Layout metrics
        margin_left = 60
        margin_right = 40
        margin_top = 40
        margin_bottom = 60
        row_height = 50
        bar_height = 30
        time_unit_px = max(35, 800 // int(total_time))  # Dynamic scaling

        canvas_width = margin_left + total_time * time_unit_px + margin_right
        canvas_height = margin_top + n_rows * row_height + margin_bottom

        # Allow canvas to scroll if content is larger
        self._canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

        color_map = {
            pid: PROCESS_COLORS[i % len(PROCESS_COLORS)]
            for i, pid in enumerate(pids)
        }

        # Draw X-axis grid and labels
        for t in range(int(total_time) + 1):
            x = margin_left + t * time_unit_px
            # Grid line
            self._canvas.create_line(x, margin_top, x, margin_top + n_rows * row_height,
                                     fill=COLORS['surface1'], dash=(2, 2))
            # Time label
            self._canvas.create_text(x, margin_top + n_rows * row_height + 12,
                                     text=str(t), fill=COLORS['text'], font=FONTS['small'])

        # Draw Y-axis labels
        for pid, row_idx in seen.items():
            y_center = margin_top + row_idx * row_height + row_height / 2
            self._canvas.create_text(margin_left - 15, y_center, text=f"P{pid}",
                                     fill=COLORS['text'], anchor="e", font=FONTS['body'])

        # Draw execution bars
        for pid, start, end in segments:
            row_idx = seen[pid]
            x1 = margin_left + start * time_unit_px
            x2 = margin_left + end * time_unit_px
            y1 = margin_top + row_idx * row_height + (row_height - bar_height) / 2
            y2 = y1 + bar_height

            self._canvas.create_rectangle(x1, y1, x2, y2, 
                                          fill=color_map[pid], outline=COLORS['base'], width=1.5)
            
            mid_x = (x1 + x2) / 2
            mid_y = (y1 + y2) / 2
            
            # Draw start-end text inside the bar if it fits
            if (x2 - x1) > 30:
                self._canvas.create_text(mid_x, mid_y, text=f"{start:.0f}-{end:.0f}",
                                         fill=COLORS['base'], font=('Segoe UI', 8, 'bold'))

        # Draw Legend
        legend_y = canvas_height - 25
        start_x = margin_left
        for pid in pids:
            self._canvas.create_rectangle(start_x, legend_y - 6, start_x + 12, legend_y + 6,
                                          fill=color_map[pid], outline=COLORS['base'])
            self._canvas.create_text(start_x + 20, legend_y, text=f"P{pid}",
                                     fill=COLORS['text'], anchor="w", font=FONTS['small'])
            start_x += 60
