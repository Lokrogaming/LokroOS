// LokroOS Calamares-Slideshow (API 2) – Glass-Look, DE/EN via System-Locale.
// Aufruf: Calamares zeigt diese Datei waehrend der Exec-Phase (Installation).
// Sprache: Qt.locale().name ("de_DE" -> DE, sonst EN). Reduzierte Bewegung wird
// respektiert, indem Uebergaenge kurz bleiben (Installer-Kontext, kein Full-Motion).
import QtQuick 2.15

Item {
    id: root
    anchors.fill: parent
    property bool isDE: Qt.locale().name.substring(0, 2) === "de"
    property int idx: 0
    property var slides: isDE ? slidesDE : slidesEN
    property var slidesDE: [
        { t: "Willkommen bei LokroOS", b: "Modernes Linux von LOKRO – dunkel, schnell, wartbar. Die Installation kopiert jetzt das Live-System auf deine Platte." },
        { t: "Bereit für Entwicklung", b: "Node.js + npm, Git, GitHub CLI, VS Code und Build-Werkzeuge sind direkt nach dem ersten Start einsatzbereit." },
        { t: "Bereit für Gaming", b: "Steam + Proton, Wine und Winetricks an Bord. Hinweis: .exe-Dateien werden nie automatisch geöffnet – Rechtsklick, mit Wine ausführen." },
        { t: "VPN optional", b: "ProtonVPN lässt sich nach der Installation mit einem Klick einrichten. Ohne VPN läuft LokroOS vollständig normal." }
    ]
    property var slidesEN: [
        { t: "Welcome to LokroOS", b: "Modern Linux by LOKRO – dark, fast, maintainable. The installer is now copying the live system to your disk." },
        { t: "Ready for development", b: "Node.js + npm, Git, GitHub CLI, VS Code and build tools are ready right after first boot." },
        { t: "Ready for gaming", b: "Steam + Proton, Wine and Winetricks on board. Note: .exe files never auto-launch – right-click, run with Wine." },
        { t: "VPN optional", b: "ProtonVPN can be set up with one click after installation. Without VPN, LokroOS works fully normally." }
    ]

    function onActivate() { advanceTimer.running = true; }
    function onLeave() { advanceTimer.running = false; }

    Timer {
        id: advanceTimer
        interval: 8000
        repeat: true
        running: false
        onTriggered: root.idx = (root.idx + 1) % root.slides.length
    }

    Rectangle {
        anchors.fill: parent
        color: "#06090F"
        // dezenter Cyan-Schimmer oben rechts
        Rectangle {
            width: parent.width * 0.7; height: 220
            anchors.top: parent.top; anchors.right: parent.right
            rotation: -12
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#0E3A52" }
                GradientStop { position: 1.0; color: "#06090F" }
            }
        }
        Column {
            anchors.centerIn: parent
            width: parent.width * 0.8
            spacing: 18
            Image {
                source: "logo.svg"
                width: 88; height: 88
                anchors.horizontalCenter: parent.horizontalCenter
                fillMode: Image.PreserveAspectFit
            }
            Text {
                text: root.slides[root.idx].t
                color: "#F1F5F9"
                font.pixelSize: 30
                font.bold: true
                wrapMode: Text.WordWrap
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
            }
            Text {
                text: root.slides[root.idx].b
                color: "#94A3B8"
                font.pixelSize: 17
                wrapMode: Text.WordWrap
                width: parent.width
                horizontalAlignment: Text.AlignHCenter
            }
            Row {
                anchors.horizontalCenter: parent.horizontalCenter
                spacing: 10
                Repeater {
                    model: root.slides.length
                    Rectangle {
                        width: 10; height: 10; radius: 5
                        color: index === root.idx ? "#22D3EE" : "#334155"
                    }
                }
            }
        }
    }
}
