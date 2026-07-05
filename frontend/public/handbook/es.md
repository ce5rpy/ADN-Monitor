# Manual del operador de radio — ADN DMR Server

> **Para quién es este documento:** para quienes usan la radio para hablar y
> escuchar. No necesitas saber nada de servidores, redes ni programación. Si
> sabes encender la radio y pulsar PTT, este manual es para ti.

---

## ¿Qué es ADN?

ADN es una **red de comunicación por radio** que conecta tu hotspot (o
repetidor) con otros radioaficionados en todo el mundo a través de internet.

Tú hablas por tu radio → tu hotspot envía la voz por internet → otros la
escuchan en sus radios. Y viceversa.

<div class="manual-flow">
  <div class="manual-flow-node">Tu radio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Tu hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">Servidor ADN</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Otros hotspots</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Sus radios</div>
</div>

Los canales por los que hablamos se llaman **Talk Groups** (grupos de charla)
o **TG**. Cada TG es como una "sala" o "canal" donde la gente se reúne a
hablar de un tema.

---

## Conceptos básicos (lo mínimo que necesitas saber)

### Talk Group (TG)

Un número que identifica un canal. Ejemplos:
- **TG 730** — sala general de Chile.
- **TG 714** — sala general de Panamá.
- **TG 4000** — número especial para "colgar" (ver más abajo).

### Timeslot (slot)

DMR divide cada frecuencia en **dos canales de tiempo**: **slot 1** y **slot 2**.
Es como tener dos carriles en una autopista: pueden circular dos conversaciones
a la vez sin molestarse. Tu hotspot y el servidor coordinan esto por ti.

Para ti, como usuario, casi nunca tienes que pensar en el slot: tu hotspot está
configurado para usar el slot correcto automáticamente.

### PTT (Push To Talk)

El botón de tu radio. Lo pulsas para hablar, lo sueltas para escuchar.

---

## Lo que puedes hacer

### Hablar en un Talk Group

1. **Selecciona el TG** en tu radio (igual que cambias de canal).
2. **Pulsa PTT** y habla.
3. **Suelta PTT** para escuchar las respuestas.

Eso es todo. El resto lo hace el servidor.

### Activar un Talk Group nuevo (dinámico)

Si quieres escuchar un TG que **no tienes configurado** en tu hotspot,
simplemente **transmite en ese TG**. Ejemplo: nunca has usado el TG 730507, pero
quieres escucharlo:

1. Programa el TG 730507 en tu radio.
2. Pulsa PTT un segundo (sólo para "avisar" al servidor).
3. A partir de ese momento, **tu hotspot queda escuchando ese TG** hasta que lo
   desactives (marcando 4000) o se acabe el tiempo.

> **Importante:** en este servidor **una sola transmisión basta** para activar
> y escuchar. No necesitas transmitir dos veces.

### Desactivar un Talk Group (colgar)

Si ya no quieres escuchar un TG que activaste, **marca el TG 4000** y pulsa PTT.
Es como "colgar el teléfono":

1. Selecciona **TG 4000** en tu radio.
2. Pulsa PTT un segundo.
3. El TG dinámico se borra. Ya no lo escucharás.

> TG 4000 **sólo borra los TG que activaste tú**. No afecta a los TG estáticos
> (los que configuraste en la línea OPTIONS, en el panel de auto-servicio o en
> el servidor).

### Escuchar tu propia voz (eco)

Quiere probar si tu audio llega bien al servidor? **Marca TG 9990** y pulsa
PTT. El servidor te devolverá tu voz grabada para que compruebes la calidad.

> El eco vuelve **sólo a tu hotspot**, aunque tengas varios registrados con el
> mismo DMR ID.

### Escuchar mensajes de información

Marcando **9991 a 9999** puedes escuchar clips pregrabados con información
del servicio (depende de qué clips haya configurado el administrador).

---

## Reglas que el servidor aplica por ti (no tienes que hacer nada)

El servidor tiene reglas automáticas para que las conversaciones no se pisen.
Tú sólo hablas; el servidor se encarga de que todo funcione.

### Una conversación por TG a la vez

Si alguien está hablando en el TG 730, **nadie más puede interrumpir** en
ese mismo TG. Si pulsas PTT en 730 mientras otro habla, el servidor te
ignora (no molesta al que habla) pero te deja escuchar lo que dicen.

### No te corta si alguien llega tarde

Si estás hablando y otro radioaficionado **se conecta a mitad**, el servidor
le entrega tu audio a partir de ese momento. No tiene que esperar a que
termines para empezar a escucharte.

### Tiempo de espera entre TGs (hangtime)

Cuando termina una conversación en un slot, hay unos **5 segundos** de pausa
antes de que ese slot acepte otro TG distinto. Esto evita que dos
conversaciones se crucen. Es automático; tú no lo notas.

### No puedes hablar y escuchar a la vez en el mismo slot

Si estás transmitiendo en el slot 2, no puedes recibir otra llamada en el
slot 2 hasta que sueltes PTT. Es normal: tu radio tampoco puede hacer las dos
cosas a la vez en el mismo slot.

Pero **sí puedes hablar en el slot 1 y escuchar en el slot 2** al mismo tiempo
(si tu radio es dúplex).

---

## Configurar tu hotspot

Tu hotspot (Pi-Star, MMDVM, etc.) se configura con una línea llamada
**OPTIONS** que dice qué TGs quieres escuchar. No tienes que editarla a mano:
el **panel web** (self-service) te deja cambiar tus TGs desde el navegador.

### La línea OPTIONS y tu contraseña

Tu hotspot envía una línea llamada **OPTIONS** al servidor después de
conectarse. El servidor espera 10 segundos a que llegue esa línea; lo que
envíes (o no envías) decide **quién controla tus TGs**:

| Tu hotspot envía | Quién decide tus TGs | Qué pasa |
|---|---|---|
| `OPTIONS=PASS=tu_clave;` | **Auto-servicio** (panel web) | El servidor verifica tu contraseña y luego lee tus TGs de la base de datos. **Puedes entrar al dashboard con contraseña y por IP.** |
| `OPTIONS=` vacío | **Auto-servicio** (panel web) | El servidor lee tus TGs de la base de datos. Solo puedes usar **auto-login por IP** en el dashboard (sin contraseña). |
| No envía OPTIONS (pasan los 10 s) | **Auto-servicio** (panel web) | El servidor asume que tu hotspot no tiene OPTIONS propias y usa la base de datos. Igual que el caso vacío. |
| `OPTIONS=TS2=730;` (con TGs, SINGLE, etc.) | **Tu hotspot** | El servidor toma los TGs directamente de la línea. **Ignora el panel web.** Solo puedes usar **auto-login por IP** en el dashboard (sin contraseña). |

> **Importante:** si tu hotspot **no** envía `PASS=`, **no podrás entrar al
> dashboard con contraseña**. Solo podrás usar auto-login por IP (si tu IP
> coincide). Para entrar con contraseña, tu hotspot debe enviar
> `OPTIONS=PASS=tu_clave;` en su configuración (Pi-Star / WPSD: campo
> `optsfile`). La contraseña debe ser la misma que registraste en el panel.

**Pi-Star — dónde poner tu contraseña (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: campo Password en DMR Network" class="manual-img" />

**WPSD — dónde poner tu contraseña (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: campo Password en DMR Gateway" class="manual-img" />

### TGs estáticos (siempre encendidos)

Los TGs que pones en tu configuración o panel se quedan **siempre escuchando**,
sin que tengas que hacer nada. Ejemplo: si configuras `TS2=730`, tu hotspot
escuchará 730 permanentemente hasta que lo quites.

**Pi-Star — dónde poner la línea OPTIONS manualmente:**

<img src="/img/pi-star_options.png" alt="Pi-Star: campo Options en DMR Network" class="manual-img" />

**WPSD — dónde poner la línea OPTIONS manualmente:**

<img src="/img/wpsd_options.png" alt="WPSD: campo Options en DMR Gateway" class="manual-img" />

### TGs dinámicos (los activas tú)

Los TGs que activas con PTT (sin tenerlos configurados) son **dinámicos**:
durarán un tiempo (configurado por el administrador, suele ser ~10 minutos) y
luego se borran solos, o se borran cuando marcas 4000.

### Modo SINGLE (escucha exclusiva)

Algunos hotspots tienen **SINGLE=1**, que significa: **sólo un TG dinámico a
la vez por slot**. Si activas un TG nuevo, reemplaza al anterior.

Otros tienen **SINGLE=0**, que deja acumular varios TGs dinámicos. Tu
administrador decide cuál usar.

---

## Problemas comunes y qué hacer

| Problema | Causa probable | Qué hacer |
|---|---|---|
| **No escucho nada** | Tu TG no está activo, o el slot está ocupado con otro TG | Transmite en ese TG para activarlo; o espera a que termine el otro QSO |
| **Mi voz no llega** | El TG está ocupado por otra persona | Espera a que termine la conversación y vuelve a intentarlo |
| **El audio se corta al principio** | El slot estaba en tiempo de espera (hangtime) | Es normal; espera 5 segundos y repite |
| **Activo un TG pero no lo escucho** | Nadie está transmitiendo en ese TG ahora mismo | El TG está activado pero en silencio; cuando alguien hable, lo escucharás |
| **Se borró mi TG dinámico** | Se acabó el tiempo o alguien marcó 4000 | Vuelve a transmitir en ese TG para reactivarlo |
| **No puedo hablar, me ignoran** | Alguien más está usando el TG en este momento | Espera tu turno (escucha primero) |

---

## Los números especiales (resumen)

| Número | Qué hace |
|---|---|
| **4000** | "Colgar": borra los TG dinámicos que activaste. |
| **9990** | Eco: te devuelve tu voz para probar audio. |
| **9991-9999** | Mensajes de información pregrabados. |
| **Cualquier otro TG** | Canal de charla normal. |

---

## Buenas prácticas de operador

1. **Escucha antes de hablar.** Antes de pulsar PTT, espera un segundo para
   ver si alguien más está hablando. La regla "una conversación por TG" te
   impide interrumpir, pero es de buena educación escuchar primero.

2. **Identifícate.** Di tu indicativo al empezar y al terminar. Es norma
   reglamentaria y ayuda a que los demás sepan quién habla.

3. **Pausas entre turnos.** Deja 2-3 segundos entre tu mensaje y el del otro.
   Esto da tiempo a que otros puedan unirse a la conversación y evita
   cortes.

4. **No pulses PTT demasiado rápido.** Si sueltas y vuelves a pulsar en menos
   de un segundo, el servidor puede no procesar bien el cambio. Una pausa
   corta es sana.

5. **Si activas un TG dinámico, márcalo 4000 cuando termines.** Así liberas
   recursos y evitas escuchar tráfico que ya no te interesa.

---

## Resumen en una frase

> **Selecciona el TG, pulsa PTT para hablar, suelta para escuchar, y marca
> 4000 cuando quieras "colgar". El servidor hace todo lo demás.**
