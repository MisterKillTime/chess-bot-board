"""
Board Controller — Orchestratore principale del progetto chess-bot-board.

Coordina tutti i sottosistemi:
- SensorMatrix: rileva le mosse del giocatore
- ChessEngine: valida le mosse e calcola la risposta IA
- XYController: muove fisicamente i pezzi tramite magnete

Flusso principale:
1. Sensori rilevano mossa umana
2. ChessEngine valida la mossa
3. Se illegale: XYController riporta il pezzo indietro
4. Se IA mode: ChessEngine calcola risposta -> XYController muove il pezzo
"""

import logging
import sys

from chess_engine import ChessEngine
from sensor_matrix import SensorMatrix
from config import GameMode, STOCKFISH_SKILL_LEVEL

# TODO: importare XYController quando il firmware e pronto
# from firmware.motor_controller import XYController, Stepper

logger = logging.getLogger(__name__)


class BoardController:
    """Orchestratore principale: sensori -> validazione -> movimento."""

    def __init__(self, game_mode: str = GameMode.IA_MODE,
                 skill_level: int = STOCKFISH_SKILL_LEVEL):
        """
        Inizializza il controller della scacchiera.

        Args:
            game_mode: Modalita di gioco (IA_MODE, MULTIPLAYER_MODE, PUZZLE_MODE)
            skill_level: Livello Stockfish 1-20 (solo per IA_MODE)
        """
        self.game_mode = game_mode
        self.engine = ChessEngine(skill_level=skill_level)
        self.sensors = SensorMatrix()
        # TODO: inizializzare XYController con i pin da config.py
        # self.xy = XYController(stepper_a, stepper_b)

        self._running = False

        logger.info(f"BoardController inizializzato — modalita: {game_mode}")

    def setup(self) -> None:
        """Prepara il sistema per una partita."""
        # TODO: eseguire homing del sistema XY
        # TODO: verificare posizione iniziale pezzi tramite sensori
        # TODO: avviare Stockfish se in IA_MODE

        if self.game_mode == GameMode.IA_MODE:
            self.engine.start_engine()

        logger.info("Setup completato — pronto per giocare")

    def play_game(self) -> None:
        """
        Loop principale della partita.

        Gestisce l'alternanza dei turni fino a fine partita.
        """
        self._running = True
        self.setup()

        logger.info("=== PARTITA INIZIATA ===")

        while self._running and not self.engine.is_game_over:
            if self.engine.board.turn:  # Turno del bianco (umano)
                self._handle_human_turn()
            else:
                if self.game_mode == GameMode.IA_MODE:
                    self._handle_ai_turn()
                else:
                    self._handle_human_turn()

        # Partita finita
        result = self.engine.game_result
        logger.info(f"=== PARTITA FINITA — Risultato: {result} ===")

    def _handle_human_turn(self) -> None:
        """
        Gestisce il turno del giocatore umano.

        1. Attende mossa dai sensori
        2. Valida con ChessEngine
        3. Se illegale, riporta il pezzo indietro
        """
        logger.info("Turno umano — in attesa della mossa...")

        from_sq, to_sq = self.sensors.wait_for_move()
        move = self.engine.validate_move(from_sq, to_sq)

        if move is None:
            # Mossa illegale — riporta il pezzo nella posizione originale
            logger.warning(f"Mossa illegale: {from_sq} -> {to_sq}")
            # TODO: self.xy.move_piece(to_sq, from_sq)  # Undo fisico
            return

        # Controlla se e una cattura — prima sposta il pezzo catturato nel cimitero
        if self.engine.is_capture(move):
            # TODO: spostare il pezzo catturato nella zona cimitero
            logger.info(f"Cattura rilevata su {to_sq}")

        self.engine.apply_move(move)
        logger.info(f"Mossa umana confermata: {from_sq} -> {to_sq}")

    def _handle_ai_turn(self) -> None:
        """
        Gestisce il turno dell'IA (Stockfish).

        1. Calcola la mossa migliore
        2. Muove fisicamente il pezzo
        """
        logger.info("Turno IA — Stockfish sta pensando...")

        move = self.engine.get_ai_move()
        if move is None:
            return

        from_sq = str(move)[:2]
        to_sq = str(move)[2:4]

        # Se cattura, sposta prima il pezzo catturato nel cimitero
        if self.engine.is_capture(move):
            # TODO: self.xy.move_piece(to_sq, cemetery_position)
            logger.info(f"IA cattura pezzo su {to_sq}")

        # Muovi il pezzo dell'IA
        # TODO: self.xy.move_piece(from_sq, to_sq)

        # Gestisci arrocco (muovere anche la torre)
        if self.engine.is_castling(move):
            # TODO: calcolare posizione torre e muoverla
            logger.info("Arrocco — muovo anche la torre")

        self.engine.apply_move(move)
        logger.info(f"Mossa IA eseguita: {from_sq} -> {to_sq}")

    def stop(self) -> None:
        """Ferma la partita e rilascia le risorse."""
        self._running = False
        self.engine.stop_engine()
        self.sensors.cleanup()
        # TODO: self.xy.cleanup()
        logger.info("BoardController fermato")


def main():
    """Entry point del programma."""
    # TODO: configurare logging su file e console
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    # TODO: leggere modalita e livello da argomenti CLI o config
    controller = BoardController(
        game_mode=GameMode.IA_MODE,
        skill_level=STOCKFISH_SKILL_LEVEL,
    )

    try:
        controller.play_game()
    except KeyboardInterrupt:
        logger.info("Interruzione manuale (Ctrl+C)")
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
