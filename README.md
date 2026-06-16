<div align="center">

# 🔥 THALANOR: ZATOPIONE KRONIKI

### *Dark Fantasy Bomberman — Python + Pygame*

**Wersja: Final v3**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![License](https://img.shields.io/badge/Licencja-MIT-green)
![Status](https://img.shields.io/badge/Status-Final-brightgreen)
![Lines](https://img.shields.io/badge/Linie%20kodu-~1380-informational)

```
Cisza w tym lesie nie jest przypadkowa.
```

</div>

---

> 🇬🇧 **[English version below](#-thalanor-sunken-chronicles)**

---

## 🇵🇱 Wersja Polska

### 📖 O grze

**THALANOR: Zatopione Kroniki** to gra zręcznościowa w stylu *Bomberman*, osadzona w dark-fantasy świecie Thalanoru. Gracz przemierza trzy areny o narastającym poziomie trudności — Mroczny Las, Lochy Zatopionej Cytadeli i Katakumby Mroku — stawiając bomby, zbierając ulepszenia i eliminując przeciwników kierowanych przez AI.

Projekt zrealizowany w ramach przedmiotu **Projektowanie Gier**. Napisany od podstaw w Pythonie z użyciem Pygame — bez gotowych silników ani edytorów graficznych.

### 🎮 Sterowanie

| Klawisz | Akcja |
|---|---|
| `W A S D` lub strzałki | Ruch (do wyboru w opcjach) |
| `Spacja` | Postaw bombę |
| `ESC` | Pauza / wyjście |
| `Enter` | Potwierdź |

### 🕹️ Mechaniki

| Mechanika | Opis |
|---|---|
| 💣 **Bomby** | Eksplozja w krzyż, 3s opóźnienie, zasięg od 1 do 6 kafelków |
| 🔥 **Ogień** | Animowane efekty cząsteczkowe, precyzyjna detekcja trafień |
| ⬆️ **Power-upy** | Więcej bomb, większy zasięg, 5 poziomów prędkości |
| 👾 **AI wrogów** | Szkielety i orki — algorytm BFS (pościg i ucieczka przed bombami) |
| ❤️ **Życia** | 3 życia, klatki nietykalności po trafieniu, ulepszenia zachowane po trafieniu |
| 🗺️ **3 rundy** | Odrębna grafika i lore dla każdej lokacji |
| 🏆 **Ranking** | TOP 10 wyników zapisywanych w `ranking.json` |
| 🎚️ **Opcje** | Pełny ekran, sterowanie, trudność, głośność |
| 🎵 **Audio** | Muzyka w tle + proceduralne SFX generowane przez numpy |

### 🌍 Rundy

| Runda | Lokacja | Motto |
|---|---|---|
| 1 | Mroczny Las — Przeklęta Puszcza Yrendal | *„Cisza w tym lesie nie jest przypadkowa."* |
| 2 | Lochy Zatopionej Cytadeli — Podziemia Twierdzy Vrethkan | *„Gdzie kości śpiewają do ciemności..."* |
| 3 | Katakumby Mroku — Krypty Zaginionych | *„Nikt stąd nie powrócił żywy..."* |

### 🚀 Uruchomienie

#### Opcja 1 — Plik `.exe` (Windows, bez instalacji)

Pobierz `THALANOR.exe` ze strony **[Releases](https://github.com/sudomakemeadmin/thalanor-bomberman/releases/latest)** i uruchom. Przy pierwszym uruchomieniu Windows Defender może wyświetlić ostrzeżenie — kliknij „Więcej informacji" → „Uruchom mimo to".

#### Opcja 2 — Z kodu źródłowego

**Wymagania:** Python 3.10+, biblioteka `pygame`. `numpy` opcjonalnie (proceduralne SFX).

```bash
git clone https://github.com/sudomakemeadmin/thalanor-bomberman.git
cd thalanor-bomberman
pip install pygame numpy
python thalanor_final.py
```

### 📁 Struktura projektu

```
thalanor-bomberman/
├── thalanor_final.py          # Kod źródłowy (~1380 linii)
├── DOKUMENTACJA_PROJEKTU.md   # Pełna dokumentacja techniczna
└── assets2/
    ├── player/                # Sprite'y gracza (4 klatki animacji)
    ├── skeleton/              # Sprite'y szkieleta
    ├── orc/                   # Sprite'y orka
    ├── tiles/                 # Tekstury kafelków (runda 1 i 2/3)
    ├── powerups/              # Ikony ulepszeń
    └── hud/                   # Cyfry, ikony, logo
```

> Plik wykonywalny `.exe` dostępny w zakładce [Releases](https://github.com/sudomakemeadmin/thalanor-bomberman/releases/latest).

### 🏗️ Architektura

```
Game  (silnik — maszyna 15 stanów, rendering, logika)
 ├── Player   (gracz: pozycja, życia, ulepszenia)
 ├── Enemy    (szkielet / ork — AI BFS)
 ├── Bomb     (timer, zasięg, eksplozja)
 ├── PowerUp  (ulepszenia na planszy)
 └── Particle (efekty cząsteczkowe)
```

Zastosowane techniki: **BFS** (AI wrogów), **maszyna stanów** (15 ekranów), **JSON** (ranking), **proceduralne audio** (numpy + pygame.mixer), **PyInstaller** (`.exe`).

### 👥 Autorzy

| Autor | Zakres |
|---|---|
| **Adam Ostrowski** | Audio (muzyka + proceduralne SFX), efekty ognia i cząsteczek, ranking, ekrany pomocnicze, HUD, sprite'y gracza |
| **Arkadiusz Nowiszewski** | AI wrogów (BFS), mechanika bomb, generowanie mapy, klasy Enemy/Player/Bomb/PowerUp, grafika tła i poziomów |
| Wspólnie | Silnik gry, maszyna stanów, balans rozgrywki |

---
---

<div align="center">

## 🇬🇧 THALANOR: SUNKEN CHRONICLES

### *Dark Fantasy Bomberman — Python + Pygame*

</div>

### 📖 About

**THALANOR: Sunken Chronicles** is a Bomberman-style arcade game set in the dark fantasy world of Thalanor. Built from scratch in Python using Pygame — no game engines or visual editors.

The player battles through three increasingly difficult arenas (Dark Forest, Sunken Citadel Dungeons, Catacombs of Gloom), placing bombs, collecting power-ups and eliminating AI-driven enemies.

University project for a **Game Design** course.

### 🚀 Quick Start

```bash
git clone https://github.com/sudomakemeadmin/thalanor-bomberman.git
cd thalanor-bomberman
pip install pygame numpy
python thalanor_final.py
```

Or download `thalanor_final.exe` for Windows — no installation required.

### 🕹️ Controls

`W/A/S/D` or arrow keys — move &nbsp;|&nbsp; `Space` — place bomb &nbsp;|&nbsp; `ESC` — pause

### 🏗️ Architecture

6 classes: `Game` (state machine, 15 screens) · `Player` · `Enemy` (BFS AI) · `Bomb` · `PowerUp` · `Particle`

### 👥 Authors

- **Adam Ostrowski** — audio system, fire/particle effects, leaderboard, HUD, player sprites
- **Arkadiusz Nowiszewski** — enemy AI (BFS), bomb mechanics, map generation, gameplay classes, level art

### 📄 License

MIT

---

<div align="center">

*Cisza w tym lesie nie jest przypadkowa.*

🔥

</div>
