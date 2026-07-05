# Handbook voor de radio-operator — ADN DMR Server

> **Voor wie dit document is:** voor iedereen die een radio gebruikt om te
> praten en te luisteren. U hoeft niets te weten over servers, netwerken of
> programmeren. Als u de radio kunt aanzetten en op PTT kunt drukken, is deze
> handleiding voor u.

---

## Wat is ADN?

ADN is een **radiocommunicatienetwerk** dat uw hotspot (of repeater) via
internet verbindt met andere radioamateurs over de hele wereld.

U praat in uw radio → uw hotspot stuurt uw stem via internet → anderen horen
het op hun radio's. En omgekeerd.

<div class="manual-flow">
  <div class="manual-flow-node">Uw radio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Uw hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">ADN-server</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Andere hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Hun radio's</div>
</div>

De kanalen waarop we praten heten **Talk Groups** (gespreksgroepen) of **TG**.
Elke TG is als een "ruimte" of "kanaal" waar mensen samenkomen om over een
onderwerp te praten.

---

## Basisbegrippen (het minimum dat u moet weten)

### Talk Group (TG)

Een nummer dat een kanaal identificeert. Voorbeelden:
- **TG 730** — algemene ruimte voor Chili.
- **TG 714** — algemene ruimte voor Panama.
- **TG 4000** — speciaal nummer om "op te hangen" (zie hieronder).

### Timeslot (slot)

DMR deelt elke frequentie in **twee tijdkanalen**: **slot 1** en **slot 2**. Het
is als twee rijstroken op een snelweg: twee gesprekken kunnen tegelijk lopen
zonder elkaar te storen. Uw hotspot en de server coördineren dit voor u.

Als gebruiker hoeft u bijna nooit aan het slot te denken: uw hotspot is zo
geconfigureerd dat deze automatisch het juiste slot gebruikt.

### PTT (Push To Talk)

De knop op uw radio. Drukken om te praten, loslaten om te luisteren.

---

## Wat u kunt doen

### Praten in een Talk Group

1. **Selecteer de TG** op uw radio (net als van kanaal wisselen).
2. **Druk op PTT** en praat.
3. **Laat PTT los** om de antwoorden te horen.

Dat is alles. De server doet de rest.

### Een nieuwe Talk Group activeren (dynamisch)

Als u een TG wilt horen die **niet op uw hotspot is geconfigureerd**, **zend
dan gewoon uit op die TG**. Voorbeeld: u hebt TG 730507 nooit gebruikt, maar u
wilt hem horen:

1. Programmeer TG 730507 in uw radio.
2. Druk een seconde op PTT (alleen om de server te "waarschuwen").
3. Vanaf dat moment **luistert uw hotspot naar die TG** totdat u deze
   deactiveert (4000 intoetsen) of de tijd verloopt.

> **Belangrijk:** op deze server **volstaat één enkele uitzending** om te
> activeren en te luisteren. U hoeft niet twee keer uit te zenden.

### Een Talk Group deactiveren (ophangen)

Als u een geactiveerde TG niet meer wilt horen, **toets TG 4000 in** en druk op
PTT. Het is als "de telefoon ophangen":

1. Selecteer **TG 4000** op uw radio.
2. Druk een seconde op PTT.
3. De dynamische TG wordt gewist. U hoort hem niet meer.

> TG 4000 **wist alleen de TG's die u hebt geactiveerd**. Het heeft geen invloed
> op statische TG's (degene die u hebt geconfigureerd in de OPTIONS-regel, in
> het zelf-service paneel of op de server).

### Uw eigen stem horen (echo)

Wilt u testen of uw audio goed bij de server aankomt? **Toets TG 9990 in** en
druk op PTT. De server speelt uw opgenomen stem terug zodat u de kwaliteit kunt
controleren.

> De echo keert **alleen terug naar uw hotspot**, zelfs als u er meerdere hebt
> geregistreerd met dezelfde DMR-ID.

### Informatieberichten beluisteren

Met **9991 tot 9999** kunt u vooraf opgenomen clips beluisteren met
dienst informatie (afhankelijk van welke clips de beheerder heeft
geconfigureerd).

---

## Regels die de server voor u toepast (u hoeft niets te doen)

De server heeft automatische regels zodat gesprekken elkaar niet overlappen. U
praat gewoon; de server zorgt dat alles werkt.

### Eén gesprek per TG tegelijk

Als iemand op TG 730 praat, **kan niemand anders onderbreken** op dezelfde TG.
Als u op 730 op PTT drukt terwijl iemand anders praat, negeert de server u (hij
verstoort de spreker niet) maar laat u horen wat ze zeggen.

### Geen onderbreking als iemand laat binnenkomt

Als u aan het praten bent en een andere radioamateur **halverwege verbindt**,
levert de server uw audio vanaf dat moment aan hem. Hij hoeft niet te wachten
tot u klaar bent om u te horen.

### Wachttijd tussen TG's (hangtime)

Als een gesprek op een slot eindigt, is er een pauze van ongeveer **5
seconden** voordat dat slot een andere TG accepteert. Dit voorkomt dat twee
gesprekken kruisen. Het is automatisch; u merkt het niet.

### U kunt niet tegelijk praten en luisteren op hetzelfde slot

Als u uitzendt op slot 2, kunt u geen andere oproep ontvangen op slot 2 tot u
PTT loslaat. Dat is normaal: uw radio kan ook niet beide tegelijk op hetzelfde
slot.

Maar **u kunt op slot 1 praten en op slot 2 luisteren** tegelijk (als uw radio
full-duplex is).

---

## Uw hotspot configureren

Uw hotspot (Pi-Star, MMDVM, enz.) wordt geconfigureerd met een regel genaamd
**OPTIONS** die aangeeft welke TG's u wilt horen. U hoeft deze niet met de hand
te bewerken: het **webpaneel** (self-service) laat u uw TG's in de browser
wijzigen.

### De OPTIONS-regel en uw wachtwoord

Uw hotspot stuurt na het verbinden een regel genaamd **OPTIONS** naar de
server. De server wacht 10 seconden op die regel; wat u stuurt (of niet stuurt)
bepaalt **wie uw TG's bestuurt**:

| Uw hotspot stuurt | Wie beslist over uw TG's | Wat er gebeurt |
|---|---|---|
| `OPTIONS=PASS=uw_sleutel;` | **Self-service** (webpaneel) | De server controleert uw wachtwoord en leest dan uw TG's uit de database. **U kunt inloggen op het dashboard met wachtwoord en via IP.** |
| `OPTIONS=` leeg | **Self-service** (webpaneel) | De server leest uw TG's uit de database. U kunt alleen **automatisch inloggen via IP** op het dashboard (zonder wachtwoord). |
| Geen OPTIONS (10 s verstrijken) | **Self-service** (webpaneel) | De server gaat ervan uit dat uw hotspot geen eigen OPTIONS heeft en gebruikt de database. Hetzelfde als het lege geval. |
| `OPTIONS=TS2=730;` (met TG's, SINGLE, enz.) | **Uw hotspot** | De server haalt de TG's rechtstreeks uit de regel. **Negeert het webpaneel.** U kunt alleen **automatisch inloggen via IP** op het dashboard (zonder wachtwoord). |

> **Belangrijk:** als uw hotspot **geen** `PASS=` stuurt, **kunt u niet
> inloggen op het dashboard met wachtwoord**. U kunt alleen automatisch inloggen
> via IP (als uw IP overeenkomt). Om in te loggen met wachtwoord moet uw
> hotspot `OPTIONS=PASS=uw_sleutel;` in zijn configuratie sturen (Pi-Star /
> WPSD: veld `optsfile`). Het wachtwoord moet overeenkomen met wat u in het
> paneel hebt geregistreerd.

**Pi-Star — waar u uw wachtwoord (PASS) invult:**

<img src="/img/pi-star_pass.png" alt="Pi-Star: veld Password in DMR Network" class="manual-img" />

**WPSD — waar u uw wachtwoord (PASS) invult:**

<img src="/img/wpsd_pass.png" alt="WPSD: veld Password in DMR Gateway" class="manual-img" />

### Statische TG's (altijd aan)

De TG's die u in uw configuratie of paneel instelt, blijven **altijd
luisteren**, zonder dat u iets hoeft te doen. Voorbeeld: als u `TS2=730`
configureert, luistert uw hotspot permanent naar 730 tot u het verwijdert.

**Pi-Star — waar u de OPTIONS-regel handmatig invult:**

<img src="/img/pi-star_options.png" alt="Pi-Star: veld Options in DMR Network" class="manual-img" />

**WPSD — waar u de OPTIONS-regel handmatig invult:**

<img src="/img/wpsd_options.png" alt="WPSD: veld Options in DMR Gateway" class="manual-img" />

### Dynamische TG's (u activeert ze)

De TG's die u met PTT activeert (zonder ze geconfigureerd te hebben) zijn
**dynamisch**: ze duren een bepaalde tijd (door de beheerder ingesteld,
meestal ~10 minuten) en wissen dan zichzelf, of worden gewist als u 4000
intoetst.

### SINGLE-modus (exclusief luisteren)

Sommige hotspots hebben **SINGLE=1**, wat betekent: **maar één dynamische TG
tegelijk per slot**. Als u een nieuwe TG activeert, vervangt deze de vorige.

Andere hebben **SINGLE=0**, waardoor meerdere dynamische TG's kunnen
ophopen. Uw beheerder bepaalt welke wordt gebruikt.

---

## Veelvoorkomende problemen en wat te doen

| Probleem | Waarschijnlijke oorzaak | Wat te doen |
|---|---|---|
| **Ik hoor niets** | Uw TG is niet actief, of het slot is bezet met een andere TG | Zend uit op die TG om deze te activeren; of wacht tot het andere QSO voorbij is |
| **Mijn stem komt niet door** | De TG is bezet door iemand anders | Wacht tot het gesprek voorbij is en probeer opnieuw |
| **Audio valt weg aan het begin** | Het slot zat in wachttijd (hangtime) | Dat is normaal; wacht 5 seconden en herhaal |
| **Ik activeer een TG maar hoor hem niet** | Niemand zendt op dit moment uit op die TG | De TG is geactiveerd maar stil; als iemand praat, hoort u het |
| **Mijn dynamische TG is verdwenen** | De tijd is verlopen of iemand heeft 4000 intoetst | Zend opnieuw op die TG om hem te reactiveren |
| **Ik kan niet praten, word genegeerd** | Iemand anders gebruikt de TG op dit moment | Wacht op uw beurt (luister eerst) |

---

## De speciale nummers (samenvatting)

| Nummer | Wat het doet |
|---|---|
| **4000** | "Ophangen": wist de dynamische TG's die u hebt geactiveerd. |
| **9990** | Echo: speelt uw stem terug om audio te testen. |
| **9991-9999** | Vooraf opgenomen informatieberichten. |
| **Elke andere TG** | Normaal gesprekskanaal. |

---

## Goede operatorpraktijken

1. **Luister voordat u praat.** Voordat u op PTT drukt, wacht u een seconde om
   te zien of iemand anders aan het praten is. De regel "één gesprek per TG"
   voorkomt dat u onderbreekt, maar het is goede manieren om eerst te
   luisteren.

2. **Identificeer uzelf.** Zeg uw roepteken aan het begin en aan het einde. Dat
   is verplicht en helpt anderen te weten wie praat.

3. **Pauzes tussen beurten.** Laat 2-3 seconden tussen uw bericht en dat van de
   ander. Dit geeft anderen tijd om deel te nemen aan het gesprek en voorkomt
   onderbrekingen.

4. **Druk niet te snel op PTT.** Als u loslaat en binnen een seconde weer
   indrukt, kan de server de wissel mogelijk niet goed verwerken. Een korte
   pauze is gezond.

5. **Als u een dynamische TG activeert, toets 4000 in als u klaar bent.** Zo
   vrijemt u resources en voorkomt u dat u verkeer hoort dat u niet meer
   interesseert.

---

## Samenvatting in één zin

> **Selecteer de TG, druk op PTT om te praten, laat los om te luisteren, en
> toets 4000 in als u wilt "ophangen". De server doet al het andere.**
