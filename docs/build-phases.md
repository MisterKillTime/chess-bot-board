# Fasi di Costruzione

## FASE 1 — Meccanica (2-4 settimane)
- [ ] Progettare pezzi scacchiera in Blender/Fusion 360 (con incavo per magnete nella base)
- [ ] Stampare i 32 pezzi in PLA — infill 20%
- [ ] Incollare magneti N52 nelle basi con resina epossidica
- [ ] Costruire telaio XY in legno/alluminio con guide 8mm
- [ ] Montare sistema cinghie GT2 CoreXY
- [ ] Test movimento manuale del carrello — verificare scorrimento fluido

## FASE 2 — Elettronica (2-3 settimane)
- [ ] Setup Raspberry Pi OS su MicroSD — configurazione SSH e WiFi
- [ ] Cablaggio RPi -> A4988 -> NEMA 17 su breadboard
- [ ] Calibrazione corrente A4988 con multimetro
- [ ] Test movimento motori: script Python di test XY
- [ ] Installazione matrice Reed switch 8x8 sotto il piano
- [ ] Cablaggio Reed switch -> multiplexer CD74HC4067 -> RPi GPIO
- [ ] Test lettura sensori: verificare rilevamento pezzi su tutte le 64 caselle

## FASE 3 — Software (3-6 settimane)
- [ ] Installazione python-chess + Stockfish su RPi
- [ ] board_controller.py: mappatura coordinate XY <-> notazione algebrica (A1-H8)
- [ ] chess_engine.py: logica validazione mosse + integrazione Stockfish
- [ ] Implementazione modalita IA standalone (Stockfish livello configurabile)
- [ ] Implementazione modalita multiplayer fisico (due giocatori)
- [ ] Sistema 'undo': mossa illegale -> riporta pezzo nella casella originale
- [ ] Sistema cattura: pezzo catturato spostato in zona laterale

## FASE 4 — Integrazione e test (2-3 settimane)
- [ ] Test end-to-end: partita completa IA vs umano
- [ ] Tuning magnetico: regolare spessore piano (target 2.5-3mm PLA)
- [ ] Calibrazione precisione: errore < 2mm per casella
- [ ] Gestione casi speciali: arrocco, en passant, promozione pedone
- [ ] Ottimizzazione velocita movimento (accelerazione/decelerazione)
- [ ] Test robustezza: 10+ partite complete senza errori
