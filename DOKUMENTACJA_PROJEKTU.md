# THALANOR: ZATOPIONE KRONIKI
## Dokumentacja projektu zaliczeniowego

---

| | |
|---|---|
| **Przedmiot** | Projektowanie Gier |
| **Prowadzący** | mgr Artur Karwatka |
| **Autorzy** | Adam Ostrowski, Arkadiusz Nowiszewski |
| **Wersja** | Final v3 |
| **Język i technologia** | Python 3, Pygame |
| **Platforma docelowa** | Windows (plik `.exe`) |

---

## 1. Opis projektu

THALANOR: Zatopione Kroniki to gra zręcznościowa inspirowana klasycznym *Bombermanem*, osadzona w dark-fantasy świecie Thalanoru. Projekt został napisany od podstaw w języku Python z użyciem biblioteki Pygame — bez gotowych silników ani edytorów graficznych takich jak Unity czy Godot. Cała logika gry, grafika HUD i efekty wizualne zostały zrealizowane w kodzie.

Gracz porusza się po planszy podzielonej na kafelki (siatka 19×11), rozstawia bomby, niszczy przeszkody, zbiera ulepszenia i eliminuje wrogów kierowanych przez AI. Gra przebiega przez trzy rundy o narastającym poziomie trudności, z odrębną oprawą graficzną i fabularnym tłem dla każdej z nich.

---

## 2. Uruchomienie

### Wersja skompilowana (zalecana)

Plik `thalanor_final.exe` uruchamia grę bezpośrednio, bez konieczności instalowania Pythona ani żadnych bibliotek. Przy pierwszym uruchomieniu Windows Defender może wyświetlić ostrzeżenie — należy kliknąć „Więcej informacji", a następnie „Uruchom mimo to".

### Uruchomienie z kodu źródłowego

Wymagania: Python 3.10 lub nowszy, biblioteka `pygame`. Biblioteka `numpy` jest opcjonalna — bez niej gra działa poprawnie, ale bez proceduralnych efektów dźwiękowych.

```
pip install pygame numpy
python thalanor_final.py
```

### Sterowanie

| Klawisz | Akcja |
|---|---|
| W / A / S / D lub strzałki | Ruch (do wyboru w opcjach) |
| Spacja | Postawienie bomby |
| ESC | Pauza / wyjście do menu |
| Enter | Potwierdzenie wyboru |

---

## 3. Struktura plików

```
final_package/
├── thalanor_final.py          — kod źródłowy gry (ok. 1380 linii)
├── thalanor_final.exe         — skompilowana wersja dla Windows
├── ranking.json               — zapis rankingu TOP 10 (generowany przy pierwszym uruchomieniu)
└── assets2/
    ├── player/                — sprite'y gracza (walk_0..3.png, 4 klatki animacji)
    ├── skeleton/              — sprite'y szkieleta (walk_0..3.png)
    ├── orc/                   — sprite'y orka (walk_0..3.png)
    ├── tiles/                 — tekstury podłogi i ścian dla rundy 1 i 2/3
    │     floor.png, floor_grid.png, hard.png, soft.png
    │     floor_r2.png, floor_grid_r2.png, hard_r2.png, soft_r2.png
    ├── powerups/              — ikony ulepszeń (bomb_extra, range_up, speed_up)
    ├── hud/                   — cyfry wyników (digit_0..9), ikony paska HUD, logo
    ├── music/                 — pliki muzyki i efektów dźwiękowych (opcjonalne)
    ├── menu_main.png          — grafika tytułowa menu
    ├── menu_bg.png            — tło menu
    ├── menu_bg_dark.png       — przyciemnione tło menu
    ├── round1_screen.png      — ekran przejścia do rundy 1
    ├── round2_screen.png      — ekran przejścia do rundy 2
    ├── victory_scaled.png     — ekran zwycięstwa
    ├── game_over_scaled.png   — ekran porażki
    └── demo_end.png           — ekran zakończenia demo
```

Łącznie: 49 plików graficznych.

---

## 4. Technologie i uzasadnienie wyboru

**Python 3** — język projektu. Zapewnia szybki cykl implementacji i czytelną składnię, co przy projekcie zaliczeniowym z ograniczonym czasem ma istotne znaczenie.

**Pygame** — biblioteka do tworzenia gier 2D. Dostarcza pętlę gry, obsługę zdarzeń klawiatury, rendering grafiki i zarządzanie dźwiękiem w jednym miejscu. Wybór Pygame zamiast gotowego silnika (Unity, Godot) był świadomy — zależało nam na pełnej kontroli nad kodem i możliwości zademonstrowania własnej implementacji mechanik gry.

**numpy (opcjonalny)** — używany wyłącznie do generowania proceduralnych efektów dźwiękowych. Funkcje takie jak `snd_boom()` czy `snd_powerup()` tworzą surowe próbki audio matematycznie (fale sinusoidalne, szum, obwiednia zaniku), co eliminuje zależność od zewnętrznych plików audio. Jeśli numpy nie jest dostępny, gra działa bez dźwięku.

**JSON** — format zapisu rankingu. Wbudowany w Pythona, czytelny dla człowieka, wystarczający do prostego zapisu listy wyników.

**PyInstaller** — narzędzie do kompilacji do pliku `.exe`. Pakuje kod źródłowy razem z grafikami i wymaganymi bibliotekami w jeden plik wykonywalny. W kodzie obsługa ścieżek odbywa się przez `sys._MEIPASS` (folder tymczasowy z zasobami) i `SAVE_DIR` (katalog obok `.exe` do zapisu rankingu).

---

## 5. Architektura — klasy

Projekt oparty jest na sześciu klasach.

```
Game  (silnik gry — maszyna stanów, rendering, logika)
 ├── Player   (gracz: pozycja, życia, ulepszenia)
 ├── Enemy    (szkielet / ork — AI oparte na BFS)
 ├── Bomb     (bomba: timer, zasięg, eksplozja)
 ├── PowerUp  (ulepszenie na planszy)
 └── Particle (cząsteczka efektu wizualnego)
```

**Particle** — reprezentuje pojedynczą iskrę lub element efektu ognia. Używa `__slots__` dla oszczędności pamięci, gdyż obiektów tej klasy może być w danej chwili kilkadziesiąt.

**Bomb** — przechowuje pozycję na siatce, odliczanie do wybuchu (`timer`), zasięg eksplozji (`rng` — kopiowany z gracza w momencie postawienia) oraz stan wybuchu: listę płonących kafelków i pozostały czas ognia.

**PowerUp** — ulepszenie leżące na planszy po zniszczeniu miękkiej ściany. Typ losowany spośród trzech wariantów: `bomb_extra`, `range_up`, `speed_up`.

**Enemy** — szkielet lub ork. Oprócz pozycji na siatce posiada pozycję wizualną (`vx`, `vy`) umożliwiającą płynną animację ruchu między kafelkami. Każdy egzemplarz otrzymuje losowy offset interwału podejmowania decyzji i nieznacznie różniącą się prędkość, dzięki czemu skupina wrogów porusza się naturalnie, nie jak jeden obiekt.

**Player** — gracz. Przechowuje liczbę żyć (start: 3), klatki nietykalności po trafieniu (`inv`), aktualną i maksymalną liczbę bomb, zasięg eksplozji oraz poziom prędkości (1–5).

**Game** — centralny silnik. Zawiera maszynę stanów z 15 ekranami, główną pętlę renderingu i aktualizacji, definicję plansz, AI wrogów i wszystkie ekrany (menu, ranking, opcje, pauza itd.).

---

## 6. Kluczowe mechaniki

### Plansza i generowanie mapy

Plansza ma rozmiar 19 × 11 kafelków (kafelek 56 × 56 px, okno 1200 × 820 px). Funkcja `gen_map()` losowo rozmieszcza ściany twarde (niezniszczalne) i miękkie (do zniszczenia bombą), gwarantując wolną przestrzeń startową w narożniku gracza.

### Bomby i eksplozje

Bomba wybucha po 3 sekundach (90 klatek przy 30 FPS). Eksplozja rozchodzi się w czterech kierunkach do zasięgu `rng` kafelków. Ściana twarda zatrzymuje ogień; ściana miękka zostaje zniszczona. Po zniszczeniu miękkiej ściany może pojawić się ulepszenie.

Obrażenia od ognia wykrywane są na podstawie procentowego pokrycia kafla ognia przez wizualną pozycję jednostki (`_tile_overlap`) — trafienie następuje przy pokryciu co najmniej 25%. Pole ognia pozostaje aktywne przez `FIRE_DMG_FRAMES` klatek po wybuchu, co zapewnia precyzję odpowiadającą temu, co gracz widzi na ekranie. Trafienie przez ogień odbiera jedno życie, ale nie resetuje zdobytych ulepszeń.

### Sztuczna inteligencja wrogów

Każdy wróg co kilka klatek podejmuje decyzję na podstawie algorytmu BFS (przeszukiwanie wszerz):

- jeśli stoi w zasięgu nadchodzącej eksplozji — funkcja `flee()` wskazuje bezpieczny kierunek ucieczki,
- w pozostałych przypadkach — funkcja `bfs()` wyznacza najkrótszą ścieżkę do gracza po siatce planszy, z opcją unikania pól zagrożonych bombami.

Interwał decyzji i prędkość są dla każdego wroga losowo przesunięte, co zapobiega synchronizacji ruchu grupy.

### Ulepszenia (power-upy)

| Ulepszenie | Efekt |
|---|---|
| bomb_extra | +1 do maksymalnej liczby bomb stawianych jednocześnie |
| range_up | +1 do zasięgu eksplozji (max. 6) |
| speed_up | +1 poziom prędkości (5 poziomów: 5.0 → 5.7 → 6.4 → 7.2 → 8.2 px/klatkę) |

Ulepszenia zachowywane są między rundami — resetują się tylko przy starcie nowej gry.

### Dźwięk proceduralny

Efekty dźwiękowe (eksplozja, zebranie power-upa, śmierć wroga, ukończenie rundy) generowane są przez funkcje `snd_*` przy użyciu biblioteki numpy. Każda funkcja zwraca surową tablicę próbek audio, z której Pygame tworzy obiekt dźwiękowy. Jeśli numpy lub mikser audio nie są dostępne, funkcje zwracają `None`, a gra kontynuuje działanie bez dźwięku.

### Maszyna stanów

Pole `self.state` w klasie `Game` determinuje aktywny ekran i zachowanie pętli głównej. Gra obsługuje 15 stanów: `menu`, `countdown`, `play`, `round_title`, `clear`, `over`, `pause`, `pause_confirm`, `name_input`, `ranking`, `opcje`, `o_projekcie`, `round1_intro`, `demo_end`, `fade_out`.

### Ranking

Po zakończeniu gry (zwycięstwo lub utrata wszystkich żyć) gracz wpisuje swoje imię. Wynik trafia do pliku `ranking.json` — lista jest sortowana malejąco i ograniczona do 10 pozycji.

---

## 7. Rundy

| Runda | Nazwa | Lokacja | Motto |
|---|---|---|---|
| 1 | Mroczny Las | Przeklęta Puszcza Yrendal | „Cisza w tym lesie nie jest przypadkowa." |
| 2 | Lochy Zatopionej Cytadeli | Podziemia Twierdzy Vrethkan | „Gdzie kości śpiewają do ciemności..." |
| 3 | Katakumby Mroku | Krypty Zaginionych | „Nikt stąd nie powrócił żywy..." |

Liczba wrogów rośnie z każdą rundą: runda 1 — 5 przeciwników, runda 2 — 7, runda 3 — 9 (górny limit: 16). Od rundy 2 mogą pojawiać się orki (45% szans) — wolniejsze niż szkielety, ale z innym profilem zachowania AI.

---

## 8. Podział pracy

### Adam Ostrowski

- System audio: inicjalizacja miksera, funkcje generujące proceduralne efekty dźwiękowe (`snd_place`, `snd_boom`, `snd_death`, `snd_powerup`, `snd_win`), wczytywanie plików muzycznych z fallbackiem na dźwięk proceduralny, regulacja głośności.
- Efekty wizualne: klasa `Particle`, animacje ognia i eksplozji (`fire_c`, `fire_h`, `fire_v`), animowana runa pod bombą (`draw_rune`), aktualizacja cząsteczek (`_upd_parts`).
- Rysowanie postaci i HUD: funkcje `draw_heart` (serduszka życia rysowane wektorowo) i `blit_char` (animowana postać z efektem poświaty i odbiciem lewo/prawo).
- System rankingu: `load_ranking`, `save_to_ranking`, ekran TOP 10 (`_draw_ranking`), ekran wpisywania imienia (`_draw_name_input`).
- Ekrany pomocnicze: „O projekcie" (`_draw_o_projekcie`), opcje (`_draw_opcje`), przełączanie pełnego ekranu (`_toggle_fullscreen`).
- Obsługa ścieżek dla wersji `.exe`: konfiguracja `sys._MEIPASS` i `SAVE_DIR`.
- Grafika: sprite'y gracza, ikony i cyfry HUD.

### Arkadiusz Nowiszewski

- Klasy gameplayowe: `Bomb`, `PowerUp`, `Enemy`, `Player`.
- Wczytywanie zasobów: `load_img`, `load_assets`.
- Generowanie mapy: `gen_map`, `_spawn`.
- Sztuczna inteligencja wrogów: `bfs`, `flee`, `move_to`, `_blast`, `_think`, `_upd_enemies`.
- Mechanika bomb i obrażeń: `_bomb`, `_explode`, `_fire_dmg`, `_tile_overlap`, `_take_damage`, `_check_powerups`, `_upd_bombs`.
- Winieta ekranu: `make_vignette`.
- Grafika: tła ekranów, grafiki rund, tekstury kafelków dla obu zestawów.
- Ekrany: menu główne (`_draw_menu`), tytuły rund (`_draw_round_title`), rysowanie wrogów (`_draw_e`), wybór tekstur (`_tiles`).

### Wspólnie

- Klasa `Game`: inicjalizacja, główna pętla (`run`), metody `update` i `draw`, pasek HUD (`_hud`).
- Maszyna stanów i ekrany przejściowe.
- Balans rozgrywki: prędkości wrogów, liczba bomb startowych, zasięgi eksplozji, poziomy trudności.
- Testowanie i debugowanie.

---

## 9. Statystyki projektu

| | |
|---|---|
| Linie kodu | ok. 1380 |
| Klas | 6 |
| Metod klasy Game | ok. 45 |
| Stanów gry (ekranów) | 15 |
| Plików graficznych | 49 |
| Plików audio | 8 (opcjonalne) |
| Typów power-upów | 3 |
| Typów wrogów | 2 (szkielet, ork) |
| Rund | 3 |

---

*THALANOR: Zatopione Kroniki — projekt zaliczeniowy z przedmiotu Projektowanie Gier*
