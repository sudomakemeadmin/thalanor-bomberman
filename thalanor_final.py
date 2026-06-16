"""
THALANOR: FINAL v3
Dark Fantasy Bomberman | Python + Pygame
WASD/strzałki=ruch  SPACJA=bomba  ESC=wyjście
"""
import pygame, sys, random, math, os, json, json
from collections import deque

try:    import numpy as np; NP=True
except: NP=False

pygame.init()
try:    pygame.mixer.init(22050,-16,2,512); AU=True
except Exception as e:
    AU=False
    print(f"[MUZYKA] mixer.init nie powiódł się: {e}")

# ── ŚCIEŻKI ──────────────────────────────────────────────────────────────────
if getattr(sys,'frozen',False):
    BASE = sys._MEIPASS              # folder tymczasowy PyInstallera (assety wbudowane w EXE)
    SAVE_DIR = os.path.dirname(sys.executable)  # ranking.json zapisuj koło EXE
else:
    BASE = os.path.dirname(os.path.abspath(__file__))
    SAVE_DIR = BASE
ASS  = os.path.join(BASE,'assets2')

# ── STAŁE ────────────────────────────────────────────────────────────────────
SW,SH      = 1200,820
TILE       = 56
COLS,ROWS  = 19,11
OX         = (SW - COLS*TILE)//2    # 68
OY         = 132                      # HUD height
FPS        = 30
BOMB_FUSE  = FPS*3
BOMB_RANGE_START = 1    # start od 1!
BOMB_RANGE_MAX   = 6
FIRE_DUR   = FPS//2+4
FIRE_DMG_FRAMES = FIRE_DUR   # ile klatek po wybuchu pole ognia może zadać obrażenia
                              # (= cały czas trwania animacji ognia)
SPD_LEVELS = [5.0, 5.7, 6.4, 7.2, 8.2]  # poziomy 1-5
SPD_P      = SPD_LEVELS[0]               # start poziom 1
SPD_SK     = 3.8
SPD_ORC    = 3.0
SPD_ORC    = 3.0
MI_SK      = 10
MI_ORC     = 16
EMPTY,HARD,SOFT = 0,1,2

# ── MUZYKA ──────────────────────────
MUSIC_TRACK     = os.path.join('assets2','music','theme.ogg')
MUSIC_TRACK_MP3 = os.path.join('assets2','music','theme.mp3')
MUSIC_VOLUME    = 0.5

SFX_FILES = {
    'place':   os.path.join('assets2','music','bomb_place.wav'),
    'explode': os.path.join('assets2','music','bomb_explode.wav'),
    'death':   os.path.join('assets2','music','enemy_death.wav'),
    'hit':     os.path.join('assets2','music','player_hit.wav'),
    'powerup': os.path.join('assets2','music','powerup.wav'),
    'win':     os.path.join('assets2','music','round_clear.wav'),
    'click':   os.path.join('assets2','music','click.wav'),
}

# ── NAZWY RUND ────────────────────────────────────────────────────────────────
ROUND_LORE = {
    1: ("MROCZNY LAS", "Przeklęta Puszcza Yrendal", '"Cisza w tym lesie nie jest przypadkowa."'),
    2: ("LOCHY ZATOPIONEJ\nCYTADELI", "Podziemia Twierdzy Vrethkan", '"Gdzie kości śpiewają do ciemności..."'),
    3: ("KATAKUMBY MROKU",      "Krypty Zaginionych",           '"Nikt stąd nie powrócił żywy..."'),
}
FADE_SPEED = 5   # px alpha per frame (255/5 = 51 klatek = ~1.7 sek)


# ── PALETA ───────────────────────────────────────────────────────────────────
BG   = (8,5,16)
RN1  = (88,18,175); RN2=(155,55,248); RN3=(215,135,255)
FR1  = (195,28,8);  FR2=(255,95,18);  FR3=(255,198,45); FR4=(255,238,175)
WH3  = (68,55,98);  GOLD=(208,172,48); GRAY=(98,88,118)
RED  = (175,18,18); WHT=(240,230,220)
HEART_RED  = (220,35,55); HEART_DARK = (160,20,35)
WS2=(65,52,42); WS3=(92,76,60)
OR1=(48,92,46); OR2=(70,128,66)
BN2=(218,208,184)

# ── DŹWIĘK ───────────────────────────────────────────────────────────────────
def _s(w): return np.hstack([w.reshape(-1,1)]*2) if NP else None
def snd_place():
    if not NP or not AU: return None
    sr=22050;n=int(sr*.25);t=np.linspace(0,.25,n,False)
    w=np.sin(2*np.pi*220*t)*.5+np.sin(2*np.pi*440*t)*.25
    return pygame.sndarray.make_sound(_s((w*np.exp(-t*10)*24000).astype(np.int16)))
def snd_boom():
    if not NP or not AU: return None
    sr=22050;n=int(sr*.6);t=np.linspace(0,.6,n,False)
    w=(np.random.uniform(-1,1,n)*.6+np.sin(2*np.pi*55*t)*.4)*np.exp(-t*6)
    return pygame.sndarray.make_sound(_s((w*30000).astype(np.int16)))
def snd_death():
    if not NP or not AU: return None
    sr=22050;n=int(sr*.4);t=np.linspace(0,.4,n,False)
    freq=np.linspace(380,70,n)
    w=np.sin(np.cumsum(2*np.pi*freq/sr))*np.exp(-t*5)
    return pygame.sndarray.make_sound(_s((w*22000).astype(np.int16)))
def snd_powerup():
    if not NP or not AU: return None
    sr=22050;n=int(sr*.3);t=np.linspace(0,.3,n,False)
    w=(np.sin(2*np.pi*523*t)*.4+np.sin(2*np.pi*659*t)*.3+np.sin(2*np.pi*784*t)*.3)*np.exp(-t*5)
    return pygame.sndarray.make_sound(_s((w*24000).astype(np.int16)))
def snd_win():
    if not NP or not AU: return None
    sr=22050;n=int(sr*.5);t=np.linspace(0,.5,n,False)
    w=(np.sin(2*np.pi*440*t)*.4+np.sin(2*np.pi*554*t)*.3+np.sin(2*np.pi*659*t)*.3)*np.exp(-t*3)
    return pygame.sndarray.make_sound(_s((w*24000).astype(np.int16)))

# ── ASSETY ───────────────────────────────────────────────────────────────────
def load_img(path, size=None, alpha=True):
    try:
        img=pygame.image.load(path)
        img=img.convert_alpha() if alpha else img.convert()
        if size: img=pygame.transform.scale(img,size)
        return img
    except: return None

def load_assets():
    A={}; p=lambda *x: os.path.join(ASS,*x)
    # Lekkie przycięcie sprite'ów wrogów, by lepiej wpasowały się w kafel (TILE)
    ENEMY_SCALE={'orc':(TILE-2)/66.0, 'skeleton':0.92}
    for char in ('player','skeleton','orc'):
        fr=[]; fl=[]
        for i in range(4):
            img=load_img(p(char,f'walk_{i}.png'))
            if img:
                sc=ENEMY_SCALE.get(char)
                if sc:
                    w,h=img.get_size()
                    nw,nh=max(1,int(w*sc)),max(1,int(h*sc))
                    img=pygame.transform.smoothscale(img,(nw,nh))
                fr.append(img)
                fl.append(pygame.transform.flip(img,True,False))
        A[f'{char}_r']=fr; A[f'{char}_l']=fl
    for n in ('bomb_extra','range_up','speed_up'):
        A[f'pw_{n}']=load_img(p('powerups',f'{n}.png'))
    A['floor']    = load_img(p('tiles','floor_grid.png'),(COLS*TILE,ROWS*TILE),False)
    A['hard']     = load_img(p('tiles','hard.png'),(TILE,TILE),False)  # RGB - czarne tło
    A['soft']     = load_img(p('tiles','soft.png'),(TILE,TILE),False)  # RGB - czarne tło
    A['gameover'] = load_img(p('game_over_scaled.png'),(SW,SH),False)
    A['menu_bg']  = load_img(p('menu_bg.png'),(SW,SH),False)
    A['menu_dark']  = load_img(p('menu_bg_dark.png'),(SW,SH),False)
    A['round1_scr'] = load_img(p('round1_screen.png'),(SW,SH),False)
    A['round2_scr'] = load_img(p('round2_screen.png'),(SW,SH),False)
    # Kafle rundy 1 (las)
    A['floor_r1']   = A.get('floor')
    A['hard_r1']    = A.get('hard')
    A['soft_r1']    = A.get('soft')
    # Kafle rundy 2 (lochy)
    A['floor_r2']   = load_img(p('tiles','floor_grid_r2.png'),(COLS*TILE,ROWS*TILE),False)
    A['hard_r2']    = load_img(p('tiles','hard_r2.png'),(TILE,TILE),False)
    A['soft_r2']    = load_img(p('tiles','soft_r2.png'),(TILE,TILE),False)
    # Nowe menu główne
    A['menu_main']  = load_img(p('menu_main.png'),(SW,SH),False)
    A['demo_end']   = load_img(p('demo_end.png'),(SW,SH),False)
    # HUD etykiety gothic
    for lbl in ('wynik','runda','zycia','wrogow','bomby','zasieg','tempo','thalanor_title'):
        A[f'lbl_{lbl}']=load_img(p('hud',f'{lbl}.png'))
    for d in range(10):
        A[f'digit_{d}']=load_img(p('hud',f'digit_{d}.png'))
    A['victory']  = load_img(p('victory_scaled.png'),(SW,SH),False)
    ok=sum(1 for v in A.values() if v is not None and (not isinstance(v,list) or len(v)>0))
    print(f"Assets: {ok}/{len(A)}")
    return A

# ── SERDUSZKO ────────────────────────────────────────────────────────────────
def draw_heart(surf, cx, cy, size=13, filled=True):
    col = HEART_RED if filled else (50,20,30)
    dark = HEART_DARK if filled else (30,10,18)
    r = size//3
    # Dwa kółka na górze
    pygame.draw.circle(surf, col, (cx-r+1, cy-1), r)
    pygame.draw.circle(surf, col, (cx+r-1, cy-1), r)
    # Trójkąt na dole
    pts=[(cx-size//2+1,cy+1),(cx+size//2-1,cy+1),(cx,cy+size//2+2)]
    pygame.draw.polygon(surf, col, pts)
    # Podświetlenie
    pygame.draw.circle(surf, (min(255,col[0]+40),min(255,col[1]+20),min(255,col[2]+20)),
                       (cx-r+2,cy-2), max(1,r//2))

# ── SPRITE ────────────────────────────────────────────────────────────────────
def blit_char(surf, frames, fi, px, py, right=True, glow=False):
    if not frames: return
    idx = (fi // 3) % len(frames)
    sp = frames[idx]
    sw2,sh2 = sp.get_size()
    dx = (TILE-sw2)//2
    dy = TILE - sh2 - 1
    bx,by=px+max(0,dx), py+max(0,dy)
    if glow:
        # Aura fioletowa wokół sprite'a (3 warstwy przesunięte)
        tinted=sp.copy()
        tint=pygame.Surface(sp.get_size(),pygame.SRCALPHA)
        tint.fill((150,50,255,60))
        tinted.blit(tint,(0,0),special_flags=pygame.BLEND_RGBA_MULT)
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
            surf.blit(tinted,(bx+ox,by+oy))
    surf.blit(sp,(bx,by))

# ── EFEKTY OGNIA ─────────────────────────────────────────────────────────────
def draw_rune(s,px,py,timer):
    p=math.sin(timer*.22)*.5+.5
    c=(int(RN1[0]+(RN2[0]-RN1[0])*p),int(RN1[1]+(RN2[1]-RN1[1])*p),int(RN1[2]))
    cx,cy=px+TILE//2,py+TILE//2
    pygame.draw.circle(s,(int(c[0]*.3),int(c[1]*.2),int(c[2]*.5)),(cx,cy),19)
    pygame.draw.circle(s,c,(cx,cy),13)
    pygame.draw.circle(s,RN2,(cx,cy),8)
    pygame.draw.circle(s,RN3,(cx,cy),4)
    pygame.draw.line(s,RN2,(cx,cy-12),(cx,cy+12),2)
    pygame.draw.line(s,RN2,(cx-8,cy-4),(cx+8,cy-4),2)
    pygame.draw.line(s,RN2,(cx-6,cy-11),(cx,cy-2),2)
    pygame.draw.line(s,RN2,(cx+6,cy-11),(cx,cy-2),2)
    if timer<FPS and timer%5<3: pygame.draw.circle(s,RN3,(cx,cy),21,2)

def fire_c(s,px,py,t):
    f=t%8
    pygame.draw.rect(s,FR1,(px,py,TILE,TILE))
    pygame.draw.rect(s,FR2,(px+2,py+2,TILE-4,TILE-4))
    pygame.draw.rect(s,FR3,(px+6,py+5+f%4,TILE-12,TILE-10))
    pygame.draw.rect(s,FR4,(px+10,py+4+f%5,TILE-20,TILE-12))
    pygame.draw.circle(s,FR4,(px+TILE//2,py+TILE//3),6)

def fire_h(s,px,py,t):
    f=t%6
    # Najpierw wypełnij cały kafel - brak czarnych pasków
    pygame.draw.rect(s,FR1,(px,py,TILE,TILE))
    pygame.draw.rect(s,FR2,(px,py+TILE//5,TILE,TILE*3//5))
    pygame.draw.rect(s,FR3,(px,py+TILE//4,TILE,TILE//2))
    pygame.draw.rect(s,FR4,(px+f,py+TILE//2-6,TILE-f,12))

def fire_v(s,px,py,t):
    f=t%6
    pygame.draw.rect(s,FR1,(px,py,TILE,TILE))
    pygame.draw.rect(s,FR2,(px+TILE//5,py,TILE*3//5,TILE))
    pygame.draw.rect(s,FR3,(px+TILE//4,py,TILE//2,TILE))
    pygame.draw.rect(s,FR4,(px+TILE//2-6,py+f,12,TILE-f))

# ── AI ────────────────────────────────────────────────────────────────────────
def move_to(vx,vy,tx,ty,spd):
    dx,dy=tx-vx,ty-vy; d=math.sqrt(dx*dx+dy*dy)
    if d<=spd: return tx,ty,True
    f=spd/d; return vx+dx*f,vy+dy*f,False

def _blast(grid,bx,by,out):
    out.add((bx,by))
    for dx,dy in[(1,0),(-1,0),(0,1),(0,-1)]:
        for st in range(1,BOMB_RANGE_MAX+1):
            nx,ny=bx+dx*st,by+dy*st
            if not(0<=nx<COLS and 0<=ny<ROWS): break
            if grid[ny][nx]==HARD: break
            out.add((nx,ny))
            if grid[ny][nx]==SOFT: break

def bfs(grid,start,goal,bombs,avoid=False):
    if start==goal: return None
    danger=set()
    if avoid:
        for b in bombs:
            if b.timer<FPS*2 or b.exploding: _blast(grid,b.gx,b.gy,danger)
    vis={start}; q=deque([(start,None)])
    while q:
        pos,first=q.popleft(); cx,cy=pos
        for dx,dy in[(0,1),(0,-1),(1,0),(-1,0)]:
            nx,ny=cx+dx,cy+dy; np_=(nx,ny)
            if np_ in vis or not(0<=nx<COLS and 0<=ny<ROWS): continue
            if grid[ny][nx]!=EMPTY: continue
            if np_ in danger and avoid: continue
            nf=first if first else np_
            if np_==goal: return nf
            vis.add(np_); q.append((np_,nf))
    return None

def flee(grid,pos,bombs):
    danger=set()
    for b in bombs:
        if b.timer<FPS*2 or b.exploding: _blast(grid,b.gx,b.gy,danger)
    if pos not in danger: return None
    vis={pos}; q=deque([(pos,None)])
    while q:
        cur,first=q.popleft(); cx,cy=cur
        for dx,dy in[(0,1),(0,-1),(1,0),(-1,0)]:
            nx,ny=cx+dx,cy+dy; np_=(nx,ny)
            if np_ in vis or not(0<=nx<COLS and 0<=ny<ROWS): continue
            if grid[ny][nx]!=EMPTY: continue
            nf=first if first else np_
            if np_ not in danger: return nf
            vis.add(np_); q.append((np_,nf))
    return None

# ── MAPA ─────────────────────────────────────────────────────────────────────
def gen_map(rnd):
    g=[[EMPTY]*COLS for _ in range(ROWS)]
    for c in range(COLS): g[0][c]=g[ROWS-1][c]=HARD
    for r in range(ROWS): g[r][0]=g[r][COLS-1]=HARD
    for r in range(2,ROWS-1,2):
        for c in range(2,COLS-1,2): g[r][c]=HARD
    dens=min(0.40+rnd*0.04,0.60)
    safe={(1,1),(2,1),(1,2),(COLS-2,1),(COLS-3,1),(COLS-2,2)}
    for r in range(1,ROWS-1):
        for c in range(1,COLS-1):
            if g[r][c]==HARD or (c,r) in safe: continue
            if random.random()<dens: g[r][c]=SOFT
    return g

# ── KLASY ────────────────────────────────────────────────────────────────────
class Particle:
    __slots__=('x','y','vx','vy','col','life','ml')
    def __init__(self,x,y,vx,vy,col,life):
        self.x=x;self.y=y;self.vx=vx;self.vy=vy;self.col=col;self.life=life;self.ml=life

class Bomb:
    def __init__(self,gx,gy,rng):
        self.gx=gx;self.gy=gy;self.timer=BOMB_FUSE;self.rng=rng
        self.exploding=False;self.cells=[];self.ft=0

class PowerUp:
    TYPES=('bomb_extra','range_up','speed_up')
    def __init__(self,gx,gy):
        self.gx=gx;self.gy=gy
        self.kind=random.choice(self.TYPES)
        self.pulse=random.randint(0,60)

class Enemy:
    def __init__(self,gx,gy,kind):
        self.gx=gx;self.gy=gy;self.kind=kind
        self.vx=float(gx*TILE+OX);self.vy=float(gy*TILE+OY)
        self.tx=self.vx;self.ty=self.vy
        self.alive=True;self.dt=0
        # DESYNC: każdy wróg ma inny offset i lekko inne tempo
        base_mi = MI_SK if kind=='skeleton' else MI_ORC
        self.mi = base_mi + random.randint(-3,3)
        self.mt = random.randint(0, self.mi)   # losowy start!
        self.spd = (SPD_SK if kind=='skeleton' else SPD_ORC) + random.uniform(-0.3,0.3)
        self.frame=0;self.ft=0;self.right=True;self.moving=False

def load_ranking():
    try:
        with open(os.path.join(SAVE_DIR,'ranking.json'),'r',encoding='utf-8') as f:
            return json.load(f)
    except: return []

def save_to_ranking(name,score,rnd):
    r=load_ranking()
    r.append({'name':name,'score':score,'round':rnd})
    r.sort(key=lambda x:x['score'],reverse=True)
    r=r[:10]
    with open(os.path.join(SAVE_DIR,'ranking.json'),'w',encoding='utf-8') as f:
        json.dump(r,f,ensure_ascii=False,indent=2)

class Player:
    def __init__(self):
        self.gx=1;self.gy=1
        self.vx=float(TILE+OX);self.vy=float(TILE+OY)
        self.tx=self.vx;self.ty=self.vy
        self.alive=True;self.lives=3;self.inv=0
        self.frame=0;self.ft=0;self.right=True;self.moving=False
        self.placed=0;self.bmax=1
        self.brange=BOMB_RANGE_START  # start od 1
        self.speed_lvl=1              # poziom 1-5
        self.speed=SPD_LEVELS[0]

# ── VIGNETTE ─────────────────────────────────────────────────────────────────
def make_vignette(w,h):
    s=pygame.Surface((w,h),pygame.SRCALPHA);s.fill((0,0,0,0))
    for i in range(55):
        a=int(145*(1-i/55)**1.8);m=i*6
        if m>=min(w,h)//2: break
        for pts in[((m,m),(w-m,m)),((m,h-m),(w-m,h-m)),((m,m),(m,h-m)),((w-m,m),(w-m,h-m))]:
            pygame.draw.line(s,(0,0,0,a),pts[0],pts[1])
    return s

# ── GRA ──────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self):
        self.screen=pygame.display.set_mode((SW,SH))
        pygame.display.set_caption("THALANOR: Przeklęte Ruiny")
        self.clock=pygame.time.Clock()
        self.fb=pygame.font.SysFont("consolas",34,bold=True)
        self.fm=pygame.font.SysFont("consolas",18,bold=True)
        self.fs=pygame.font.SysFont("consolas",14)
        self.fxl=pygame.font.SysFont("consolas",54,bold=True)
        self.fhuge=pygame.font.SysFont("consolas",140,bold=True)
        self.s_place=snd_place();self.s_boom=snd_boom()
        self.s_death=snd_death();self.s_pw=snd_powerup();self.s_win=snd_win()
        self.s_hit=snd_death()  # fallback - nadpisany przez SFX jeśli plik istnieje
        self.s_click=None       # dźwięk nawigacji w menu (jeśli plik click.wav istnieje)
        self.A=load_assets()
        self._load_sfx()       # wczytaj realne dźwięki z assets2/music/ (jeśli są)
        self.music_volume=0.5      # domyślna głośność muzyki 50%
        self._start_music()    # uruchom muzykę w tle (zapętloną)
        self.vignette=make_vignette(SW,SH)
        self.rnd=1;self.score=0;self.tick=0
        self.state='menu';self.menu_sel=0;self.msg='';self.msg_t=0
        self.player_name='Podróżnik'
        self.fullscreen=False
        self.ctrl_wasd=False
        self.difficulty=1
        self.opcje_sel=0
        self.opcje_return='menu'   # gdzie wrócić z opcji: 'menu' lub 'pause'
        self.pause_sel=0
        self.countdown_timer=0
        self.ranking_data=[]
        self.fade_alpha=0;self.fade_surf=pygame.Surface((SW,SH))
        self.tick=0

    def _new(self,keep=False):
        """keep=True: zachowaj ulepszenia i życia między rundami"""
        saved=None
        if keep and hasattr(self,'player') and self.player:
            p=self.player
            saved=(p.bmax,p.brange,p.speed_lvl,p.speed,p.lives)
        self.grid=gen_map(self.rnd)
        self.player=Player();self.bombs=[];self.parts=[];self.powerups=[]
        self.fire_cells_active=[]
        if saved:
            self.player.bmax,self.player.brange=saved[0],saved[1]
            self.player.speed_lvl,self.player.speed=saved[2],saved[3]
            self.player.lives=saved[4]
        self.enemies=self._spawn()
        self.state='countdown';self.countdown_timer=FPS*5
        self.msg=f"RUNDA  {self.rnd}";self.msg_t=FPS*2

    def _spawn(self):
        count=min(3+self.rnd*2,16)
        safe={(1,1),(2,1),(1,2),(COLS-2,1),(COLS-3,1),(COLS-2,2)}
        placed=set();enemies=[];att=0
        while len(enemies)<count and att<400:
            att+=1;gx=random.randint(1,COLS-2);gy=random.randint(1,ROWS-2)
            if self.grid[gy][gx]!=EMPTY or (gx,gy) in safe or (gx,gy) in placed: continue
            if abs(gx-1)+abs(gy-1)<4: continue
            placed.add((gx,gy))
            kind='orc' if(self.rnd>1 and random.random()<0.45) else 'skeleton'
            enemies.append(Enemy(gx,gy,kind))
        return enemies

    def _snd(self,s):
        if s:
            try: s.play()
            except: pass

    def _bomb(self):
        p=self.player
        if p.placed>=p.bmax: return
        if any(b.gx==p.gx and b.gy==p.gy for b in self.bombs): return
        self.bombs.append(Bomb(p.gx,p.gy,p.brange));p.placed+=1;self._snd(self.s_place)

    def _explode(self,bomb):
        bomb.exploding=True;bomb.ft=FIRE_DUR
        bomb.cells=[(bomb.gx,bomb.gy,'c')]
        for dx,dy in((1,0),(-1,0),(0,1),(0,-1)):
            for st in range(1,bomb.rng+1):
                nx,ny=bomb.gx+dx*st,bomb.gy+dy*st
                if not(0<=nx<COLS and 0<=ny<ROWS): break
                if self.grid[ny][nx]==HARD: break
                bomb.cells.append((nx,ny,'h' if dy==0 else 'v'))
                if self.grid[ny][nx]==SOFT:
                    self.grid[ny][nx]=EMPTY
                    self.score+=10  # punkty za zniszczenie ściany
                    wx=nx*TILE+OX+TILE//2;wy=ny*TILE+OY+TILE//2
                    for _ in range(8):
                        self.parts.append(Particle(wx,wy,random.uniform(-4,4),
                            random.uniform(-6,-.5),random.choice([WS2,WS3,BN2]),FPS))
                    if random.random()<0.15:
                        self.powerups.append(PowerUp(nx,ny))
                    break
        # Pola ognia z TEJ klatki (do _fire_dmg) - aktywne na kilka klatek,
        # niezależnie od kolejności bomb (działa też dla reakcji łańcuchowej)
        for gx,gy,_ in bomb.cells:
            self.fire_cells_active.append((gx,gy,FIRE_DMG_FRAMES))
        # Reakcja łańcuchowa: jeśli inna bomba stoi w polu ognia, też wybucha
        blast_cells={(cx_,cy_) for cx_,cy_,_ in bomb.cells}
        for ob in self.bombs:
            if ob is not bomb and not ob.exploding and (ob.gx,ob.gy) in blast_cells:
                self._explode(ob)
        self._snd(self.s_boom)
        for gx,gy,_ in bomb.cells:
            wx=gx*TILE+OX+TILE//2;wy=gy*TILE+OY+TILE//2
            for _ in range(6):
                self.parts.append(Particle(wx,wy,random.uniform(-4,4),
                    random.uniform(-5,1),random.choice([FR2,FR3,FR4]),FIRE_DUR))
        self.player.placed=max(0,self.player.placed-1)

    def _tile_overlap(self,vx,vy,fgx,fgy):
        """Zwraca procent powierzchni kafla (0-1) jednostki o pozycji wizualnej
        (vx,vy) pokrywającej się z kaflem ognia (fgx,fgy)."""
        ex0,ey0=vx,vy; ex1,ey1=vx+TILE,vy+TILE
        fx0,fy0=OX+fgx*TILE,OY+fgy*TILE; fx1,fy1=fx0+TILE,fy0+TILE
        ox=max(0,min(ex1,fx1)-max(ex0,fx0))
        oy=max(0,min(ey1,fy1)-max(ey0,fy0))
        return (ox*oy)/(TILE*TILE)

    def _fire_dmg(self):
        # Pola ognia aktywne przez kilka klatek po wybuchu (FIRE_DMG_FRAMES) -
        # dopalający się ogień po tym czasie już nie zadaje obrażeń
        fire_cells={(gx,gy) for gx,gy,_ in self.fire_cells_active}
        if not fire_cells: return

        def hit(vx,vy):
            for fgx,fgy in fire_cells:
                if self._tile_overlap(vx,vy,fgx,fgy)>=0.25: return True
            return False

        p=self.player
        if p.inv<=0 and hit(p.vx,p.vy):
            self._take_damage()
        for e in self.enemies:
            if not e.alive or not hit(e.vx,e.vy): continue
            e.alive=False;e.dt=FPS
            self.score+=100 if e.kind=='skeleton' else 160
            self._snd(self.s_death)
            wx=e.gx*TILE+OX+TILE//2;wy=e.gy*TILE+OY+TILE//2
            cols=[(192,182,158),(218,208,184)] if e.kind=='skeleton' else [(48,92,46),(70,128,66)]
            for _ in range(12):
                self.parts.append(Particle(wx,wy,random.uniform(-5,5),
                    random.uniform(-6,-.5),random.choice(cols),FPS))

    def _take_damage(self):
        """Gracz traci życie, ale zachowuje zebrane ulepszenia (bomby/zasięg/tempo)"""
        p=self.player
        self._snd(self.s_hit)
        p.lives-=1; p.inv=FPS*2
        if p.lives<=0:
            p.alive=False; self.state='over'
            save_to_ranking(self.player_name,self.score,self.rnd)

    def _check_powerups(self):
        p=self.player
        for pw in self.powerups[:]:
            if pw.gx==p.gx and pw.gy==p.gy:
                self.powerups.remove(pw);self._snd(self.s_pw);self.score+=50
                if pw.kind=='bomb_extra':   p.bmax=min(p.bmax+1,5)
                elif pw.kind=='range_up':   p.brange=min(p.brange+1,BOMB_RANGE_MAX)
                elif pw.kind=='speed_up':
                    p.speed_lvl=min(p.speed_lvl+1,5)
                    p.speed=SPD_LEVELS[p.speed_lvl-1]

    def update(self,keys):
        if self.state in ('menu','name_input','ranking','opcje','demo_end','over','clear','round_title','o_projekcie','pause','pause_confirm','round1_intro'): self.tick+=1; return
        if self.state=='countdown':
            self.tick+=1
            if self.msg_t>0: self.msg_t-=1
            self.countdown_timer-=1
            if self.countdown_timer<=0:
                self.state='play'
            return
        if self.state=='fade_out':
            self.fade_alpha=min(255,self.fade_alpha+FADE_SPEED)
            if self.fade_alpha>=255:
                if self.rnd>=2: save_to_ranking(self.player_name,self.score,self.rnd); self.state='demo_end'
                else: self.state='round_title'
            return
        if self.state!='play': return
        self.tick+=1
        if self.msg_t>0: self.msg_t-=1
        self._upd_player(keys);self._upd_enemies()
        self._upd_bombs();self._fire_dmg()
        self._check_powerups();self._upd_parts()
        for pw in self.powerups: pw.pulse=(pw.pulse+1)%60
        if not any(e.alive for e in self.enemies) and self.player.alive:
            self.state='fade_out';self.fade_alpha=0;self._snd(self.s_win)

    def _upd_player(self,keys):
        p=self.player
        if not p.alive: return
        if p.inv>0: p.inv-=1
        p.vx,p.vy,at=move_to(p.vx,p.vy,p.tx,p.ty,p.speed)
        if abs(p.vx-p.tx)<1.5 and abs(p.vy-p.ty)<1.5:
            p.vx,p.vy=p.tx,p.ty; at=True
        p.moving=not at
        if p.moving: p.ft+=1
        if p.ft>=4: p.ft=0; p.frame+=1
        if at:
            dx=dy=0
            if self.ctrl_wasd:
                kl,kr,ku,kd=pygame.K_a,pygame.K_d,pygame.K_w,pygame.K_s
            else:
                kl,kr,ku,kd=pygame.K_LEFT,pygame.K_RIGHT,pygame.K_UP,pygame.K_DOWN
            if keys[kl]: dx=-1;p.right=False
            elif keys[kr]: dx=1; p.right=True
            elif keys[ku]: dy=-1
            elif keys[kd]: dy=1
            if dx or dy:
                nx,ny=p.gx+dx,p.gy+dy
                if 0<=nx<COLS and 0<=ny<ROWS and self.grid[ny][nx]==EMPTY:
                    if not any(b.gx==nx and b.gy==ny and not b.exploding for b in self.bombs):
                        p.gx,p.gy=nx,ny
                        p.tx=float(nx*TILE+OX); p.ty=float(ny*TILE+OY)
                        p.moving=True


    def _upd_enemies(self):
        p=self.player
        for e in self.enemies:
            if not e.alive:
                if e.dt>0: e.dt-=1
                continue
            e.vx,e.vy,at=move_to(e.vx,e.vy,e.tx,e.ty,e.spd)
            if abs(e.vx-e.tx)<1.5 and abs(e.vy-e.ty)<1.5:
                e.vx,e.vy=e.tx,e.ty; at=True
            e.moving=not at
            if e.moving: e.ft+=1
            if e.ft>=8: e.ft=0; e.frame+=1
            if at:
                self._think(e,p)  # natychmiast nastepny krok!
            if e.gx==p.gx and e.gy==p.gy and p.inv<=0 and p.alive:
                self._take_damage()


    def _think(self,e,p):
        safe=flee(self.grid,(e.gx,e.gy),self.bombs)
        if safe and(e.kind=='orc' or random.random()<0.55):
            nx,ny=safe
            if self.grid[ny][nx]==EMPTY and not any(b.gx==nx and b.gy==ny for b in self.bombs):
                e.right=(nx>=e.gx);e.gx,e.gy=nx,ny
                e.tx=float(nx*TILE+OX);e.ty=float(ny*TILE+OY);return
        step=bfs(self.grid,(e.gx,e.gy),(p.gx,p.gy),self.bombs,e.kind=='orc')
        if step:
            nx,ny=step
            if self.grid[ny][nx]==EMPTY and not any(b.gx==nx and b.gy==ny for b in self.bombs):
                e.right=(nx>=e.gx);e.gx,e.gy=nx,ny
                e.tx=float(nx*TILE+OX);e.ty=float(ny*TILE+OY);return
        dirs=[(0,1),(0,-1),(1,0),(-1,0)];random.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny=e.gx+dx,e.gy+dy
            if 0<=nx<COLS and 0<=ny<ROWS and self.grid[ny][nx]==EMPTY:
                if not any(b.gx==nx and b.gy==ny for b in self.bombs):
                    e.right=(nx>=e.gx);e.gx,e.gy=nx,ny
                    e.tx=float(nx*TILE+OX);e.ty=float(ny*TILE+OY);return
        # Zablokowany - poczekaj chwilę przed następną próbą
        # (pozostań w miejscu - tx/ty już równa się vx/vy)

    def _upd_bombs(self):
        # Pola ognia są "aktywne" (mogą zadać obrażenia) tylko kilka klatek po wybuchu
        self.fire_cells_active=[(gx,gy,ttl-1) for gx,gy,ttl in self.fire_cells_active if ttl-1>0]
        for b in self.bombs[:]:
            if not b.exploding:
                b.timer-=1
                if b.timer<=0: self._explode(b)
            else:
                b.ft-=1
                if b.ft<=0: self.bombs.remove(b)

    def _upd_parts(self):
        for pt in self.parts: pt.x+=pt.vx;pt.y+=pt.vy;pt.vy+=0.2;pt.life-=1
        self.parts=[pt for pt in self.parts if pt.life>0]

    # ── RYSOWANIE ─────────────────────────────────────────────────────────────
    def _tiles(self):
        """Zwróć kafle floor/hard/soft dla bieżącej rundy"""
        sfx = '_r2' if self.rnd >= 2 else '_r1'
        return (self.A.get('floor'+sfx) or self.A.get('floor'),
                self.A.get('hard'+sfx)  or self.A.get('hard'),
                self.A.get('soft'+sfx)  or self.A.get('soft'))

    def _toggle_fullscreen(self):
        self.fullscreen=not self.fullscreen
        if self.fullscreen:
            self.screen=pygame.display.set_mode((SW,SH),pygame.FULLSCREEN)
        else:
            self.screen=pygame.display.set_mode((SW,SH))

    def _start_music(self):
        """Odtwarza główny utwór 8-bit w tle, zapętlony, od startu gry"""
        print(f"[MUZYKA] AU={AU}  BASE={BASE}")
        for path in (MUSIC_TRACK, MUSIC_TRACK_MP3):
            full=os.path.join(BASE,path)
            exists=os.path.exists(full)
            print(f"[MUZYKA] sprawdzam: {full}  istnieje={exists}")
            if exists:
                try:
                    pygame.mixer.music.load(full)
                    pygame.mixer.music.set_volume(self.music_volume)
                    pygame.mixer.music.play(-1)
                    print(f"[MUZYKA] OK, odtwarzam {full}, głośność={self.music_volume}")
                except Exception as e:
                    print(f"[MUZYKA] BŁĄD wczytywania {full}: {e}")
                return
        print("[MUZYKA] Nie znaleziono pliku theme.ogg / theme.mp3")

    def _set_music_volume(self,delta):
        """Zmienia głośność muzyki o delta (np. +-0.05), zakres 0.0-1.0"""
        self.music_volume=max(0.0,min(1.0,round(self.music_volume+delta,2)))
        try: pygame.mixer.music.set_volume(self.music_volume)
        except Exception: pass

    def _load_sfx(self):
        """Wczytaj realne pliki SFX (jeśli istnieją) - nadpisują proceduralne dźwięki"""
        for key,path in SFX_FILES.items():
            full=os.path.join(BASE,path)
            if os.path.exists(full):
                try:
                    snd=pygame.mixer.Sound(full)
                    if key=='place':   self.s_place=snd
                    elif key=='explode': self.s_boom=snd
                    elif key=='death':   self.s_death=snd
                    elif key=='hit':     self.s_hit=snd
                    elif key=='powerup': self.s_pw=snd
                    elif key=='win':     self.s_win=snd
                    elif key=='click':   self.s_click=snd
                except Exception: pass

    def _draw_o_projekcie(self):
        self.screen.fill((0,0,0))
        bg=self.A.get('menu_main')
        if bg:
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,205))
            self.screen.blit(bg,(0,0)); self.screen.blit(ov,(0,0))
        cx=SW//2

        # Tytuł
        t=self.fb.render("O PROJEKCIE",True,GOLD)
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2)]:
            self.screen.blit(self.fb.render("O PROJEKCIE",True,(80,50,0)),(cx-t.get_width()//2+ox,40+oy))
        self.screen.blit(t,(cx-t.get_width()//2,40))
        pygame.draw.line(self.screen,(100,75,35),(cx-340,95),(cx+340,95),1)

        y=118
        def line(txt,col=(200,170,110),size='m',gap=30):
            nonlocal y
            f=self.fm if size=='m' else self.fs if size=='s' else self.fb
            t=f.render(txt,True,col)
            self.screen.blit(t,(cx-t.get_width()//2,y)); y+=gap

        line("THALANOR: ZATOPIONE KRONIKI",GOLD,'b',gap=44)
        line("Autorzy: Adam Ostrowski, Arkadiusz Nowiszewski",(210,190,150),'m',gap=30)
        line('Projekt zrealizowany w ramach przedmiotu "Projektowanie Gier"',(170,150,110),'s',gap=22)
        line("Prowadzący: mgr Artur Karwatka",(170,150,110),'s',gap=30)

        pygame.draw.line(self.screen,(100,75,35),(cx-340,y),(cx+340,y),1)
        y+=24

        # Dwie kolumny
        lx=cx-330; rx=cx+24
        HEAD=(220,170,60); ROW=(190,175,150)
        ly=y; ry=y
        def lcol(txt,col=ROW,size='s',gap=22,bold=False):
            nonlocal ly
            f=self.fm if size=='m' else self.fs
            t=f.render(txt,True,col)
            self.screen.blit(t,(lx,ly)); ly+=gap
        def rcol(txt,col=ROW,size='s',gap=22,bold=False):
            nonlocal ry
            f=self.fm if size=='m' else self.fs
            t=f.render(txt,True,col)
            self.screen.blit(t,(rx,ry)); ry+=gap

        # --- Lewa kolumna: TECHNOLOGIA + STATYSTYKI ---
        lcol("TECHNOLOGIA",HEAD,'m',gap=32)
        lcol("Język programowania: Python 3",ROW,'s')
        lcol("Środowisko (IDE): PyCharm",ROW,'s')
        lcol("Biblioteka graficzna: Pygame",ROW,'s')
        lcol("Dystrybucja: PyInstaller (plik .exe)",ROW,'s',gap=34)

        lcol("STATYSTYKI PROJEKTU",HEAD,'m',gap=32)
        lcol("Kod źródłowy: ~1330 linii",ROW,'s')
        lcol("Klasy w kodzie: 6",ROW,'s')
        lcol("  (Player, Enemy, Bomb,",(160,145,120),'s')
        lcol("   PowerUp, Particle, Game)",(160,145,120),'s')
        lcol("Stany / ekrany gry: 15",ROW,'s')
        lcol("Pliki graficzne (sprite'y, tła, HUD): 49",ROW,'s')
        lcol("Pliki audio (muzyka + SFX): 8",ROW,'s')
        lcol("Metody klasy Game: ~45",ROW,'s')

        # --- Prawa kolumna: TECHNIKI + SMACZKI ---
        rcol("WYKORZYSTANE TECHNIKI",HEAD,'m',gap=32)
        rcol("pygame.mixer + numpy - dźwięki SFX",ROW,'s')
        rcol("  generowane proceduralnie (8-bit)",(160,145,120),'s')
        rcol("pygame.transform - skalowanie i",ROW,'s')
        rcol("  odbicia sprite'ów (lewo/prawo)",(160,145,120),'s')
        rcol("Surface(SRCALPHA) - przezroczyste",ROW,'s')
        rcol("  nakładki, glow, winieta",(160,145,120),'s')
        rcol("BFS - sztuczna inteligencja wrogów",ROW,'s')
        rcol("JSON - zapis rankingu TOP wyników",ROW,'s')
        rcol("Maszyna stanów (15 stanów gry)",ROW,'s')
        rcol("sys._MEIPASS - zasoby w pliku .exe",ROW,'s',gap=34)

        pygame.draw.line(self.screen,(100,75,35),(cx-340,SH-70),(cx+340,SH-70),1)
        h=self.fs.render("ENTER / ESC — Powrót do menu",True,(80,65,40))
        self.screen.blit(h,(cx-h.get_width()//2,SH-50))


    def _draw_ranking(self):
        self.screen.fill((0,0,0))
        bg=self.A.get('menu_main')
        if bg:
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,200))
            self.screen.blit(bg,(0,0)); self.screen.blit(ov,(0,0))
        cx=SW//2
        # Tytuł
        t=self.fb.render("RANKING",True,GOLD)
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2)]:
            sh=self.fb.render("RANKING",True,(80,50,0))
            self.screen.blit(sh,(cx-t.get_width()//2+ox,45+oy))
        self.screen.blit(t,(cx-t.get_width()//2,45))
        pygame.draw.line(self.screen,(100,75,35),(cx-320,100),(cx+320,100),1)
        # Nagłówek
        for txt,x in [("MIEJSCE",cx-320),("GRACZ",cx-220),("WYNIK",cx+80),("RUNDA",cx+220)]:
            h=self.fs.render(txt,True,(90,70,35))
            self.screen.blit(h,(x,115))
        pygame.draw.line(self.screen,(60,45,20),(cx-320,138),(cx+320,138),1)
        # Wyniki
        data=load_ranking()
        if not data:
            t2=self.fm.render("Brak wyników — zagraj i ustaw rekord!",True,(100,80,50))
            self.screen.blit(t2,(cx-t2.get_width()//2,320))
        for i,e in enumerate(data[:10]):
            y=150+i*52; col=((220,180,50) if i==0 else (180,170,150) if i==1 else (180,120,60) if i==2 else (140,110,55))
            self.screen.blit(self.fm.render(f"{i+1}.",True,col),(cx-320,y))
            self.screen.blit(self.fm.render(e.get('name','?')[:14],True,(210,165,65)),(cx-220,y))
            self.screen.blit(self.fm.render(str(e.get('score',0)),True,GOLD),(cx+80,y))
            self.screen.blit(self.fm.render(str(e.get('round',1)),True,RN2),(cx+240,y))
        pygame.draw.line(self.screen,(100,75,35),(cx-320,SH-80),(cx+320,SH-80),1)
        h2=self.fs.render("ENTER / ESC — Powrót do menu",True,(80,65,40))
        self.screen.blit(h2,(cx-h2.get_width()//2,SH-60))

    def _draw_opcje(self):
        self.screen.fill((0,0,0))
        bg=self.A.get('menu_main')
        if bg:
            ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,190))
            self.screen.blit(bg,(0,0)); self.screen.blit(ov,(0,0))
        cx=SW//2
        t=self.fb.render("OPCJE",True,GOLD)
        self.screen.blit(t,(cx-t.get_width()//2,50))
        pygame.draw.line(self.screen,(100,75,35),(cx-280,105),(cx+280,105),1)
        opts=[
            ("Pełny ekran", "WŁ" if self.fullscreen else "WYŁ", GOLD if self.fullscreen else (140,110,55)),
            ("Sterowanie",  "WASD" if self.ctrl_wasd else "Strzałki", GOLD),
            ("Trudność",    ["Łatwa","Normalna","Trudna"][self.difficulty],
                            [(60,200,60),(GOLD[0],GOLD[1],GOLD[2]),(220,80,50)][self.difficulty]),
            ("Głośność muzyki", f"{int(round(self.music_volume*100))}%", GOLD),
        ]
        for i,(label,val,vcol) in enumerate(opts):
            y=200+i*100; sel=(i==self.opcje_sel)
            if sel:
                pulse=abs(math.sin(self.tick*0.08))*0.4+0.6
                ov2=pygame.Surface((600,60),pygame.SRCALPHA)
                ov2.fill((int(80*pulse),int(50*pulse),int(20*pulse),100))
                pygame.draw.rect(ov2,(int(180*pulse),int(120*pulse),int(40*pulse),200),(0,0,600,60),2)
                self.screen.blit(ov2,(cx-300,y-8))
            lc=(220,170,60) if sel else (130,100,45)
            lt=self.fm.render(label,True,lc)
            vt=self.fm.render(val,True,vcol)
            self.screen.blit(lt,(cx-280,y))
            self.screen.blit(vt,(cx+150,y))
            # Strzałki dla wybranych
            if sel:
                self.screen.blit(self.fs.render("◄ ►",True,(180,140,50)),(cx+150+vt.get_width()+10,y+5))
        pygame.draw.line(self.screen,(100,75,35),(cx-280,SH-90),(cx+280,SH-90),1)
        h=self.fs.render("↑↓ wybór    ◄►/ENTER zmień    ESC powrót",True,(80,65,40))
        self.screen.blit(h,(cx-h.get_width()//2,SH-65))

    def _draw_countdown(self):
        # Lekkie przyciemnienie pola gry pod liczbą
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,90))
        self.screen.blit(ov,(0,0))
        cx,cy=SW//2,SH//2
        # Etykieta rundy - nad cyfrą
        rnd_txt=f"RUNDA {self.rnd}"
        rt=self.fb.render(rnd_txt,True,RN3)
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2)]:
            self.screen.blit(self.fb.render(rnd_txt,True,(40,15,60)),(cx-rt.get_width()//2+ox,cy-160+oy))
        self.screen.blit(rt,(cx-rt.get_width()//2,cy-160))
        secs_left=self.countdown_timer//FPS + 1
        secs_left=max(1,min(5,secs_left))
        txt=str(secs_left)
        pulse=abs(math.sin((self.countdown_timer%FPS)*0.25))*0.4+0.8
        big=self.fhuge.render(txt,True,GOLD)
        shadow_t=self.fhuge.render(txt,True,(60,30,5))
        if pulse!=1.0:
            w,h=big.get_size()
            big=pygame.transform.smoothscale(big,(max(1,int(w*pulse)),max(1,int(h*pulse))))
            sw_,sh_=shadow_t.get_size()
            shadow_t=pygame.transform.smoothscale(shadow_t,(max(1,int(sw_*pulse)),max(1,int(sh_*pulse))))
        for ox,oy in[(-4,0),(4,0),(0,-4),(0,4)]:
            self.screen.blit(shadow_t,(cx-shadow_t.get_width()//2+ox,cy-shadow_t.get_height()//2+oy))
        self.screen.blit(big,(cx-big.get_width()//2,cy-big.get_height()//2))
        ready=self.fm.render("Przygotuj się...",True,(220,200,160))
        self.screen.blit(ready,(cx-ready.get_width()//2,cy+big.get_height()//2+20))

    def _draw_pause(self):
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,170))
        self.screen.blit(ov,(0,0))
        cx,cy=SW//2,SH//2
        t=self.fb.render("PAUZA",True,GOLD)
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2)]:
            self.screen.blit(self.fb.render("PAUZA",True,(80,50,0)),(cx-t.get_width()//2+ox,cy-160+oy))
        self.screen.blit(t,(cx-t.get_width()//2,cy-160))
        opts=["KONTYNUUJ","OPCJE","MENU GŁÓWNE"]
        for i,name in enumerate(opts):
            y=cy-60+i*60
            sel=(i==self.pause_sel)
            if sel:
                pulse=abs(math.sin(self.tick*0.08))*0.4+0.6
                ov2=pygame.Surface((360,46),pygame.SRCALPHA)
                ov2.fill((int(80*pulse),int(50*pulse),int(20*pulse),140))
                pygame.draw.rect(ov2,(int(200*pulse),int(150*pulse),int(40*pulse),220),(0,0,360,46),2)
                self.screen.blit(ov2,(cx-180,y-8))
            col=(230,190,80) if sel else (150,120,70)
            txt=self.fm.render(name,True,col)
            self.screen.blit(txt,(cx-txt.get_width()//2,y))
        h=self.fs.render("↑↓ wybór    ENTER zatwierdź    ESC wróć do gry",True,(180,160,120))
        self.screen.blit(h,(cx-h.get_width()//2,cy+150))

    def _draw_pause_confirm(self):
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,190))
        self.screen.blit(ov,(0,0))
        cx,cy=SW//2,SH//2
        panel_w,panel_h=640,220
        panel=pygame.Surface((panel_w,panel_h),pygame.SRCALPHA)
        panel.fill((40,15,15,210))
        pygame.draw.rect(panel,(220,80,60),(0,0,panel_w,panel_h),3)
        self.screen.blit(panel,(cx-panel_w//2,cy-panel_h//2))
        t=self.fm.render("Wrócić do menu głównego?",True,(240,200,90))
        self.screen.blit(t,(cx-t.get_width()//2,cy-panel_h//2+30))
        t2=self.fs.render("Cały postęp tej rozgrywki zostanie utracony.",True,(220,160,140))
        self.screen.blit(t2,(cx-t2.get_width()//2,cy-panel_h//2+75))
        t3=self.fs.render("Twój wynik zostanie zapisany do rankingu.",True,(180,200,160))
        self.screen.blit(t3,(cx-t3.get_width()//2,cy-panel_h//2+100))
        h=self.fs.render("ENTER — Tak, wróć do menu      ESC — Nie, wróć do gry",True,(200,180,150))
        self.screen.blit(h,(cx-h.get_width()//2,cy+panel_h//2-35))

    def _overlay(self,msg,col=(255,255,255)):
        if not msg: return
        t=self.fb.render(msg,True,col)
        x=SW//2-t.get_width()//2; y=SH//2-t.get_height()//2
        bg=pygame.Surface((t.get_width()+20,t.get_height()+10),pygame.SRCALPHA)
        bg.fill((0,0,0,160))
        self.screen.blit(bg,(x-10,y-5))
        self.screen.blit(t,(x,y))

    def draw(self):
        if self.state=='menu':
            self._draw_menu()
            pygame.display.flip(); return
        if self.state=='ranking':
            self._draw_ranking()
            pygame.display.flip(); return
        if self.state=='opcje':
            self._draw_opcje()
            pygame.display.flip(); return
        if self.state=='demo_end':
            bg=self.A.get('demo_end')
            if bg: self.screen.blit(bg,(0,0))
            pygame.display.flip(); return
        if self.state=='o_projekcie':
            self._draw_o_projekcie()
            pygame.display.flip(); return
        if self.state=='round1_intro':
            bg=self.A.get('round1_scr')
            if bg: self.screen.blit(bg,(0,0))
            else: self.screen.fill((5,3,12))
            pygame.display.flip(); return
        if self.state=='name_input':
            self._draw_name_input()
            pygame.display.flip(); return
        self.screen.fill(BG)
        floor_t,hard_t,soft_t=self._tiles()
        if floor_t: self.screen.blit(floor_t,(OX,OY))
        for r in range(ROWS):
            for c in range(COLS):
                t=self.grid[r][c]; px=OX+c*TILE; py=OY+r*TILE
                if t==HARD:
                    if hard_t: self.screen.blit(hard_t,(px,py))
                elif t==SOFT:
                    if soft_t: self.screen.blit(soft_t,(px,py))
        # Power-upy
        for pw in self.powerups:
            px=OX+pw.gx*TILE; py=OY+pw.gy*TILE
            glow=int(abs(math.sin(pw.pulse*0.1))*55+25)
            pygame.draw.circle(self.screen,(glow,glow//2,0),(px+TILE//2,py+TILE//2),16)
            icon=self.A.get(f'pw_{pw.kind}')
            if icon:
                iw,ih=icon.get_size()
                self.screen.blit(icon,(px+(TILE-iw)//2,py+(TILE-ih)//2))
        # Bomby
        for b in self.bombs:
            px=OX+b.gx*TILE; py=OY+b.gy*TILE
            if not b.exploding: draw_rune(self.screen,px,py,b.timer)
            else:
                for gx,gy,ft in b.cells:
                    fpx=OX+gx*TILE; fpy=OY+gy*TILE
                    if ft=='c': fire_c(self.screen,fpx,fpy,self.tick)
                    elif ft=='h': fire_h(self.screen,fpx,fpy,self.tick)
                    else: fire_v(self.screen,fpx,fpy,self.tick)
        # Cząsteczki
        for pt in self.parts:
            c=(max(0,min(255,pt.col[0])),max(0,min(255,pt.col[1])),max(0,min(255,pt.col[2])))
            sz=max(1,int(4*pt.life/pt.ml))
            pygame.draw.rect(self.screen,c,(int(pt.x),int(pt.y),sz,sz))
        # Wrogowie
        for e in self.enemies:
            if not e.alive:
                if e.dt>0 and e.dt%4<2: self._draw_e(e)
                continue
            self._draw_e(e)
        # Gracz
        p=self.player
        if p.alive and(p.inv==0 or p.inv%4<2):
            # Świecący okrąg pod graczem
            _cx=int(p.vx)+TILE//2; _cy=int(p.vy)+TILE-6
            _pulse=abs(math.sin(self.tick*0.08))*0.4+0.6
            _gs=pygame.Surface((48,20),pygame.SRCALPHA)
            pygame.draw.ellipse(_gs,(140,50,240,int(90*_pulse)),(0,0,48,20))
            pygame.draw.ellipse(_gs,(200,100,255,int(130*_pulse)),(8,4,32,12))
            self.screen.blit(_gs,(_cx-24,_cy-10))
            # Sprite z aurą fioletową
            frames=self.A.get('player_l',[]) if p.right else self.A.get('player_r',[])
            blit_char(self.screen,frames,p.frame,int(p.vx),int(p.vy),p.right,glow=True)
            blit_char(self.screen,frames,p.frame,int(p.vx),int(p.vy),p.right)
        self.screen.blit(self.vignette,(0,0))
        self._hud()
        if self.msg_t>0 and self.state=='play': self._overlay(self.msg,RN3)
        if self.state=='countdown':
            self._draw_countdown()
        # Fade overlay
        if self.state in ('fade_out','round_title'):
            self.fade_surf.fill((0,0,0))
            self.fade_surf.set_alpha(self.fade_alpha if self.state=='fade_out' else 255)
            self.screen.blit(self.fade_surf,(0,0))
        if self.state=='round_title':
            self._draw_round_title()
        if self.state=='over':
            if self.A.get('gameover'):
                self.screen.blit(self.A['gameover'],(0,0))
                t=self.fs.render(f"Wynik: {self.score}   ENTER = nowa gra   ESC = wyjście",True,(200,180,140))
                self.screen.blit(t,(SW//2-t.get_width()//2,SH-50))
            else: self._overlay("GAME  OVER",FR1,f"Wynik: {self.score}")
        elif self.state=='clear':
            if self.A.get('victory'):
                self.screen.blit(self.A['victory'],(0,0))
                t=self.fs.render(f"Wynik: {self.score}   ENTER = następna runda",True,(200,180,100))
                self.screen.blit(t,(SW//2-t.get_width()//2,SH-50))
            else: self._overlay("RUNDA UKOŃCZONA!",RN3,f"Wynik: {self.score}")
        elif self.state=='pause':
            self._draw_pause()
        elif self.state=='pause_confirm':
            self._draw_pause()
            self._draw_pause_confirm()
        pygame.display.flip()

    def _draw_e(self,e):
        # Fix: sprite wrogów domyślnie w lewo → odwróć logikę jak u gracza
        key=f"{e.kind}_l" if e.right else f"{e.kind}_r"
        blit_char(self.screen,self.A.get(key,[]),e.frame,int(e.vx),int(e.vy),e.right)

    def _draw_name_input(self):
        """Ekran wpisywania imienia gracza"""
        # Tło jak menu
        bg=self.A.get('menu_main') or self.A.get('menu_bg')
        if bg: self.screen.blit(bg,(0,0))
        else: self.screen.fill((5,3,12))
        # Ciemna nakładka
        ov=pygame.Surface((SW,SH),pygame.SRCALPHA); ov.fill((0,0,0,160))
        self.screen.blit(ov,(0,0))
        cx=SW//2

        # Tytuł
        th=self.A.get('lbl_thalanor_title')
        if th: self.screen.blit(th,(cx-th.get_width()//2,70))

        # Duży podświetlony panel z napisem + polem tekstowym
        panel_w,panel_h=760,300
        panel_x,panel_y=cx-panel_w//2,210
        pulse=abs(math.sin(self.tick*0.1))*0.3+0.7
        panel=pygame.Surface((panel_w,panel_h),pygame.SRCALPHA)
        panel.fill((int(45*pulse),int(25*pulse),int(60*pulse),190))
        pygame.draw.rect(panel,(int(200*pulse),int(150*pulse),int(255*pulse)),(0,0,panel_w,panel_h),3)
        self.screen.blit(panel,(panel_x,panel_y))

        # Instrukcja - większa czcionka
        t1=self.fxl.render("WPISZ SWOJE IMIĘ",True,(240,200,90))
        for ox,oy in[(-2,0),(2,0),(0,-2),(0,2)]:
            self.screen.blit(self.fxl.render("WPISZ SWOJE IMIĘ",True,(90,55,15)),(cx-t1.get_width()//2+ox,panel_y+35+oy))
        self.screen.blit(t1,(cx-t1.get_width()//2,panel_y+35))

        # Pole tekstowe
        field_w=560; field_h=70
        field_x=cx-field_w//2; field_y=panel_y+125
        pygame.draw.rect(self.screen,(int(80*pulse),int(50*pulse),int(120*pulse)),
                         (field_x,field_y,field_w,field_h),0)
        pygame.draw.rect(self.screen,(int(220*pulse),int(170*pulse),int(255*pulse)),
                         (field_x,field_y,field_w,field_h),3)
        # Tekst + kursor
        cursor='|' if (self.tick//15)%2==0 else ''
        txt=self.fxl.render(self.player_name+cursor,True,(250,215,120))
        self.screen.blit(txt,(field_x+24,field_y+field_h//2-txt.get_height()//2))

        # Podpowiedź
        t2=self.fs.render("ENTER — zatwierdź    ESC — wróć do menu",True,(150,120,80))
        self.screen.blit(t2,(cx-t2.get_width()//2,panel_y+panel_h-35))

        # Walidacja
        if len(self.player_name)==0:
            hint=self.fm.render("Imię musi mieć przynajmniej 1 znak",True,(230,90,90))
            self.screen.blit(hint,(cx-hint.get_width()//2,panel_y+panel_h+25))

    def _draw_menu(self):
        """Menu główne z nową grafiką i podświetleniem opcji"""
        # Tło — nowe menu główne
        bg=self.A.get('menu_main') or self.A.get('menu_bg')
        if bg: self.screen.blit(bg,(0,0))
        else: self.screen.fill((5,3,12))

        # Pozycje opcji (center_y, wykryte z obrazka 1200x820)
        OPTS=[
            (433,"NOWA GRA",    True),
            (484,"RANKING",     True),
            (536,"OPCJE",       True),
            (586,"WYJŚCIE",     True),
            (636,"O PROJEKCIE", True),
        ]
        HIGHLIGHT_W=440; HIGHLIGHT_H=46
        cx=SW//2

        for i,(cy,name,active) in enumerate(OPTS):
            rect_x=cx-HIGHLIGHT_W//2
            rect_y=cy-HIGHLIGHT_H//2

            if i==self.menu_sel:
                # Podświetlenie wybranej opcji
                pulse=abs(math.sin(self.tick*0.07))*0.5+0.5
                ov=pygame.Surface((HIGHLIGHT_W,HIGHLIGHT_H),pygame.SRCALPHA)
                if active:
                    alpha=int(120*pulse+40)
                    ov.fill((180,130,20,alpha))
                    # Złota ramka
                    pygame.draw.rect(ov,(220,170,40,200),(0,0,HIGHLIGHT_W,HIGHLIGHT_H),2)
                else:
                    ov.fill((60,60,60,80))
                    pygame.draw.rect(ov,(80,80,80,120),(0,0,HIGHLIGHT_W,HIGHLIGHT_H),1)
                self.screen.blit(ov,(rect_x,rect_y))
            elif not active:
                # Przyciemnij zablokowane opcje
                ov=pygame.Surface((HIGHLIGHT_W,HIGHLIGHT_H),pygame.SRCALPHA)
                ov.fill((0,0,0,110))
                self.screen.blit(ov,(rect_x,rect_y))

        # Wskazówka nawigacji (dolny lewy róg)
        self.screen.blit(self.fs.render(
            "↑↓ — wybór    ENTER — wybierz    ESC — wyjście",
            True,(70,55,35)),(20,SH-30))

    def _draw_round_title(self):
        next_rnd = self.rnd + 1
        # Runda 2: gotowy obrazek
        if next_rnd == 2 and self.A.get('round2_scr'):
            self.screen.blit(self.A['round2_scr'],(0,0))
            return
        # Inne rundy: tekst
        cx=SW//2
        lore=ROUND_LORE.get(next_rnd,(f"RUNDA {next_rnd}","Nieznane Ziemie",'"Ciemność czeka..."'))
        title,subtitle,quote=lore
        t0=self.fs.render(f"— RUNDA {next_rnd} —",True,(130,100,60))
        self.screen.blit(t0,(cx-t0.get_width()//2,SH//2-180))
        pygame.draw.line(self.screen,(80,55,30),(cx-200,SH//2-155),(cx+200,SH//2-155),1)
        y=SH//2-130
        for line in title.split("\n"):
            t1=self.fb.render(line,True,(220,140,50))
            for ox,oy in[(-2,0),(2,0),(0,-2),(0,2)]:
                self.screen.blit(self.fb.render(line,True,(100,50,10)),(cx-t1.get_width()//2+ox,y+oy))
            self.screen.blit(t1,(cx-t1.get_width()//2,y)); y+=46
        self.screen.blit(self.fm.render(subtitle,True,(160,120,60)),(cx-self.fm.size(subtitle)[0]//2,y+10))
        pygame.draw.line(self.screen,(80,55,30),(cx-200,y+40),(cx+200,y+40),1)
        self.screen.blit(self.fs.render(quote,True,(100,85,55)),(cx-self.fs.size(quote)[0]//2,y+55))
        if (self.tick//20)%2==0:
            hint="SPACJA — Wkrocz   ENTER — Menu   ESC — Wyjście"
            self.screen.blit(self.fs.render(hint,True,(180,140,60)),(cx-self.fs.size(hint)[0]//2,SH//2+200))

    def _hud(self):
        import pygame as _pg
        def blbl(name,h=24):
            img=self.A.get(f'lbl_{name}')
            if not img: return None
            nw=max(1,int(img.get_width()*h/img.get_height()))
            return _pg.transform.smoothscale(img,(nw,h))
        def nnum(val,h=32):
            s=str(val); parts=[]; SP=3
            for ch in s:
                if ch.isdigit():
                    d=self.A.get(f'digit_{ch}')
                    if d:
                        nw=max(1,int(d.get_width()*h/d.get_height()))
                        parts.append(_pg.transform.smoothscale(d,(nw,h)))
            if not parts: return self.fm.render(str(val),True,GOLD)
            tw=sum(p.get_width() for p in parts)+SP*(len(parts)-1)
            surf=_pg.Surface((tw,h),_pg.SRCALPHA); x=0
            for p in parts: surf.blit(p,(x,0)); x+=p.get_width()+SP
            return surf

        _pg.draw.rect(self.screen,(8,5,18),(0,0,SW,OY))
        for x in range(SW):
            t=x/SW; r=int(40+t*30); b=int(70+t*30)
            _pg.draw.line(self.screen,(r,0,b),(x,OY-2),(x,OY-1))

        p=self.player; cx=SW//2
        SEP=OY//2+2
        _pg.draw.line(self.screen,(40,28,65),(0,SEP),(SW,SEP),1)

        # ── RZĄD 1: Wynik | THALANOR | Runda ─────────────────────────────────
        wl=blbl('wynik',24)
        if wl: self.screen.blit(wl,(14,6))
        ns=nnum(self.score,34); self.screen.blit(ns,(14,32))

        th=self.A.get('lbl_thalanor_title')
        if th:
            th_h=SEP-10
            th_nw=max(1,int(th.get_width()*th_h/th.get_height()))
            th_s=_pg.transform.smoothscale(th,(th_nw,th_h))
            self.screen.blit(th_s,(cx-th_nw//2,5))

        rl=blbl('runda',24)
        rn=nnum(self.rnd,34)
        if rl: self.screen.blit(rl,(SW-14-rl.get_width(),6))
        self.screen.blit(rn,(SW-14-rn.get_width(),32))

        # ── RZĄD 2 ────────────────────────────────────────────────────────────
        y2=SEP+6

        # ŻYCIA (lewo) - label, serduszka POD napisem
        zl=blbl('zycia',26)
        if zl: self.screen.blit(zl,(14,y2))
        for i in range(3):
            draw_heart(self.screen,22+i*26,y2+44,13,(i<p.lives))

        # POWER-UPS (środek) - większe etykiety, ikony, większe odstępy
        pw_data=[('bomby','pw_bomb_extra',p.bmax),('zasieg','pw_range_up',p.brange),('tempo','pw_speed_up',p.speed_lvl)]
        pw_x=cx-235
        for ln,ik,val in pw_data:
            lb=blbl(ln,22)
            if lb: self.screen.blit(lb,(pw_x,y2+4)); pw_x+=lb.get_width()+10
            ic=self.A.get(ik)
            if ic: self.screen.blit(_pg.transform.scale(ic,(30,30)),(pw_x,y2)); pw_x+=36
            nv=nnum(val,28); self.screen.blit(nv,(pw_x,y2+3)); pw_x+=nv.get_width()+34

        # WROGÓW (prawo) - label, cyfra POD napisem
        alive=sum(1 for e in self.enemies if e.alive)
        wl2=blbl('wrogow',24); wr=nnum(alive,30)
        if wl2: self.screen.blit(wl2,(SW-14-wl2.get_width(),y2))
        self.screen.blit(wr,(SW-14-wr.get_width(),y2+30))

        # ── DOLNY PASEK ────────────────────────────────────────────────────────
        bot=OY+ROWS*TILE
        _pg.draw.rect(self.screen,(8,5,18),(0,bot,SW,SH-bot))
        _pg.draw.line(self.screen,(40,28,65),(0,bot),(SW,bot),1)
        steer="WASD" if self.ctrl_wasd else "STRZAŁKI"
        ctrl=self.fs.render(f"STEROWANIE: {steer}    SPACJA=bomba    ESC=menu    F11=fullscreen",True,(65,52,82))
        self.screen.blit(ctrl,(cx-ctrl.get_width()//2,bot+10))

    def run(self):
        while True:
            keys=pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type==pygame.QUIT: pygame.quit();sys.exit()
                if ev.type==pygame.KEYDOWN:
                    k=ev.key
                    if k==pygame.K_F11:
                        self._toggle_fullscreen()
                    elif self.state=='menu':
                        ACTIVE=[0,1,2,3,4]
                        if k==pygame.K_ESCAPE: pygame.quit();sys.exit()
                        elif k==pygame.K_UP:
                            cur=ACTIVE.index(self.menu_sel) if self.menu_sel in ACTIVE else 0
                            self.menu_sel=ACTIVE[(cur-1)%len(ACTIVE)]
                            self._snd(self.s_click)
                        elif k in(pygame.K_DOWN,pygame.K_s):
                            cur=ACTIVE.index(self.menu_sel) if self.menu_sel in ACTIVE else 0
                            self.menu_sel=ACTIVE[(cur+1)%len(ACTIVE)]
                            self._snd(self.s_click)
                        elif k==pygame.K_RETURN:
                            if self.menu_sel==0: self.state='name_input'
                            elif self.menu_sel==1: self.state='ranking'
                            elif self.menu_sel==2: self.state='opcje'; self.opcje_return='menu'
                            elif self.menu_sel==3: pygame.quit();sys.exit()
                            elif self.menu_sel==4: self.state='o_projekcie'
                    elif self.state=='name_input':
                        if k==pygame.K_RETURN and len(self.player_name)>0:
                            self.rnd=1;self.score=0;self.state='round1_intro'
                        elif k==pygame.K_ESCAPE:
                            self.state='menu'
                        elif k==pygame.K_BACKSPACE:
                            self.player_name=self.player_name[:-1]
                        elif len(self.player_name)<15 and ev.unicode.isprintable() and ev.unicode.strip():
                            self.player_name+=ev.unicode
                    elif self.state=='round1_intro':
                        if k==pygame.K_SPACE:
                            self._new()
                        elif k==pygame.K_ESCAPE:
                            pygame.quit();sys.exit()
                    elif self.state=='play':
                        if k==pygame.K_ESCAPE: self.state='pause'; self.pause_sel=0
                        elif k==pygame.K_SPACE: self._bomb()
                    elif self.state=='over':
                        if k==pygame.K_SPACE:
                            self.rnd=1;self.score=0;self._new()
                        elif k==pygame.K_RETURN:
                            self.state='menu'
                        elif k==pygame.K_ESCAPE:
                            self.state='menu'
                    elif self.state=='clear':
                        if k==pygame.K_RETURN:
                            self.rnd+=1;self._new(keep=True)
                    elif self.state=='round_title':
                        if k==pygame.K_SPACE:
                            self.rnd+=1;self.fade_alpha=0;self._new(keep=True)
                        elif k==pygame.K_RETURN:
                            self.state='menu'
                        elif k==pygame.K_ESCAPE:
                            pygame.quit();sys.exit()
                    elif self.state=='demo_end':
                        if k==pygame.K_SPACE:
                            self.rnd=1;self.score=0;self._new()
                        elif k==pygame.K_RETURN:
                            self.state='menu'
                        elif k==pygame.K_ESCAPE:
                            pygame.quit();sys.exit()
                    elif self.state=='ranking':
                        if k in(pygame.K_ESCAPE,pygame.K_RETURN):
                            self.state='menu'
                    elif self.state=='o_projekcie':
                        if k in(pygame.K_ESCAPE,pygame.K_RETURN):
                            self.state='menu'
                    elif self.state=='opcje':
                        if k==pygame.K_ESCAPE:
                            self.state=self.opcje_return
                        elif k==pygame.K_UP:
                            self.opcje_sel=(self.opcje_sel-1)%4
                            self._snd(self.s_click)
                        elif k==pygame.K_DOWN:
                            self.opcje_sel=(self.opcje_sel+1)%4
                            self._snd(self.s_click)
                        elif k==pygame.K_LEFT:
                            if self.opcje_sel==0: self._toggle_fullscreen()
                            elif self.opcje_sel==1: self.ctrl_wasd=not self.ctrl_wasd
                            elif self.opcje_sel==2: self.difficulty=(self.difficulty-1)%3
                            elif self.opcje_sel==3: self._set_music_volume(-0.05)
                            self._snd(self.s_click)
                        elif k==pygame.K_RIGHT:
                            if self.opcje_sel==0: self._toggle_fullscreen()
                            elif self.opcje_sel==1: self.ctrl_wasd=not self.ctrl_wasd
                            elif self.opcje_sel==2: self.difficulty=(self.difficulty+1)%3
                            elif self.opcje_sel==3: self._set_music_volume(0.05)
                            self._snd(self.s_click)
                        elif k in(pygame.K_RETURN,pygame.K_SPACE):
                            if self.opcje_sel==0: self._toggle_fullscreen()
                            elif self.opcje_sel==1: self.ctrl_wasd=not self.ctrl_wasd
                            elif self.opcje_sel==2: self.difficulty=(self.difficulty+1)%3
                            elif self.opcje_sel==3: self._set_music_volume(0.05)
                            self._snd(self.s_click)
                    elif self.state=='pause':
                        if k==pygame.K_ESCAPE:
                            self.state='play'
                        elif k==pygame.K_UP:
                            self.pause_sel=(self.pause_sel-1)%3
                            self._snd(self.s_click)
                        elif k==pygame.K_DOWN:
                            self.pause_sel=(self.pause_sel+1)%3
                            self._snd(self.s_click)
                        elif k==pygame.K_RETURN:
                            if self.pause_sel==0:
                                self.state='play'
                            elif self.pause_sel==1:
                                self.opcje_return='pause'; self.state='opcje'
                            elif self.pause_sel==2:
                                self.state='pause_confirm'
                    elif self.state=='pause_confirm':
                        if k==pygame.K_ESCAPE:
                            self.state='pause'
                        elif k==pygame.K_RETURN:
                            save_to_ranking(self.player_name,self.score,self.rnd)
                            self.state='menu'
            self.update(keys)
            self.draw()
            self.clock.tick(FPS)

if __name__=='__main__':
    Game().run()
