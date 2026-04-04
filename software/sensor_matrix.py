"""
Sensor Matrix — Lettura della matrice 8x8 di Reed switch tramite multiplexer CD74HC4067.

Gestisce:
- Scansione di tutti i 64 sensori
- Rilevamento posizione pezzi sulla scacchiera
- Rilevamento mosse del giocatore (differenza tra scansioni successive)
"""

import logging
import time
from typing import List, Optional, Tuple

from config import (
    MUX1_S0_PIN, MUX1_S1_PIN, MUX1_S2_PIN, MUX1_S3_PIN, MUX1_SIG_PIN,
    MUX2_S0_PIN, MUX2_S1_PIN, MUX2_S2_PIN, MUX2_S3_PIN, MUX2_SIG_PIN,
)

# TODO: importare RPi.GPIO o gpiozero
# import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


class SensorMatrix:
    """Legge la matrice 8x8 di Reed switch tramite 2 multiplexer CD74HC4067."""

    def __init__(self):
        """Inizializza i pin GPIO per i multiplexer."""
        # Pin di selezione (condivisi tra i due mux)
        self._select_pins = [MUX1_S0_PIN, MUX1_S1_PIN, MUX1_S2_PIN, MUX1_S3_PIN]

        # Pin segnale (uno per mux)
        self._sig_pins = [MUX1_SIG_PIN, MUX2_SIG_PIN]

        # Stato corrente della scacchiera (True = pezzo presente)
        self._state: List[List[bool]] = [[False] * 8 for _ in range(8)]

        # Stato precedente per rilevare cambiamenti
        self._prev_state: Optional[List[List[bool]]] = None

        # TODO: configurare pin GPIO — select come OUTPUT, sig come INPUT con pull-down

        logger.info("SensorMatrix inizializzata — 64 reed switch via 2x CD74HC4067")

    def _select_channel(self, channel: int) -> None:
        """
        Imposta i pin di selezione per leggere un canale del multiplexer.

        Args:
            channel: Numero canale 0-15
        """
        # TODO: scrivere i 4 bit del canale sui pin S0-S3
        for i, pin in enumerate(self._select_pins):
            bit = (channel >> i) & 1
            # GPIO.output(pin, bit)
            pass

    def _read_sensor(self, row: int, col: int) -> bool:
        """
        Legge un singolo reed switch.

        Args:
            row: Riga 0-7 (1-8 nella notazione scacchistica)
            col: Colonna 0-7 (A-H nella notazione scacchistica)

        Returns:
            True se un pezzo e presente sulla casella
        """
        # Determina quale multiplexer usare
        if row < 4:
            mux_index = 0
            channel = row * 8 + col  # Canale 0-31 -> mux1 gestisce righe 0-3
        else:
            mux_index = 1
            channel = (row - 4) * 8 + col  # Canale 0-31 -> mux2 gestisce righe 4-7

        # TODO: selezionare il canale e leggere il segnale
        self._select_channel(channel)
        # TODO: breve pausa per stabilizzazione segnale
        # value = GPIO.input(self._sig_pins[mux_index])

        return False  # Placeholder

    def scan_board(self) -> List[List[bool]]:
        """
        Scansiona l'intera scacchiera leggendo tutti i 64 sensori.

        Returns:
            Matrice 8x8 di booleani (True = pezzo presente)
        """
        self._prev_state = [row[:] for row in self._state]

        for row in range(8):
            for col in range(8):
                self._state[row][col] = self._read_sensor(row, col)

        occupied = sum(1 for r in self._state for c in r if c)
        logger.debug(f"Scansione completata — {occupied} caselle occupate")

        return self._state

    def detect_move(self) -> Optional[Tuple[str, str]]:
        """
        Rileva una mossa del giocatore confrontando lo stato attuale con il precedente.

        Una mossa valida produce esattamente:
        - Una casella che da occupata diventa vuota (partenza)
        - Una casella che da vuota diventa occupata (arrivo)

        Returns:
            Tupla (from_square, to_square) in notazione algebrica, o None
        """
        if self._prev_state is None:
            return None

        self.scan_board()

        lifted = []   # Caselle dove un pezzo e stato tolto
        placed = []   # Caselle dove un pezzo e stato messo

        columns = 'abcdefgh'
        for row in range(8):
            for col in range(8):
                prev = self._prev_state[row][col]
                curr = self._state[row][col]

                square = f"{columns[col]}{row + 1}"
                if prev and not curr:
                    lifted.append(square)
                elif not prev and curr:
                    placed.append(square)

        # Mossa semplice: un pezzo tolto + un pezzo messo
        if len(lifted) == 1 and len(placed) == 1:
            logger.info(f"Mossa rilevata: {lifted[0]} -> {placed[0]}")
            return (lifted[0], placed[0])

        # TODO: gestire cattura (2 caselle cambiano, ma una ha pezzo rimosso dall'avversario)
        # TODO: gestire arrocco (2 pezzi si muovono contemporaneamente)
        # TODO: gestire en passant

        if lifted or placed:
            logger.warning(f"Stato ambiguo — tolti: {lifted}, messi: {placed}")

        return None

    def wait_for_move(self, poll_interval_s: float = 0.1) -> Tuple[str, str]:
        """
        Attende che il giocatore faccia una mossa (polling dei sensori).

        Args:
            poll_interval_s: Intervallo di polling in secondi

        Returns:
            Tupla (from_square, to_square)
        """
        logger.info("In attesa della mossa del giocatore...")

        # TODO: implementare debounce per evitare letture spurie
        while True:
            move = self.detect_move()
            if move is not None:
                return move
            time.sleep(poll_interval_s)

    def get_initial_position(self) -> List[List[bool]]:
        """
        Verifica che i pezzi siano nella posizione iniziale standard.

        Returns:
            Stato corrente della scacchiera
        """
        self.scan_board()

        # Nella posizione iniziale: righe 0-1 e 6-7 occupate, righe 2-5 vuote
        # TODO: verificare e segnalare caselle mancanti

        return self._state

    def cleanup(self) -> None:
        """Rilascia le risorse GPIO."""
        # TODO: GPIO.cleanup() per i pin usati
        logger.info("SensorMatrix cleanup completato")
