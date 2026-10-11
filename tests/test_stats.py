"""Tests für shell/stats/lokroos-stats.py – mit Fixture-/proc (plattformunabhängig)."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATS = ROOT / "shell" / "stats" / "lokroos-stats.py"
FIX = Path(__file__).parent / "fixtures" / "proc"


def load_module():
    spec = importlib.util.spec_from_file_location("lokroos_stats", STATS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_proc(tmp_path):
    """Baut Fake-/proc: stat, meminfo, net/dev, zwei PIDs."""
    proc = tmp_path / "proc"
    (proc / "net").mkdir(parents=True)
    shutil.copy(FIX / "stat", proc / "stat")
    shutil.copy(FIX / "meminfo", proc / "meminfo")
    shutil.copy(FIX / "net_dev", proc / "net" / "dev")
    for pid, name, state, rss in (("1", "systemd", "S", 12500),
                                  ("42", "plasmashell", "R", 310000)):
        d = proc / pid
        d.mkdir()
        (d / "comm").write_text(name + "\n", encoding="utf-8")
        (d / "status").write_text(f"Name:\t{name}\nState:\t{state} (running)\n"
                                  f"VmRSS:\t{rss} kB\n", encoding="utf-8")
    return proc


def test_cpu_usage_math():
    mod = load_module()
    prev = {"cpu": [100, 0, 0, 900, 0, 0, 0]}
    cur = {"cpu": [200, 0, 0, 1700, 0, 0, 0]}
    out = mod.cpu_usage(prev, cur)
    assert out["cpu"] == 11.1  # d_total=900, d_idle=800
    assert mod.cpu_usage(prev, prev)["cpu"] == 0.0  # keine Division durch 0


def test_read_mem_fixture(tmp_path):
    mod = load_module()
    proc = make_proc(tmp_path)
    mem = mod.read_mem(str(proc))
    assert mem["total_mb"] == round(8000000 / 1024.0, 1)
    assert mem["used_pct"] == 50.0  # (8000000-4000000)/8000000
    assert mem["swap_pct"] == 25.0


def test_read_net_skips_lo(tmp_path):
    mod = load_module()
    proc = make_proc(tmp_path)
    counters = mod.read_net_counters(str(proc))
    assert set(counters) == {"eth0", "wlan0"}
    rx, tx = mod.net_rates({}, counters, 1.0)
    assert rx == round((2048000 + 4096000) / 1024.0, 1)
    assert tx == round((1024000 + 2048000) / 1024.0, 1)


def test_read_tasks_fixture(tmp_path):
    mod = load_module()
    proc = make_proc(tmp_path)
    tasks = mod.read_tasks(str(proc), limit=8)
    assert tasks["count"] == 2
    assert tasks["running"] == 1
    assert tasks["top"][0]["name"] == "plasmashell"  # höchstes RSS zuerst
    assert tasks["top"][0]["mem_kb"] == 310000


def test_gpu_no_drivers_graceful(monkeypatch):
    mod = load_module()
    monkeypatch.setattr(mod.shutil, "which", lambda _name: None)
    gpu = mod.read_gpu()
    assert gpu == {"present": False, "vendor": "none", "name": "",
                   "load_pct": 0.0, "mem_used_mb": 0.0, "mem_total_mb": 0.0}


def test_gpu_nvidia_parsing(monkeypatch):
    mod = load_module()
    monkeypatch.setattr(mod.shutil, "which",
                        lambda name: "/usr/bin/nvidia-smi" if name == "nvidia-smi" else None)
    gpu = mod.read_gpu(run=lambda _cmd, timeout=3:
                       "GeForce RTX 4070, 37, 2048, 12288")
    assert gpu["vendor"] == "nvidia" and gpu["load_pct"] == 37.0
    assert gpu["mem_total_mb"] == 12288.0


def test_snapshot_end_to_end(tmp_path):
    mod = load_module()
    proc = make_proc(tmp_path)
    snap = mod.snapshot(str(proc), gap=0.01, sleep_fn=lambda _s: None)
    assert snap["supported"] is True
    assert set(snap) >= {"cpu", "mem", "net", "gpu", "tasks", "ts"}
    assert snap["mem"]["used_pct"] == 50.0
    assert snap["tasks"]["count"] == 2
    assert isinstance(snap["cpu"]["per_core"], list)


def test_cli_once_and_check(tmp_path):
    proc = make_proc(tmp_path)
    r = subprocess.run([sys.executable, str(STATS), "--once", "--proc", str(proc)],
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 0
    payload = json.loads(r.stdout.strip())
    assert payload["supported"] is True and "cpu" in payload
    r2 = subprocess.run([sys.executable, str(STATS), "--check", "--proc", str(proc)],
                        capture_output=True, text=True, timeout=30)
    assert r2.returncode == 0 and "OK" in r2.stdout
