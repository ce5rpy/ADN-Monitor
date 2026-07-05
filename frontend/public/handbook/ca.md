# Manual de l'operador de ràdio — Servidor ADN DMR

> **A qui va dirigit aquest document:** a qualsevol persona que utilitzi una ràdio per parlar i escoltar.
> No cal que sàpiga res de servidors, xarxes ni programació.
> Si sap encendre la ràdio i prémer el PTT, aquest manual és per a vostè.

---

## Què és ADN?

ADN és una **xarxa de comunicacions per ràdio** que connecta el seu hotspot (o
repetidor) amb altres radioaficionats d'arreu del món a través d'internet.

Vostè parla per la ràdio → el seu hotspot envia la veu per internet →
d'altres l'escolten a les seves ràdios. I a la inversa.

<div class="manual-flow">
  <div class="manual-flow-node">La seva ràdio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">El seu hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">Servidor ADN</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Altres hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Les seves ràdios</div>
</div>

Els canals pels que parlem s'anomenen **Talk Groups** o **TG**. Cada TG és com
una "sala" o "canal" on la gent es reuneix per parlar d'un tema.

---

## Conceptes bàsics (el mínim que ha de saber)

### Talk Group (TG)

Un número que identifica un canal. Exemples:
- **TG 730** — sala general de Xile.
- **TG 714** — sala general de Panamà.
- **TG 4000** — número especial per "penjar" (vegeu més avall).

### Timeslot (slot)

DMR divideix cada freqüència en **dos canals temporals**: **slot 1** i **slot 2**.
És com tenir dos carrils en una autopista: poden circular dues converses al
mateix temps sense interferir. El seu hotspot i el servidor ho coordinen per
vostè.

Com a usuari, gairebé mai no ha de pensar en el slot: el seu hotspot està
configurat per utilitzar el slot correcte automàticament.

### PTT (Push To Talk)

El botó de la ràdio. Premi'l per parlar, deixi'l anar per escoltar.

---

## Què pot fer

### Parlar en un Talk Group

1. **Seleccioni el TG** a la ràdio (com canviar de canal).
2. **Premi PTT** i parli.
3. **Deixi anar PTT** per escoltar les respostes.

Això és tot. El servidor fa la resta.

### Activar un Talk Group nou (dinàmic)

Si vol escoltar un TG que **no està configurat** al seu hotspot,
simplement **transmeti en aquest TG**. Exemple: mai ha utilitzat TG 730507, però
vol escoltar-lo:

1. Programi TG 730507 a la ràdio.
2. Premi PTT durant un segon (només per "dir-ho" al servidor).
3. A partir d'aquest moment, **el seu hotspot comença a escoltar aquest TG** fins que
   el desactivi (marcant 4000) o s'acabi el temps.

> **Important:** en aquest servidor **una sola transmissió és suficient** per activar
> i escoltar. No cal transmetre dues vegades.

### Desactivar un Talk Group (penjar)

Si ja no vol sentir un TG que hagi activat, **marqui TG 4000** i premi PTT.
És com "penjar el telèfon":

1. Seleccioni **TG 4000** a la ràdio.
2. Premi PTT durant un segon.
3. El TG dinàmic queda esborrat. Ja no el sentirà.

> TG 4000 **només esborra els TG que hagi activat**. No afecta els TG estàtics
> (els que hagi configurat a la línia OPTIONS, al panell d'autoservei, o al
> servidor).

### Escoltar la seva pròpia veu (eco)

Vol comprovar si el seu àudio arriba correctament al servidor? **Marqui TG 9990** i
premi PTT. El servidor reproduirà la seva veu enregistrada perquè pugui comprovar
la qualitat.

> L'eco retorna **només al seu hotspot**, fins i tot si en té diversos registrats
> amb el mateix DMR ID.

### Escoltar missatges d'informació

Marcant de **9991 a 9999** pot escoltar fragments pregravats amb informació
del servei (depenent de quins clips hagi configurat l'administrador).

---

## Regles que el servidor aplica per vostè (no ha de fer res)

El servidor té regles automàtiques perquè les converses no se superposin. Vostè només
parla; el servidor s'encarrega que tot funcioni.

### Una conversa per TG cada vegada

Si algú està parlant al TG 730, **ningú més pot interrompre** en aquest mateix
TG. Si prem PTT al 730 mentre algú altre parla, el servidor
l'ignora (no molesta el parlant) però li permet escoltar el que diuen.

### No l'interromp si algú s'uneix a mig camí

Si vostè està parlant i un altre aficionat **es connecta a mig camí**, el servidor
lliura el seu àudio a partir d'aquest moment. No han d'esperar que vostè
acabi per començar a sentir-lo.

### Temps d'espera entre TG (hangtime)

Quan acaba una conversa en un slot, hi ha una pausa de **5 segons** abans que
aquest slot accepti un TG diferent. Això evita que dues converses es creuin.
És automàtic; no se n'adona.

### No pot parlar i escoltar alhora al mateix slot

Si està transmetent al slot 2, no pot rebre una altra trucada al slot 2
fins que deixi anar PTT. Això és normal: la ràdio tampoc pot fer les dues coses
alhora al mateix slot.

Però **pot parlar al slot 1 i escoltar al slot 2** al mateix temps (si la ràdio
és full-dúplex).

---

## Configuració del hotspot

El seu hotspot (Pi-Star, MMDVM, etc.) es configura amb una línia anomenada
**OPTIONS** que indica quins TG vol sentir. No ha d'editar-la a
mà: el **panell web** (autoservei) li permet canviar els TG des del
navegador.

### La línia OPTIONS i la seva contrasenya

El seu hotspot envia una línia anomenada **OPTIONS** al servidor després de connectar-se. El
servidor espera 10 segons que arribi aquesta línia; allò que enviï (o no enviï)
decideix **qui controla els seus TG**:

| El seu hotspot envia | Qui decideix els seus TG | Què passa |
|---|---|---|
| `OPTIONS=PASS=la_seva_clau;` | **Autoservei** (panell web) | El servidor verifica la contrasenya i després llegeix els seus TG de la base de dades. **Pot iniciar sessió al dashboard amb contrasenya i per IP.** |
| `OPTIONS=` buida | **Autoservei** (panell web) | El servidor llegeix els seus TG de la base de dades. Només pot utilitzar **inici de sessió automàtic per IP** al dashboard (sense contrasenya). |
| Sense OPTIONS (10 s d'espera) | **Autoservei** (panell web) | El servidor assumeix que el seu hotspot no té OPTIONS pròpies i utilitza la base de dades. Igual que el cas buit. |
| `OPTIONS=TS2=730;` (amb TG, SINGLE, etc.) | **El seu hotspot** | El servidor agafa els TG directament de la línia. **Ignora el panell web.** Només pot utilitzar **inici de sessió automàtic per IP** al dashboard (sense contrasenya). |

> **Important:** si el seu hotspot **no** envia `PASS=`, **no podrà
> iniciar sessió al dashboard amb contrasenya**. Només pot utilitzar
> l'inici de sessió automàtic per IP (si la seva IP coincideix). Per iniciar sessió amb contrasenya, el seu hotspot
> ha d'enviar `OPTIONS=PASS=la_seva_clau;` a la configuració (Pi-Star / WPSD:
> camp `optsfile`). La contrasenya ha de coincidir amb la que va registrar al
> panell.

**Pi-Star — on posar la contrasenya (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: camp Password a DMR Network" class="manual-img" />

**WPSD — on posar la contrasenya (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: camp Password a DMR Gateway" class="manual-img" />

### TG estàtics (sempre encesos)

Els TG que poseu a la configuració o al panell es mantenen **sempre escoltant**, sense
que hagi de fer res. Exemple: si configura `TS2=730`, el seu hotspot
escoltarà 730 permanentment fins que l'elimini.

**Pi-Star — on posar la línia OPTIONS manualment:**

<img src="/img/pi-star_options.png" alt="Pi-Star: camp Options a DMR Network" class="manual-img" />

**WPSD — on posar la línia OPTIONS manualment:**

<img src="/img/wpsd_options.png" alt="WPSD: camp Options a DMR Gateway" class="manual-img" />

### TG dinàmics (vostè els activa)

Els TG que activi amb PTT (sense tenir-los configurats) són **dinàmics**:
duren un cert temps (configurat per l'administrador, normalment ~10 minuts)
i després s'esborren sols, o s'esborren quan marqui 4000.

### Mode SINGLE (escolta exclusiva)

Alguns hotspots tenen **SINGLE=1**, que vol dir: **només un TG dinàmic cada vegada
per slot**. Si activa un TG nou, substitueix l'anterior.

D'altres tenen **SINGLE=0**, que permet acumular diversos TG dinàmics. El seu
administrador decideix quin utilitzar.

---

## Problemes freqüents i què fer

| Problema | Causa probable | Què fer |
|---|---|---|
| **No sento res** | El seu TG no està actiu, o el slot està ocupat per un altre TG | Transmeti en aquest TG per activar-lo; o esperi que acabi l'altre QSO |
| **La meva veu no hi arriba** | El TG està ocupat per algú altre | Esperi que acabi la conversa i torni-ho a provar |
| **L'àudio es talla al començament** | El slot estava en hangtime | És normal; esperi 5 segons i repeteixi |
| **Activo un TG però no el sento** | Ningú no està transmetent en aquest TG ara mateix | El TG està activat però en silenci; quan algú parli, el sentirà |
| **El meu TG dinàmic ha desaparegut** | S'ha esgotat el temps o algú ha marcat 4000 | Transmeti novament en aquest TG per reactivar-lo |
| **No puc parlar, m'ignoren** | Algú altre està utilitzant el TG ara mateix | Esperi el seu torn (escolti primer) |

---

## Números especials (resum)

| Número | Què fa |
|---|---|
| **4000** | "Penjar": esborra els TG dinàmics que hagi activat. |
| **9990** | Eco: reprodueix la seva veu per provar l'àudio. |
| **9991-9999** | Missatges d'informació pregravats. |
| **Qualsevol altre TG** | Canal de conversa normal. |

---

## Bones pràctiques de l'operador

1. **Escolti abans de parlar.** Abans de prémer PTT, esperi un segon per veure si
   algú altre està parlant. La regla "una conversa per TG" l'evita
   d'interrompre, però és de bona educació escoltar primer.

2. **Identifiqui's.** Digui el seu indicatiu al començament i al final. És
   un requisit reglamentari i ajuda els altres a saber qui parla.

3. **Pauses entre torns.** Deixi 2-3 segons entre el seu missatge i el de
   l'altra persona. Això dóna temps als altres per unir-se a la conversa i evita
   talls.

4. **No premi PTT massa ràpid.** Si deixa anar i torna a prémer en menys
   d'un segon, el servidor pot no processar el canvi correctament. Una pausa
   curta és sana.

5. **Si activa un TG dinàmic, marqui 4000 quan hagi acabat.** Això allibera
   recursos i evita sentir trànsit que ja no li interessa.

---

## Resum en una frase

> **Seleccioni el TG, premi PTT per parlar, deixi anar per escoltar, i marqui 4000 quan
> vulgui "penjar". El servidor fa tota la resta.**
