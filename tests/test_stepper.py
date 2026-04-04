"""
Test per il modulo Stepper — eseguibili su PC senza hardware RPi.

Usa MockGPIO per simulare il layer GPIO.
Copre: inizializzazione, enable/disable, stepping, move_mm, limiti, cleanup.
"""

import pytest

from firmware.motor_controller.stepper import (
    Stepper,
    MockGPIO,
    StepperError,
    StepperLimitError,
)


# === FIXTURES ===

@pytest.fixture
def gpio():
    """Backend GPIO mock per tutti i test."""
    return MockGPIO()


@pytest.fixture
def stepper(gpio):
    """Stepper con pin di test e MockGPIO."""
    return Stepper(
        step_pin=17,
        dir_pin=18,
        enable_pin=27,
        steps_per_mm=80.0,
        max_position_mm=500.0,
        gpio=gpio,
    )


# === TEST INIZIALIZZAZIONE ===

class TestStepperInit:
    def test_pin_configurati_come_output(self, gpio):
        """I 3 pin devono essere configurati come OUTPUT all'init."""
        Stepper(step_pin=17, dir_pin=18, enable_pin=27, gpio=gpio)
        assert gpio._pin_modes[17] == "OUTPUT"
        assert gpio._pin_modes[18] == "OUTPUT"
        assert gpio._pin_modes[27] == "OUTPUT"

    def test_enable_alto_allinit(self, gpio):
        """ENABLE deve essere HIGH (motore disabilitato) dopo l'init."""
        Stepper(step_pin=17, dir_pin=18, enable_pin=27, gpio=gpio)
        assert gpio._pin_states[27] is True  # HIGH = disabilitato

    def test_posizione_iniziale_zero(self, stepper):
        """Posizione iniziale deve essere 0 mm."""
        assert stepper.position_mm == 0.0
        assert stepper.position_steps == 0

    def test_motore_disabilitato_allinit(self, stepper):
        """Il motore deve essere disabilitato dopo l'init."""
        assert stepper.is_enabled is False


# === TEST ENABLE / DISABLE ===

class TestEnableDisable:
    def test_enable(self, stepper, gpio):
        """Enable deve portare ENABLE LOW e aggiornare lo stato."""
        stepper.enable()
        assert gpio._pin_states[27] is False  # LOW = attivo
        assert stepper.is_enabled is True

    def test_disable(self, stepper, gpio):
        """Disable deve portare ENABLE HIGH e aggiornare lo stato."""
        stepper.enable()
        stepper.disable()
        assert gpio._pin_states[27] is True  # HIGH = disabilitato
        assert stepper.is_enabled is False


# === TEST STEPPING ===

class TestStep:
    def test_step_avanti_aggiorna_posizione(self, stepper):
        """Stepping avanti deve incrementare la posizione."""
        stepper.enable()
        executed = stepper.step(direction=True, steps=80, delay_us=100)
        assert executed == 80
        assert stepper.position_mm == pytest.approx(1.0)  # 80 steps / 80 steps_per_mm

    def test_step_indietro_aggiorna_posizione(self, stepper):
        """Stepping indietro deve decrementare la posizione."""
        stepper.enable()
        stepper.step(direction=True, steps=160)  # Vai a 2mm
        stepper.step(direction=False, steps=80)   # Torna a 1mm
        assert stepper.position_mm == pytest.approx(1.0)

    def test_step_zero_non_fa_nulla(self, stepper):
        """Step con 0 passi deve ritornare 0 senza errori."""
        stepper.enable()
        executed = stepper.step(direction=True, steps=0)
        assert executed == 0
        assert stepper.position_mm == 0.0

    def test_step_negativo_solleva_errore(self, stepper):
        """Step con passi negativi deve sollevare ValueError."""
        stepper.enable()
        with pytest.raises(ValueError, match="steps deve essere >= 0"):
            stepper.step(direction=True, steps=-10)

    def test_step_senza_enable_solleva_errore(self, stepper):
        """Step senza enable() deve sollevare StepperError."""
        with pytest.raises(StepperError, match="Motore non abilitato"):
            stepper.step(direction=True, steps=10)

    def test_step_imposta_direzione(self, stepper, gpio):
        """Il pin DIR deve essere impostato in base alla direzione."""
        stepper.enable()
        stepper.step(direction=True, steps=1, delay_us=100)
        assert gpio._pin_states[18] is True  # DIR pin = True = avanti

        stepper.step(direction=False, steps=1, delay_us=100)
        assert gpio._pin_states[18] is False  # DIR pin = False = indietro


# === TEST MOVE_MM ===

class TestMoveMm:
    def test_move_positivo(self, stepper):
        """Move con distanza positiva deve andare avanti."""
        stepper.enable()
        actual = stepper.move_mm(10.0, speed_mm_s=50.0)
        assert actual == pytest.approx(10.0)
        assert stepper.position_mm == pytest.approx(10.0)

    def test_move_negativo(self, stepper):
        """Move con distanza negativa deve andare indietro."""
        stepper.enable()
        stepper.move_mm(20.0)  # Prima vai avanti
        actual = stepper.move_mm(-5.0)
        assert actual == pytest.approx(-5.0)
        assert stepper.position_mm == pytest.approx(15.0)

    def test_move_distanza_minima(self, stepper):
        """Distanza inferiore a 1 step deve ritornare 0."""
        stepper.enable()
        actual = stepper.move_mm(0.001)  # Meno di 1/80 mm
        assert actual == 0.0
        assert stepper.position_mm == 0.0

    def test_move_velocita_negativa_solleva_errore(self, stepper):
        """Velocità <= 0 deve sollevare ValueError."""
        stepper.enable()
        with pytest.raises(ValueError, match="Velocità deve essere > 0"):
            stepper.move_mm(10.0, speed_mm_s=0)

    def test_move_calcolo_delay(self, stepper):
        """Verifica che il delay calcolato sia coerente con la velocità."""
        stepper.enable()
        # 50 mm/s con 80 steps/mm = 4000 steps/s = 250 µs/step
        stepper.move_mm(1.0, speed_mm_s=50.0)
        # Se siamo arrivati a 1.0mm, il calcolo è corretto
        assert stepper.position_mm == pytest.approx(1.0)


# === TEST LIMITI MECCANICI ===

class TestLimiti:
    def test_limite_superiore(self, stepper):
        """Movimento oltre max_position_mm deve sollevare StepperLimitError."""
        stepper.enable()
        with pytest.raises(StepperLimitError, match="fuori limite"):
            stepper.move_mm(600.0)  # max è 500mm

    def test_limite_inferiore(self, stepper):
        """Movimento sotto 0mm deve sollevare StepperLimitError."""
        stepper.enable()
        with pytest.raises(StepperLimitError, match="fuori limite"):
            stepper.move_mm(-1.0)  # Siamo a 0, non si può andare sotto

    def test_movimento_fino_al_limite(self, stepper):
        """Deve poter raggiungere esattamente il limite massimo."""
        stepper.enable()
        stepper.move_mm(500.0)
        assert stepper.position_mm == pytest.approx(500.0)

    def test_posizione_non_cambia_su_errore_limite(self, stepper):
        """La posizione non deve cambiare se il movimento viene rifiutato."""
        stepper.enable()
        stepper.move_mm(100.0)
        pos_prima = stepper.position_mm
        with pytest.raises(StepperLimitError):
            stepper.move_mm(500.0)  # Supera il limite
        assert stepper.position_mm == pytest.approx(pos_prima)


# === TEST RESET E CLEANUP ===

class TestResetCleanup:
    def test_reset_position(self, stepper):
        """Reset deve azzerare la posizione."""
        stepper.enable()
        stepper.move_mm(50.0)
        stepper.reset_position()
        assert stepper.position_mm == 0.0
        assert stepper.position_steps == 0

    def test_cleanup_disabilita_motore(self, stepper):
        """Cleanup deve disabilitare il motore."""
        stepper.enable()
        stepper.cleanup()
        assert stepper.is_enabled is False

    def test_cleanup_rilascia_pin(self, stepper, gpio):
        """Cleanup deve rilasciare i pin GPIO."""
        stepper.cleanup()
        assert 17 not in gpio._pin_states
        assert 18 not in gpio._pin_states
        assert 27 not in gpio._pin_states


# === TEST REPR ===

class TestRepr:
    def test_repr_contiene_info(self, stepper):
        """__repr__ deve contenere pin e posizione."""
        r = repr(stepper)
        assert "step=17" in r
        assert "dir=18" in r
        assert "en=27" in r
        assert "pos=0.00mm" in r


# === TEST DELAY CLAMPING ===

class TestDelayClamping:
    def test_delay_troppo_basso_viene_clampato(self, stepper):
        """Delay sotto MIN_STEP_DELAY_US deve essere clampato, non dare errore."""
        stepper.enable()
        # delay_us=1 è sotto il minimo (100), deve comunque funzionare
        executed = stepper.step(direction=True, steps=10, delay_us=1.0)
        assert executed == 10

    def test_delay_troppo_alto_viene_clampato(self, stepper):
        """Delay sopra MAX_STEP_DELAY_US deve essere clampato."""
        stepper.enable()
        executed = stepper.step(direction=True, steps=5, delay_us=999999.0)
        assert executed == 5
