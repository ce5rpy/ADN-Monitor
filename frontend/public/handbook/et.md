# Raadiooperaatori käsiraamat — ADN DMR Server

> **Kellele see dokument on mõeldud:** kõigile, kes kasutavad raadiot rääkimiseks
> ja kuulamiseks. Teil pole vaja teada midagi serveritest, võrkudest ega
> programmeerimisest. Kui osiate raadio sisse lülitada ja vajutada PTT, on see
> käsiraamat teile.

---

## Mis on ADN?

ADN on **raadiosidevõrk**, mis ühendab teie hotspoti (või
repeatteri) teiste raadioamatööridega kogu maailmas interneti vahendusel.

Te räägite oma raadiosse → teie hotspot saadab teie hääle interneti kaudu →
teised kuulevad seda oma raadiotes. Ja vastupidi.

<div class="manual-flow">
  <div class="manual-flow-node">Teie raadio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Teie hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">ADN Server</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Teised hotspotid</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Nende raadiod</div>
</div>

Kanalid, mille peal me räägime, kannavad nime **Talk Groups** ehk **TG**. Iga TG
on nagu "ruum" või "kanal", kus inimesed kogunevad rääkima mingil teemal.

---

## Põhimõisted (miinimum, mida peate teadma)

### Talk Group (TG)

Number, mis identifitseerib kanali. Näited:
- **TG 730** — Tšiili üldruum.
- **TG 714** — Panama üldruum.
- **TG 4000** — erinumber "toru hüppamiseks" (vt allpool).

### Timeslot (slot)

DMR jagab iga sageduse **kaheks ajakanaliks**: **slot 1** ja **slot 2**. See on
nagu kaks rööbaid maanteel: kaks vestlust saavad kulgeda samal ajal ilma
teineteist segamata. Teie hotspot ja server koordineerivad seda teie eest.

Kasutajana ei pea te sloti peale peaaegu kunagi mõtlema: teie hotspot on
seadistatud kasutama automaatselt õiget sloti.

### PTT (Push To Talk)

Nupp teie raadiol. Vajutage, et rääkida, vabastage, et kuulata.

---

## Mida saate teha

### Rääkida Talk Groupis

1. **Valige TG** oma raadiol (nagu kanali vahetamine).
2. **Vajutage PTT** ja rääkige.
3. **Vabastage PTT**, et kuulata vastuseid.

See on kõik. Ülejäänu teeb server.

### Uue Talk Groupi aktiveerimine (dünaamiline)

Kui soovite kuulata TG-d, mis **pole teie hotspotis seadistatud**, lihtsalt
**saatke edastus sellel TG-l**. Näide: te pole kunagi kasutanud TG 730507, aga
soovite seda kuulata:

1. Programmeerige TG 730507 oma raadiosse.
2. Vajutage PTT ühe sekundi (ainult et "teatada" serverile).
3. Sellest hetkest alates **hakkab teie hotspot seda TG-d kuulama**, kuni te selle
   desaktiveerite (markeerides 4000) või aeg otsa saab.

> **Oluline:** selles serveris **piisab ühest edastusest** aktiveerimiseks ja
> kuulamiseks. Te ei pea kaks korda edastama.

### Talk Groupi desaktiveerimine (toru hüppamine)

Kui te ei soovi enam kuulata TG-d, mille aktiveerisite, **markeerige TG 4000**
ja vajutage PTT. See on nagu "telefoni hüppamine":

1. Valige **TG 4000** oma raadiol.
2. Vajutage PTT ühe sekundi.
3. Dünaamiline TG kustutatakse. Te seda enam ei kuule.

> TG 4000 **kustutab ainult need TG-d, mis teie aktiveerisite**. See ei mõjuta
> staatilisi TG-sid (need, mille seadistasite OPTIONS reas, iseteeninduse
> paneelis või serveris).

### Kuulda omaenda häält (kaja)

Soovite kontrollida, kas teie audio jõuab serverini korralikult? **Markeerige
TG 9990** ja vajutage PTT. Server mängib teie salvestatud hääle tagasi, et
saaksite kvaliteeti kontrollida.

> Kaja naaseb **ainult teie hotspotisse**, isegi kui teil on mitu registreeritud
> sama DMR ID-ga.

### Teabesõnumite kuulamine

Markeerides **9991 kuni 9999** saate kuulata eelsalvestatud klippe
teenindusteabega (olenevalt sellest, millised klipid administraator on
seadistanud).

---

## Reeglid, mida server teie jaoks rakendab (teie ei pea midagi tegema)

Serveris on automaatsed reeglid, et vestlused ei kattuks. Te lihtsalt räägite;
server hoolitseb, et kõik toimiks.

### Üks vestlus korraga ühe TG kohta

Kui keegi räägib TG 730 peal, **keegi teine ei saa katkestada** samal TG-l. Kui
te vajutate PTT-d 730 peal, kui teine räägib, ignoreerib server teid (ta ei
hägile kõnelejat), aga laseb teil kuulata, mida nad ütlevad.

### Ta ei lõika teid katki, kui keegi ühineb hiljem

Kui te räägite ja teine amatöör **ühineb poole pealt**, server edastab teie
audio alates sellest hetkest. Nad ei pea ootama, kuni te lõpetate, enne kui
hakkavad teid kuulma.

### Ooteaeg TG-de vahel (hangtime)

Kui vestlus lõpeb slotil, on seal **5-sekundiline** paus, enne kui see slot
võtab vastu teistsuguse TG. See hoiab ära kahe vestluse ristumise. See on
automaatne; te seda ei märka.

### Te ei saa rääkida ja kuulata samal ajal samal slotil

Kui te edastate slot 2 peal, ei saa te vastu võtta teist kõnet slot 2 peal enne,
kui vabastate PTT. See on normaalne: teie raadio ei suuda samal slotil mõlemat
korraga teha.

Aga **te saate rääkida slot 1 peal ja kuulata slot 2 peal** samal ajal (kui teie
raadio on täisduplex).

---

## Hotspoti seadistamine

Teie hotspot (Pi-Star, MMDVM jne) seadistatakse reaga nimega **OPTIONS**, mis
ütleb, milliseid TG-sid soovite kuulda. Te ei pea seda käsitsi muutma:
**veebipaneel** (iseteenindus) laseb teil muuta oma TG-sid brauserist.

### OPTIONS rida ja teie parool

Teie hotspot saadab pärast ühendumist serverile rea nimega **OPTIONS**. Server
ootab 10 sekundit, et see rida jõuaks kohale; see, mida saadate (või ei
saada), otsustab **kes kontrollib teie TG-sid**:

| Teie hotspot saadab | Kes otsustab teie TG-d | Mis juhtub |
|---|---|---|
| `OPTIONS=PASS=teie_võti;` | **Iseteenindus** (veebipaneel) | Server kontrollib teie parooli ja seejärel loeb teie TG-d andmebaasist. **Saate logida dashboardile parooliga ja IP alusel.** |
| `OPTIONS=` tühi | **Iseteenindus** (veebipaneel) | Server loeb teie TG-d andmebaasist. Saate dashboardil kasutada ainult **IP-põhist automaatset sisselogimist** (paroolita). |
| OPTIONS puudub (10 s möödub) | **Iseteenindus** (veebipaneel) | Server eeldab, et teie hotspotil pole oma OPTIONS rida ja kasutab andmebaasi. Sama mis tühi juht. |
| `OPTIONS=TS2=730;` (koos TG-de, SINGLE jne-ga) | **Teie hotspot** | Server võtab TG-d otse reast. **Ignoreerib veebipaneeli.** Saate dashboardil kasutada ainult **IP-põhist automaatset sisselogimist** (paroolita). |

> **Oluline:** kui teie hotspot **ei** saada `PASS=`, **ei saa te dashboardile
> parooliga sisse logida**. Saate kasutada ainult IP-põhist automaatset
> sisselogimist (kui teie IP kattub). Parooliga sisselogimiseks peab teie
> hotspot saatma oma seadistuses `OPTIONS=PASS=teie_võti;` (Pi-Star / WPSD:
> väli `optsfile`). Parool peab kattuma sellega, mille panis registris.

**Pi-Star — kuhu panna oma parool (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: Password väli DMR Networkis" class="manual-img" />

**WPSD — kuhu panna oma parool (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: Password väli DMR Gateway's" class="manual-img" />

### Staatilised TG-d (alati sees)

TG-d, mille panete oma seadistusse või paneeli, jäävad **alati kuulama**, ilma
et te peaksite midagi tegema. Näide: kui seadistate `TS2=730`, kuulab teie
hotspot 730 püsivalt, kuni te selle eemaldate.

**Pi-Star — kuhu panna OPTIONS rida käsitsi:**

<img src="/img/pi-star_options.png" alt="Pi-Star: Options väli DMR Networkis" class="manual-img" />

**WPSD — kuhu panna OPTIONS rida käsitsi:**

<img src="/img/wpsd_options.png" alt="WPSD: Options väli DMR Gateway's" class="manual-img" />

### Dünaamilised TG-d (teie need aktiveerite)

TG-d, mida aktiveerite PTT-ga (ilma neid seadistamata), on **dünaamilised**: need
kestavad teatud aja (administraatori poolt seadistatud, tavaliselt ~10
minutit) ja kustutavad siis ise end või kustutatakse, kui markeerite 4000.

### SINGLE režiim (eksklusiivne kuulamine)

Mõnedel hotspotidel on **SINGLE=1**, mis tähendab: **ainult üks dünaamiline TG
korraga sloti kohta**. Kui aktiveerite uue TG, asendab see eelmise.

Teistel on **SINGLE=0**, mis laseb mitmel dünaamilisel TG-l koguneda. Teie
administraator otsustab, millist kasutada.

---

## Levinumad probleemid ja mida teha

| Probleem | Tõenäoline põhjus | Mida teha |
|---|---|---|
| **Ma ei kuule midagi** | Teie TG pole aktiivne või slot on hõivatud teise TG-ga | Saatke edastus sellel TG-l, et see aktiveerida; või oodake, kuni teine QSO lõpeb |
| **Minu hääl ei jõua kohale** | TG on hõivatud teise isikuga | Oodake, kuni vestlus lõpeb, ja proovige uuesti |
| **Audio läheb algul katki** | Slot oli hangtime'is | See on normaalne; oodake 5 sekundit ja korrake |
| **Ma aktiveerin TG-d, aga ei kuule seda** | Keegi ei edasta praegu sellel TG-l | TG on aktiveeritud, aga vaikselt; kui keegi räägib, kuulete teda |
| **Minu dünaamiline TG kadus** | Aeg otsa sai või keegi markeeris 4000 | Saatke sellel TG-l uuesti, et reaktiveerida |
| **Ma ei saa rääkida, mind ignoreeritakse** | Keegi teine kasutab praegu seda TG-d | Oodake oma järjekorda (kuulake kõigepealt) |

---

## Erinumbrid (kokkuvõte)

| Number | Mida see teeb |
|---|---|
| **4000** | "Hüppa toru": kustutab teie aktiveeritud dünaamilised TG-d. |
| **9990** | Kaja: mängib teie hääle tagasi audio testiks. |
| **9991-9999** | Eelsalvestatud teabesõnumid. |
| **Kõik muud TG-d** | Tavaline kõnekanal. |

---

## Head operaatoritavad

1. **Kuulake enne rääkimist.** Enne PTT vajutamist oodake sekund, et näha, kas
   keegi teine räägib. Reegel "üks vestlus TG kohta" hoiab teid ära katkestamast,
   aga viisakas on esmalt kuulata.

2. **Identifitseerige end.** Öelge oma kutsung algul ja lõpus. See on
   eeskirjades nõutud ja aitab teistel teada, kes räägib.

3. **Pausid vooremu vahel.** Jätke 2-3 sekundit enda sõnumi ja teise isiku
   vahele. See annab teistele aega vestlusega ühineda ja väldib katkestusi.

4. **Ärge vajutage PTT liiga kiiresti.** Kui vabastate ja vajutage uuesti vähem
   kui sekundiga, ei pruugi server muudatust korralikult töödelda. Lühike paus
   on tervislik.

5. **Kui aktiveerite dünaamilise TG, markeerige 4000, kui olete lõpetanud.** See
   vabastab ressursid ja väldib liikluse kuulmist, mis teid enam ei huvita.

---

## Kokkuvõte ühes lauses

> **Valige TG, vajutage PTT rääkimiseks, vabastage kuulamiseks ja markeerige
> 4000, kui soovite "hüpata toru". Server teeb kõik muu.**
