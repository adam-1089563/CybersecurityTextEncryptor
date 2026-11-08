# Text Encryptor / Decryptor

Een desktop-applicatie (Python + Tkinter) waarmee gebruikers eenvoudig tekst
kunnen versleutelen en ontsleutelen met symmetrische encryptie (AES via Fernet),
met sleutelafleiding op basis van een wachtwoord (PBKDF2).


## Inhoud

1. [Hoe de applicatie werkt](#1-hoe-de-applicatie-werkt)
2. [Installatie en gebruik](#2-installatie-en-gebruik)

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