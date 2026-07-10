# Manuel de l'opérateur radio — ADN DMR Server

> **À qui s'adresse ce document :** à toute personne qui utilise une radio pour
> parler et écouter. Vous n'avez pas besoin de connaître les serveurs, les
> réseaux ou la programmation. Si vous savez allumer votre radio et appuyer sur
> PTT, ce manuel est pour vous.

---

## Qu'est-ce qu'ADN ?

ADN est un **réseau de communication radio** qui relie votre hotspot (ou
répéteur) à d'autres radioamateurs partout dans le monde via Internet.

Vous parlez sur votre radio → votre hotspot envoie votre voix sur Internet →
d'autres l'entendent sur leurs radios. Et vice-versa.

<div class="manual-flow">
  <div class="manual-flow-node">Votre radio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Votre hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">Serveur ADN</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Autres hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Leurs radios</div>
</div>

Les canaux sur lesquels nous parlons s'appellent des **Talk Groups** (groupes
de discussion) ou **TG**. Chaque TG est comme une « salle » ou un « canal » où
les gens se réunissent pour parler d'un sujet.

---

## Notions de base (le minimum à savoir)

### Talk Group (TG)

Un numéro qui identifie un canal. Exemples :
- **TG 730** — salle générale du Chili.
- **TG 714** — salle générale du Panama.
- **TG 4000** — numéro spécial pour « raccrocher » (voir ci-dessous).

### Timeslot (slot)

Le DMR divise chaque fréquence en **deux canaux temporels** : **slot 1** et
**slot 2**. C'est comme avoir deux voies sur une autoroute : deux conversations
peuvent circuler en même temps sans se gêner. Votre hotspot et le serveur
coordonnent cela pour vous.

En tant qu'utilisateur, vous n'avez presque jamais à vous soucier du slot :
votre hotspot est configuré pour utiliser le bon slot automatiquement.

### PTT (Push To Talk)

Le bouton de votre radio. Appuyez pour parler, relâchez pour écouter.

---

## Ce que vous pouvez faire

### Parler sur un Talk Group

1. **Sélectionnez le TG** sur votre radio (comme changer de canal).
2. **Appuyez sur PTT** et parlez.
3. **Relâchez PTT** pour écouter les réponses.

C'est tout. Le serveur fait le reste.

### Activer un nouveau Talk Group (dynamique)

Si vous voulez écouter un TG qui **n'est pas configuré** sur votre hotspot,
**transmettez simplement sur ce TG**. Exemple : vous n'avez jamais utilisé le
TG 730507, mais vous voulez l'écouter :

1. Programmez le TG 730507 dans votre radio.
2. Appuyez sur PTT pendant une seconde (juste pour « prévenir » le serveur).
3. À partir de ce moment, **votre hotspot écoute ce TG** jusqu'à ce que vous le
   désactiviez (en composant 4000) ou que le temps s'écoule.

> **Important :** sur ce serveur **une seule transmission suffit** pour activer
> et écouter. Vous n'avez pas besoin de transmettre deux fois.

### Désactiver un Talk Group (raccrocher)

Si vous ne voulez plus entendre un TG que vous avez activé, **composez le
TG 4000** et appuyez sur PTT. C'est comme « raccrocher le téléphone » :

1. Sélectionnez **TG 4000** sur votre radio.
2. Appuyez sur PTT pendant une seconde.
3. Le TG dynamique est effacé. Vous ne l'entendrez plus.

> Le TG 4000 **n'efface que les TG que vous avez activés**. Il n'affecte pas les
> TG statiques (ceux que vous avez configurés dans la ligne OPTIONS, dans le
> panneau libre-service ou sur le serveur).

### Écouter votre propre voix (écho)

Vous voulez tester si votre audio arrive bien au serveur ? **Composez le
TG 9990** et appuyez sur PTT. Le serveur vous renverra votre voix enregistrée
pour que vous puissiez en vérifier la qualité.

> L'écho revient **uniquement à votre hotspot**, même si vous en avez plusieurs
> enregistrés avec le même ID DMR.

### Écouter des messages d'information

En composant **9991 à 9999**, vous pouvez écouter des clips préenregistrés avec
des informations sur le service (selon les clips configurés par
l'administrateur).

---

## Règles que le serveur applique pour vous (vous n'avez rien à faire)

Le serveur a des règles automatiques pour que les conversations ne se
chevauchent pas. Vous parlez simplement ; le serveur s'occupe de faire
fonctionner tout cela.

### Une conversation par TG à la fois

Si quelqu'un parle sur le TG 730, **personne d'autre ne peut interrompre** sur
ce même TG. Si vous appuyez sur PTT sur 730 pendant que quelqu'un d'autre
parle, le serveur vous ignore (il ne dérange pas celui qui parle) mais vous
permet d'écouter ce qu'ils disent.

### Pas de coupure si quelqu'un arrive tard

Si vous parlez et qu'un autre radioamateur **se connecte en cours de route**,
le serveur lui livre votre audio à partir de ce moment. Il n'a pas besoin
d'attendre que vous ayez terminé pour commencer à vous entendre.

### Temps d'attente entre TG (hangtime)

Lorsqu'une conversation se termine sur un slot, il y a une pause d'environ
**5 secondes** avant que ce slot n'accepte un autre TG différent. Cela évite
que deux conversations ne se croisent. C'est automatique ; vous ne le remarquez
pas.

### Vous ne pouvez pas parler et écouter en même temps sur le même slot

Si vous transmettez sur le slot 2, vous ne pouvez pas recevoir un autre appel
sur le slot 2 jusqu'à ce que vous relâchiez le PTT. C'est normal : votre radio
ne peut pas non plus faire les deux à la fois sur le même slot.

Mais **vous pouvez parler sur le slot 1 et écouter sur le slot 2** en même
temps (si votre radio est full-duplex).

---

## Configurer votre hotspot

Votre hotspot (Pi-Star, MMDVM, etc.) se configure avec une ligne appelée
**OPTIONS** qui indique quels TG vous voulez entendre. Vous n'avez pas à la
modifier à la main : le **panneau web** (libre-service) vous permet de modifier
vos TG depuis le navigateur.

### La ligne OPTIONS et votre mot de passe

Votre hotspot envoie une ligne appelée **OPTIONS** au serveur après la
connexion. Le serveur attend 10 secondes que cette ligne arrive ; ce que vous
envoyez (ou n'envoyez pas) décide **qui contrôle vos TG** :

| Votre hotspot envoie | Qui décide de vos TG | Ce qui se passe |
|---|---|---|
| `OPTIONS=PASS=votre_clé;` | **Libre-service** (panneau web) | Le serveur vérifie votre mot de passe puis lit vos TG depuis la base de données. **Vous pouvez vous connecter au tableau de bord avec mot de passe et par IP.** |
| `OPTIONS=` vide | **Libre-service** (panneau web) | Le serveur lit vos TG depuis la base de données. Vous ne pouvez utiliser que la **connexion automatique par IP** sur le tableau de bord (sans mot de passe). |
| Pas d'OPTIONS (10 s écoulées) | **Libre-service** (panneau web) | Le serveur suppose que votre hotspot n'a pas ses propres OPTIONS et utilise la base de données. Comme le cas vide. |
| `OPTIONS=TS2=730;` (avec TG, SINGLE, etc.) | **Votre hotspot** | Le serveur prend les TG directement depuis la ligne. **Ignore le panneau web.** Vous ne pouvez utiliser que la **connexion automatique par IP** sur le tableau de bord (sans mot de passe). |

> **Important :** si votre hotspot **n'envoie pas** `PASS=`, **vous ne pourrez
> pas vous connecter au tableau de bord avec un mot de passe**. Vous ne pouvez
> utiliser que la connexion automatique par IP (si votre IP correspond). Pour
> vous connecter avec un mot de passe, votre hotspot doit envoyer
> `OPTIONS=PASS=votre_clé;` dans sa configuration (Pi-Star / WPSD : champ
> `optsfile`). Le mot de passe doit correspondre à celui que vous avez
> enregistré dans le panneau.

**Pi-Star — où mettre votre mot de passe (PASS) :**

<img src="/img/pi-star_pass.png" alt="Pi-Star : champ Password dans DMR Network" class="manual-img" />

**WPSD — où mettre votre mot de passe (PASS) :**

<img src="/img/wpsd_pass.png" alt="WPSD : champ Password dans DMR Gateway" class="manual-img" />

### TG statiques (toujours actifs)

Les TG que vous mettez dans votre configuration ou votre panneau restent
**toujours à l'écoute**, sans que vous ayez à faire quoi que ce soit. Exemple :
si vous configurez `TS2=730`, votre hotspot écoutera 730 en permanence jusqu'à
ce que vous le supprimiez.

**Pi-Star — où mettre la ligne OPTIONS manuellement :**

<img src="/img/pi-star_options.png" alt="Pi-Star : champ Options dans DMR Network" class="manual-img" />

**WPSD — où mettre la ligne OPTIONS manuellement :**

<img src="/img/wpsd_options.png" alt="WPSD : champ Options dans DMR Gateway" class="manual-img" />

### TG dynamiques (vous les activez)

Les TG que vous activez avec PTT (sans les avoir configurés) sont
**dynamiques** : ils durent un certain temps (configuré par l'administrateur,
généralement ~10 minutes) puis s'effacent eux-mêmes, ou s'effacent lorsque vous
composez 4000.

### Mode SINGLE (écoute exclusive)

Certains hotspots ont **SINGLE=1**, ce qui signifie : **un seul TG dynamique à
la fois par slot**. Si vous activez un nouveau TG, il remplace le précédent.

D'autres ont **SINGLE=0**, ce qui permet d'accumuler plusieurs TG dynamiques.
Votre administrateur décide lequel utiliser.

---

## Problèmes courants et quoi faire

| Problème | Cause probable | Que faire |
|---|---|---|
| **Je n'entends rien** | Votre TG n'est pas actif, ou le slot est occupé par un autre TG | Transmettez sur ce TG pour l'activer ; ou attendez que l'autre QSO se termine |
| **Ma voix ne passe pas** | Le TG est occupé par quelqu'un d'autre | Attendez que la conversation se termine et réessayez |
| **L'audio coupe au début** | Le slot était en temps d'attente (hangtime) | C'est normal ; attendez 5 secondes et répétez |
| **J'active un TG mais ne l'entends pas** | Personne ne transmet sur ce TG en ce moment | Le TG est activé mais silencieux ; quand quelqu'un parlera, vous l'entendrez |
| **Mon TG dynamique a disparu** | Le temps est écoulé ou quelqu'un a composé 4000 | Retransmettez sur ce TG pour le réactiver |
| **Je ne peux pas parler, on m'ignore** | Quelqu'un d'autre utilise le TG en ce moment | Attendez votre tour (écoutez d'abord) |

---

## Les numéros spéciaux (résumé)

| Numéro | Ce qu'il fait |
|---|---|
| **4000** | « Raccrocher » : efface les TG dynamiques que vous avez activés. |
| **9990** | Écho : renvoie votre voix pour tester l'audio. |
| **9991-9999** | Messages d'information préenregistrés. |
| **Tout autre TG** | Canal de discussion normal. |

---

## Bonnes pratiques d'opérateur

1. **Écoutez avant de parler.** Avant d'appuyer sur PTT, attendez une seconde
   pour voir si quelqu'un d'autre parle. La règle « une conversation par TG »
   vous empêche d'interrompre, mais il est de bon ton d'écouter d'abord.

2. **Identifiez-vous.** Dites votre indicatif au début et à la fin. C'est
   réglementaire et cela aide les autres à savoir qui parle.

3. **Pauses entre les tours.** Laissez 2-3 secondes entre votre message et
   celui de l'autre. Cela donne le temps à d'autres de se joindre à la
   conversation et évite les coupures.

4. **N'appuyez pas sur PTT trop rapidement.** Si vous relâchez et appuyez à
   nouveau en moins d'une seconde, le serveur peut ne pas traiter correctement
   le changement. Une courte pause est saine.

5. **Si vous activez un TG dynamique, composez 4000 quand vous avez fini.**
   Cela libère des ressources et évite d'entendre un trafic qui ne vous
   intéresse plus.

---

## Résumé en une phrase

> **Sélectionnez le TG, appuyez sur PTT pour parler, relâchez pour écouter, et
> composez 4000 quand vous voulez « raccrocher ». Le serveur fait tout le
> reste.**
