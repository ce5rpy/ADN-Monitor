# Radyo operatörü el kitabı — ADN DMR Sunucusu

> **Bu belge kimin için:** konuşmak ve dinlemek için radyo kullanan herkes içindir.
> Sunucular, ağlar veya programlama hakkında hiçbir şey bilmenize gerek yoktur.
> Radyonuzu açıp PTT'ye basabiliyorsanız, bu el kitabı sizin içindir.

---

## ADN nedir?

ADN, hotspot'unuzu (veya
tekrarlayıcınızı) dünyadaki diğer radyo amatörleriyle internet üzerinden
bağlayan bir **radyo iletişim ağıdır**.

Radyonuzda konuşursunuz → hotspot'unuz sesinizi internet üzerinden gönderir →
diğerleri kendi radyolarında duyar. Ve bunun tersi de geçerlidir.

<div class="manual-flow">
  <div class="manual-flow-node">Radyonuz</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Hotspot'unuz</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node manual-flow-server">ADN Sunucusu</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span><span class="manual-flow-label">internet</span></div>
  <div class="manual-flow-node">Diğer hotspot'lar</div>
  <div class="manual-flow-link"><span class="manual-flow-arrow"></span></div>
  <div class="manual-flow-node">Onların radyoları</div>
</div>

Konuştuğumuz kanallara **Talk Groups** veya **TG** denir. Her TG, belirli bir
konu hakkında konuşmak için insanların toplandığı bir "oda" veya "kanal"
gibidir.

---

## Temel kavramlar (bilmeniz gereken asgari bilgiler)

### Talk Group (TG)

Bir kanalı tanımlayan numara. Örnekler:
- **TG 730** — Şili için genel oda.
- **TG 714** — Panama için genel oda.
- **TG 4000** — "Telefonu kapatmak" için özel numara (aşağıya bakın).

### Timeslot (slot)

DMR her frekansı **iki zaman kanalına** böler: **slot 1** ve **slot 2**.
Bu, bir otoyolda iki şerit olması gibidir: iki görüşme aynı anda hiçbir
karışıklık olmadan devam edebilir. Hotspot'unuz ve sunucu bunu sizin için
koordine eder.

Kullanıcı olarak slot hakkında neredeyse hiç düşünmeniz gerekmez: hotspot'unuz
doğru slot'u otomatik olarak kullanacak şekilde yapılandırılmıştır.

### PTT (Push To Talk)

Radyonuzdaki düğme. Konuşmak için basın, dinlemek için bırakın.

---

## Neler yapabilirsiniz

### Bir Talk Group'ta konuşmak

1. Radyonuzda **TG'yi seçin** (kanal değiştirmek gibi).
2. **PTT'ye basın** ve konuşun.
3. Yanıtları duymak için **PTT'yi bırakın**.

İşte bu kadar. Geri kalanını sunucu yapar.

### Yeni bir Talk Group'u etkinleştirmek (dinamik)

Hotspot'unuzda **yapılandırılmamış** bir TG'yi dinlemek istiyorsanız,
sadece **o TG'de yayın yapın**. Örnek: TG 730507'yi hiç kullanmadınız ama onu
dinlemek istiyorsunuz:

1. TG 730507'yi radyonuza programlayın.
2. PTT'ye bir saniye basın (sadece sunucuya "söylemek" için).
3. O andan itibaren, **hotspot'unuz o TG'yi dinlemeye başlar** ve onu
   devre dışı bırakana (4000 tuşlayarak) veya süre dolana kadar dinlemeye devam eder.

> **Önemli:** Bu sunucuda **etkinleştirmek ve dinlemek için tek bir yayın yeterlidir**.
> İki kez yayınlamanıza gerek yoktur.

### Bir Talk Group'u devre dışı bırakmak (telefonu kapatmak)

Etkinleştirdiğiniz bir TG'yi artık duymak istemiyorsanız, **TG 4000'i tuşlayın** ve
PTT'ye basın. Bu, "telefonu kapatmak" gibidir:

1. Radyonuzda **TG 4000**'i seçin.
2. PTT'ye bir saniye basın.
3. Dinamik TG temizlenir. Artık duymazsınız.

> TG 4000 **yalnızca sizin etkinleştirdiğiniz TG'leri temizler**. Statik TG'leri
> etkilemez (OPTIONS satırında, self-service panelinde veya sunucuda
> yapılandırdığınız TG'ler).

### Kendi sesinizi duymak (yankı)

Sesinizin sunucuya düzgün ulaştığını test etmek mi istiyorsunuz? **TG 9990'ı tuşlayın**
ve PTT'ye basın. Sunucu, kaliteyi kontrol edebilmeniz için kaydedilmiş sesinizi
geri çalacaktır.

> Yankı, aynı DMR ID ile birkaç tane kaydetmiş olsanız bile **yalnızca
> hotspot'unuza** döner.

### Bilgi mesajlarını dinlemek

**9991 ile 9999** arası tuşlayarak, servis bilgileri içeren önceden kaydedilmiş
küçük parçaları duyabilirsiniz (yöneticinin hangi parçaları yapılandırdığına bağlı olarak).

---

## Sunucunun sizin için uyguladığı kurallar (hiçbir şey yapmanız gerekmez)

Sunucu, görüşmelerin çakışmaması için otomatik kurallara sahiptir. Siz sadece
konuşursunuz; sunucu her şeyin düzgün çalışmasını sağlar.

### Her TG'de aynı anda tek bir görüşme

Birisi TG 730'da konuşuyorsa, **aynı TG'de başka kimse araya giremez**.
Birisi konuşurken 730'da PTT'ye basarsanız, sunucu sizi yok sayar (konuşmacıyı
rahatsız etmez) ancak ne söylediklerini dinlemenize izin verir.

### Biri geç katılırsa sizi kesmez

Konuşuyorsanız ve başka bir amatör **yol ortasında bağlanırsa**, sunucu
o andan itibaren sesinizi iletir. Sizi duymaya başlamadan önce sizin
konuşmanızı bitirmenizi beklemelerine gerek yoktur.

### TG'ler arası bekleme süresi (hangtime)

Bir slot'taki görüşme bittiğinde, o slot farklı bir TG'yi kabul etmeden önce
**5 saniyelik** bir duraklama olur. Bu, iki görüşmenin çaprazlaşmasını önler.
Otomatiktir; farkında bile olmazsınız.

### Aynı slot'ta aynı anda hem konuşup hem dinleyemezsiniz

Slot 2'de yayın yapıyorsanız, PTT'yi bırakana kadar slot 2'de başka bir çağrı
alamazsınız. Bu normaldir: radyonuz da aynı slot'ta ikisini birden aynı anda yapamaz.

Ancak **slot 1'de konuşup slot 2'de dinleyebilirsiniz** (radyonuz tam-duplex
ise).

---

## Hotspot'unuzu yapılandırma

Hotspot'unuz (Pi-Star, MMDVM vb.) **OPTIONS** adı verilen ve hangi TG'leri
duymak istediğinizi söyleyen bir satırla yapılandırılır. Bunu elle düzenlemenize
gerek yok: **web paneli** (self-service), TG'lerinizi tarayıcıdan değiştirmenize
olanak tanır.

### OPTIONS satırı ve parolanız

Hotspot'unuz bağlandıktan sonra **OPTIONS** adı verilen bir satırı sunucuya gönderir.
Sunucu o satırın gelmesi için 10 saniye bekler; gönderdiğiniz (veya göndermediğiniz)
şey **TG'lerinizi kimin kontrol edeceğini** belirler:

| Hotspot'unuz gönderir | TG'lerinize kim karar verir | Ne olur |
|---|---|---|
| `OPTIONS=PASS=anahtarınız;` | **Self-service** (web paneli) | Sunucu parolanızı doğrular ve ardından TG'lerinizi veritabanından okur. **Dashboard'a parola ve IP ile giriş yapabilirsiniz.** |
| `OPTIONS=` boş | **Self-service** (web paneli) | Sunucu TG'lerinizi veritabanından okur. Dashboard'da yalnızca **IP ile otomatik giriş** kullanabilirsiniz (parola yok). |
| OPTIONS yok (10 sn geçer) | **Self-service** (web paneli) | Sunucu hotspot'unuzun kendi OPTIONS'ı olmadığını varsayar ve veritabanını kullanır. Boş durum ile aynıdır. |
| `OPTIONS=TS2=730;` (TG'ler, SINGLE vb. ile) | **Hotspot'unuz** | Sunucu TG'leri doğrudan satırdan alır. **Web panelini yok sayar.** Dashboard'da yalnızca **IP ile otomatik giriş** kullanabilirsiniz (parola yok). |

> **Önemli:** hotspot'unuz `PASS=` **göndermiyorsa**, **dashboard'a parola ile
> giriş yapamazsınız**. Yalnızca IP ile otomatik giriş kullanabilirsiniz (IP'niz
> eşleşiyorsa). Parola ile giriş yapmak için hotspot'unuz yapılandırmasında
> `OPTIONS=PASS=anahtarınız;` göndermelidir (Pi-Star / WPSD: `optsfile`
> alanı). Parola, panelde kaydettiğinizle aynı olmalıdır.

**Pi-Star — parolanızı (PASS) nereye koyacağınız:**

<img src="/img/pi-star_pass.png" alt="Pi-Star: DMR Network'te Parola alanı" class="manual-img" />

**WPSD — parolanızı (PASS) nereye koyacağınız:**

<img src="/img/wpsd_pass.png" alt="WPSD: DMR Gateway'de Parola alanı" class="manual-img" />

### Statik TG'ler (her zaman açık)

Yapılandırmanıza veya panelinize koyduğunuz TG'ler, sizin hiçbir şey yapmanıza
gerek kalmadan **sürekli dinleme** durumunda kalır. Örnek: `TS2=730` yapılandırırsanız,
hotspot'unuz 730'u siz kaldırana kadar kalıcı olarak dinler.

**Pi-Star — OPTIONS satırını elle nereye koyacağınız:**

<img src="/img/pi-star_options.png" alt="Pi-Star: DMR Network'te Options alanı" class="manual-img" />

**WPSD — OPTIONS satırını elle nereye koyacağınız:**

<img src="/img/wpsd_options.png" alt="WPSD: DMR Gateway'de Options alanı" class="manual-img" />

### Dinamik TG'ler (siz etkinleştirirsiniz)

PTT ile etkinleştirdiğiniz (ancak yapılandırmadığınız) TG'ler **dinamiktir**:
belirli bir süre boyunca (yönetici tarafından yapılandırılır, genellikle ~10 dakika)
sürerler ve sonra kendiliğinden temizlenir, ya da 4000 tuşladığınızda temizlenirler.

### SINGLE modu (özel dinleme)

Bazı hotspot'larda **SINGLE=1** bulunur, bu şu anlama gelir: **slot başına aynı anda yalnızca bir dinamik TG**.
Yeni bir TG etkinleştirirseniz, öncekinin yerini alır.

Diğerlerinde **SINGLE=0** vardır ve bu, birden fazla dinamik TG'nin birikmesine izin verir.
Hangisini kullanacağınızı yöneticiniz belirler.

---

## Yaygın sorunlar ve çözümleri

| Sorun | Olası neden | Ne yapmalı |
|---|---|---|
| **Hiçbir şey duymuyorum** | TG'niz aktif değil veya slot başka bir TG ile meşgul | Etkinleştirmek için o TG'de yayın yapın; veya diğer QSO'nun bitmesini bekleyin |
| **Sesim geçmiyor** | TG başka biriyle meşgul | Görüşmenin bitmesini bekleyin ve tekrar deneyin |
| **Ses başta kesiliyor** | Slot hangtime içindeydi | Bu normaldir; 5 saniye bekleyin ve tekrarlayın |
| **TG'yi etkinleştiriyorum ama duymuyorum** | Şu anda o TG'de kimse yayın yapmıyor | TG etkinleştirildi ama sessiz; biri konuştuğunda duyarsınız |
| **Dinamik TG'im kayboldu** | Süre doldu veya biri 4000 tuşladı | Yeniden etkinleştirmek için o TG'de tekrar yayın yapın |
| **Konuşamıyorum, yok sayılıyorum** | Şu anda TG'yi başka biri kullanıyor | Sıranızı bekleyin (önce dinleyin) |

---

## Özel numaralar (özet)

| Numara | Ne yapar |
|---|---|
| **4000** | "Telefonu kapat": etkinleştirdiğiniz dinamik TG'leri temizler. |
| **9990** | Yankı: sesi test etmek için sesinizi geri çalar. |
| **9991-9999** | Önceden kaydedilmiş bilgi mesajları. |
| **Başka herhangi bir TG** | Normal konuşma kanalı. |

---

## İyi operatör uygulamaları

1. **Konuşmadan önce dinleyin.** PTT'ye basmadan önce, başka biri
   konuşuyor mu diye bir saniye bekleyin. "Her TG'de tek görüşme" kuralı
   araya girmenizi engeller, ama önce dinlemek iyi görgü kuralıdır.

2. **Kendinizi tanıtın.** Başta ve sonda çağrı işaretinizi (callsign) söyleyin. Bu
   yasal bir gerekliliktir ve diğerlerinin kimin konuştuğunu bilmesine yardımcı olur.

3. **Sıralar arasında duraklayın.** Sizin mesajınız ile diğer kişinin
   mesajı arasında 2-3 saniye bırakın. Bu, başkalarına görüşmeye katılma
   zamanı verir ve kesilmeleri önler.

4. **PTT'ye çok hızlı basmayın.** Bir saniyeden kısa sürede bırakıp
   tekrar basarsanız, sunucu değişikliği düzgün işleyemeyebilir. Kısa bir
   duraklama sağlıklıdır.

5. **Dinamik bir TG etkinleştirdiğinizde işiniz bitince 4000 tuşlayın.** Bu,
   kaynakları serbest bırakır ve artık ilgilenmediğiniz trafiği duymaktan kaçınır.

---

## Tek cümlede özet

> **TG'yi seçin, konuşmak için PTT'ye basın, dinlemek için bırakın ve
> "telefonu kapatmak" istediğinizde 4000 tuşlayın. Geri kalan her şeyi sunucu yapar.**
