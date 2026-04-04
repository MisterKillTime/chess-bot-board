# Schema Cablaggio — Pin GPIO Mapping

## Stepper A (Asse X+Y)
| Funzione | GPIO | Pin fisico |
|----------|------|------------|
| STEP     | GPIO17 | Pin 11 |
| DIR      | GPIO18 | Pin 12 |
| ENABLE   | GPIO27 | Pin 13 |

## Stepper B (Asse X-Y)
| Funzione | GPIO | Pin fisico |
|----------|------|------------|
| STEP     | GPIO22 | Pin 15 |
| DIR      | GPIO23 | Pin 16 |
| ENABLE   | GPIO24 | Pin 18 |

## Multiplexer 1 — Righe 0-3 (Reed switch caselle A1-D8)
| Funzione | GPIO |
|----------|------|
| S0       | GPIO5  |
| S1       | GPIO6  |
| S2       | GPIO13 |
| S3       | GPIO19 |
| SIG      | GPIO26 |

## Multiplexer 2 — Righe 4-7 (Reed switch caselle E1-H8)
| Funzione | GPIO |
|----------|------|
| S0       | GPIO5  |
| S1       | GPIO6  |
| S2       | GPIO13 |
| S3       | GPIO19 |
| SIG      | GPIO21 |

## Endstop / Home Switch
| Funzione | GPIO |
|----------|------|
| Home X   | GPIO4  |
| Home Y   | GPIO25 |

## Note
- I multiplexer condividono i pin di selezione (S0-S3) — si leggono alternando il pin SIG
- I driver A4988 ricevono alimentazione 12V separata (non dai GPIO)
- Il RPi alimentato via USB-C 5V 3A dedicato
- ENABLE basso = motore attivo, alto = motore libero
