# Handbuch für Funkbetreiber — ADN DMR Server

> **Für wen dieses Dokument ist:** für alle, die ein Funkgerät zum Sprechen und
> Hören nutzen. Sie müssen nichts über Server, Netzwerke oder Programmierung
> wissen. Wenn Sie das Funkgerät einschalten und die PTT-Taste drücken können,
> ist dieses Handbuch für Sie.

---

## Was ist ADN?

ADN ist ein **Funkkommunikationsnetz**, das Ihren Hotspot (oder Repeater) über
das Internet mit anderen Funkamateuren weltweit verbindet.

Sie sprechen in Ihr Funkgerät → Ihr Hotspot sendet Ihre Stimme über das
Internet → andere hören sie auf ihren Geräten. Und umgekehrt.

<div class="manual-flow">
  <div class="manual-flow-node">Ihr Funkgerät</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Ihr Hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">ADN-Server</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Andere Hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Ihre Funkgeräte</div>
</div>

Die Kanäle, über die wir sprechen, heißen **Talk Groups** (Gesprächsgruppen)
oder **TG**. Jede TG ist wie ein „Raum" oder „Kanal", in dem sich Leute
versammeln, um über ein Thema zu sprechen.

---

## Grundlagen (das Minimum, das Sie wissen müssen)

### Talk Group (TG)

Eine Nummer, die einen Kanal bezeichnet. Beispiele:
- **TG 730** — genereller Raum für Chile.
- **TG 714** — genereller Raum für Panama.
- **TG 4000** — spezielle Nummer zum „Auflegen" (siehe unten).

### Timeslot (Slot)

DMR teilt jede Frequenz in **zwei Zeitkanäle**: **Slot 1** und **Slot 2**. Das
ist wie zwei Spuren auf einer Autobahn: zwei Gespräche können gleichzeitig
laufen, ohne sich zu stören. Ihr Hotspot und der Server koordinieren das für
Sie.

Als Benutzer müssen Sie sich fast nie um den Slot kümmern: Ihr Hotspot ist so
konfiguriert, dass er den richtigen Slot automatisch verwendet.

### PTT (Push To Talk)

Die Taste an Ihrem Funkgerät. Drücken zum Sprechen, loslassen zum Hören.

---

## Was Sie tun können

### In einer Talk Group sprechen

1. **Wählen Sie den TG** an Ihrem Funkgerät (wie einen Kanalwechsel).
2. **Drücken Sie PTT** und sprechen Sie.
3. **Lassen Sie PTT los**, um die Antworten zu hören.

Das ist alles. Den Rest erledigt der Server.

### Einen neuen Talk Group aktivieren (dynamisch)

Wenn Sie einen TG hören möchten, der **nicht auf Ihrem Hotspot konfiguriert**
ist, **senden Sie einfach auf diesem TG**. Beispiel: Sie haben TG 730507 noch
nie benutzt, möchten ihn aber hören:

1. Programmieren Sie TG 730507 in Ihr Funkgerät.
2. Drücken Sie PTT für eine Sekunde (nur um den Server zu „benachrichtigen").
3. Von diesem Moment an **hört Ihr Hotspot diesen TG**, bis Sie ihn
   deaktivieren (4000 eingeben) oder die Zeit abläuft.

> **Wichtig:** Auf diesem Server **genügt eine einzige Übertragung** zum
> Aktivieren und Hören. Sie müssen nicht zweimal senden.

### Einen Talk Group deaktivieren (auflegen)

Wenn Sie einen aktivierten TG nicht mehr hören möchten, **wählen Sie TG 4000**
und drücken Sie PTT. Das ist wie „Auflegen beim Telefon":

1. Wählen Sie **TG 4000** an Ihrem Funkgerät.
2. Drücken Sie PTT für eine Sekunde.
3. Der dynamische TG wird gelöscht. Sie hören ihn nicht mehr.

> TG 4000 **löscht nur die TGs, die Sie aktiviert haben**. Es betrifft nicht die
> statischen TGs (diejenigen, die Sie in der OPTIONS-Zeile, im
> Selbstbedienungs-Panel oder auf dem Server konfiguriert haben).

### Ihre eigene Stimme hören (Echo)

Möchten Sie testen, ob Ihr Audio den Server gut erreicht? **Wählen Sie
TG 9990** und drücken Sie PTT. Der Server spielt Ihre aufgezeichnete Stimme
zurück, damit Sie die Qualität prüfen können.

> Das Echo kehrt **nur zu Ihrem Hotspot** zurück, auch wenn Sie mehrere mit
> derselben DMR-ID registriert haben.

### Informationsmeldungen hören

Mit **9991 bis 9999** können Sie voraufgezeichnete Clips mit
Dienstinformationen hören (abhängig davon, welche Clips der Administrator
konfiguriert hat).

---

## Regeln, die der Server für Sie anwendet (Sie müssen nichts tun)

Der Server hat automatische Regeln, damit sich Gespräche nicht überschneiden.
Sie sprechen einfach; der Server sorgt dafür, dass alles funktioniert.

### Ein Gespräch pro TG gleichzeitig

Wenn jemand auf TG 730 spricht, **kann niemand sonst auf demselben TG
unterbrechen**. Wenn Sie bei 730 PTT drücken, während ein anderer spricht,
ignoriert der Server Sie (er stört den Sprecher nicht), lässt Sie aber hören,
was gesagt wird.

### Kein Abbruch bei spätem Einstieg

Wenn Sie sprechen und ein anderer Funkamateur **sich中途 verbindet**, liefert
der Server ihm Ihr Audio ab diesem Zeitpunkt. Er muss nicht warten, bis Sie
fertig sind, um Sie zu hören.

### Wartezeit zwischen TGs (Hangtime)

Wenn ein Gespräch auf einem Slot endet, gibt es eine **5-Sekunden**-Pause, bevor
dieser Slot einen anderen TG annimmt. Das verhindert, dass sich zwei Gespräche
kreuzen. Das passiert automatisch; Sie bemerken es nicht.

### Sie können nicht gleichzeitig sprechen und hören auf demselben Slot

Wenn Sie auf Slot 2 senden, können Sie auf Slot 2 keinen weiteren Anruf
empfangen, bis Sie PTT loslassen. Das ist normal: Auch Ihr Funkgerät kann nicht
beides gleichzeitig auf demselben Slot.

Aber **Sie können auf Slot 1 sprechen und auf Slot 2 hören** gleichzeitig (wenn
Ihr Funkgerät Vollduplex ist).

---

## Ihren Hotspot konfigurieren

Ihr Hotspot (Pi-Star, MMDVM usw.) wird mit einer Zeile namens **OPTIONS**
konfiguriert, die angibt, welche TGs Sie hören möchten. Sie müssen sie nicht
per Hand bearbeiten: das **Web-Panel** (Selbstbedienung) lässt Sie Ihre TGs im
Browser ändern.

### Die OPTIONS-Zeile und Ihr Passwort

Ihr Hotspot sendet nach der Verbindung eine Zeile namens **OPTIONS** an den
Server. Der Server wartet 10 Sekunden auf diese Zeile; was Sie senden (oder
nicht senden), entscheidet, **wer Ihre TGs steuert**:

| Ihr Hotspot sendet | Wer entscheidet | Was passiert |
|---|---|---|
| `OPTIONS=PASS=ihr_schlüssel;` | **Selbstbedienung** (Web-Panel) | Der Server prüft Ihr Passwort und liest dann Ihre TGs aus der Datenbank. **Sie können sich mit Passwort und per IP im Dashboard anmelden.** |
| `OPTIONS=` leer | **Selbstbedienung** (Web-Panel) | Der Server liest Ihre TGs aus der Datenbank. Sie können nur **Auto-Login per IP** im Dashboard nutzen (ohne Passwort). |
| Keine OPTIONS (10 s vergehen) | **Selbstbedienung** (Web-Panel) | Der Server nimmt an, dass Ihr Hotspot keine eigenen OPTIONS hat und nutzt die Datenbank. Wie beim leeren Fall. |
| `OPTIONS=TS2=730;` (mit TGs, SINGLE usw.) | **Ihr Hotspot** | Der Server nimmt die TGs direkt aus der Zeile. **Ignoriert das Web-Panel.** Sie können nur **Auto-Login per IP** im Dashboard nutzen (ohne Passwort). |

> **Wichtig:** Wenn Ihr Hotspot **kein** `PASS=` sendet, **können Sie sich nicht
> mit Passwort im Dashboard anmelden**. Sie können nur Auto-Login per IP nutzen
> (wenn Ihre IP übereinstimmt). Zur Anmeldung mit Passwort muss Ihr Hotspot
> `OPTIONS=PASS=ihr_schlüssel;` in seiner Konfiguration senden (Pi-Star / WPSD:
> Feld `optsfile`). Das Passwort muss mit dem im Panel registrierten
> übereinstimmen.

**Pi-Star — wo Sie Ihr Passwort (PASS) eintragen:**

<img src="/img/pi-star_pass.png" alt="Pi-Star: Feld Password in DMR Network" class="manual-img" />

**WPSD — wo Sie Ihr Passwort (PASS) eintragen:**

<img src="/img/wpsd_pass.png" alt="WPSD: Feld Password in DMR Gateway" class="manual-img" />

### Statische TGs (immer aktiv)

Die TGs, die Sie in Ihrer Konfiguration oder im Panel einstellen, bleiben
**immer empfangsbereit**, ohne dass Sie etwas tun müssen. Beispiel: Wenn Sie
`TS2=730` konfigurieren, hört Ihr Hotspot 730 dauerhaft, bis Sie es entfernen.

**Pi-Star — wo Sie die OPTIONS-Zeile manuell eintragen:**

<img src="/img/pi-star_options.png" alt="Pi-Star: Feld Options in DMR Network" class="manual-img" />

**WPSD — wo Sie die OPTIONS-Zeile manuell eintragen:**

<img src="/img/wpsd_options.png" alt="WPSD: Feld Options in DMR Gateway" class="manual-img" />

### Dynamische TGs (Sie aktivieren sie)

Die TGs, die Sie mit PTT aktivieren (ohne sie konfiguriert zu haben), sind
**dynamisch**: Sie halten eine bestimmte Zeit (vom Administrator eingestellt,
meist ~10 Minuten) und löschen sich dann selbst, oder werden gelöscht, wenn Sie
4000 eingeben.

### SINGLE-Modus (exklusives Hören)

Einige Hotspots haben **SINGLE=1**, was bedeutet: **nur ein dynamischer TG pro
Slot**. Wenn Sie einen neuen TG aktivieren, ersetzt er den vorherigen.

Andere haben **SINGLE=0**, wodurch mehrere dynamische TGs gesammelt werden.
Ihr Administrator entscheidet, was verwendet wird.

---

## Häufige Probleme und was zu tun ist

| Problem | Wahrscheinliche Ursache | Was zu tun ist |
|---|---|---|
| **Ich höre nichts** | Ihr TG ist nicht aktiv oder der Slot ist mit einem anderen TG belegt | Senden Sie auf diesem TG, um ihn zu aktivieren; oder warten Sie, bis das andere QSO endet |
| **Meine Stimme kommt nicht durch** | Der TG ist von jemand anderem belegt | Warten Sie, bis das Gespräch endet, und versuchen Sie es erneut |
| **Audio schneidet am Anfang ab** | Der Slot war in der Hangtime | Das ist normal; warten Sie 5 Sekunden und wiederholen Sie |
| **Ich aktiviere einen TG, höre ihn aber nicht** | Niemand sendet gerade auf diesem TG | Der TG ist aktiviert, aber still; wenn jemand spricht, hören Sie es |
| **Mein dynamischer TG ist verschwunden** | Die Zeit ist abgelaufen oder jemand hat 4000 eingegeben | Senden Sie erneut auf diesem TG, um ihn zu reaktivieren |
| **Ich kann nicht sprechen, werde ignoriert** | Jemand anderes nutzt den TG gerade | Warten Sie auf Ihren Zug (zuerst hören) |

---

## Die speziellen Nummern (Zusammenfassung)

| Nummer | Was sie tut |
|---|---|
| **4000** | „Auflegen": löscht die von Ihnen aktivierten dynamischen TGs. |
| **9990** | Echo: spielt Ihre Stimme zurück zum Audiotest. |
| **9991-9999** | Voraufgezeichnete Informationsmeldungen. |
| **Jeder andere TG** | Normaler Gesprächskanal. |

---

## Gute Betriebspraktiken

1. **Zuerst hören, dann sprechen.** Bevor Sie PTT drücken, warten Sie eine
   Sekunde, um zu sehen, ob jemand anderes spricht. Die Regel „ein Gespräch pro
   TG" verhindert Unterbrechungen, aber es ist guter Ton, zuerst zu hören.

2. **Identifizieren Sie sich.** Sagen Sie Ihr Rufzeichen zu Beginn und am Ende.
   Das ist Vorschrift und hilft anderen zu wissen, wer spricht.

3. **Pausen zwischen den Beiträgen.** Lassen Sie 2-3 Sekunden zwischen Ihrer
   Nachricht und der des anderen. Das gibt anderen Zeit, sich dem Gespräch
   anzuschließen, und vermeidet Abbrüche.

4. **Drücken Sie PTT nicht zu schnell.** Wenn Sie loslassen und in weniger als
   einer Sekunde wieder drücken, kann der Server den Wechsel eventuell nicht
   richtig verarbeiten. Eine kurze Pause ist gesund.

5. **Wenn Sie einen dynamischen TG aktivieren, geben Sie 4000 ein, wenn Sie
   fertig sind.** So geben Sie Ressourcen frei und vermeiden, Verkehr zu hören,
   der Sie nicht mehr interessiert.

---

## Zusammenfassung in einem Satz

> **Wählen Sie den TG, drücken Sie PTT zum Sprechen, lassen Sie los zum Hören,
> und geben Sie 4000 ein, wenn Sie „auflegen" wollen. Der Server erledigt alles
> andere.**
