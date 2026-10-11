// LokroOS Launcher – Rastersuche über installierte .desktop-Dateien.
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    color: "#0E141D"
    opacity: 0.92
    radius: 22
    border.color: "#94C5FF29"
    border.width: 1

    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        TextField {
            id: search
            placeholderText: "Suchen … / Search …"
            width: parent.width
        }
        Grid {
            columns: 5
            spacing: 10
            Repeater {
                // Platzhalter-Modell; echte Implementierung liest
                // /usr/share/applications/*.desktop (QML FolderListModel)
                model: ["Terminal", "VS Code", "Steam", "Bottles",
                        "ProtonVPN", "Dateien", "Einstellungen",
                        "Systemverwaltung", "Browser", "GitHub CLI"]
                Button { text: modelData; width: 120 }
            }
        }
    }
}
