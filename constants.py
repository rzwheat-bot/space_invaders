# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60

# Colors (Retro Arcade Style)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Game States
STATE_START = "START"
STATE_PLAYING = "PLAYING"
STATE_ENTER_NAME = "ENTER_NAME"
STATE_LEADERBOARD = "LEADERBOARD"

# High Scores File
HIGH_SCORES_FILE = "high_scores.json"

# --- Sprite Bitmaps (Retro Pixel Art) ---
PLAYER_PIXELS = [
    "      11      ",
    "     1111     ",
    "     1111     ",
    " 111111111111 ",
    "11111111111111",
    "11111111111111",
    "11111111111111",
]

SQUID_PIXELS = [
    "   110011   ",
    "  11111111  ",
    " 1111111111 ",
    "111001100111",
    "111111111111",
    "  11011011  ",
    " 1100000011 ",
    "  11    11  ",
]

CRAB_PIXELS = [
    "  10000001  ",
    "   100001   ",
    "  11111111  ",
    " 1101110111 ",
    "111111111111",
    "1 11111111 1",
    "1 1      1 1",
    "   11  11   ",
]

OCTOPUS_PIXELS = [
    "    1111    ",
    " 1111111111 ",
    "111111111111",
    "111001100111",
    "111111111111",
    "  11100111  ",
    " 1101111011 ",
    "11      1111",
]

UFO_PIXELS = [
    "     111111     ",
    "   1111111111   ",
    "  111111111111  ",
    " 11011011011011 ",
    "1111111111111111",
    "  111      111  ",
]
