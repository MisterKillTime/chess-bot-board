"""
Config — Costanti e configurazione globale del progetto chess-bot-board.

Contiene: dimensioni scacchiera, pin GPIO, parametri motori, percorso Stockfish.
"""

# === DIMENSIONI SCACCHIERA ===
BOARD_SIZE_MM = 400.0        # Lato scacchiera in mm
SQUARE_SIZE_MM = 50.0        # Lato singola casella in mm
SQUARE_CENTER_OFFSET = 25.0  # Offset dal bordo al centro casella

# === COORDINATE ===
# Casella A1 = (0, 0) mm — angolo in basso a sinistra
# Casella H8 = (350, 350) mm — angolo in alto a destra
ORIGIN_X_MM = 0.0
ORIGIN_Y_MM = 0.0

# === MOTORI STEPPER ===
STEPS_PER_MM = 80.0  # NEMA17 1.8deg, A4988 1/16 microstepping, puleggia GT2 20T
DEFAULT_SPEED_MM_S = 50.0      # Velocita di movimento standard
DRAG_SPEED_MM_S = 30.0         # Velocita durante trascinamento pezzo
HOMING_SPEED_MM_S = 10.0       # Velocita durante homing (lenta per precisione)

# === PIN GPIO — STEPPER A (asse X+Y) ===
STEPPER_A_STEP_PIN = 17
STEPPER_A_DIR_PIN = 18
STEPPER_A_ENABLE_PIN = 27

# === PIN GPIO — STEPPER B (asse X-Y) ===
STEPPER_B_STEP_PIN = 22
STEPPER_B_DIR_PIN = 23
STEPPER_B_ENABLE_PIN = 24

# === PIN GPIO — MULTIPLEXER 1 (righe 0-3, caselle A1-D8) ===
MUX1_S0_PIN = 5
MUX1_S1_PIN = 6
MUX1_S2_PIN = 13
MUX1_S3_PIN = 19
MUX1_SIG_PIN = 26

# === PIN GPIO — MULTIPLEXER 2 (righe 4-7, caselle E1-H8) ===
MUX2_S0_PIN = 5   # Condivisi con MUX1
MUX2_S1_PIN = 6
MUX2_S2_PIN = 13
MUX2_S3_PIN = 19
MUX2_SIG_PIN = 21  # Pin SIG diverso

# === PIN GPIO — ENDSTOP ===
HOME_X_PIN = 4
HOME_Y_PIN = 25

# === STOCKFISH ===
STOCKFISH_PATH = "/usr/games/stockfish"  # Percorso su RPi OS
STOCKFISH_DEPTH = 15           # Profondita di analisi default
STOCKFISH_TIME_LIMIT_S = 2.0   # Tempo massimo per mossa in secondi
STOCKFISH_SKILL_LEVEL = 10     # Livello 1-20 (default medio)

# === MODALITA DI GIOCO ===
class GameMode:
    IA_MODE = "ia"              # Umano vs Stockfish
    MULTIPLAYER_MODE = "multi"  # Due giocatori fisici
    PUZZLE_MODE = "puzzle"      # Risolvi posizione (futura)

# === CIMITERO (zona pezzi catturati) ===
# Coordinate mm delle posizioni di parcheggio per pezzi catturati
CEMETERY_WHITE_X_MM = -40.0   # A sinistra della scacchiera
CEMETERY_BLACK_X_MM = 440.0   # A destra della scacchiera

# === LOGGING ===
LOG_FILE = "logs/chess-bot.log"
LOG_LEVEL = "DEBUG"
