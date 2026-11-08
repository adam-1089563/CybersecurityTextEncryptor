# Text Encryptor / Decryptor

Een desktop-applicatie (Python + Tkinter) waarmee gebruikers eenvoudig tekst
kunnen versleutelen en ontsleutelen met symmetrische encryptie (AES via Fernet),
met sleutelafleiding op basis van een wachtwoord (PBKDF2).

## Repository

https://github.com/adam-1089563/CybersecurityTextEncryptor

## Inhoud

1. [Hoe de applicatie werkt](#1-hoe-de-applicatie-werkt)
2. [Installatie en gebruik](#2-installatie-en-gebruik)
3. [Gebruikte cryptografie en onderbouwing](#3-gebruikte-cryptografie-en-onderbouwing)
4. [Sleutelbeheer en beveiligingsimplicaties](#4-sleutelbeheer-en-beveiligingsimplicaties)
5. [Reflectie](#5-reflectie)
---

## 1. Hoe de applicatie werkt

De applicatie is een grafische desktop-app (Tkinter) met twee tabbladen:

- **Encrypt-tab**: de gebruiker voert platte tekst in, vult een wachtwoord in en
  klikt op *Encrypt*. De app toont de versleutelde output in de vorm
  `salt:ciphertext` (Base64). Er is een knop *Copy encrypted* om het resultaat
  naar het klembord te kopiëren.
- **Decrypt-tab**: de gebruiker plakt de `salt:ciphertext`-string, vult hetzelfde
  wachtwoord in en klikt op *Decrypt*. De originele platte tekst verschijnt.

Overige UI-kenmerken:

- Wachtwoordveld met een *Show*-checkbox (tonen/verbergen).
- Statusbalk onderaan die de laatste actie toont ("Encryption successful.",
  "Copied to clipboard.", etc.).
- Duidelijke foutmeldingen via `messagebox` bij:
  - leeg wachtwoord,
  - lege input,
  - verkeerd wachtwoord of gemanipuleerde ciphertext (decryptie mislukt).

### Datastroom
platte tekst + wachtwoord

│

▼

salt = os.urandom(16) (willekeurig, geen geheim)

│

▼

key = PBKDF2-HMAC-SHA256(wachtwoord, salt, 480000 iteraties, 32 bytes)

│

▼

token = Fernet(key).encrypt(platte tekst)

│

▼

output = base64(salt) + ":" + token


Bij decryptie wordt de salt uit de string gehaald, opnieuw dezelfde sleutel
afgeleid uit het wachtwoord, en `Fernet.decrypt()` aangeroepen. Als het
wachtwoord fout is of de ciphertext is aangepast, gooit Fernet een
`InvalidToken`-exception, die door de app wordt opgevangen en als
gebruikersvriendelijke foutmelding wordt getoond.

---

## 2. Installatie en gebruik

### Vereisten

- Python 3.12 of nieuwer
- `cryptography` bibliotheek

### Installatie

```bash
git clone https://github.com/adam-1089563/CybersecurityEncryptor.git
cd CybersecurityEncryptor
pip install -r requirements.txt
```

### Opstarten

```bash
python app.py
```

---

## 3. Gebruikte cryptografie en onderbouwing

**Algoritme:** AES-128 via Fernet

De applicatie gebruikt Fernet uit de `cryptography`-bibliotheek. Fernet is geen nieuw algoritme, maar een high-level recept dat intern combineert:

| Component | Functie |
|---|---|
| AES-128 in CBC-modus | Vertrouwelijkheid (versleuteling van de data) |
| PKCS7-padding | Correcte blokvulling |
| HMAC-SHA256 | Integriteit en authenticiteit (Authenticated Encryption) |
| Willekeurige IV per bericht | Zorgt dat identieke platte tekst anders versleutelt |

### Waarom AES?

AES is de door NIST gestandaardiseerde symmetrische standaard (FIPS 197) en is de afgelopen decennia intensief geanalyseerd. Het is snel, breed ondersteund en er zijn geen praktische aanvallen bekend die de volledige AES-128-brede sleutel kraken. Het is de logische keuze voor symmetrische tekstversleuteling.

### Waarom Fernet in plaats van zelf AES-CBC implementeren?

Het principe **"Don't roll your own crypto"** is hier leidend. Bij handmatige AES-CBC-implementatie moet de ontwikkelaar zelf de IV genereren, padding toevoegen, een MAC berekenen en verifiëren — en op elk van die punten gaat het in de praktijk regelmatig mis (IV-hergebruik, padding-oracle-aanvallen, gebrek aan integriteitscontrole). Fernet verpakt deze stappen veilig en dwingt authenticated encryption af. Daarmee is de kans op een implementatiefout aanzienlijk kleiner dan bij zelfgebouwde AES-code.

### Waarom authenticated encryption belangrijk is

Zonder MAC zou een aanvaller ciphertext kunnen manipuleren (bit-flipping) en zo mogelijk de platte tekst beïnvloeden. Fernet's HMAC-SHA256 zorgt dat elke wijziging in de ciphertext bij decryptie direct wordt gedetecteerd.

### Waarom geen asymmetrische encryptie?

De opdracht richt zich op symmetrische encryptie. Asymmetrische encryptie (zoals RSA of ECC) is vooral nuttig voor sleuteluitwisseling en digitale handtekeningen, maar is voor het versleutelen van willekeurige hoeveelheden tekst veel trager en complexer. Een hybride aanpak (asymmetrisch voor de sleutel, symmetrisch voor de data) is in productie gebruikelijk, maar valt buiten de kernscope van deze opdracht. In sectie 6 wordt dit als uitbreiding benoemd.

---

## 4. Sleutelbeheer en beveiligingsimplicaties

Sleutelbeheer is bij symmetrische encryptie het moeilijkste en meest kritische onderdeel. Daarom is hier expliciet voor gekozen:

### Generatie

- De gebruiker voert een wachtwoord (passphrase) in.
- De applicatie genereert per versleuteling een willekeurige salt van 16 bytes (`os.urandom(16)`).
- Met PBKDF2-HMAC-SHA256 (480.000 iteraties, 32-byte output) wordt uit wachtwoord + salt een Fernet-sleutel afgeleid.

De salt is geen geheim: hij wordt samen met de ciphertext opgeslagen en verzonden (`salt:ciphertext`). De salt voorkomt dat twee gebruikers met hetzelfde wachtwoord dezelfde sleutel krijgen en bemoeilijkt rainbow-table-aanvallen.

### Opslag

De applicatie slaat geen wachtwoord en geen sleutel op. De afgeleide sleutel bestaat alleen tijdelijk in het geheugen tijdens de encryptie- of decryptiebewerking. De output die de gebruiker bewaart is `salt:ciphertext`; de salt is niet geheim, de ciphertext is zonder wachtwoord onbruikbaar.

### Uitwisseling

De `salt:ciphertext`-string kan via elk kanaal worden verzonden (e-mail, chat, opslag). De vertrouwelijkheid hangt volledig af van het gedeelde wachtwoord. Dit is een bewuste keuze: de applicatie hoeft geen sleutels uit te wisselen, maar de gebruikers moeten het wachtwoord via een apart, veilig kanaal afspreken (bijvoorbeeld mondeling of via een aparte beveiligde app).

### Beveiligingsimplicaties

| Aspect | Implicatie |
|---|---|
| Wachtwoordsterkte | Zwakke wachtwoorden blijven kwetsbaar voor woordenboekaanvallen. PBKDF2 met 480.000 iteraties verhoogt de kosten per poging, maar kan een slecht wachtwoord niet redden. Gebruik bij voorkeur een lange passphrase of een wachtwoordmanager. |
| Wachtwoord delen | Het wachtwoord is de enige geheime factor. Als het uitlekt, is alle ciphertext die met dat wachtwoord is gemaakt, ontsleutelbaar. |
| Geen voorwaartse geheimhouding | Bij symmetrische encryptie met een gedeeld wachtwoord is er geen forward secrecy: als het wachtwoord later uitlekt, is ook oude ciphertext te ontsleutelen. |
| Schaalbaarheid | Dit model werkt goed voor individueel gebruik of kleine groepen die één wachtwoord delen. Bij veel gebruikers wordt symmetrisch sleutelbeheer al snel onpraktisch: N gebruikers die paarsgewijs veilig willen communiceren hebben N×(N−1)/2 sleutels nodig, of ze moeten één gedeeld wachtwoord gebruiken (wat de impact van een lek vergroot). Dit is precies de complexiteit die de opdracht benoemt. |
| Integriteit | Door Fernet's HMAC wordt manipulatie van ciphertext gedetecteerd; een verkeerd wachtwoord of gewijzigde data levert een `InvalidToken`-fout op. |

Kortom: de gekozen aanpak is veilig voor kleinschalig gebruik, mits het wachtwoord sterk is en via een veilig kanaal wordt gedeeld. Voor grootschalige of organisatiebrede toepassingen is een hybride systeem met asymmetrische sleuteluitwisseling (bijvoorbeeld ECDH) nodig, waarbij per sessie een symmetrische sleutel wordt afgesproken.

---

## 5. Reflectie

Ik had geprobeerd om een algoritme te vinden dat wel veilig was, in vergelijking met vorig jaar toen ik alleen base64 gebruikte. Ik wilde opletten om een echt encryptiealgoritme te gebruiken.

Ik wilde ook opletten dat de encryptie symmetrisch is, dat je met een vastgesteld wachtwoord of sleutel een tekst kan versleutelen en ontsleutelen.

Ik heb de broncode van de applicatie openbaar gezet omdat het in GitHub staat, waarbij het gevonden kan worden en gecontroleerd kan worden hoe het werkt.

De gebruikte algoritmen voor de encryptie zijn openbare standaarden die informatie bevatten over hoe het werkt.

De versleuteling is afhankelijk van het wachtwoord dat gebruikt was. Het is geen perfect systeem, maar het werkt: hoe de tekst gesalt wordt, zorgt ervoor dat een tekst hetzelfde kan zijn met verschillende wachtwoorden, maar de salt die terugkomt ziet er heel erg anders uit.

Een van de zwaktes is dat het wachtwoord dat als sleutel gezet kan worden geen minimum heeft om te zorgen dat het veiliger zou kunnen zijn.