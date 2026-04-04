"""
XY Controller — Gestione del sistema CoreXY per il posizionamento del magnete.

Converte coordinate cartesiane (X, Y) in passi motore secondo la cinematica CoreXY:
  - Motore A controlla (X + Y)
  - Motore B controlla (X - Y)

Scacchiera: 40x40cm, caselle 5x5cm.
Casella A1 = (0, 0) mm, H8 = (350, 350) mm.
Centro casella = (colonna * 50 + 25, riga * 50 + 25) mm.
"""

import logging
from typing import Tuple

from .stepper import Stepper

logger = logging.getLogger(__name__)

# Dimensioni scacchiera
SQUARE_SIZE_MM = 50.0  # Lato casella in mm
BOARD_OFFSET_MM = 25.0  # Offset dal bordo al centro della prima casella


class XYController:
    """Controlla il sistema CoreXY a due motori per posizionare il magnete."""

    def __init__(self, stepper_a: Stepper, stepper_b: Stepper):
        """
        Inizializza il controller XY con i due motori CoreXY.

        Args:
            stepper_a: Motore A — controlla asse (X+Y)
            stepper_b: Motore B — controlla asse (X-Y)
        """
        self.stepper_a = stepper_a
        self.stepper_b = stepper_b
        self._x_mm = 0.0
        self._y_mm = 0.0

        logger.info("XYController CoreXY inizializzato")

    def square_to_mm(self, square: str) -> Tuple[float, float]:
        """
        Converte notazione algebrica (es. 'E4') in coordinate mm.

        Args:
            square: Casella in notazione algebrica (A1-H8)

        Returns:
            Tupla (x_mm, y_mm) del centro della casella
        """
        # TODO: validare che la casella sia nel range A1-H8
        col = ord(square[0].upper()) - ord('A')  # 0-7
        row = int(square[1]) - 1  # 0-7

        x_mm = col * SQUARE_SIZE_MM + BOARD_OFFSET_MM
        y_mm = row * SQUARE_SIZE_MM + BOARD_OFFSET_MM

        return (x_mm, y_mm)

    def move_to_mm(self, target_x: float, target_y: float,
                   speed_mm_s: float = 50.0) -> None:
        """
        Muove il carrello alle coordinate XY specificate (cinematica CoreXY).

        In CoreXY:
          delta_A = delta_X + delta_Y
          delta_B = delta_X - delta_Y

        Args:
            target_x: Coordinata X target in mm
            target_y: Coordinata Y target in mm
            speed_mm_s: Velocita di movimento in mm/s
        """
        delta_x = target_x - self._x_mm
        delta_y = target_y - self._y_mm

        # Cinematica CoreXY
        delta_a = delta_x + delta_y
        delta_b = delta_x - delta_y

        # TODO: muovere i motori simultaneamente (threading o stepping alternato)
        # TODO: implementare accelerazione/decelerazione trapezoidale

        self.stepper_a.move_mm(delta_a, speed_mm_s)
        self.stepper_b.move_mm(delta_b, speed_mm_s)

        self._x_mm = target_x
        self._y_mm = target_y

        logger.info(f"Posizione raggiunta: ({target_x:.1f}, {target_y:.1f}) mm")

    def move_to_square(self, square: str, speed_mm_s: float = 50.0) -> None:
        """
        Muove il carrello al centro di una casella.

        Args:
            square: Casella in notazione algebrica (es. 'E4')
            speed_mm_s: Velocita di movimento
        """
        x, y = self.square_to_mm(square)
        logger.info(f"Movimento verso casella {square} -> ({x:.1f}, {y:.1f}) mm")
        self.move_to_mm(x, y, speed_mm_s)

    def move_piece(self, from_square: str, to_square: str,
                   speed_mm_s: float = 30.0) -> None:
        """
        Muove un pezzo da una casella all'altra tramite magnete.

        Sequenza:
        1. Vai sotto la casella di partenza
        2. (magnete attira il pezzo)
        3. Trascina il pezzo fino alla casella di destinazione

        Args:
            from_square: Casella di partenza (es. 'E2')
            to_square: Casella di arrivo (es. 'E4')
            speed_mm_s: Velocita durante il trascinamento
        """
        # TODO: implementare percorso che evita le altre caselle occupate
        # TODO: per catture, spostare prima il pezzo catturato nel cimitero

        logger.info(f"Spostamento pezzo: {from_square} -> {to_square}")

        self.move_to_square(from_square, speed_mm_s=80.0)  # Vai veloce alla partenza
        # TODO: pausa per aggancio magnetico
        self.move_to_square(to_square, speed_mm_s=speed_mm_s)  # Trascina lento

    def home(self) -> None:
        """
        Esegue la routine di homing — porta il carrello all'origine (0, 0).

        Usa gli endstop su GPIO4 (X) e GPIO25 (Y).
        """
        # TODO: muovere verso endstop X fino a trigger
        # TODO: muovere verso endstop Y fino a trigger
        # TODO: resettare posizione a (0, 0)

        self._x_mm = 0.0
        self._y_mm = 0.0
        self.stepper_a.reset_position()
        self.stepper_b.reset_position()

        logger.info("Homing completato — posizione (0, 0)")

    def cleanup(self) -> None:
        """Rilascia tutte le risorse."""
        self.stepper_a.cleanup()
        self.stepper_b.cleanup()
        logger.info("XYController cleanup completato")
