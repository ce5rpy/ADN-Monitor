# Radio operator manual — ADN DMR Server

> **Who this document is for:** anyone who uses a radio to talk and listen.
> You do not need to know anything about servers, networks, or programming.
> If you can turn on your radio and press PTT, this manual is for you.

---

## What is ADN?

ADN is a **radio communication network** that connects your hotspot (or
repeater) with other radio amateurs around the world over the internet.

You talk on your radio → your hotspot sends your voice over the internet →
others hear it on their radios. And vice versa.

<div class="manual-flow">
  <div class="manual-flow-node">Your radio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Your hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">ADN Server</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Other hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Their radios</div>
</div>

The channels we talk on are called **Talk Groups** or **TG**. Each TG is like
a "room" or "channel" where people gather to talk about a topic.

---

## Basic concepts (the minimum you need to know)

### Talk Group (TG)

A number that identifies a channel. Examples:
- **TG 730** — general room for Chile.
- **TG 714** — general room for Panama.
- **TG 4000** — special number to "hang up" (see below).

### Timeslot (slot)

DMR splits each frequency into **two time channels**: **slot 1** and **slot 2**.
It is like having two lanes on a highway: two conversations can travel at the
same time without interfering. Your hotspot and the server coordinate this for
you.

As a user, you almost never have to think about the slot: your hotspot is
configured to use the correct slot automatically.

### PTT (Push To Talk)

The button on your radio. Press it to talk, release it to listen.

---

## What you can do

### Talk on a Talk Group

1. **Select the TG** on your radio (just like changing channels).
2. **Press PTT** and talk.
3. **Release PTT** to hear replies.

That is it. The server does the rest.

### Activate a new Talk Group (dynamic)

If you want to listen to a TG that is **not configured** on your hotspot,
simply **transmit on that TG**. Example: you have never used TG 730507, but you
want to listen to it:

1. Program TG 730507 into your radio.
2. Press PTT for one second (just to "tell" the server).
3. From that moment on, **your hotspot starts listening to that TG** until you
   deactivate it (by keying 4000) or the time runs out.

> **Important:** on this server **a single transmission is enough** to activate
> and listen. You do not need to transmit twice.

### Deactivate a Talk Group (hang up)

If you no longer want to hear a TG you activated, **key TG 4000** and press PTT.
It is like "hanging up the phone":

1. Select **TG 4000** on your radio.
2. Press PTT for one second.
3. The dynamic TG is cleared. You will no longer hear it.

> TG 4000 **only clears the TGs you activated**. It does not affect static TGs
> (the ones you configured in the OPTIONS line, in the self-service panel, or on
> the server).

### Hear your own voice (echo)

Want to test whether your audio reaches the server properly? **Key TG 9990** and
press PTT. The server will play your recorded voice back so you can check the
quality.

> The echo returns **only to your hotspot**, even if you have several registered
> with the same DMR ID.

### Listen to information messages

By keying **9991 through 9999** you can hear prerecorded clips with service
information (depending on which clips the administrator has configured).

---

## Rules the server applies for you (you do not have to do anything)

The server has automatic rules so that conversations do not overlap. You just
talk; the server makes sure everything works.

### One conversation per TG at a time

If someone is talking on TG 730, **no one else can interrupt** on that same
TG. If you press PTT on 730 while someone else is talking, the server
ignores you (it does not disturb the speaker) but lets you listen to what they
say.

### It does not cut you off if someone joins late

If you are talking and another amateur **connects halfway through**, the server
delivers your audio from that moment on. They do not have to wait for you to
finish before they start hearing you.

### Wait time between TGs (hangtime)

When a conversation ends on a slot, there is a **5-second** pause before that
slot accepts a different TG. This prevents two conversations from crossing over.
It is automatic; you do not notice it.

### You cannot talk and listen at the same time on the same slot

If you are transmitting on slot 2, you cannot receive another call on slot 2
until you release PTT. This is normal: your radio cannot do both at once on the
same slot either.

But **you can talk on slot 1 and listen on slot 2** at the same time (if your
radio is full-duplex).

---

## Configuring your hotspot

Your hotspot (Pi-Star, MMDVM, etc.) is configured with a line called
**OPTIONS** that says which TGs you want to hear. You do not have to edit it by
hand: the **web panel** (self-service) lets you change your TGs from the
browser.

### The OPTIONS line and your password

Your hotspot sends a line called **OPTIONS** to the server after connecting. The
server waits 10 seconds for that line to arrive; what you send (or do not send)
decides **who controls your TGs**:

| Your hotspot sends | Who decides your TGs | What happens |
|---|---|---|
| `OPTIONS=PASS=your_key;` | **Self-service** (web panel) | The server verifies your password and then reads your TGs from the database. **You can log in to the dashboard with password and by IP.** |
| `OPTIONS=` empty | **Self-service** (web panel) | The server reads your TGs from the database. You can only use **auto-login by IP** on the dashboard (no password). |
| No OPTIONS (10 s pass) | **Self-service** (web panel) | The server assumes your hotspot has no OPTIONS of its own and uses the database. Same as the empty case. |
| `OPTIONS=TS2=730;` (with TGs, SINGLE, etc.) | **Your hotspot** | The server takes the TGs directly from the line. **Ignores the web panel.** You can only use **auto-login by IP** on the dashboard (no password). |

> **Important:** if your hotspot **does not** send `PASS=`, **you will not be
> able to log in to the dashboard with a password**. You can only use
> auto-login by IP (if your IP matches). To log in with a password, your hotspot
> must send `OPTIONS=PASS=your_key;` in its configuration (Pi-Star / WPSD:
> `optsfile` field). The password must match the one you registered in the
> panel.

**Pi-Star — where to put your password (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: Password field in DMR Network" class="manual-img" />

**WPSD — where to put your password (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: Password field in DMR Gateway" class="manual-img" />

### Static TGs (always on)

The TGs you put in your configuration or panel stay **always listening**, without
you having to do anything. Example: if you configure `TS2=730`, your hotspot
will listen to 730 permanently until you remove it.

**Pi-Star — where to put the OPTIONS line manually:**

<img src="/img/pi-star_options.png" alt="Pi-Star: Options field in DMR Network" class="manual-img" />

**WPSD — where to put the OPTIONS line manually:**

<img src="/img/wpsd_options.png" alt="WPSD: Options field in DMR Gateway" class="manual-img" />

### Dynamic TGs (you activate them)

The TGs you activate with PTT (without having them configured) are **dynamic**:
they last a certain time (configured by the administrator, usually ~10 minutes)
and then clear themselves, or are cleared when you key 4000.

### SINGLE mode (exclusive listening)

Some hotspots have **SINGLE=1**, which means: **only one dynamic TG at a time
per slot**. If you activate a new TG, it replaces the previous one.

Others have **SINGLE=0**, which lets several dynamic TGs accumulate. Your
administrator decides which to use.

---

## Common problems and what to do

| Problem | Likely cause | What to do |
|---|---|---|
| **I hear nothing** | Your TG is not active, or the slot is busy with another TG | Transmit on that TG to activate it; or wait for the other QSO to finish |
| **My voice does not get through** | The TG is busy with someone else | Wait for the conversation to end and try again |
| **Audio cuts off at the start** | The slot was in hangtime | It is normal; wait 5 seconds and repeat |
| **I activate a TG but do not hear it** | No one is transmitting on that TG right now | The TG is activated but silent; when someone talks, you will hear them |
| **My dynamic TG disappeared** | The time ran out or someone keyed 4000 | Transmit on that TG again to reactivate it |
| **I cannot talk, I am ignored** | Someone else is using the TG right now | Wait your turn (listen first) |

---

## Special numbers (summary)

| Number | What it does |
|---|---|
| **4000** | "Hang up": clears the dynamic TGs you activated. |
| **9990** | Echo: plays your voice back to test audio. |
| **9991-9999** | Prerecorded information messages. |
| **Any other TG** | Normal talk channel. |

---

## Good operator practices

1. **Listen before talking.** Before pressing PTT, wait a second to see if
   anyone else is speaking. The "one conversation per TG" rule prevents you
   from interrupting, but it is good manners to listen first.

2. **Identify yourself.** Say your callsign at the start and at the end. It is
   a regulatory requirement and helps others know who is talking.

3. **Pauses between turns.** Leave 2-3 seconds between your message and the
   other person's. This gives others time to join the conversation and avoids
   cut-offs.

4. **Do not press PTT too quickly.** If you release and press again in less
   than a second, the server may not process the change properly. A short pause
   is healthy.

5. **If you activate a dynamic TG, key 4000 when you are done.** That frees up
   resources and avoids hearing traffic you no longer care about.

---

## Summary in one sentence

> **Select the TG, press PTT to talk, release to listen, and key 4000 when you
> want to "hang up". The server does everything else.**
