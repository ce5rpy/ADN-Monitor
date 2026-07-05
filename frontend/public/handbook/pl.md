# Podręcznik operatora radia — ADN DMR Server

> **Dla kogo jest ten dokument:** dla każdego, kto używa radia do mówienia i
> nasłuchiwania. Nie musisz nic wiedzieć o serwerach, sieciach ani
> programowaniu. Jeśli potrafisz włączyć radio i nacisnąć PTT, ten podręcznik
> jest dla Ciebie.

---

## Czym jest ADN?

ADN to **sieć łączności radiowej**, która łączy Twój hotspot (lub
repeater) z innymi krótkofalowcami na całym świecie przez internet.

Mówisz do swojego radia → Twój hotspot wysyła Twój głos przez internet → inni
słyszą go w swoich radiach. I odwrotnie.

<div class="manual-flow">
  <div class="manual-flow-node">Twoje radio</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Twój hotspot</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">Serwer ADN</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Inne hotspoty</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Ich radia</div>
</div>

Kanały, na których rozmawiamy, nazywają się **Talk Groups** lub **TG**. Każdy
TG jest jak "pokój" lub "kanał", w którym ludzie zbierają się, by rozmawiać na
jakiś temat.

---

## Podstawowe pojęcia (minimum, które musisz znać)

### Talk Group (TG)

Numer identyfikujący kanał. Przykłady:
- **TG 730** — ogólny pokój dla Chile.
- **TG 714** — ogólny pokój dla Panamy.
- **TG 4000** — specjalny numer, aby "rozłączyć się" (patrz niżej).

### Timeslot (slot)

DMR dzieli każdą częstotliwość na **dwa kanały czasowe**: **slot 1** i
**slot 2**. To jak dwie pasma na autostradzie: dwie rozmowy mogą przebiegać w
tym samym czasie bez zakłócania się. Twój hotspot i serwer koordynują to za
Ciebie.

Jako użytkownik prawie nigdy nie musisz myśleć o slocie: Twój hotspot jest
skonfigurowany tak, aby automatycznie używać właściwego slota.

### PTT (Push To Talk)

Przycisk w Twoim radiu. Naciśnij go, aby mówić, puść, aby słuchać.

---

## Co możesz robić

### Rozmawiać w Talk Group

1. **Wybierz TG** w swoim radiu (tak jak zmieniasz kanały).
2. **Naciśnij PTT** i mów.
3. **Puść PTT**, aby usłyszeć odpowiedzi.

To wszystko. Resztę robi serwer.

### Aktywować nowy Talk Group (dynamiczny)

Jeśli chcesz słuchać TG, który **nie jest skonfigurowany** w Twoim hopspocie,
po prostu **nadaj na tym TG**. Przykład: nigdy nie używałeś TG 730507, ale
chcesz go słuchać:

1. Zaprogramuj TG 730507 w swoim radiu.
2. Naciśnij PTT na jedną sekundę (tylko po to, by "powiadomić" serwer).
3. Od tego momentu **Twój hotspot zaczyna słuchać tego TG**, dopóki go nie
   dezaktywujesz (przez wybranie 4000) lub nie upłynie czas.

> **Ważne:** na tym serwerze **wystarczy jedna transmisja**, aby aktywować i
> słuchać. Nie musisz nadawać dwa razy.

### Dezaktywować Talk Group (rozłączenie)

Jeśli nie chcesz już słuchać TG, który aktywowałeś, **wybierz TG 4000** i
naciśnij PTT. To jak "rozłączenie telefonu":

1. Wybierz **TG 4000** w swoim radiu.
2. Naciśnij PTT na jedną sekundę.
3. Dynamiczny TG zostaje wyczyszczony. Nie będziesz go już słyszeć.

> TG 4000 **czyści tylko te TG, które aktywowałeś Ty**. Nie wpływa na TG
> statyczne (te, które skonfigurowałeś w linii OPTIONS, w panelu
> samoobsługi lub na serwerze).

### Usłyszeć własny głos (echo)

Chcesz sprawdzić, czy Twoje audio dociera do serwera prawidłowo? **Wybierz TG
9990** i naciśnij PTT. Serwer odtworzy Twój nagrany głos, abyś mógł sprawdzić
jakość.

> Echo wraca **tylko do Twojego hotspotu**, nawet jeśli masz kilka zarejestrowanych
> z tym samym DMR ID.

### Słuchać komunikatów informacyjnych

Wybierając **9991 do 9999** możesz odsłuchać wcześniej nagrane klipy z
informacjami serwisowymi (w zależności od tego, jakie klipy skonfigurował
administrator).

---

## Zasady, które serwer stosuje za Ciebie (nie musisz nic robić)

Serwer ma automatyczne reguły, aby rozmowy się nie nakładały. Ty po prostu
mówisz; serwer dba o to, żeby wszystko działało.

### Jedna rozmowa na TG naraz

Jeśli ktoś mówi na TG 730, **nikt inny nie może wejść w słowo** na tym samym
TG. Jeśli naciskasz PTT na 730, gdy ktoś inny mówi, serwer Cię ignoruje (nie
zakłóca mówiącego), ale pozwala Ci słuchać, co mówią.

### Nie ucina Cię, gdy ktoś dołączy z opóźnieniem

Jeśli mówisz, a inny krótkofalowiec **dołącza w połowie**, serwer dostarcza
Twoje audio od tego momentu. Nie musi czekać, aż skończysz, zanim zacznie Cię
słyszeć.

### Czas oczekiwania między TG (hangtime)

Gdy rozmowa kończy się na slocie, następuje **5-sekundowa** pauza, zanim ten
slot przyjmie inny TG. Zapobiega to nakładaniu się dwóch rozmów. Działa
automatycznie; tego nie zauważasz.

### Nie możesz mówić i słuchać jednocześnie na tym samym slocie

Jeśli nadajesz na slocie 2, nie możesz odebrać innej rozmowy na slocie 2, dopóki
nie puścisz PTT. To normalne: Twoje radio również nie potrafi robić obu rzeczy
naraz na tym samym slocie.

Ale **możesz mówić na slocie 1 i słuchać na slocie 2** w tym samym czasie (jeśli
Twoje radio jest pełnodupleksowe).

---

## Konfiguracja hotspotu

Twój hotspot (Pi-Star, MMDVM itp.) konfiguruje się linią o nazwie **OPTIONS**,
która określa, jakich TG chcesz słuchać. Nie musisz edytować jej ręcznie:
**panel webowy** (samoobsługa) pozwala zmieniać Twoje TG z przeglądarki.

### Linia OPTIONS i Twoje hasło

Twój hotspot wysyła po połączeniu linię o nazwie **OPTIONS** do serwera. Serwer
czeka 10 sekund na nadejście tej linii; to, co wyślesz (lub czego nie
wyślesz), decyduje **kto kontroluje Twoje TG**:

| Twój hotspot wysyła | Kto decyduje o Twoich TG | Co się dzieje |
|---|---|---|
| `OPTIONS=PASS=twoj_klucz;` | **Samoobsługa** (panel webowy) | Serwer weryfikuje Twoje hasło, a następnie odczytuje Twoje TG z bazy danych. **Możesz logować się do dashboardu hasłem i po IP.** |
| `OPTIONS=` puste | **Samoobsługa** (panel webowy) | Serwer odczytuje Twoje TG z bazy danych. Możesz używać tylko **auto-logowania po IP** w dashboardzie (bez hasła). |
| Brak OPTIONS (mija 10 s) | **Samoobsługa** (panel webowy) | Serwer zakłada, że Twój hotspot nie ma własnej linii OPTIONS i używa bazy danych. To samo co przypadek pusty. |
| `OPTIONS=TS2=730;` (z TG, SINGLE itp.) | **Twój hotspot** | Serwer pobiera TG bezpośrednio z linii. **Ignoruje panel webowy.** Możesz używać tylko **auto-logowania po IP** w dashboardzie (bez hasła). |

> **Ważne:** jeśli Twój hotspot **nie** wysyła `PASS=`, **nie będziesz mógł
> zalogować się do dashboardu hasłem**. Możesz używać tylko auto-logowania po IP
> (jeśli Twoje IP się zgadza). Aby logować się hasłem, Twój hotspot musi
> wysyłać `OPTIONS=PASS=twoj_klucz;` w swojej konfiguracji (Pi-Star / WPSD:
> pole `optsfile`). Hasło musi być zgodne z tym, które zarejestrowałeś w panelu.

**Pi-Star — gdzie wpisać swoje hasło (PASS):**

<img src="/img/pi-star_pass.png" alt="Pi-Star: Pole Password w DMR Network" class="manual-img" />

**WPSD — gdzie wpisać swoje hasło (PASS):**

<img src="/img/wpsd_pass.png" alt="WPSD: Pole Password w DMR Gateway" class="manual-img" />

### Statyczne TG (zawsze włączone)

TG, które wpiszesz w konfiguracji lub w panelu, pozostają **zawsze w
nasłuchu**, bez żadnej Twojej akcji. Przykład: jeśli ustawisz `TS2=730`, Twój
hotspot będzie nasłuchiwał 730 na stałe, dopóki go nie usuniesz.

**Pi-Star — gdzie wpisać linię OPTIONS ręcznie:**

<img src="/img/pi-star_options.png" alt="Pi-Star: Pole Options w DMR Network" class="manual-img" />

**WPSD — gdzie wpisać linię OPTIONS ręcznie:**

<img src="/img/wpsd_options.png" alt="WPSD: Pole Options w DMR Gateway" class="manual-img" />

### Dynamiczne TG (aktywujesz je Ty)

TG, które aktywujesz za pomocą PTT (bez ich konfigurowania), są **dynamiczne**:
trwają określony czas (ustawiony przez administratora, zazwyczaj ~10 minut), a
następnie same się czyszczą, albo są czyszczone, gdy wpiszesz 4000.

### Tryb SINGLE (nasłuch wyłączny)

Niektóre hotspoty mają **SINGLE=1**, co oznacza: **tylko jeden dynamiczny TG
naraz na slot**. Jeśli aktywujesz nowy TG, zastępuje on poprzedni.

Inne mają **SINGLE=0**, co pozwala na gromadzenie kilku dynamicznych TG. Twój
administrator decyduje, którego używać.

---

## Częste problemy i co zrobić

| Problem | Prawdopodobna przyczyna | Co zrobić |
|---|---|---|
| **Nic nie słyszę** | Twój TG nie jest aktywny lub slot jest zajęty innym TG | Nadaj na tym TG, aby go aktywować; lub poczekaj, aż skończy się inne QSO |
| **Mój głos nie dociera** | TG jest zajęty przez kogoś innego | Poczekaj, aż rozmowa się skończy, i spróbuj ponownie |
| **Audio urywa się na początku** | Slot był w hangtime | To normalne; odczekaj 5 sekund i powtórz |
| **Aktywuję TG, ale go nie słyszę** | Nikt teraz nie nadaje na tym TG | TG jest aktywowany, ale milczy; gdy ktoś przemówi, go usłyszysz |
| **Mój dynamiczny TG zniknął** | Czas minął lub ktoś wybrał 4000 | Nadaj ponownie na tym TG, aby go reaktywować |
| **Nie mogę mówić, jestem ignorowany** | Ktoś inny używa teraz tego TG | Poczekaj na swoją kolej (najpierw posłuchaj) |

---

## Numery specjalne (podsumowanie)

| Numer | Co robi |
|---|---|
| **4000** | "Rozłączenie": czyści dynamiczne TG, które aktywowałeś. |
| **9990** | Echo: odtwarza Twój głos, by przetestować audio. |
| **9991-9999** | Wstępnie nagrane komunikaty informacyjne. |
| **Każdy inny TG** | Zwykły kanał rozmów. |

---

## Dobre praktyki operatora

1. **Słuchaj, zanim zaczniesz mówić.** Przed naciśnięciem PTT odczekaj sekundę,
   aby sprawdzić, czy ktoś inny nie mówi. Zasada "jedna rozmowa na TG"
   powstrzymuje Cię przed wchodzeniem w słowo, ale dobrym tonem jest najpierw
   posłuchać.

2. **Identyfikuj się.** Podaj swój znak wywoławczy na początku i na końcu. Jest
   to wymóg regulaminowy i pomaga innym wiedzieć, kto mówi.

3. **Pauzy między turami.** Zostaw 2-3 sekundy między swoją wiadomością a
   wiadomością drugiej osoby. Daje to innym czas na dołączenie do rozmowy i
   unika urywań.

4. **Nie naciskaj PTT za szybko.** Jeśli puścisz i naciśniesz ponownie w mniej
   niż sekundę, serwer może nie przetworzyć zmiany prawidłowo. Krótka pauza jest
   zdrowa.

5. **Jeśli aktywujesz dynamiczny TG, wybierz 4000, gdy skończysz.** Dzięki temu
   zwalniasz zasoby i unikasz słuchania ruchu, który już Cię nie interesuje.

---

## Podsumowanie w jednym zdaniu

> **Wybierz TG, naciśnij PTT, aby mówić, puść, aby słuchać, i wybierz 4000,
> gdy chcesz się "rozłączyć". Serwer robi całą resztę.**
