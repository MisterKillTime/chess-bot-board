# Guida Componenti

## 1. Raspberry Pi 4 Model B 2GB — Il cervello
- Mini-computer con Linux, WiFi, Bluetooth e 40 pin GPIO
- Esegue Stockfish, logica scacchi, controllo motori
- Gestione via SSH durante sviluppo
- **~74 EUR** — idealo.it / Amazon.it

## 2. NEMA 17 Stepper Motor (x2) — I muscoli
- 200 passi = 1 giro completo, movimento preciso in mm
- Asse X (sinistra-destra) + Asse Y (avanti-indietro)
- Connettore a 4 fili, nessuna saldatura
- **~9 EUR/cad** — Amazon.it (STEPPERONLINE 17HS15-1504S)

## 3. Driver A4988 (x2) — Il traduttore
- Converte segnali RPi in corrente per i motori
- Segnali STEP e DIR dal RPi
- Trimmer da calibrare con multimetro
- **~8 EUR pack da 5** — Amazon.it

## 4. Cinghia GT2 6mm + Pulegge 20T — Il sistema di movimento
- Cinghia dentata, converte rotazione in movimento lineare
- Sistema CoreXY: 2 cinghie + 2 motori per entrambi gli assi
- **~10 EUR kit** — Amazon.it

## 5. Guide lineari 8mm + cuscinetti LM8UU — I binari
- Aste acciaio + cuscinetti lineari senza attrito
- 2 aste per asse X, 2 per asse Y
- Fissaggio con staffe stampate 3D + viti M3
- **~15 EUR set 4x400mm** — Amazon.it

## 6. Magneti neodimio N52 10x3mm — Il gancio invisibile
- Forza ~1-2kg per magnete
- Uno nella base di ogni pezzo, uno sul carrello
- Colla epossidica nell'incavo stampato
- **~8 EUR pack 20 pz** — Amazon.it

## 7. Reed Switch (x64) — I sensori presenza
- Interruttore magnetico: magnete vicino = circuito chiuso
- Uno sotto ogni casella, matrice 8x8
- Con multiplexer CD74HC4067 per ottimizzare pin GPIO
- **~6 EUR pack 20 pz** — Amazon.it (servono 3-4 pack)

## 8. Alimentatore 12V 3A — Corrente motori
- 220V AC a 12V DC per i driver A4988
- RPi alimentato separatamente via USB-C 5V
- **~12 EUR** — Amazon.it

## 9. Multiplexer CD74HC4067 (x2) — L'espansore GPIO
- Legge 16 ingressi con solo 4 pin RPi
- Gestisce la matrice 8x8 dei Reed switch
- **~3 EUR/cad** — Amazon.it / AliExpress

## BOM Totale Stimato: ~208 EUR
