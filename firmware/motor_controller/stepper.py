"""
Stepper — Wrapper per il controllo di un singolo motore stepper NEMA 17 via driver A4988.

Gestisce: direzione, passi, velocita, enable/disable.
Comunicazione tramite GPIO del Raspberry Pi.
"""

import time
import logging

# TODO: importare RPi.GPIO o gpiozero (solo su Raspberry Pi)
# import RPi.GPIO as GPIO

logger = logging.getLogger(__name__)


class Stepper:
    """Controlla un singolo motore stepper tramite driver A4988."""

    def __init__(self, step_pin: int, dir_pin: int, enable_pin: int,
                 steps_per_mm: float = 80.0):
        """
        Inizializza il motore stepper.

        Args:
            step_pin: Pin GPIO per il segnale STEP
            dir_pin: Pin GPIO per il segnale DIR (direzione)
            enable_pin: Pin GPIO per ENABLE (LOW = attivo)
            steps_per_mm: Passi per millimetro (default 80 per 1/16 microstepping)
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.steps_per_mm = steps_per_mm
        self._position_steps = 0  # Posizione attuale in passi

        # TODO: inizializzare i pin GPIO come OUTPUT
        # TODO: impostare ENABLE su HIGH (motore disabilitato all'avvio)

        logger.info(f"Stepper inizializzato — STEP={step_pin}, DIR={dir_pin}, EN={enable_pin}")

    def enable(self) -> None:
        """Abilita il motore (ENABLE LOW)."""
        # TODO: GPIO.output(self.enable_pin, GPIO.LOW)
        logger.debug("Motore abilitato")

    def disable(self) -> None:
        """Disabilita il motore (ENABLE HIGH) — il motore gira libero."""
        # TODO: GPIO.output(self.enable_pin, GPIO.HIGH)
        logger.debug("Motore disabilitato")

    def step(self, direction: bool, steps: int, delay_us: float = 500.0) -> None:
        """
        Esegue un numero di passi in una direzione.

        Args:
            direction: True = avanti, False = indietro
            steps: Numero di passi da eseguire
            delay_us: Ritardo tra passi in microsecondi (controlla la velocita)
        """
        # TODO: impostare il pin DIR in base alla direzione
        # TODO: generare impulsi sul pin STEP con il delay specificato
        # TODO: aggiornare self._position_steps

        logger.debug(f"Step: dir={'FWD' if direction else 'REV'}, steps={steps}, delay={delay_us}us")

    def move_mm(self, distance_mm: float, speed_mm_s: float = 50.0) -> None:
        """
        Muove il motore di una distanza in millimetri.

        Args:
            distance_mm: Distanza in mm (positivo = avanti, negativo = indietro)
            speed_mm_s: Velocita in mm/s
        """
        steps = abs(int(distance_mm * self.steps_per_mm))
        direction = distance_mm > 0
        delay_us = 1_000_000 / (speed_mm_s * self.steps_per_mm)

        self.step(direction, steps, delay_us)

    @property
    def position_mm(self) -> float:
        """Restituisce la posizione attuale in mm."""
        return self._position_steps / self.steps_per_mm

    def reset_position(self) -> None:
        """Resetta la posizione a zero (dopo homing)."""
        self._position_steps = 0
        logger.info("Posizione resettata a 0")

    def cleanup(self) -> None:
        """Rilascia le risorse GPIO."""
        self.disable()
        # TODO: GPIO.cleanup() per i pin usati
        logger.info("Stepper cleanup completato")
