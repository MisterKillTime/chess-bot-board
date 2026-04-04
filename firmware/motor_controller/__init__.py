"""
Motor Controller — Modulo firmware per il controllo dei motori stepper.

Gestisce il sistema CoreXY tramite driver A4988 e NEMA 17.
Sottosistema del progetto chess-bot-board.
"""

from .stepper import Stepper
from .xy_controller import XYController
from .calibration import CalibrationRoutine
