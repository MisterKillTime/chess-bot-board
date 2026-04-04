# Chess-Bot Board

Scacchiera robotica standalone che muove i pezzi fisicamente in autonomia tramite un sistema di magneti e motori stepper, controllata da un Raspberry Pi 4 con Stockfish come motore IA.

## Stack tecnico

| Layer | Tecnologie |
|-------|-----------|
| Meccanico | PLA, magneti N52, cinghia GT2, guide lineari 8mm |
| Elettronico | NEMA 17, A4988, Reed switch 8x8, RPi 4, 12V PSU |
| Software | Python 3.11, Stockfish, python-chess, GPIO |

## Struttura progetto

```
chess-bot-board/
├── docs/              # Documentazione hardware e fasi
├── cad/pieces/        # STL pezzi scacchiera
├── firmware/          # Controllo motori e calibrazione
│   └── motor_controller/
└── software/          # Logica scacchi, sensori, orchestratore
```

## Modalita di gioco

- **IA Mode** — Umano vs Stockfish (livello 1-20)
- **Multiplayer Mode** — Due giocatori fisici, validazione mosse automatica
- **Puzzle Mode** *(futura)* — Risolvi posizioni con aiuto IA

## Come funziona

1. Il giocatore muove un pezzo fisicamente
2. I Reed switch rilevano il cambiamento di posizione
3. Il RPi valida la mossa (python-chess) — se illegale, riporta il pezzo
4. In modalita IA: Stockfish calcola la risposta
5. I motori stepper muovono il magnete sotto il pezzo avversario
6. Se cattura: il pezzo catturato viene spostato nel "cimitero" laterale

## Specifiche CoreXY

- Scacchiera 40x40cm, caselle 5x5cm
- Steps/mm: 80 (NEMA17 1.8deg, A4988 1/16 microstepping, puleggia GT2 20T)
- Precisione target: errore < 2mm per casella

## Budget stimato

~208 EUR (componenti da Amazon.it, aprile 2026)

## Stato

Pianificazione — pre-acquisto componenti

## Autore

Cristian Alexandru Durbaca
