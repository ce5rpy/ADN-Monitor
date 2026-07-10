# Manual do operador de rádio — ADN DMR Server

> **Para quem é este documento:** para quem usa o rádio para falar e ouvir. Não
> precisa saber nada de servidores, redes ou programação. Se sabe ligar o rádio
> e carregar no PTT, este manual é para si.

---

## O que é a ADN?

A ADN é uma **rede de comunicação por rádio** que liga o seu hotspot (ou
repetidor) a outros radioamadores em todo o mundo através da internet.

Fala no seu rádio → o seu hotspot envia a voz pela internet → outros ouvem-na
nos seus rádios. E vice-versa.

<div class="manual-flow">
  <div class="manual-flow-node">O seu rádio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">O seu hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">Servidor ADN</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Outros hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Os seus rádios</div>
</div>

Os canais onde falamos chamam-se **Talk Groups** (grupos de conversa) ou
**TG**. Cada TG é como uma "sala" ou "canal" onde as pessoas se reúnem para
falar sobre um tema.

---

## Conceitos básicos (o mínimo que precisa saber)

### Talk Group (TG)

Um número que identifica um canal. Exemplos:
- **TG 730** — sala geral do Chile.
- **TG 714** — sala geral do Panamá.
- **TG 4000** — número especial para "desligar" (ver abaixo).

### Timeslot (slot)

O DMR divide cada frequência em **dois canais de tempo**: **slot 1** e **slot 2**.
É como ter duas faixas numa autoestrada: podem circular duas conversações ao
mesmo tempo sem interferir. O seu hotspot e o servidor coordenam isto por si.

Como utilizador, quase nunca precisa de pensar no slot: o seu hotspot está
configurado para usar o slot correto automaticamente.

### PTT (Push To Talk)

O botão do seu rádio. Carrega para falar, larga para ouvir.

---

## O que pode fazer

### Falar num Talk Group

1. **Selecione o TG** no seu rádio (como mudar de canal).
2. **Carregue no PTT** e fale.
3. **Largue o PTT** para ouvir as respostas.

É tudo. O resto é feito pelo servidor.

### Ativar um Talk Group novo (dinâmico)

Se quer ouvir um TG que **não tem configurado** no seu hotspot, basta
**transmitir nesse TG**. Exemplo: nunca usou o TG 730507, mas quer ouvi-lo:

1. Programe o TG 730507 no seu rádio.
2. Carregue no PTT durante um segundo (só para "avisar" o servidor).
3. A partir desse momento, **o seu hotspot passa a ouvir esse TG** até o
   desativar (marcando 4000) ou o tempo acabar.

> **Importante:** neste servidor **uma única transmissão chega** para ativar e
> ouvir. Não precisa de transmitir duas vezes.

### Desativar um Talk Group (desligar)

Se já não quer ouvir um TG que ativou, **marque o TG 4000** e carregue no PTT.
É como "desligar o telefone":

1. Selecione **TG 4000** no seu rádio.
2. Carregue no PTT durante um segundo.
3. O TG dinâmico é apagado. Já não o ouvirá.

> O TG 4000 **só apaga os TG que ativou**. Não afeta os TG estáticos (os que
> configurou na linha OPTIONS, no painel de auto-serviço ou no servidor).

### Ouvir a sua própria voz (eco)

Quer testar se o seu áudio chega bem ao servidor? **Marque TG 9990** e carregue
no PTT. O servidor devolve a sua voz gravada para verificar a qualidade.

> O eco volta **só para o seu hotspot**, mesmo que tenha vários registados com
> o mesmo DMR ID.

### Ouvir mensagens de informação

Marcando **9991 a 9999** pode ouvir clips pré-gravados com informações do
serviço (depende dos clips que o administrador configurou).

---

## Regras que o servidor aplica por si (não precisa fazer nada)

O servidor tem regras automáticas para que as conversações não se sobreponham.
Só fala; o servidor encarrega-se de que tudo funcione.

### Uma conversação por TG de cada vez

Se alguém está a falar no TG 730, **ninguém mais pode interromper** nesse
mesmo TG. Se carregar no PTT em 730 enquanto outro fala, o servidor ignora-o
(não incomoda quem fala) mas deixa-o ouvir o que dizem.

### Não corta se alguém chegar tarde

Se está a falar e outro radioamador **se liga a meio**, o servidor entrega-lhe
o seu áudio a partir desse momento. Não precisa de esperar que termine para
começar a ouvi-lo.

### Tempo de espera entre TGs (hangtime)

Quando uma conversação termina num slot, há uns **5 segundos** de pausa antes
de esse slot aceitar outro TG diferente. Isto evita que duas conversações se
cruzem. É automático; não dá por isso.

### Não pode falar e ouvir ao mesmo tempo no mesmo slot

Se está a transmitir no slot 2, não pode receber outra chamada no slot 2 até
largar o PTT. É normal: o seu rádio também não consegue fazer as duas coisas
ao mesmo tempo no mesmo slot.

Mas **pode falar no slot 1 e ouvir no slot 2** ao mesmo tempo (se o seu rádio
for duplex).

---

## Configurar o seu hotspot

O seu hotspot (Pi-Star, MMDVM, etc.) configura-se com uma linha chamada
**OPTIONS** que indica quais os TG que quer ouvir. Não precisa de a editar à
mão: o **painel web** (auto-serviço) deixa-o mudar os seus TG pelo navegador.

### A linha OPTIONS e a sua palavra-passe

O seu hotspot envia uma linha chamada **OPTIONS** ao servidor depois de se
ligar. O servidor espera 10 segundos por essa linha; o que envia (ou não envia)
decide **quem controla os seus TG**:

| O seu hotspot envia | Quem decide os seus TG | O que acontece |
|---|---|---|
| `OPTIONS=PASS=sua_chave;` | **Auto-serviço** (painel web) | O servidor verifica a sua palavra-passe e depois lê os seus TG da base de dados. **Pode entrar no dashboard com palavra-passe e por IP.** |
| `OPTIONS=` vazio | **Auto-serviço** (painel web) | O servidor lê os seus TG da base de dados. Só pode usar **auto-login por IP** no dashboard (sem palavra-passe). |
| Não envia OPTIONS (passam 10 s) | **Auto-serviço** (painel web) | O servidor assume que o seu hotspot não tem OPTIONS próprias e usa a base de dados. Igual ao caso vazio. |
| `OPTIONS=TS2=730;` (com TG, SINGLE, etc.) | **O seu hotspot** | O servidor pega nos TG diretamente da linha. **Ignora o painel web.** Só pode usar **auto-login por IP** no dashboard (sem palavra-passe). |

> **Importante:** se o seu hotspot **não** envia `PASS=`, **não poderá entrar
> no dashboard com palavra-passe**. Só pode usar auto-login por IP (se o seu IP
> coincidir). Para entrar com palavra-passe, o seu hotspot deve enviar
> `OPTIONS=PASS=sua_chave;` na sua configuração (Pi-Star / WPSD: campo
> `optsfile`). A palavra-passe deve ser a mesma que registou no painel.

**Pi-Star — onde pôr a sua palavra-passe (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: campo Password em DMR Network" class="manual-img" />

**WPSD — onde pôr a sua palavra-passe (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: campo Password em DMR Gateway" class="manual-img" />

### TG estáticos (sempre ligados)

Os TG que põe na sua configuração ou painel ficam **sempre a ouvir**, sem
precisar de fazer nada. Exemplo: se configurar `TS2=730`, o seu hotspot ouvirá
730 permanentemente até o remover.

**Pi-Star — onde pôr a linha OPTIONS manualmente:**

<img src="/img/pi-star_options.png" alt="Pi-Star: campo Options em DMR Network" class="manual-img" />

**WPSD — onde pôr a linha OPTIONS manualmente:**

<img src="/img/wpsd_options.png" alt="WPSD: campo Options em DMR Gateway" class="manual-img" />

### TG dinâmicos (ativa-os você)

Os TG que ativa com PTT (sem os ter configurados) são **dinâmicos**: duram um
tempo (configurado pelo administrador, geralmente ~10 minutos) e depois
apagam-se sozinhos, ou apagam-se quando marca 4000.

### Modo SINGLE (escuta exclusiva)

Alguns hotspots têm **SINGLE=1**, que significa: **só um TG dinâmico de cada
vez por slot**. Se ativar um TG novo, substitui o anterior.

Outros têm **SINGLE=0**, que deixa acumular vários TG dinâmicos. O seu
administrador decide qual usar.

---

## Problemas comuns e o que fazer

| Problema | Causa provável | O que fazer |
|---|---|---|
| **Não ouço nada** | O seu TG não está ativo, ou o slot está ocupado com outro TG | Transmita nesse TG para o ativar; ou espere que o outro QSO termine |
| **A minha voz não chega** | O TG está ocupado por outra pessoa | Espere que a conversação termine e tente de novo |
| **O áudio corta no início** | O slot estava em tempo de espera (hangtime) | É normal; espere 5 segundos e repita |
| **Ativo um TG mas não o ouço** | Ninguém está a transmitir nesse TG agora | O TG está ativado mas em silêncio; quando alguém falar, ouvi-lo-á |
| **O meu TG dinâmico desapareceu** | O tempo acabou ou alguém marcou 4000 | Volte a transmitir nesse TG para o reativar |
| **Não consigo falar, ignoram-me** | Alguém mais está a usar o TG neste momento | Espere a sua vez (ouça primeiro) |

---

## Os números especiais (resumo)

| Número | O que faz |
|---|---|
| **4000** | "Desligar": apaga os TG dinâmicos que ativou. |
| **9990** | Eco: devolve a sua voz para testar áudio. |
| **9991-9999** | Mensagens de informação pré-gravadas. |
| **Qualquer outro TG** | Canal de conversa normal. |

---

## Boas práticas de operador

1. **Ouça antes de falar.** Antes de carregar no PTT, espere um segundo para
   ver se alguém mais está a falar. A regra "uma conversação por TG" impede-o
   de interromper, mas é de boa educação ouvir primeiro.

2. **Identifique-se.** Diga o seu indicativo ao começar e ao terminar. É
   regulamentar e ajuda os outros a saberem quem fala.

3. **Pausas entre turnos.** Deixe 2-3 segundos entre a sua mensagem e a do
   outro. Isto dá tempo a que outros se possam juntar à conversação e evita
   cortes.

4. **Não carregue no PTT demasiado rápido.** Se larga e volta a carregar em
   menos de um segundo, o servidor pode não processar bem a mudança. Uma pausa
   curta é saudável.

5. **Se ativa um TG dinâmico, marque 4000 quando terminar.** Assim liberta
   recursos e evita ouvir tráfego que já não lhe interessa.

---

## Resumo numa frase

> **Selecione o TG, carregue no PTT para falar, largue para ouvir, e marque
> 4000 quando quiser "desligar". O servidor faz todo o resto.**
