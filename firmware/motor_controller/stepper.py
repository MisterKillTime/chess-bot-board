"""
Stepper — Wrapper per il controllo di un singolo motore stepper NEMA 17 via driver A4988.

Gestisce: direzione, passi, velocità, enable/disable, protezione limiti meccanici.
Comunicazione tramite GPIO del Raspberry Pi.

Design: dependency injection del layer GPIO tramite `gpio_backend` per permettere
test mockabili su PC senza hardware reale.
"""

import time
import logging
from typing import Optional, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


# === ASTRAZIONE GPIO ===

@runtime_checkable
class GPIOBackend(Protocol):
    """Interfaccia per il layer GPIO — implementata da RPiGPIO o MockGPIO."""

    def setup_output(self, pin: int) -> None:
        """Configura un pin come output."""
        ...

    def setup_input(self, pin: int, pull_up: bool = False) -> None:
        """Configura un pin come input con pull-up/down opzionale."""
        ...

    def write(self, pin: int, value: bool) -> None:
        """Scrive un valore digitale su un pin."""
        ...

    def read(self, pin: int) -> bool:
        """Legge un valore digitale da un pin."""
        ...

    def cleanup(self, pin: int) -> None:
        """Rilascia un singolo pin."""
        ...


class RPiGPIO:
    """Backend GPIO reale per Raspberry Pi — usa RPi.GPIO."""

    def __init__(self):
        import RPi.GPIO as GPIO
        self._gpio = GPIO
        self._gpio.setmode(GPIO.BCM)
        self._gpio.setwarnings(False)

    def setup_output(self, pin: int) -> None:
        self._gpio.setup(pin, self._gpio.OUT, initial=self._gpio.LOW)

    def setup_input(self, pin: int, pull_up: bool = False) -> None:
        pud = self._gpio.PUD_UP if pull_up else self._gpio.PUD_DOWN
        self._gpio.setup(pin, self._gpio.IN, pull_up_down=pud)

    def write(self, pin: int, value: bool) -> None:
        self._gpio.output(pin, self._gpio.HIGH if value else self._gpio.LOW)

    def read(self, pin: int) -> bool:
        return bool(self._gpio.input(pin))

    def cleanup(self, pin: int) -> None:
        self._gpio.cleanup(pin)


class MockGPIO:
    """Backend GPIO mock per test su PC — logga le operazioni senza hardware."""

    def __init__(self):
        self._pin_states: dict[int, bool] = {}
        self._pin_modes: dict[int, str] = {}
        logger.debug("MockGPIO inizializzato — nessun hardware reale")

    def setup_output(self, pin: int) -> None:
        self._pin_modes[pin] = "OUTPUT"
        self._pin_states[pin] = False

    def setup_input(self, pin: int, pull_up: bool = False) -> None:
        self._pin_modes[pin] = "INPUT"
        self._pin_states[pin] = pull_up  # Simula pull-up/down

    def write(self, pin: int, value: bool) -> None:
        self._pin_states[pin] = value

    def read(self, pin: int) -> bool:
        return self._pin_states.get(pin, False)

    def cleanup(self, pin: int) -> None:
        self._pin_states.pop(pin, None)
        self._pin_modes.pop(pin, None)


def get_default_gpio() -> GPIOBackend:
    """Ritorna RPiGPIO su Raspberry Pi, MockGPIO su PC."""
    try:
        return RPiGPIO()
    except (ImportError, RuntimeError):
        logger.warning("RPi.GPIO non disponibile — uso MockGPIO")
        return MockGPIO()


# === ECCEZIONI ===

class StepperError(Exception):
    """Errore generico del motore stepper."""
    pass


class StepperTimeoutError(StepperError):
    """Il motore non ha completato il movimento nel tempo previsto."""
    pass


class StepperLimitError(StepperError):
    """Tentativo di movimento oltre i limiti meccanici."""
    pass


# === CLASSE PRINCIPALE ===

class Stepper:
    """Controlla un singolo motore stepper NEMA 17 tramite driver A4988."""

    # Limiti di sicurezza per il delay tra passi (microsecondi)
    MIN_STEP_DELAY_US = 100.0    # Velocità massima (~125 mm/s a 80 steps/mm)
    MAX_STEP_DELAY_US = 50000.0  # Velocità minima (~0.25 mm/s)

    def __init__(
        self,
        step_pin: int,
        dir_pin: int,
        enable_pin: int,
        steps_per_mm: float = 80.0,
        max_position_mm: float = 500.0,
        gpio: Optional[GPIOBackend] = None,
    ):
        """
        Inizializza il motore stepper.

        Args:
            step_pin: Pin GPIO per il segnale STEP
            dir_pin: Pin GPIO per il segnale DIR (direzione)
            enable_pin: Pin GPIO per ENABLE (LOW = attivo su A4988)
            steps_per_mm: Passi per millimetro (default 80 per 1/16 microstepping)
            max_position_mm: Limite massimo di corsa in mm (protezione meccanica)
            gpio: Backend GPIO — se None, auto-detect RPi vs PC
        """
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.steps_per_mm = steps_per_mm
        self.max_position_mm = max_position_mm

        self._gpio = gpio or get_default_gpio()
        self._position_steps: int = 0
        self._enabled: bool = False

        # Configura i pin come output
        self._gpio.setup_output(self.step_pin)
        self._gpio.setup_output(self.dir_pin)
        self._gpio.setup_output(self.enable_pin)

        # Motore disabilitato all'avvio (ENABLE HIGH = disabilitato su A4988)
        self._gpio.write(self.enable_pin, True)

        logger.info(
            f"Stepper inizializzato — STEP={step_pin}, DIR={dir_pin}, "
            f"EN={enable_pin}, steps/mm={steps_per_mm}"
        )

    def enable(self) -> None:
        """Abilita il motore (ENABLE LOW su A4988 = motore bloccato con coppia)."""
        self._gpio.write(self.enable_pin, False)  # LOW = attivo
        self._enabled = True
        logger.debug("Motore abilitato")

    def disable(self) -> None:
        """Disabilita il motore (ENABLE HIGH su A4988 = motore libero, nessuna coppia)."""
        self._gpio.write(self.enable_pin, True)  # HIGH = disabilitato
        self._enabled = False
        logger.debug("Motore disabilitato")

    @property
    def is_enabled(self) -> bool:
        """Ritorna True se il motore è abilitato."""
        return self._enabled

    def step(self, direction: bool, steps: int, delay_us: float = 500.0) -> int:
        """
        Esegue un numero di passi in una direzione.

        Args:
            direction: True = avanti (posizione aumenta), False = indietro
            steps: Numero di passi da eseguire (deve essere >= 0)
            delay_us: Ritardo tra passi in microsecondi (controlla la velocità)

        Returns:
            Numero di passi effettivamente eseguiti

        Raises:
            StepperError: Se il motore non è abilitato
            StepperLimitError: Se si supera il limite meccanico
            ValueError: Se steps < 0 o delay fuori range
        """
        if steps < 0:
            raise ValueError(f"steps deve essere >= 0, ricevuto {steps}")
        if steps == 0:
            return 0

        # Clamp del delay ai limiti di sicurezza
        delay_us = max(self.MIN_STEP_DELAY_US, min(delay_us, self.MAX_STEP_DELAY_US))

        if not self._enabled:
            raise StepperError("Motore non abilitato — chiama enable() prima di muovere")

        # Imposta la direzione
        self._gpio.write(self.dir_pin, direction)

        # Calcola il delay in secondi (metà per HIGH, metà per LOW = 1 ciclo completo)
        half_delay_s = delay_us / 2_000_000.0

        # Verifica limiti meccanici prima di partire
        sign = 1 if direction else -1
        target_steps = self._position_steps + (sign * steps)
        target_mm = target_steps / self.steps_per_mm

        if target_mm < 0 or target_mm > self.max_position_mm:
            raise StepperLimitError(
                f"Movimento fuori limite: posizione target {target_mm:.1f}mm "
                f"(range: 0 — {self.max_position_mm:.1f}mm)"
            )

        # Genera impulsi STEP
        executed = 0
        try:
            for _ in range(steps):
                self._gpio.write(self.step_pin, True)
                time.sleep(half_delay_s)
                self._gpio.write(self.step_pin, False)
                time.sleep(half_delay_s)
                executed += 1
                self._position_steps += sign
        except Exception as e:
            logger.error(
                f"Errore durante stepping dopo {executed}/{steps} passi: {e}"
            )
            raise StepperError(f"Stepping interrotto dopo {executed} passi: {e}") from e

        logger.debug(
            f"Step completati: dir={'FWD' if direction else 'REV'}, "
            f"passi={executed}, pos={self.position_mm:.2f}mm"
        )

        return executed

    def move_mm(self, distance_mm: float, speed_mm_s: float = 50.0) -> float:
        """
        Muove il motore di una distanza in millimetri.

        Args:
            distance_mm: Distanza in mm (positivo = avanti, negativo = indietro)
            speed_mm_s: Velocità in mm/s (verrà clamped ai limiti di sicurezza)

        Returns:
            Distanza effettivamente percorsa in mm

        Raises:
            StepperError: Se il motore non è abilitato
            StepperLimitError: Se si supera il limite meccanico
            ValueError: Se speed_mm_s <= 0
        """
        if speed_mm_s <= 0:
            raise ValueError(f"Velocità deve essere > 0, ricevuto {speed_mm_s}")

        if abs(distance_mm) < (1.0 / self.steps_per_mm):
            # Distanza inferiore a 1 step — non muovere
            return 0.0

        steps = abs(round(distance_mm * self.steps_per_mm))
        direction = distance_mm > 0
        delay_us = 1_000_000.0 / (speed_mm_s * self.steps_per_mm)

        executed = self.step(direction, steps, delay_us)
        actual_mm = executed / self.steps_per_mm
        if not direction:
            actual_mm = -actual_mm

        return actual_mm

    @property
    def position_mm(self) -> float:
        """Restituisce la posizione attuale in mm."""
        return self._position_steps / self.steps_per_mm

    @property
    def position_steps(self) -> int:
        """Restituisce la posizione attuale in passi."""
        return self._position_steps

    def reset_position(self) -> None:
        """Resetta la posizione a zero (da chiamare dopo homing)."""
        self._position_steps = 0
        logger.info("Posizione resettata a 0")

    def cleanup(self) -> None:
        """Disabilita il motore e rilascia le risorse GPIO."""
        self.disable()
        self._gpio.cleanup(self.step_pin)
        self._gpio.cleanup(self.dir_pin)
        self._gpio.cleanup(self.enable_pin)
        logger.info(
            f"Stepper cleanup completato — pin {self.step_pin}, "
            f"{self.dir_pin}, {self.enable_pin}"
        )

    def __repr__(self) -> str:
        return (
            f"Stepper(step={self.step_pin}, dir={self.dir_pin}, "
            f"en={self.enable_pin}, pos={self.position_mm:.2f}mm, "
            f"enabled={self._enabled})"
        )
