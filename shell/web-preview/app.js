/* LokroOS Web-Preview: Fenstermanager + Dashboard (Home) + Live-Stats-Simulation.
   Echtdaten auf dem Zielsystem: shell/stats/lokroos-stats.py (JSON) – hier simuliert,
   ehrlich per "Preview-Simulation"-Badge gekennzeichnet. Stand 2026-10-11 (v0.2.0). */
(function () {
  "use strict";

  var I18N = {
    de: {
      welcome: "Willkommen zurück, {user}!",
      dashboard: "Dashboard", launcher: "Anwendungslauncher", devtools: "Entwicklerwerkzeuge",
      sim: "Preview-Simulation", "tab-overview": "Übersicht", "tab-processes": "Prozesse",
      "tab-network": "Netzwerk", cpu: "CPU", ram: "RAM", gpu: "GPU", net: "Netzwerk",
      "top-procs": "Top-Prozesse", ifaces: "Interfaces", "tabs-empty": "Alle Tabs geschlossen.",
      "tabs-restore": "Tabs wiederherstellen",
      "stats-note": "Echtzeitwerte vom Zielsystem liefert shell/stats/lokroos-stats.py (CPU/RAM/GPU/Netz/Tasks als JSON).",
      "wine-hint": ".exe-Dateien werden nicht automatisch geöffnet – Rechtsklick → „Mit Wine ausführen“.",
      search: "Suchen …",
      "theme-title": "Farbschema wechseln (dunkel/hell)"
    },
    en: {
      welcome: "Welcome back, {user}!",
      dashboard: "Dashboard", launcher: "Application launcher", devtools: "Developer tools",
      sim: "Preview simulation", "tab-overview": "Overview", "tab-processes": "Processes",
      "tab-network": "Network", cpu: "CPU", ram: "RAM", gpu: "GPU", net: "Network",
      "top-procs": "Top processes", ifaces: "Interfaces", "tabs-empty": "All tabs closed.",
      "tabs-restore": "Restore tabs",
      "stats-note": "Live values on target come from shell/stats/lokroos-stats.py (CPU/RAM/GPU/Net/Tasks as JSON).",
      "wine-hint": ".exe files never auto-launch – right-click → “Run with Wine”.",
      search: "Search …",
      "theme-title": "Toggle color scheme (dark/light)"
    }
  };

  var APPS = [
    { name: "Terminal", glyph: "▣" }, { name: "VS Code", glyph: "◈" },
    { name: "Dateien", glyph: "▤" }, { name: "Steam", glyph: "◉" },
    { name: "Bottles", glyph: "▦" }, { name: "ProtonVPN", glyph: "⬢" },
    { name: "Einstellungen", glyph: "⚙" }, { name: "Systemverwaltung", glyph: "◍" },
    { name: "GitHub CLI", glyph: "⑂" }, { name: "Browser", glyph: "◎" }
  ];
  var DEVTOOLS = ["Node.js + npm", "Git", "GitHub CLI (gh)", "VS Code", "Python 3",
    "Build-Essentials", "Wine + Winetricks", "curl / wget / unzip", "OpenSSH-Client"];
  var GAMING = ["Steam", "Proton (in Steam)", "Wine", "Winetricks", "Bottles (optional)"];
  var PROCS = [
    { name: "plasmashell", cpu: 4, mem: 310 }, { name: "kwin_wayland", cpu: 6, mem: 220 },
    { name: "steam", cpu: 9, mem: 480 }, { name: "code", cpu: 12, mem: 620 },
    { name: "firefox", cpu: 15, mem: 840 }, { name: "wine64-preloader", cpu: 11, mem: 350 },
    { name: "explorer.exe (Wine)", cpu: 3, mem: 120 }, { name: "konsole", cpu: 2, mem: 95 },
    { name: "pipewire", cpu: 1, mem: 40 }, { name: "lokroos-stats", cpu: 1, mem: 18 }
  ];

  var lang = "de", user = "gast", reduced = false;
  var HIST = 60;
  var sim = { cpu: [], ram: [], gpu: [], net: [], rx: [], tx: [],
              cpuV: 24, ramV: 46, gpuV: 31, rxV: 420, txV: 130 };

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
  function walk(v, min, max, step) {
    v += (Math.random() - 0.5) * step;
    if (v < min) v = min + Math.random() * step;
    if (v > max) v = max - Math.random() * step;
    return v;
  }
  function push(arr, v) { arr.push(v); if (arr.length > HIST) arr.shift(); }

  /* ---------- Charts ---------- */
  function isLight() { return document.documentElement.getAttribute("data-theme") === "light"; }
  function pal() {
    return isLight()
      ? { main: "#0284C7", second: "#0369A1", grid: "rgba(14,60,110,0.14)", fill0: "rgba(2,132,199,0.35)", fill1: "rgba(2,132,199,0.02)" }
      : { main: "#22D3EE", second: "#7DD3FC", grid: "rgba(148,197,255,0.15)", fill0: "rgba(34,211,238,0.45)", fill1: "rgba(34,211,238,0.02)" };
  }
  function drawSpark(id, arr, max) {
    var cv = $(id);
    if (!cv) return;
    var dpr = window.devicePixelRatio || 1;
    var w = cv.clientWidth || 220, h = cv.clientHeight || 56;
    if (cv.width !== w * dpr) { cv.width = w * dpr; cv.height = h * dpr; }
    var ctx = cv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    ctx.strokeStyle = pal().grid;
    ctx.lineWidth = 1;
    for (var g = 1; g < 4; g++) {
      ctx.beginPath(); ctx.moveTo(0, h * g / 4); ctx.lineTo(w, h * g / 4); ctx.stroke();
    }
    if (arr.length < 2) return;
    var grad = ctx.createLinearGradient(0, 0, 0, h);
    grad.addColorStop(0, pal().fill0);
    grad.addColorStop(1, pal().fill1);
    ctx.beginPath();
    arr.forEach(function (v, i) {
      var x = i / (HIST - 1) * w, y = h - Math.min(v / max, 1) * (h - 6) - 3;
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    });
    ctx.strokeStyle = pal().main; ctx.lineWidth = 1.8; ctx.stroke();
    ctx.lineTo((arr.length - 1) / (HIST - 1) * w, h);
    ctx.lineTo(0, h); ctx.closePath();
    ctx.fillStyle = grad; ctx.fill();
  }

  function drawNetBig() {
    var cv = $("c-netbig");
    if (!cv || $("pane-network").hidden) return;
    var dpr = window.devicePixelRatio || 1;
    var w = cv.clientWidth || 400, h = cv.clientHeight || 120;
    if (cv.width !== w * dpr) { cv.width = w * dpr; cv.height = h * dpr; }
    var ctx = cv.getContext("2d");
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, w, h);
    var max = 1200;
    [["rx", pal().main], ["tx", pal().second]].forEach(function (pair) {
      var arr = sim[pair[0]];
      if (arr.length < 2) return;
      ctx.beginPath();
      arr.forEach(function (v, i) {
        var x = i / (HIST - 1) * w, y = h - Math.min(v / max, 1) * (h - 10) - 5;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      });
      ctx.strokeStyle = pair[1]; ctx.lineWidth = 1.8; ctx.stroke();
    });
  }

  /* ---------- Fenster (Taskbar) ---------- */
  function setWin(id, show, animate) {
    var w = $(id);
    var btn = document.querySelector('.task-btn[data-open="' + id + '"]');
    if (show) {
      w.hidden = false;
      if (animate && !reduced) {
        w.classList.remove("opening"); void w.offsetWidth; w.classList.add("opening");
      }
      if (btn) btn.classList.add("active");
    } else {
      var hide = function () { w.hidden = true; w.classList.remove("closing"); };
      if (animate && !reduced) {
        w.classList.add("closing"); setTimeout(hide, 150);
      } else hide();
      if (btn) btn.classList.remove("active");
    }
  }
  function bindWindows() {
    document.querySelectorAll(".task-btn[data-open]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-open");
        setWin(id, $(id).hidden, true);
      });
    });
    document.querySelectorAll(".win-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        setWin(btn.getAttribute("data-win"), false, true); // min + close: sanft ausblenden
      });
    });
  }

  /* ---------- Dashboard-Tabs (schließbar) ---------- */
  var TAB_ORDER = ["pane-overview", "pane-processes", "pane-network"];
  var closedTabs = {};
  function bindTabs() {
    var bar = $("dash-tabs");
    if (!bar.dataset.enhanced) {
      bar.dataset.enhanced = "1";
      bar.querySelectorAll(".tab").forEach(function (tab) {
        var x = document.createElement("button");
        x.className = "x"; x.textContent = "×";
        x.setAttribute("aria-label", "Tab schließen");
        x.addEventListener("click", function (e) { e.stopPropagation(); closeTab(tab); });
        tab.appendChild(x);
        tab.addEventListener("click", function () {
          if (tab.dataset.closed) return;
          activateTab(tab.getAttribute("data-tab"));
        });
      });
    }
    $("tab-restore").addEventListener("click", restoreTabs);
    $("btn-restore-tabs").addEventListener("click", restoreTabs);
  }
  function activateTab(id) {
    document.querySelectorAll("#dash-tabs .tab").forEach(function (t) {
      t.classList.toggle("active", t.getAttribute("data-tab") === id && !t.dataset.closed);
    });
    TAB_ORDER.forEach(function (p) { $(p).hidden = (p !== id); });
    $("tabs-empty").hidden = true;
    if (id === "pane-network") drawNetBig();
  }
  function closeTab(tab) {
    tab.dataset.closed = "1"; tab.style.display = "none";
    closedTabs[tab.getAttribute("data-tab")] = true;
    $(tab.getAttribute("data-tab")).hidden = true;
    var next = TAB_ORDER.find(function (p) { return !closedTabs[p]; });
    if (next) activateTab(next);
    else {
      document.querySelectorAll("#dash-tabs .tab").forEach(function (t) { t.classList.remove("active"); });
      $("tabs-empty").hidden = false;
    }
  }
  function restoreTabs() {
    closedTabs = {};
    document.querySelectorAll("#dash-tabs .tab").forEach(function (t) {
      delete t.dataset.closed; t.style.display = "";
    });
    activateTab("pane-overview");
  }

  /* ---------- Stats-Engine (Simulation; Target: lokroos-stats.py) ---------- */
  function tickStats() {
    sim.cpuV = walk(sim.cpuV, 6, 88, 9);
    sim.ramV = walk(sim.ramV, 34, 74, 2.5);
    sim.gpuV = walk(sim.gpuV, 5, 96, 12);
    sim.rxV = Math.max(20, walk(sim.rxV, 20, 1100, 220));
    sim.txV = Math.max(8, walk(sim.txV, 8, 420, 90));
    push(sim.cpu, sim.cpuV); push(sim.ram, sim.ramV);
    push(sim.gpu, sim.gpuV); push(sim.net, (sim.rxV + sim.txV) / 14);
    push(sim.rx, sim.rxV); push(sim.tx, sim.txV);

    $("v-cpu").textContent = Math.round(sim.cpuV) + " %";
    $("b-cpu").style.width = sim.cpuV + "%";
    $("s-cpu").textContent = "8 Kerne · Ryzen 7";
    $("v-ram").textContent = Math.round(sim.ramV) + " %";
    $("b-ram").style.width = sim.ramV + "%";
    $("s-ram").textContent = (sim.ramV * 32 / 100).toFixed(1) + " / 32 GB";
    $("v-gpu").textContent = Math.round(sim.gpuV) + " %";
    $("b-gpu").style.width = sim.gpuV + "%";
    $("s-gpu").textContent = lang === "de" ? "Ziel: nvidia-smi / rocm / intel" : "Target: nvidia-smi / rocm / intel";
    var netPct = Math.min((sim.rxV + sim.txV) / 14, 100);
    $("v-net").textContent = Math.round(sim.rxV + sim.txV) + " KB/s";
    $("b-net").style.width = netPct + "%";
    $("s-net").textContent = "eth0 · wlan0";

    drawSpark("c-cpu", sim.cpu, 100); drawSpark("c-ram", sim.ram, 100);
    drawSpark("c-gpu", sim.gpu, 100); drawSpark("c-net", sim.net, 100);
    drawNetBig();
    $("v-rx").textContent = Math.round(sim.rxV) + " KB/s";
    $("v-tx").textContent = Math.round(sim.txV) + " KB/s";
    $("v-if").textContent = "2";
    renderProcs();
  }

  function renderProcs() {
    var box = $("proc-list");
    if (!box || $("pane-processes").hidden) return;
    var rows = PROCS.map(function (p) {
      p.cpu = Math.max(0.2, walk(p.cpu, 0.2, 60, 4));
      return p;
    }).sort(function (a, b) { return b.cpu - a.cpu; }).slice(0, 8);
    $("proc-count").textContent = PROCS.length + (lang === "de" ? " Prozesse" : " processes");
    box.innerHTML = rows.map(function (p) {
      return '<div class="proc-row"><span class="nm">' + esc(p.name) + "</span>" +
        '<span class="pc">' + p.cpu.toFixed(1) + ' %</span><span class="bar"><i style="width:' +
        Math.min(p.cpu * 1.6, 100) + '%"></i></span></div>';
    }).join("");
  }

  /* ---------- Launcher / Listen / Uhr / Toast ---------- */
  function toast(msg) {
    var d = document.createElement("div");
    d.className = "toast"; d.textContent = msg;
    $("toast-region").appendChild(d);
    setTimeout(function () { d.remove(); }, 2600);
  }
  function renderLauncher(filter) {
    var grid = $("launcher-grid");
    grid.innerHTML = "";
    APPS.filter(function (a) {
      return !filter || a.name.toLowerCase().indexOf(filter.toLowerCase()) !== -1;
    }).forEach(function (a) {
      var b = document.createElement("button");
      b.className = "launcher-item";
      b.innerHTML = '<span class="glyph">' + esc(a.glyph) + '</span><span>' + esc(a.name) + "</span>";
      b.addEventListener("click", function () { toast(a.name + " … (Prototyp)"); });
      grid.appendChild(b);
    });
  }
  function renderLists() {
    $("tool-list").innerHTML = DEVTOOLS.map(function (t) {
      return "<li><span>" + esc(t) + '</span><span class="badge">M2-VM</span></li>';
    }).join("");
    $("gaming-list").innerHTML = GAMING.map(function (t) {
      return "<li><span>" + esc(t) + '</span><span class="badge">M2-VM</span></li>';
    }).join("");
    $("iface-chips").innerHTML = ["eth0", "wlan0"].map(function (i) {
      return '<span class="chip">' + esc(i) + "</span>";
    }).join("");
  }
  function applyLang(l) {
    lang = l;
    var dict = I18N[l] || I18N.de;
    document.documentElement.lang = l;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var k = el.getAttribute("data-i18n");
      if (dict[k]) el.textContent = dict[k];
    });
    $("launcher-search").placeholder = dict.search;
    $("btn-lang").textContent = l.toUpperCase();
    $("btn-theme").title = dict["theme-title"] || "";
    $("welcome-text").innerHTML = esc(dict.welcome.split("{user}")[0]) +
      "<span>" + esc(user) + "</span>" + esc(dict.welcome.split("{user}")[1] || "");
    return dict;
  }
  function tickClock() {
    function tick() {
      var d = new Date();
      $("clock").textContent = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
    }
    tick(); setInterval(tick, 15000);
  }

  function init() {
    lang = (navigator.language || "de").toLowerCase().indexOf("en") === 0 ? "en" : "de";
    try {
      var m = String(window.location.pathname).match(/\/Users\/([^\/]+)/);
      if (m) user = m[1];
    } catch (e) { /* ignore */ }
    reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    applyLang(lang);
    $("btn-user").textContent = (user[0] || "U").toUpperCase();

    bindWindows(); bindTabs();
    renderLauncher(""); renderLists(); tickClock();

    $("launcher-search").addEventListener("input", function (e) { renderLauncher(e.target.value); });
    $("btn-lang").addEventListener("click", function () {
      applyLang(lang === "de" ? "en" : "de");
      toast(lang === "de" ? "Sprache: Deutsch" : "Language: English");
    });
    $("btn-theme").addEventListener("click", function () {
      var h = document.documentElement;
      if (h.getAttribute("data-theme") === "light") h.removeAttribute("data-theme");
      else h.setAttribute("data-theme", "light");
    });
    ["q-wifi", "q-audio", "q-bright", "q-vpn"].forEach(function (id) {
      $(id).addEventListener("click", function (e) { e.currentTarget.classList.toggle("active"); });
    });
    $("btn-power").addEventListener("click", function () {
      toast(lang === "de" ? "Energieoptionen (Prototyp)" : "Power options (prototype)");
    });

    // Welcome → Desktop → Dashboard (Home) öffnet automatisch
    function reveal() {
      $("welcome-overlay").classList.add("hidden");
      $("desktop").classList.remove("desktop-hidden");
      setWin("win-dashboard", true, true);
      tickStats();
      setInterval(tickStats, 1000);
    }
    if (reduced) reveal(); else setTimeout(reveal, 1800);
    window.addEventListener("resize", function () {
      drawSpark("c-cpu", sim.cpu, 100); drawSpark("c-ram", sim.ram, 100);
      drawSpark("c-gpu", sim.gpu, 100); drawSpark("c-net", sim.net, 100);
      drawNetBig();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
