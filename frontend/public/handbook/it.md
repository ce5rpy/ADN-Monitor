# Manuale dell'operatore radio — ADN DMR Server

> **A chi è rivolto questo documento:** a chi usa la radio per parlare e
> ascoltare. Non serve sapere nulla di server, reti o programmazione. Se sai
> accendere la radio e premere il PTT, questo manuale è per te.

---

## Cos'è ADN?

ADN è una **rete di comunicazione radio** che collega il tuo hotspot (o
ripetitore) con altri radioamatori in tutto il mondo tramite internet.

Parli alla tua radio → il tuo hotspot invia la voce su internet → altri la
sentono sulle loro radio. E viceversa.

<div class="manual-flow">
  <div class="manual-flow-node">La tua radio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Il tuo hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">Server ADN</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Altri hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Le loro radio</div>
</div>

I canali su cui parliamo si chiamano **Talk Group** (gruppi di conversazione) o
**TG**. Ogni TG è come una "stanza" o "canale" dove le persone si riuniscono
per parlare di un argomento.

---

## Concetti base (il minimo che devi sapere)

### Talk Group (TG)

Un numero che identifica un canale. Esempi:
- **TG 730** — stanza generale del Cile.
- **TG 714** — stanza generale di Panama.
- **TG 4000** — numero speciale per "riagganciare" (vedi sotto).

### Timeslot (slot)

Il DMR divide ogni frequenza in **due canali temporali**: **slot 1** e
**slot 2**. È come avere due corsie su un'autostrada: possono viaggiare due
conversazioni contemporaneamente senza disturbarsi. Il tuo hotspot e il server
coordinano questo per te.

Come utente, quasi mai devi pensare allo slot: il tuo hotspot è configurato per
usare lo slot corretto automaticamente.

### PTT (Push To Talk)

Il pulsante della tua radio. Premi per parlare, rilasci per ascoltare.

---

## Cosa puoi fare

### Parlare in un Talk Group

1. **Seleziona il TG** sulla tua radio (come cambi canale).
2. **Premi PTT** e parla.
3. **Rilascia PTT** per ascoltare le risposte.

Questo è tutto. Il resto lo fa il server.

### Attivare un nuovo Talk Group (dinamico)

Se vuoi ascoltare un TG che **non è configurato** sul tuo hotspot, basta
**trasmettere su quel TG**. Esempio: non hai mai usato il TG 730507, ma vuoi
ascoltarlo:

1. Programa il TG 730507 nella tua radio.
2. Premi PTT per un secondo (solo per "avvisare" il server).
3. Da quel momento, **il tuo hotspot resta in ascolto di quel TG** finché non
   lo disattivi (componendo 4000) o non scade il tempo.

> **Importante:** su questo server **basta una sola trasmissione** per attivare
> e ascoltare. Non devi trasmettere due volte.

### Disattivare un Talk Group (riagganciare)

Se non vuoi più ascoltare un TG che hai attivato, **componi il TG 4000** e premi
PTT. È come "riagganciare il telefono":

1. Seleziona **TG 4000** sulla tua radio.
2. Premi PTT per un secondo.
3. Il TG dinamico viene cancellato. Non lo sentirai più.

> Il TG 4000 **cancella solo i TG che hai attivato tu**. Non influisce sui TG
> statici (quelli che hai configurato nella riga OPTIONS, nel pannello di
> self-service o sul server).

### Ascoltare la tua stessa voce (eco)

Vuoi verificare se il tuo audio arriva bene al server? **Componi il TG 9990** e
premi PTT. Il server ti restituirà la tua voce registrata per controllarne la
qualità.

> L'eco torna **solo al tuo hotspot**, anche se ne hai diversi registrati con lo
> stesso ID DMR.

### Ascoltare messaggi informativi

Componendo **da 9991 a 9999** puoi ascoltare clip preregistrate con informazioni
del servizio (dipende da quali clip ha configurato l'amministratore).

---

## Regole che il server applica per te (non devi fare nulla)

Il server ha regole automatiche affinché le conversazioni non si sovrappongano.
Tu parli soltanto; il server si occupa di far funzionare tutto.

### Una conversazione per TG alla volta

Se qualcuno sta parlando sul TG 730, **nessun altro può interrompere** su quello
stesso TG. Se premi PTT su 730 mentre un altro parla, il server ti ignora (non
disturba chi parla) ma ti lascia ascoltare cosa dicono.

### Non ti taglia se qualcuno arriva tardi

Se stai parlando e un altro radioamatore **si collega a metà**, il server gli
consegna il tuo audio da quel momento. Non deve aspettare che tu finisca per
iniziare a sentirti.

### Tempo di attesa tra TG (hangtime)

Quando una conversazione termina su uno slot, c'è una pausa di circa **5
secondi** prima che quello slot accetti un altro TG diverso. Questo evita che
due conversazioni si incrocino. È automatico; non te ne accorgi.

### Non puoi parlare e ascoltare contemporaneamente sullo stesso slot

Se stai trasmettendo sullo slot 2, non puoi ricevere un'altra chiamata sullo
slot 2 finché non rilasci il PTT. È normale: anche la tua radio non può fare
entrambe le cose contemporaneamente sullo stesso slot.

Ma **puoi parlare sullo slot 1 e ascoltare sullo slot 2** allo stesso tempo (se
la tua radio è full-duplex).

---

## Configurare il tuo hotspot

Il tuo hotspot (Pi-Star, MMDVM, ecc.) si configura con una riga chiamata
**OPTIONS** che indica quali TG vuoi ascoltare. Non devi modificarla a mano: il
**pannello web** (self-service) ti permette di cambiare i tuoi TG dal browser.

### La riga OPTIONS e la tua password

Il tuo hotspot invia una riga chiamata **OPTIONS** al server dopo la
connessione. Il server attende 10 secondi che arrivi quella riga; ciò che invii
(o non invii) decide **chi controlla i tuoi TG**:

| Il tuo hotspot invia | Chi decide i tuoi TG | Cosa succede |
|---|---|---|
| `OPTIONS=PASS=tua_chiave;` | **Self-service** (pannello web) | Il server verifica la tua password e poi legge i tuoi TG dal database. **Puoi accedere alla dashboard con password e tramite IP.** |
| `OPTIONS=` vuoto | **Self-service** (pannello web) | Il server legge i tuoi TG dal database. Puoi usare solo **login automatico tramite IP** sulla dashboard (senza password). |
| Nessun OPTIONS (passano 10 s) | **Self-service** (pannello web) | Il server presume che il tuo hotspot non abbia OPTIONS proprie e usa il database. Come nel caso vuoto. |
| `OPTIONS=TS2=730;` (con TG, SINGLE, ecc.) | **Il tuo hotspot** | Il server prende i TG direttamente dalla riga. **Ignora il pannello web.** Puoi usare solo **login automatico tramite IP** sulla dashboard (senza password). |

> **Importante:** se il tuo hotspot **non** invia `PASS=`, **non potrai accedere
> alla dashboard con password**. Puoi usare solo il login automatico tramite IP
> (se il tuo IP coincide). Per accedere con password, il tuo hotspot deve
> inviare `OPTIONS=PASS=tua_chiave;` nella sua configurazione (Pi-Star / WPSD:
> campo `optsfile`). La password deve coincidere con quella registrata nel
> pannello.

**Pi-Star — dove inserire la tua password (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: campo Password in DMR Network" class="manual-img" />

**WPSD — dove inserire la tua password (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: campo Password in DMR Gateway" class="manual-img" />

### TG statici (sempre attivi)

I TG che inserisci nella tua configurazione o nel pannello restano **sempre in
ascolto**, senza che tu debba fare nulla. Esempio: se configuri `TS2=730`, il
tuo hotspot ascolterà 730 permanentemente finché non lo rimuovi.

**Pi-Star — dove inserire la riga OPTIONS manualmente:**

<img src="/img/pi-star_options.png" alt="Pi-Star: campo Options in DMR Network" class="manual-img" />

**WPSD — dove inserire la riga OPTIONS manualmente:**

<img src="/img/wpsd_options.png" alt="WPSD: campo Options in DMR Gateway" class="manual-img" />

### TG dinamici (li attivi tu)

I TG che attivi con PTT (senza averli configurati) sono **dinamici**: durano un
certo tempo (configurato dall'amministratore, di solito ~10 minuti) e poi si
cancellano da soli, o si cancellano quando componi 4000.

### Modalità SINGLE (ascolto esclusivo)

Alcuni hotspot hanno **SINGLE=1**, che significa: **solo un TG dinamico alla
volta per slot**. Se attivi un nuovo TG, sostituisce quello precedente.

Altri hanno **SINGLE=0**, che permette di accumulare più TG dinamici. Il tuo
amministratore decide quale usare.

---

## Problemi comuni e cosa fare

| Problema | Causa probabile | Cosa fare |
|---|---|---|
| **Non sento nulla** | Il tuo TG non è attivo, oppure lo slot è occupato con un altro TG | Trasmetti su quel TG per attivarlo; oppure aspetta che finisca l'altro QSO |
| **La mia voce non arriva** | Il TG è occupato da un'altra persona | Aspetta che finisca la conversazione e riprova |
| **L'audio si interrompe all'inizio** | Lo slot era in tempo di attesa (hangtime) | È normale; aspetta 5 secondi e ripeti |
| **Attivo un TG ma non lo sento** | Nessuno sta trasmettendo su quel TG in questo momento | Il TG è attivato ma silenzioso; quando qualcuno parlerà, lo sentirai |
| **Il mio TG dinamico è scomparso** | Il tempo è scaduto o qualcuno ha composto 4000 | Trasmetti di nuovo su quel TG per riattivarlo |
| **Non riesco a parlare, vengo ignorato** | Qualcun altro sta usando il TG in questo momento | Aspetta il tuo turno (ascolta prima) |

---

## I numeri speciali (riepilogo)

| Numero | Cosa fa |
|---|---|
| **4000** | "Riagganciare": cancella i TG dinamici che hai attivato. |
| **9990** | Eco: riproduce la tua voce per testare l'audio. |
| **9991-9999** | Messaggi informativi preregistrati. |
| **Qualsiasi altro TG** | Canale di conversazione normale. |

---

## Buone pratiche dell'operatore

1. **Ascolta prima di parlare.** Prima di premere PTT, aspetta un secondo per
   vedere se qualcun altro sta parlando. La regola "una conversazione per TG" ti
   impedisce di interrompere, ma è buona educazione ascoltare prima.

2. **Identificati.** Di' il tuo nominativo all'inizio e alla fine. È un obbligo
   regolamentare e aiuta gli altri a sapere chi parla.

3. **Pause tra i turni.** Lascia 2-3 secondi tra il tuo messaggio e quello
   dell'altro. Questo dà tempo agli altri di unirsi alla conversazione ed evita
   interruzioni.

4. **Non premere PTT troppo velocemente.** Se rilasci e premi di nuovo in meno
   di un secondo, il server potrebbe non elaborare bene il cambio. Una breve
   pausa è salutare.

5. **Se attivi un TG dinamico, componi 4000 quando hai finito.** Così liberi
   risorse ed eviti di ascoltare traffico che non ti interessa più.

---

## Riassunto in una frase

> **Seleziona il TG, premi PTT per parlare, rilascia per ascoltare e componi
> 4000 quando vuoi "riagganciare". Il server fa tutto il resto.**
