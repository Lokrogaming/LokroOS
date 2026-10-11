// LokroOS Shell – Root-Komponente (Plasma/Wayland, Qt 6 / QtQuick).
// Architektur: Plasma-Panel bleibt zuständig für Fenster-Management;
// LokroOS-Shell läuft als EIN planteskript-/applet-Prozess (Single-Instance).
// Anti-Doppelstart: LockFile in $XDG_RUNTIME_DIR (siehe Main.qml guard unten sinngemäß,
// echte Sperre übernimmt der Wrapper lokroos-shell.sh via flock).
// Status: PARTIAL – Struktur + Verträge stehen, Wayland-Sitzungstest UNVERIFIED.
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

Item {
    id: shell
    anchors.fill: parent

    // Design-Tokens (1:1 aus branding/tokens.json)
    readonly property color cBlack: "#06090F"
    readonly property color cRaised: "#151D29"
    readonly property color cCyan: "#22D3EE"
    readonly property color cText: "#F1F5F9"
    readonly property color cMuted: "#94A3B8"
    readonly property int motionBase: 220

    // Phasen: boot → login (SDDM) → welcome (Overlay) → desktop
    property string phase: "desktop"
    property bool reduceMotion: false

    // Komponenten-Verträge:
    // - Taskbar: pinned Apps + Power (Neustart/Herunterfahren via loginctl, kein Root-Daemon)
    // - Launcher: Rastersuche über .desktop-Dateien (KRunner-kompatibel)
    // - SystemOverview: Glass-Cards (Netzwerk/Audio/Helligkeit/VPN/Uhrzeit/Updates)
    Taskbar { id: taskbar; anchors.bottom: parent.bottom }
    Launcher { id: launcher; visible: false }
    SystemOverview { id: overview; visible: false }
    Connections {
        target: taskbar
        function onToggleLauncher() { launcher.visible = !launcher.visible }
        function onToggleOverview() { overview.visible = !overview.visible }
    }
}
