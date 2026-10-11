// LokroOS Dashboard (QML) – Home-Fenster der Plasma-Shell.
// Daten: lokroos-stats.py --once (JSON) via executable-Datenquelle, 2-s-Polling.
// Tabs (Übersicht/Prozesse/Netzwerk) schließbar + wiederherstellbar,
// Fenster minimierbar/schließbar (Signale an Main.qml). Reduzierte Bewegung →
// Animationen aus. Status: PARTIAL (Struktur steht, Sitzungstest UNVERIFIED).
import QtQuick 2.15
import QtQuick.Controls 2.15
import org.kde.plasma.core 2.0 as PlasmaCore

Rectangle {
    id: dash
    signal minimized()
    signal closed()

    property bool reduceMotion: false
    property real cpuLoad: 0
    property real ramLoad: 0
    property real gpuLoad: 0
    property string netDown: "–"
    property string netUp: "–"
    property bool backendOk: false
    property var closedTabs: ({})

    color: "#0E141D"; opacity: 0.92; radius: 22
    border.color: "#94C5FF29"; border.width: 1

    // --- Backend-Polling (nur lesend, nie Root, nie Secrets) ---
    PlasmaCore.DataSource {
        id: statsSource
        engine: "executable"
        connectedSources: ["lokroos-stats.py --once"]
        interval: 2000
        onNewData: {
            try {
                var payload = JSON.parse(data["stdout"] || "{}");
                dash.backendOk = !!payload.supported;
                if (dash.backendOk) {
                    dash.cpuLoad = payload.cpu.load_pct || 0;
                    dash.ramLoad = payload.mem.used_pct || 0;
                    dash.gpuLoad = payload.gpu.present ? payload.gpu.load_pct : 0;
                    dash.netDown = (payload.net.rx_kbps || 0) + " KB/s";
                    dash.netUp = (payload.net.tx_kbps || 0) + " KB/s";
                    procModel.clear();
                    (payload.tasks.top || []).forEach(function (t) {
                        procModel.append({name: t.name, detail: t.mem_kb + " kB"});
                    });
                }
            } catch (e) { dash.backendOk = false; }
        }
    }

    Column {
        anchors.fill: parent; anchors.margins: 16; spacing: 10

        // Titelzeile: minimieren / schließen
        Row {
            width: parent.width; spacing: 8
            Text { text: "◉ Dashboard"; color: "#F1F5F9"; font.bold: true }
            Item { width: 1; height: 1 }
            Button { text: "–"; onClicked: dash.minimized() }
            Button { text: "×"; onClicked: dash.closed() }
        }

        // Tab-Leiste (Tabs einzeln schließbar)
        TabBar {
            id: tabBar; width: parent.width
            Repeater {
                model: ["Übersicht", "Prozesse", "Netzwerk"]
                TabButton {
                    text: modelData + "  ×"
                    visible: !dash.closedTabs[modelData]
                    onClicked: swipe.currentIndex = index
                }
            }
        }

        SwipeView {
            id: swipe; width: parent.width; height: 300
            // Übersicht
            Grid {
                columns: 2; spacing: 12
                Repeater {
                    model: [
                        {label: "CPU", v: dash.cpuLoad},
                        {label: "RAM", v: dash.ramLoad},
                        {label: "GPU", v: dash.gpuLoad}
                    ]
                    Column {
                        spacing: 4
                        Text { text: modelData.label + ": " + Math.round(modelData.v) + " %"; color: "#F1F5F9" }
                        ProgressBar {
                            from: 0; to: 100; width: 220
                            value: modelData.v
                            Behavior on value { enabled: !dash.reduceMotion
                                NumberAnimation { duration: 220 } }
                        }
                    }
                }
                Text { text: "↓ " + dash.netDown + "   ↑ " + dash.netUp; color: "#94A3B8" }
                Text { text: dash.backendOk ? "" : "Stats-Backend nicht erreichbar";
                       color: "#F87171"; visible: !dash.backendOk }
            }
            // Prozesse
            ListView {
                model: ListModel { id: procModel }
                delegate: Row { spacing: 12
                    Text { text: name; color: "#F1F5F9"; width: 220; elide: Text.ElideRight }
                    Text { text: detail; color: "#94A3B8" }
                }
            }
            // Netzwerk
            Column {
                Text { text: "↓ RX: " + dash.netDown; color: "#F1F5F9" }
                Text { text: "↑ TX: " + dash.netUp; color: "#F1F5F9" }
            }
        }

        Button {
            text: "Geschlossene Tabs wiederherstellen"
            onClicked: dash.closedTabs = {}
        }
    }
}
