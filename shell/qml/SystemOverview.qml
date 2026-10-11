// LokroOS SystemOverview – Glass-Cards: Netzwerk, Audio, Helligkeit,
// Uhrzeit, VPN-Status, Updates. Nutzt native Schnittstellen:
// NetworkManager (D-Bus), PulseAudio/PipeWire, powerdevil, PackageKit.
// Keine Passwörter/Secrets – VPN-App wird nur geöffnet, Status nur gelesen.
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    color: "#0E141D"
    opacity: 0.9
    radius: 22
    border.color: "#94C5FF29"
    border.width: 1

    Grid {
        anchors.fill: parent
        anchors.margins: 16
        columns: 2
        spacing: 16
        // Jeweils eine Glass-Card (vereinfachte Darstellung)
        GroupBox { title: "Netzwerk"; Label { text: "Status via NetworkManager" } }
        GroupBox { title: "Audio"; Slider { from: 0; to: 100; value: 60 } }
        GroupBox { title: "Helligkeit"; Slider { from: 5; to: 100; value: 80 } }
        GroupBox { title: "ProtonVPN"; Label { text: "App öffnen / Status lesen (kein Secret-Handling)" } }
        GroupBox { title: "Uhrzeit / Datum"; Label { text: "Plasma-Clock" } }
        GroupBox { title: "Updates"; Label { text: "PackageKit / Discover (kein eigenes Update-System)" } }
    }
}
