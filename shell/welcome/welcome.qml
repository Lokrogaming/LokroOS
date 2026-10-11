// LokroOS Welcome QML – Overlay nach Login (Plasma/Wayland).
// Backend: lokroos-welcome.py liefert {user, lang, message} als JSON.
// Sicherheitsregeln: user-String nur via text: binden (kein HTML),
// kein Blockieren (Modelless), reduced-motion → sofort schließen.
// Status: PARTIAL (QML shellexistiert, echte Sitzungsintegration UNVERIFIED).
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: root
    anchors.fill: parent
    property string welcomeUser: "gast"
    property string welcomeLang: "de"
    property bool reduceMotion: false

    property string welcomeMessage: welcomeLang === "de"
        ? "Willkommen zurück, " + welcomeUser + "!"
        : "Welcome back, " + welcomeUser + "!"

    Rectangle {
        anchors.fill: parent
        color: "#06090F"
        opacity: bgFade.running || bgFade.done ? 0.0 : 0.86
    }

    // Timer statt Blockieren: Overlay schließt sich selbst, Desktop bleibt frei
    Timer {
        id: selfClose
        interval: root.reduceMotion ? 100 : 3000
        running: true
        repeat: false
        onTriggered: root.visible = false
    }

    OpacityAnimator { id: bgFade; target: root; from: 0; to: 1;
        duration: root.reduceMotion ? 0 : 600; running: true
        onFinished: bgFade.done = true
    }
    property bool done: false

    Column {
        anchors.centerIn: parent
        spacing: 24
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            // text: statt textFormat:RichText → kein HTML-Injection via Username
            text: root.welcomeMessage
            color: "#F1F5F9"
            font.pixelSize: 40
            font.bold: true
        }
        BusyIndicator {
            anchors.horizontalCenter: parent.horizontalCenter
            running: !root.reduceMotion && root.visible
        }
    }
}
