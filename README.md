# 👾 Retro Space Invaders in Python

A pixel-perfect, standalone recreation of the original 1978 arcade classic **Space Invaders**, built using `pygame-ce` for modern Python support (compatible with Python 3.14).

---

## 🚀 Game Features

* **Retro Visuals**: Real-time rendering of pixel-art sprites using custom bitmap arrays, mimicking the classic green, white, and red arcade aesthetics.
* **Classic Pacing & Difficulty**: Invader speed increases as they get shot down or descend closer to the bunker line.
* **Interactive Bunkers**: Four destructible shields that erode dynamically when hit by player or alien lasers.
* **Mystery Ship (UFO)**: A red flying saucer randomly spawns across the top, awarding up to 300 points if shot down.
* **Persistent Leaderboard**: Saves your top 10 scores localy in a `high_scores.json` file. Prompts name entry at the Game Over screen if a player secures a top score.
* **Extra Lives Milestone**: Start with 3 lives and earn 1 extra ship for every **1,000 points** scored.

---

## 🎮 Controls

| Action | Control Key |
|---|---|
| **Move Left** | `Left Arrow` or `A` |
| **Move Right** | `Right Arrow` or `D` |
| **Fire Laser** | `Spacebar` |
| **Start Game / Main Menu** | `Spacebar` |
| **Enter Initials** | Type characters `A-Z`, press `Backspace` to edit |
| **Submit High Score** | `Enter` / `Return` |

---

## 🛠️ Installation & Setup

Ensure you have **Python 3.10+** installed, then follow these steps:

### 1. Set Up the Virtual Environment
Navigate to the project folder, then create and activate a clean virtual environment:

```powershell
# Create environment
python -m venv .venv

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies
Install the community-maintained `pygame-ce` package:

```powershell
pip install -r requirements.txt
```

---

## 🚀 How to Run

Run the game directly from the command prompt inside the virtual environment:

```powershell
python main.py
```

---

## 📂 Project Structure

```text
space_invaders/
│
├── .venv/                  # Virtual environment
├── .gitignore              # Standard git ignore definitions
├── README.md               # Extensive project documentation
├── requirements.txt        # Package dependencies (pygame-ce)
├── high_scores.json        # Persistent JSON leaderboard data
└── main.py                 # Core game engine & rendering loops
```
