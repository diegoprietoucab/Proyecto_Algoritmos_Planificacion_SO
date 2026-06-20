import sys
import queue
import threading
import tkinter as tk
from typing import Callable, Any


class AlgorithmRunner:

    def __init__(self, root: tk.Tk) -> None:
        self._root = root
        self._q: queue.Queue = queue.Queue()
        self._running = False
        self._log: tk.Text | None = None
        self._on_done: Callable | None = None
        self._output_buf: str = ""

    # Public

    def run(
        self,
        fn: Callable,
        args: tuple,
        log_widget: tk.Text,
        on_done: Callable[[bool, Any, str], None],
    ) -> None:
        if self._running:
            return 
        self._log = log_widget
        self._on_done = on_done
        self._running = True
        self._output_buf = ""

        self._clear_log()
        thread = threading.Thread(target=self._worker, args=(fn, args), daemon=True)
        thread.start()
        self._poll()

    # Private

    def _worker(self, fn: Callable, args: tuple) -> None:
        q = self._q

        class _Pipe:
            def write(self, text: str) -> None: 
                q.put(('TEXT', text))
            def flush(self) -> None:
                pass

        old = sys.stdout
        sys.stdout = _Pipe()
        try:
            result = fn(*args)
            q.put(('DONE', result))
        except Exception as exc:
            q.put(('ERROR', str(exc)))
        finally:
            sys.stdout = old

    def _poll(self) -> None:
        try:
            while True:
                kind, payload = self._q.get_nowait()
                if kind == 'TEXT':
                    self._output_buf += payload
                    self._append(payload)
                elif kind == 'DONE':
                    self._finish(True, payload)
                    return
                elif kind == 'ERROR':
                    self._append(f"\n[ERROR] {payload}\n")
                    self._finish(False, None)
                    return
        except queue.Empty:
            pass
        if self._running:
            self._root.after(50, self._poll)

    def _finish(self, success: bool, result: Any) -> None:
        self._running = False
        if self._on_done:
            self._on_done(success, result, self._output_buf)

    def _clear_log(self) -> None:
        if self._log:
            self._log.configure(state='normal')
            self._log.delete('1.0', tk.END)
            self._log.configure(state='disabled')

    def _append(self, text: str) -> None:
        if not self._log:
            return
        self._log.configure(state='normal')
        self._log.insert(tk.END, text)
        self._log.see(tk.END)
        self._log.configure(state='disabled')
