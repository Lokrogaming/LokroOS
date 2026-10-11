/* LokroOS Web-Preview Logik – spiegelt lokroos-welcome.py + Shell-Verhalten (Stand 2026-10-11) */
(function () {
  "use strict";

  var I18N = {
    de: {
      welcome: "Willkommen zurück, {user}!",
      overview: "Systemübersicht",
      launcher: "Anwendungslauncher",
      devtools: "Entwicklerwerkzeuge",
      storage: "Speicher",
      network: "Netzwerk",
      "wine-hint": ".exe-Dateien werden nicht automatisch geöffnet – Rechtsklick → „Mit Wine ausführen“.",
      search: "Suchen …"
    },
    en: {
      welcome: "Welcome back, {user}!",
      overview: "System overview",
      launcher: "Application launcher",
      devtools: "Developer tools",
      storage: "Storage",
      network: "Network",
      "wine-hint": ".exe files never auto-launch – right-click → “Run with Wine”.",
      search: "Search …"
    }
  };

  var APPS = [
    { name: "Terminal", glyph: "▣", cat: "dev" },
    { name: "VS Code", glyph: "◈", cat: "dev" },
    { name: "Dateien", glyph: "▤", cat: "sys" },
    { name: "Steam", glyph: "◉", cat: "game" },
    { name: "Bottles", glyph: "▦", cat: "game" },
    { name: "ProtonVPN", glyph: "⬢", cat: "net" },
    { name: "Einstellungen", glyph: "⚙", cat: "sys" },
    { name: "Systemverwaltung", glyph: "▣", cat: "sys" },
    { name: "GitHub CLI", glyph: "⑂", cat: "dev" },
    { name: "Browser", glyph: "◍", cat: "net" }
  ];

  var DEVTOOLS = ["Node.js + npm", "Git", "GitHub CLI (gh)", "VS Code", "Python 3", "Build-Essentials", "curl / wget / unzip", "OpenSSH-Client"];
  var GAMING = ["Steam", "Proton (in Steam)", "Wine", "Winetricks", "Bottles (optional)"];

  function detectLang() {
    var nav = (navigator.language || "de").toLowerCase();
    return nav.indexOf("en") === 0 ? "en" : "de";
  }

  function detectUser() {
    try {
      var m = String(window.location.pathname).match(/\/Users\/([^\/]+)/);
      if (m) return m[1];
    } catch (e) { /* ignore */ }
    return "gast";
  }

  function esc(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function toast(msg) {
    var r = document.getElementById("toast-region");
    var d = document.createElement("div");
    d.className = "toast";
    d.textContent = msg;
    r.appendChild(d);
    setTimeout(function () { d.remove(); }, 2600);
  }

  function renderLauncher(filter) {
    var grid = document.getElementById("launcher-grid");
    grid.innerHTML = "";
    APPS.filter(function (a) {
      return !filter || a.name.toLowerCase().indexOf(filter.toLowerCase()) !== -1;
    }).forEach(function (a) {
      var b = document.createElement("button");
      b.className = "launcher-item";
      b.innerHTML = '<span class="glyph">' + esc(a.glyph) + '</span><span>' + esc(a.name) + "</span>";
      b.addEventListener("click", function () { toast(a.name + " wird geöffnet … (Prototyp)"); });
      grid.appendChild(b);
    });
  }

  function renderLists() {
    document.getElementById("tool-list").innerHTML =
      DEVTOOLS.map(function (t) { return "<li><span>" + esc(t) + '</span><span class="badge">geplant</span></li>'; }).join("");
    document.getElementById("gaming-list").innerHTML =
      GAMING.map(function (t) { return "<li><span>" + esc(t) + '</span><span class="badge">geplant</span></li>'; }).join("");
  }

  function applyLang(lang) {
    var dict = I18N[lang] || I18N.de;
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      var k = el.getAttribute("data-i18n");
      if (dict[k]) el.textContent = dict[k];
    });
    document.getElementById("launcher-search").placeholder = dict.search;
    document.getElementById("btn-lang").textContent = lang.toUpperCase();
    return dict;
  }

  function tickClock() {
    var c = document.getElementById("clock");
    function tick() {
      var d = new Date();
      c.textContent = ("0" + d.getHours()).slice(-2) + ":" + ("0" + d.getMinutes()).slice(-2);
    }
    tick();
    setInterval(tick, 15000);
  }

  function init() {
    var lang = detectLang();
    var user = detectUser();
    var dict = applyLang(lang);
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    document.getElementById("welcome-user").textContent = user;
    document.getElementById("welcome-text").firstChild.textContent =
      dict.welcome.replace("{user},", "").replace("{user}", "").trim() + " ";
    // welcome text: "Willkommen zurück, {user}!" – setze korrekt
    document.getElementById("welcome-text").innerHTML =
      esc(dict.welcome.split("{user}")[0]) + "<span id='welcome-user'>" + esc(user) + "</span>" + esc(dict.welcome.split("{user}")[1] || "");

    document.getElementById("btn-user").textContent = (user[0] || "U").toUpperCase();
    renderLauncher("");
    renderLists();
    tickClock();

    document.getElementById("launcher-search").addEventListener("input", function (e) { renderLauncher(e.target.value); });
    document.getElementById("btn-lang").addEventListener("click", function () {
      lang = lang === "de" ? "en" : "de";
      dict = applyLang(lang);
      document.getElementById("welcome-text").innerHTML =
        esc(dict.welcome.split("{user}")[0]) + "<span id='welcome-user'>" + esc(user) + "</span>" + esc(dict.welcome.split("{user}")[1] || "");
      toast(lang === "de" ? "Sprache: Deutsch" : "Language: English");
    });
    ["q-wifi", "q-audio", "q-bright", "q-vpn"].forEach(function (id) {
      document.getElementById(id).addEventListener("click", function (e) {
        e.currentTarget.classList.toggle("active");
      });
    });
    document.getElementById("btn-power").addEventListener("click", function () {
      toast(lang === "de" ? "Energieoptionen (Prototyp)" : "Power options (prototype)");
    });

    // Welcome-Sequenz: kein Blockieren, kein langes Warten; reduced-motion → sofort Desktop
    var overlay = document.getElementById("welcome-overlay");
    var desktop = document.getElementById("desktop");
    function reveal() {
      overlay.classList.add("hidden");
      desktop.classList.remove("desktop-hidden");
    }
    if (reduced) { reveal(); }
    else { setTimeout(reveal, 1800); }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
