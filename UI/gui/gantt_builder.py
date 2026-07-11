import re
from plan.process.process_class import Process


def build_segments(log: str, procesos: list[Process]) -> list[tuple[int, float, float]]:
    segments: list[tuple[int, float, float]] = []
    active: dict[int, float] = {}
    current_time: float = 0.0

    for raw in log.splitlines():
        line = raw.strip()
        if not line:
            continue

        t_match = re.match(r'Tiempo\s+([\d.]+)', line)
        if t_match:
            current_time = float(t_match.group(1))

        # "Inicia proceso X"
        sm = re.search(r'[Ii]nicia proceso (\d+)', line)
        if sm:
            pid = int(sm.group(1))
            active[pid] = current_time

        em = re.search(r'Termina proceso (\d+)', line)
        if em:
            pid = int(em.group(1))
            if pid in active:
                segments.append((pid, active.pop(pid), current_time))

        im = re.search(r'[Pp]roceso (\d+) se interrumpe', line)
        if im:
            pid = int(im.group(1))
            if pid in active:
                segments.append((pid, active.pop(pid), current_time))

        pm = re.search(r'[Ss]e interrumpe proceso (\d+)', line)
        if pm:
            pid = int(pm.group(1))
            if pid in active:
                segments.append((pid, active.pop(pid), current_time))

    for pid, start in active.items():
        segments.append((pid, start, current_time))

    return sorted(segments, key=lambda s: s[1])
