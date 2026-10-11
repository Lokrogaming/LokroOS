#!/usr/bin/env python3
"""LokroOS System-Stats – Backend für das Dashboard (CPU/RAM/GPU/Netz/Tasks).

Quellen (Linux): /proc/stat, /proc/meminfo, /proc/net/dev, /proc/<pid>/…,
GPU: nvidia-smi → rocm-smi → intel_gpu_top (jeweils mit Timeout, nur lesend).
Auf Nicht-Linux oder bei Fehlern: strukturierter Payload mit "supported": false –
das Dashboard zeigt dann einen klaren Hinweis. NIEMALS Crash (Exit immer 0),
kein Root nötig, keine Secrets.

CLI:
    lokroos-stats.py --once [--proc DIR]          ein JSON-Objekt (QML-Polling)
    lokroos-stats.py --loop [SEKUNDEN] [--proc DIR]  JSON-Zeilen fortlaufend
    lokroos-stats.py --check                      Exit 0 + Kurzdiagnose

Der Parameter --proc dient Tests (Fixture-Verzeichnis statt /proc).
Status: IMPLEMENTED (Backend + Tests), QML-Einbindung UNVERIFIED.
"""
import json
import os
import shutil
import subprocess
import sys
import time

SAMPLE_GAP = 0.25  # Sekunden zwischen zwei CPU/Net-Samples im --once-Modus


# ---------------------------------------------------------------- CPU
def read_cpu_times(proc_dir="/proc"):
    """Liest {cpu-id: [user,nice,system,idle,iowait,irq,softirq,...]}."""
    times = {}
    try:
        with open(os.path.join(proc_dir, "stat"), encoding="utf-8") as fh:
            for line in fh:
                if not line.startswith("cpu"):
                    continue
                parts = line.split()
                name = parts[0]
                vals = [int(x) for x in parts[1:]]
                if len(vals) >= 4:
                    times[name] = vals
    except OSError:
        pass
    return times


def cpu_usage(prev, cur):
    """Berechnet Auslastung je cpu-id aus zwei Samples (0..100)."""
    out = {}
    for name, c in cur.items():
        p = prev.get(name)
        if not p:
            continue
        total_p, total_c = sum(p), sum(c)
        idle_p, idle_c = p[3] + p[4] if len(p) > 4 else p[3], c[3] + c[4] if len(c) > 4 else c[3]
        d_total, d_idle = total_c - total_p, idle_c - idle_p
        out[name] = round((1.0 - d_idle / d_total) * 100.0, 1) if d_total > 0 else 0.0
    return out


# ---------------------------------------------------------------- RAM
def read_mem(proc_dir="/proc"):
    mem = {"total_kb": 0, "available_kb": 0, "swap_total_kb": 0, "swap_free_kb": 0}
    try:
        with open(os.path.join(proc_dir, "meminfo"), encoding="utf-8") as fh:
            for line in fh:
                key, _, rest = line.partition(":")
                val = rest.strip().split()
                if not val:
                    continue
                num = int(val[0])
                if key == "MemTotal":
                    mem["total_kb"] = num
                elif key == "MemAvailable":
                    mem["available_kb"] = num
                elif key == "SwapTotal":
                    mem["swap_total_kb"] = num
                elif key == "SwapFree":
                    mem["swap_free_kb"] = num
    except OSError:
        pass
    total = mem["total_kb"]
    used = max(total - mem["available_kb"], 0)
    st, sf = mem["swap_total_kb"], mem["swap_free_kb"]
    return {
        "total_mb": round(total / 1024.0, 1),
        "used_mb": round(used / 1024.0, 1),
        "used_pct": round(used / total * 100.0, 1) if total else 0.0,
        "swap_pct": round((st - sf) / st * 100.0, 1) if st else 0.0,
    }


# ---------------------------------------------------------------- Netz
def read_net_counters(proc_dir="/proc"):
    """{iface: (rx_bytes, tx_bytes)}, ohne lo."""
    counters = {}
    try:
        with open(os.path.join(proc_dir, "net", "dev"), encoding="utf-8") as fh:
            for line in fh:
                if ":" not in line:
                    continue
                iface, _, data = line.partition(":")
                iface = iface.strip()
                if iface == "lo" or iface.startswith("Inter"):
                    continue
                fields = data.split()
                if len(fields) >= 9:
                    counters[iface] = (int(fields[0]), int(fields[8]))
    except OSError:
        pass
    return counters


def net_rates(prev, cur, gap):
    rx = sum(c[0] - prev.get(i, (0, 0))[0] for i, c in cur.items())
    tx = sum(c[1] - prev.get(i, (0, 0))[1] for i, c in cur.items())
    if gap <= 0:
        return 0.0, 0.0
    return round(rx / gap / 1024.0, 1), round(tx / gap / 1024.0, 1)


# ---------------------------------------------------------------- Tasks
def read_tasks(proc_dir="/proc", limit=8):
    """Top-`limit`-Prozesse nach RSS + Zähler. Nur lesend."""
    procs, total, running = [], 0, 0
    try:
        pids = [d for d in os.listdir(proc_dir) if d.isdigit()]
    except OSError:
        return {"count": 0, "running": 0, "top": []}
    for pid in pids:
        total += 1
        try:
            with open(os.path.join(proc_dir, pid, "comm"), encoding="utf-8") as fh:
                name = fh.read().strip()[:48]
            state = "?"
            rss = 0
            with open(os.path.join(proc_dir, pid, "status"), encoding="utf-8",
                      errors="replace") as fh:
                for line in fh:
                    if line.startswith("State:"):
                        state = line.split()[1]
                    elif line.startswith("VmRSS:"):
                        rss = int(line.split()[1])  # kB
            if state == "R":
                running += 1
            procs.append({"pid": int(pid), "name": name or pid,
                          "state": state, "mem_kb": rss})
        except (OSError, ValueError, IndexError):
            continue
    procs.sort(key=lambda p: p["mem_kb"], reverse=True)
    return {"count": total, "running": running, "top": procs[:limit]}


# ---------------------------------------------------------------- GPU
def _run(cmd, timeout=3):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def read_gpu(run=_run):
    """Erkennt NVIDIA → AMD → Intel, nur lesend. Sonst present:false."""
    if shutil.which("nvidia-smi"):
        out = run(["nvidia-smi", "--query-gpu=name,utilization.gpu,memory.used,"
                                 "memory.total", "--format=csv,noheader,nounits"])
        if out:
            try:
                name, load, mu, mt = [x.strip() for x in out.splitlines()[0].split(",")]
                return {"present": True, "vendor": "nvidia", "name": name,
                        "load_pct": float(load), "mem_used_mb": float(mu),
                        "mem_total_mb": float(mt)}
            except (ValueError, IndexError):
                pass
    if shutil.which("rocm-smi"):
        out = run(["rocm-smi", "--showuse", "--showmeminfo", "vram"])
        if out:
            return {"present": True, "vendor": "amd", "name": "AMD GPU",
                    "load_pct": 0.0, "mem_used_mb": 0.0, "mem_total_mb": 0.0,
                    "note": "rocm-smi-Parsing folgt (M3)"}
    if shutil.which("intel_gpu_top"):
        return {"present": True, "vendor": "intel", "name": "Intel iGPU",
                "load_pct": 0.0, "mem_used_mb": 0.0, "mem_total_mb": 0.0,
                "note": "intel_gpu_top braucht i. d. R. Root (M3)"}
    return {"present": False, "vendor": "none", "name": "",
            "load_pct": 0.0, "mem_used_mb": 0.0, "mem_total_mb": 0.0}


# ---------------------------------------------------------------- Snapshot
def snapshot(proc_dir="/proc", gap=SAMPLE_GAP, sleep_fn=time.sleep):
    if proc_dir == "/proc" and not sys.platform.startswith("linux"):
        # Strukturiert statt Crash – Dashboard zeigt Hinweis.
        # Explizite --proc-Pfade (Tests) laufen plattformunabhängig.
        return {"supported": False, "reason": "nur Linux (/proc)"}
    c0, n0 = read_cpu_times(proc_dir), read_net_counters(proc_dir)
    try:
        sleep_fn(gap)
    except Exception:  # noqa: BLE001
        pass
    c1, n1 = read_cpu_times(proc_dir), read_net_counters(proc_dir)
    usage = cpu_usage(c0, c1)
    cores = sorted(k for k in usage if k != "cpu")
    rx, tx = net_rates(n0, n1, gap)
    return {
        "supported": True,
        "ts": time.time(),
        "cpu": {"load_pct": usage.get("cpu", 0.0), "cores": len(cores),
                "per_core": [usage[k] for k in cores]},
        "mem": read_mem(proc_dir),
        "net": {"rx_kbps": rx, "tx_kbps": tx, "ifaces": sorted(n1)},
        "gpu": read_gpu(),
        "tasks": read_tasks(proc_dir),
    }


def main(argv):
    try:
        proc_dir = "/proc"
        if "--proc" in argv:
            proc_dir = argv[argv.index("--proc") + 1]
        if "--check" in argv:
            s = snapshot(proc_dir, gap=0.05)
            print("lokroos-stats OK" if s.get("supported") else "lokroos-stats: " +
                  s.get("reason", "nicht unterstützt"))
            return 0
        if "--loop" in argv:
            try:
                gap = float(argv[argv.index("--loop") + 1])
            except (ValueError, IndexError):
                gap = 2.0
            gap = min(max(gap, 0.5), 60.0)
            prev_c, prev_n = read_cpu_times(proc_dir), read_net_counters(proc_dir)
            while True:
                time.sleep(gap)
                cur_c, cur_n = read_cpu_times(proc_dir), read_net_counters(proc_dir)
                usage = cpu_usage(prev_c, cur_c)
                cores = sorted(k for k in usage if k != "cpu")
                rx, tx = net_rates(prev_n, cur_n, gap)
                print(json.dumps({
                    "supported": True, "ts": time.time(),
                    "cpu": {"load_pct": usage.get("cpu", 0.0), "cores": len(cores),
                            "per_core": [usage[k] for k in cores]},
                    "mem": read_mem(proc_dir),
                    "net": {"rx_kbps": rx, "tx_kbps": tx, "ifaces": sorted(cur_n)},
                    "gpu": read_gpu(),
                    "tasks": read_tasks(proc_dir),
                }), flush=True)
                prev_c, prev_n = cur_c, cur_n
            return 0  # unerreichbar, nur für Klarheit
        print(json.dumps(snapshot(proc_dir)))
        return 0
    except Exception as exc:  # noqa: BLE001 – Dashboard darf nie hängen
        print(json.dumps({"supported": False, "reason": f"Fehler: {exc}"}))
        return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
