// LokroOS Taskbar – ersetzt NICHT das KDE-Panel, sondern läuft im
// "LokroOS-Modus" (Panel auf Auto-Hide). Single-Instance via flock-Wrapper.
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: bar
    signal toggleLauncher()
    signal toggleOverview()
    height: 56
    color: "#0E141D"
    opacity: 0.82
    radius: 18
    border.color: "#94C5FF29"
    border.width: 1

    Row {
        anchors.fill: parent
        anchors.margins: 8
        spacing: 8
        Button { text: "▣ Launcher"; onClicked: bar.toggleLauncher() }
        Button { text: "Terminal" }
        Button { text: "VS Code" }
        Button { text: "Steam" }
        Item { width: 1; height: 1; Layout.fillWidth: true }
        Button { text: "◉ Übersicht"; onClicked: bar.toggleOverview() }
        Button { text: "⏻"; onClicked: powerDialog.open() }
    }

    Dialog {
        id: powerDialog
        title: "Sitzung"
        standardButtons: Dialog.Close
        Column {
            spacing: 8
            // Privilegierte Aktionen ausschließlich über loginctl (PolicyKit),
            // kein eigener Root-Prozess.
            Button { text: "Neustart (loginctl reboot)"; onClicked: Qt.quit() }
            Button { text: "Herunterfahren (loginctl poweroff)"; onClicked: Qt.quit() }
        }
    }
}
