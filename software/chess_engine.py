"""
Chess Engine — Wrapper per Stockfish e logica scacchistica con python-chess.

Gestisce:
- Stato della partita (board)
- Validazione mosse
- Calcolo mossa IA tramite Stockfish
- Rilevamento scacco matto, stallo, patta
"""

import logging
from typing import Optional, List

import chess
import chess.engine

from config import (
    STOCKFISH_PATH,
    STOCKFISH_DEPTH,
    STOCKFISH_TIME_LIMIT_S,
    STOCKFISH_SKILL_LEVEL,
)

logger = logging.getLogger(__name__)


class ChessEngine:
    """Motore scacchistico: gestisce la partita e comunica con Stockfish."""

    def __init__(self, skill_level: int = STOCKFISH_SKILL_LEVEL):
        """
        Inizializza il motore scacchistico.

        Args:
            skill_level: Livello Stockfish da 1 (facile) a 20 (massimo)
        """
        self.board = chess.Board()
        self.skill_level = skill_level
        self._engine: Optional[chess.engine.SimpleEngine] = None
        self._move_history: List[chess.Move] = []

        logger.info(f"ChessEngine inizializzato — livello Stockfish: {skill_level}")

    def start_engine(self) -> None:
        """Avvia il processo Stockfish."""
        # TODO: gestire eccezione se Stockfish non trovato
        self._engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self._engine.configure({"Skill Level": self.skill_level})
        logger.info("Stockfish avviato")

    def stop_engine(self) -> None:
        """Ferma il processo Stockfish."""
        if self._engine:
            self._engine.quit()
            self._engine = None
            logger.info("Stockfish fermato")

    def validate_move(self, from_square: str, to_square: str) -> Optional[chess.Move]:
        """
        Valida una mossa del giocatore.

        Args:
            from_square: Casella di partenza (es. 'e2')
            to_square: Casella di arrivo (es. 'e4')

        Returns:
            Oggetto Move se la mossa e legale, None altrimenti
        """
        try:
            from_sq = chess.parse_square(from_square.lower())
            to_sq = chess.parse_square(to_square.lower())
            move = chess.Move(from_sq, to_sq)

            # TODO: gestire promozione pedone (chiedere al giocatore quale pezzo)
            if move in self.board.legal_moves:
                return move

            # Controlla anche con promozione a donna (caso piu comune)
            promo_move = chess.Move(from_sq, to_sq, promotion=chess.QUEEN)
            if promo_move in self.board.legal_moves:
                return promo_move

        except ValueError:
            logger.warning(f"Casella non valida: {from_square} o {to_square}")

        return None

    def apply_move(self, move: chess.Move) -> None:
        """
        Applica una mossa alla scacchiera.

        Args:
            move: Mossa da applicare (gia validata)
        """
        san = self.board.san(move)
        self.board.push(move)
        self._move_history.append(move)
        logger.info(f"Mossa applicata: {san} — turno: {'Bianco' if self.board.turn else 'Nero'}")

    def undo_move(self) -> Optional[chess.Move]:
        """
        Annulla l'ultima mossa.

        Returns:
            La mossa annullata, o None se non ci sono mosse
        """
        if self._move_history:
            move = self.board.pop()
            self._move_history.pop()
            logger.info(f"Mossa annullata: {move}")
            return move
        return None

    def get_ai_move(self) -> Optional[chess.Move]:
        """
        Calcola la migliore mossa tramite Stockfish.

        Returns:
            La mossa calcolata da Stockfish, o None se partita finita
        """
        if not self._engine:
            logger.error("Stockfish non avviato — chiama start_engine() prima")
            return None

        if self.board.is_game_over():
            return None

        # TODO: implementare tempo limite configurabile
        result = self._engine.play(
            self.board,
            chess.engine.Limit(
                time=STOCKFISH_TIME_LIMIT_S,
                depth=STOCKFISH_DEPTH,
            )
        )

        logger.info(f"Mossa IA: {self.board.san(result.move)}")
        return result.move

    def is_capture(self, move: chess.Move) -> bool:
        """Verifica se una mossa e una cattura."""
        return self.board.is_capture(move)

    def is_castling(self, move: chess.Move) -> bool:
        """Verifica se una mossa e un arrocco."""
        return self.board.is_castling(move)

    def is_en_passant(self, move: chess.Move) -> bool:
        """Verifica se una mossa e un en passant."""
        return self.board.is_en_passant(move)

    @property
    def is_check(self) -> bool:
        """Verifica se il re del giocatore corrente e sotto scacco."""
        return self.board.is_check()

    @property
    def is_game_over(self) -> bool:
        """Verifica se la partita e finita."""
        return self.board.is_game_over()

    @property
    def game_result(self) -> Optional[str]:
        """
        Restituisce il risultato della partita.

        Returns:
            '1-0', '0-1', '1/2-1/2', o None se partita in corso
        """
        if self.board.is_game_over():
            return self.board.result()
        return None

    def reset(self) -> None:
        """Resetta la scacchiera alla posizione iniziale."""
        self.board.reset()
        self._move_history.clear()
        logger.info("Scacchiera resettata")

    def __del__(self):
        """Assicura che Stockfish venga fermato alla distruzione."""
        self.stop_engine()
