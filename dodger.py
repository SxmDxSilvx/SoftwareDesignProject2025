import pygame
import random
import sys
import os
from pygame.locals import *

# ====== Configuration ======
WINDOWWIDTH = 600
WINDOWHEIGHT = 600
TEXTCOLOR = (0, 0, 0)
BACKGROUNDCOLOR = (245, 227, 93)
FPS = 60
BADDIEMINSIZE = 20
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 3
ADDNEWBADDIERATE = 30
PLAYERMOVERATE = 5

# ====== Helpers ======
def terminate():
    pygame.quit()
    sys.exit()

def waitForPlayerToPressKey():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:  # ESC quits
                    terminate()
                return

def playerHasHitBaddie(playerRect, baddies):
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def drawText(text, font, surface, x, y):
    textobj = font.render(text, True, TEXTCOLOR)
    textrect = textobj.get_rect()
    textrect.topleft = (int(x), int(y))
    surface.blit(textobj, textrect)

# ====== Prépare le chemin de base (dossier du script) ======
# Si __file__ n'existe pas (ex: environnements interactifs), on tombe sur getcwd()
try:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_PATH = os.getcwd()

def path_in_base(filename):
    return os.path.join(BASE_PATH, filename)

# ====== Init pygame ======
pygame.init()
# Facultatif : pre_init pour réduire latence son (si besoin)
# pygame.mixer.pre_init(44100, -16, 2, 512)
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
pygame.display.set_caption('Dodger')
pygame.mouse.set_visible(False)

# ====== Fonts ======
font = pygame.font.SysFont(None, 48)

# ====== Sounds (robuste) ======
gameOverSound = None
background_music_loaded = False
try:
    gameover_path = path_in_base('gameover.wav')
    if os.path.isfile(gameover_path):
        gameOverSound = pygame.mixer.Sound(gameover_path)
    else:
        print(f"Info: '{gameover_path}' introuvable — le son de fin de jeu sera désactivé.")
except pygame.error as e:
    print("Erreur pygame lors du chargement du son 'gameover.wav':", e)
    gameOverSound = None

try:
    bgm_path = path_in_base('background.mid')
    if os.path.isfile(bgm_path):
        pygame.mixer.music.load(bgm_path)
        background_music_loaded = True
    else:
        print(f"Info: '{bgm_path}' introuvable — musique de fond désactivée.")
except pygame.error as e:
    print("Erreur pygame lors du chargement de 'background.mid':", e)
    background_music_loaded = False

# ====== Images (robuste : placeholder si manquante) ======
def load_image_or_placeholder(filename, default_size=(50,50), fill_color=(200,0,0)):
    full = path_in_base(filename)
    if os.path.isfile(full):
        try:
            img = pygame.image.load(full).convert_alpha()
            return img
        except pygame.error as e:
            print(f"Erreur lors du chargement de l'image '{full}':", e)
    # placeholder
    surf = pygame.Surface(default_size, pygame.SRCALPHA)
    surf.fill(fill_color)
    # petit bord pour rendre visible le placeholder
    pygame.draw.rect(surf, (0,0,0), surf.get_rect(), 2)
    return surf

playerImage = load_image_or_placeholder('player.png', default_size=(50,50), fill_color=(0,120,200))
playerRect = playerImage.get_rect()
baddieImage = load_image_or_placeholder('baddie.png', default_size=(20,20), fill_color=(200,50,50))

# ====== Écran de démarrage ======
windowSurface.fill(BACKGROUNDCOLOR)
drawText('Dodger', font, windowSurface, int(WINDOWWIDTH / 3), int(WINDOWHEIGHT / 3))
drawText('Press a key to start.', font, windowSurface, int(WINDOWWIDTH / 3) - 30, int(WINDOWHEIGHT / 3) + 50)
pygame.display.update()
waitForPlayerToPressKey()

topScore = 0
while True:
    # Set up the start of the game.
    baddies = []
    score = 0
    playerRect.topleft = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT - 50))
    moveLeft = moveRight = moveUp = moveDown = False
    reverseCheat = slowCheat = False
    baddieAddCounter = 0

    if background_music_loaded:
        try:
            pygame.mixer.music.play(-1, 0.0)
        except pygame.error as e:
            print("Impossible de lancer la musique de fond:", e)

    while True:  # boucle du jeu
        score += 1

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN:
                
                if event.key == K_z:
                    reverseCheat = True
                if event.key == K_x:
                    slowCheat = True
                if event.key == K_LEFT or event.key == K_a:
                    moveRight = False
                    moveLeft = True
                if event.key == K_RIGHT or event.key == K_d:
                    moveLeft = False
                    moveRight = True
                if event.key == K_UP or event.key == K_w:
                    moveDown = False
                    moveUp = True
                if event.key == K_DOWN or event.key == K_s:
                    moveUp = False
                    moveDown = True

            if event.type == KEYUP:
                if event.key == K_z:
                    reverseCheat = False
                    score = 0
                if event.key == K_x:
                    slowCheat = False
                    score = 0
                if event.key == K_ESCAPE:
                    terminate()

                if event.key == K_LEFT or event.key == K_a:
                    moveLeft = False
                if event.key == K_RIGHT or event.key == K_d:
                    moveRight = False
                if event.key == K_UP or event.key == K_w:
                    moveUp = False
                if event.key == K_DOWN or event.key == K_s:
                    moveDown = False

            if event.type == MOUSEMOTION:
                playerRect.centerx = event.pos[0]
                playerRect.centery = event.pos[1]

        # Ajout de nouveaux baddies
        if not reverseCheat and not slowCheat:
            baddieAddCounter += 1
        if baddieAddCounter >= ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            newBaddie = {
                'rect': pygame.Rect(random.randint(0, WINDOWWIDTH - baddieSize), 0 - baddieSize, baddieSize, baddieSize),
                'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                'surface': pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
            }
            baddies.append(newBaddie)


        # Déplacement du joueur
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

        # Déplacement des baddies
        for b in baddies:
            if not reverseCheat and not slowCheat:
                b['rect'].move_ip(0, b['speed'])
            elif reverseCheat:
                b['rect'].move_ip(0, -5)
            elif slowCheat:
                b['rect'].move_ip(0, 1)

        # Supprimer ceux passés en bas
        for b in baddies[:]:
            if b['rect'].top > WINDOWHEIGHT:
                baddies.remove(b)

        # Dessin
        windowSurface.fill(BACKGROUNDCOLOR)
        drawText(f'Score: {score}', font, windowSurface, 10, 0)
        drawText(f'Top Score: {topScore}', font, windowSurface, 10, 40)
        windowSurface.blit(playerImage, playerRect)
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])
        pygame.display.update()

        # Collision ?
        if playerHasHitBaddie(playerRect, baddies):
            if score > topScore:
                topScore = score
            break

        mainClock.tick(FPS)

    # Fin du jeu
    if background_music_loaded:
        try:
            pygame.mixer.music.stop()
        except pygame.error as e:
            print("Erreur en stoppant la musique:", e)

    if gameOverSound is not None:
        try:
            gameOverSound.play()
        except pygame.error as e:
            print("Impossible de jouer gameOverSound:", e)
    else:
        print("gameOverSound non disponible — aucun son joué.")

    drawText('GAME OVER', font, windowSurface, int(WINDOWWIDTH / 3), int(WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, int(WINDOWWIDTH / 3) - 80, int(WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()

    if gameOverSound is not None:
        try:
            gameOverSound.stop()
        except pygame.error:
            pass
