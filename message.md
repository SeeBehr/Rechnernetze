Hier ist ein einfaches, klar definiertes Protokoll für den server-basierten Peer-to-Peer Group-Chat. Es spezifiziert sowohl die Kommunikation zwischen **Client und Server** als auch die Kommunikation zwischen **Clients**.

---

## **Protokoll für die Kommunikation zwischen Client und Server (TCP)**

### **Nachrichtenformate**
- Alle Nachrichten sind **Textnachrichten**, kodiert in UTF-8.
- Jede Nachricht endet mit einem speziellen Trennzeichen, z. B. **`\n`**, damit Nachrichten im Bytestrom extrahiert werden können.

| **Aktion**         | **Nachrichtenformat**                                         | **Beschreibung**                                                                                                                                                  |
|---------------------|--------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Registrierung**   | `REGISTER <Nickname> <UDP-Port>`                             | Der Client meldet sich mit Nickname und UDP-Port beim Server an.                                                                                                  |                                                                                                                                   |
| **Benutzerliste**   | `USERS <Nickname_1> <IP_1> <UDP-Port_1>; ...`                 | Liste der derzeit angemeldeten Benutzer. Wird nach der Registrierung und bei Updates (neue oder abgemeldete Benutzer) gesendet.                                   |
| **Update: Beitritt**| `JOIN <Nickname> <IP> <UDP-Port>`                            | Benachrichtigung über einen neuen Benutzer.                                                                                                                      |
| **Update: Abgang**  | `LEAVE <Nickname>`                                           | Benachrichtigung über einen abgemeldeten Benutzer.                                                                                                               |
| **Broadcast senden**| `BROADCAST <Nachricht>`                                      | Client sendet eine Nachricht an alle registrierten Benutzer über den Server.                                                                                     |
| **Broadcast empfangen**| `MESSAGE <Nickname> <Nachricht>`                              | Server leitet eine Broadcast-Nachricht an den Client weiter.                                                                                                     |
| **Fehler**          | `ERROR <Fehlerbeschreibung>`                                 | Server meldet Fehler, z. B. bei ungültigem Format oder fehlenden Parametern.                                                                                     |

---

### **Ablauf**
1. **Registrierung:**
   - Client sendet: `REGISTER <Nickname> <UDP-Port>`.
   - Server antwortet:
     - Bei Erfolg: `REGISTERED <Nickname>` gefolgt von `USERS <Liste der Benutzer>`.
     - Bei Fehler (z. B. Nickname bereits vergeben): `ERROR <Fehlerbeschreibung>`.

2. **Updates:**
   - Server sendet `JOIN <Nickname> <IP> <UDP-Port>` bei neuen Clients.
   - Server sendet `LEAVE <Nickname>` bei abgemeldeten Clients.

3. **Broadcast:**
   - Client sendet: `BROADCAST <Nachricht>`.
   - Server verteilt: `MESSAGE <Nickname> <Nachricht>` an alle registrierten Benutzer.

4. **Fehlverhalten:**
   - Bei fehlerhaften Nachrichtenformaten sendet der Server `ERROR <Fehlerbeschreibung>` und ignoriert die Nachricht.

---

## **Protokoll für die Kommunikation zwischen Clients (UDP und TCP)**

### **Nachrichtenformate**
- UDP-Nachrichten sind kleine Textnachrichten ohne garantierte Zustellung. Jede Nachricht endet mit **`\n`**.
- TCP-Nachrichten folgen einem ähnlichen Format wie Servernachrichten, um Konsistenz zu gewährleisten.

| **Aktion**             | **Nachrichtenformat**                          | **Beschreibung**                                                                                      |
|-------------------------|-----------------------------------------------|------------------------------------------------------------------------------------------------------|
| **Verbindungsanfrage**  | `CONNECT <Nickname> <TCP-Port>`               | Initiator sendet seine TCP-Port-Informationen an den Ziel-Client über UDP.                           |
| **Verbindungsbestätigung** | Keine automatische Antwort                   | Ziel-Client baut die TCP-Verbindung auf.                                                             |
| **Chat-Nachricht**      | `MESSAGE <Nachricht>`                         | Chat-Nachrichten, die über die TCP-Verbindung ausgetauscht werden.                                   |
| **Verbindungsende**     | `DISCONNECT`                                  | Einer der Clients beendet die TCP-Verbindung.                                                       |
| **Fehler**              | `ERROR <Fehlerbeschreibung>`                  | Wird bei unerwarteten Nachrichten oder Verbindungsproblemen gesendet.                                |

---

### **Ablauf**
1. **Verbindungsaufbau (UDP):**
   - Initiator sendet: `CONNECT <Nickname> <TCP-Port>` an die UDP-Adresse des Ziel-Clients.
   - Ziel-Client überprüft die Nachricht und baut eine TCP-Verbindung auf.

2. **Chat-Nachrichten (TCP):**
   - Beide Clients senden `MESSAGE <Nachricht>` über die TCP-Verbindung.

3. **Verbindungsende (TCP):**
   - Einer der Clients sendet `DISCONNECT`, um die Verbindung sauber zu beenden.

4. **Fehlverhalten:**
   - Bei falschem Format oder unerwarteten Nachrichten wird `ERROR <Fehlerbeschreibung>` gesendet und die Nachricht ignoriert.

---

## **Spezifikation für den „Bad Path“**

### **Client-Server-Kommunikation**
1. **Falsches Nachrichtenformat:** 
   - Server sendet `ERROR <Fehlerbeschreibung>` und ignoriert die Nachricht.
2. **Ausbleibende Antwort des Servers:** 
   - Client versucht die Nachricht erneut zu senden (bis zu 3 Wiederholungen mit Zeitverzögerung).
3. **Unerwartete Nachrichten:** 
   - Server sendet `ERROR <Fehlerbeschreibung>`.

### **Client-Client-Kommunikation**
1. **UDP-Paketverlust:** 
   - Initiator wiederholt die `CONNECT`-Nachricht bis zu 3 Mal in Intervallen von 1 Sekunde.
2. **TCP-Verbindungsfehler:** 
   - Beide Clients senden `ERROR <Fehlerbeschreibung>` und schließen die Verbindung.
3. **Unerwartete Nachrichten:** 
   - Client ignoriert die Nachricht oder sendet `ERROR <Fehlerbeschreibung>`.

---

Dieses Protokoll ist robust und berücksichtigt sowohl den "Good Path" (erfolgreiche Kommunikation) als auch mögliche Fehlerfälle. Es stellt sicher, dass Nachrichten formatiert, extrahiert und verarbeitet werden können, während sowohl TCP- als auch UDP-Beschränkungen berücksichtigt werden.