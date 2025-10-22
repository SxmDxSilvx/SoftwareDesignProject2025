import pygame, random, sys
from pygame.locals import *

WINDOWWIDTH = 700
WINDOWHEIGHT = 700
TEXTCOLOR = (0, 6, 200) #rouge, bleu, vert -> de 0 à 255
BACKGROUNDCOLOR = (255, 255, 255) #la couleur du jeu
FPS = 60
BADDIEMINSIZE = 7
BADDIEMAXSIZE = 40
BADDIEMINSPEED = 1
BADDIEMAXSPEED = 8
ADDNEWBADDIERATE = 6
PLAYERMOVERATE = 5

bloqueur=None

def terminate(): #fonction
    pygame.quit() #fonction pour éteindre 
    sys.exit() # fonction pour éteindre le code

def waitForPlayerToPressKey(): #attendre que le joueur appuie sur une touche
    while True: #tant que la condition est vraie
        for event in pygame.event.get():
            if event.type == QUIT: #un évenement en rapport avec le clavier car .type/la croix rouge
                terminate()
            if event.type == KEYDOWN: #la touche pressée, sa position
                if event.key == K_ESCAPE: # Pressing ESC quits. #la touche exacte esc, mon présice la touche exacte
                    terminate()
                return

def playerHasHitBaddie(playerRect, baddies): #les méchants
    for b in baddies:
        if playerRect.colliderect(b['rect']):
            return True
    return False

def drawText(text, font, surface, x, y): 
    textobj = font.render(text, 1, TEXTCOLOR) #fonction render-> afficher le texte, prend le paramètre text
    textrect = textobj.get_rect() #le rectangle pour le texte
    textrect.topleft = (x, y) #la position du texte dans la fenetre
    surface.blit(textobj, textrect) #afficher dans la fenetre

# Set up pygame, the window, and the mouse cursor.
pygame.init() #commencer pygame 
mainClock = pygame.time.Clock() #horloge
windowSurface = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))#créer la fenetre, la surface
pygame.display.set_caption('Sam') #titre de la fenetre en haut
pygame.mouse.set_visible(False) #on ne voit pas la souris

# Set up the fonts.
font = pygame.font.SysFont(None, 48) #la police d'écriture

# Set up sounds.
gameOverSound = pygame.mixer.Sound('gameover.wav')
pygame.mixer.music.load('background.mid')

# Set up images.
playerImage = pygame.image.load('player.png')
playerRect = playerImage.get_rect() #le tour du personnage, le carré autour du personnage, quand on otuche le carré on est mort, zone de contact
baddieImage = pygame.image.load('baddie.png')

# Show the "Start" screen.
windowSurface.fill(BACKGROUNDCOLOR) #remplir la fenetre par une couleur
drawText('Dodger', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3)) #texte quand on ouvre le jeu
drawText('Press a key to start.', font, windowSurface, (WINDOWWIDTH / 3) - 30, (WINDOWHEIGHT / 3) + 50)
pygame.display.update() #mise à jour de tout ce qu'on a noté sur pygame.display
waitForPlayerToPressKey() #on lance la fonction

topScore = 0
while True:
    # Set up the start of the game.
    baddies = []
    score = 0
    playerRect.topleft = (WINDOWWIDTH / 2, WINDOWHEIGHT /2) #commencer au milieu du jeu
    moveLeft = moveRight = moveUp = moveDown = False
    reverseCheat = slowCheat = False
    baddieAddCounter = 0
    pygame.mixer.music.play(-1, 0.0)

    while True: # The game loop runs while the game part is playing.
        score += 1 # Increase score.

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            if event.type == KEYDOWN: #touche en bas donc touche
                if bloqueur is None:
                    bloqueur=event.key
                    if event.key == K_z:
                        reverseCheat = True
                    if event.key == K_x:
                      slowCheat = True
                    if event.key == K_LEFT:
                        moveRight = False
                        moveLeft = True
                    if event.key == K_RIGHT:
                        moveLeft = False
                        moveRight = True
                    if event.key == K_UP:
                        moveDown = False
                        moveUp = True
                    if event.key == K_DOWN:
                        moveUp = False
                        moveDown = True

            if event.type == KEYUP:
                if event.key==bloqueur:
                    bloqueur=None
                    if event.key == K_z:
                        reverseCheat = False
                        score = 0
                    if event.key == K_x:
                        slowCheat = False
                        score = 0
                    if event.key == K_ESCAPE:
                            terminate()

                    if event.key == K_LEFT:
                        moveLeft = False
                    if event.key == K_RIGHT:
                        moveRight = False
                    if event.key == K_UP:
                        moveUp = False
                    if event.key == K_DOWN:
                        moveDown = False

            #if event.type == MOUSEMOTION:
                # If the mouse moves, move the player where to the cursor.
                # playerRect.centerx = event.pos[0]
                # playerRect.centery = event.pos[1]
        # Add new baddies at the top of the screen, if needed.
        if not reverseCheat and not slowCheat:
            baddieAddCounter += 1
        if baddieAddCounter == ADDNEWBADDIERATE:
            baddieAddCounter = 0
            baddieSize = random.randint(BADDIEMINSIZE, BADDIEMAXSIZE)
            newBaddie = {'rect': pygame.Rect(random.randint(0, WINDOWWIDTH - baddieSize), 0 - baddieSize, baddieSize, baddieSize),
                        'speed': random.randint(BADDIEMINSPEED, BADDIEMAXSPEED),
                        'surface':pygame.transform.scale(baddieImage, (baddieSize, baddieSize)),
                        }

            baddies.append(newBaddie)

        # Move the player around.
        if moveLeft and playerRect.left > 0:
            playerRect.move_ip(-1 * PLAYERMOVERATE, 0)
        if moveRight and playerRect.right < WINDOWWIDTH:
            playerRect.move_ip(PLAYERMOVERATE, 0)
        if moveUp and playerRect.top > 0:
            playerRect.move_ip(0, -1 * PLAYERMOVERATE)
        if moveDown and playerRect.bottom < WINDOWHEIGHT:
            playerRect.move_ip(0, PLAYERMOVERATE)

       



        # Move the baddies down.
        for b in baddies:
            if not reverseCheat and not slowCheat:
                b['rect'].move_ip(0, b['speed'])
            elif reverseCheat:
                b['rect'].move_ip(0, -5)
            elif slowCheat:
                b['rect'].move_ip(0, 1)

        # Delete baddies that have fallen past the bottom.
        for b in baddies[:]:
            if b['rect'].top > WINDOWHEIGHT:
                baddies.remove(b)

        # Draw the game world on the window.
        windowSurface.fill(BACKGROUNDCOLOR)

        # Draw the score and top score.
        drawText('Score: %s' % (score), font, windowSurface, 10, 0)
        drawText('Top Score: %s' % (topScore), font, windowSurface, 10, 40)

        # Draw the player's rectangle.
        windowSurface.blit(playerImage, playerRect)

        # Draw each baddie.
        for b in baddies:
            windowSurface.blit(b['surface'], b['rect'])

        pygame.display.update()

        # Check if any of the baddies have hit the player.
        if playerHasHitBaddie(playerRect, baddies):
            if score > topScore:
                topScore = score # set new top score
            break

        mainClock.tick(FPS)

    # Stop the game and show the "Game Over" screen.
    pygame.mixer.music.stop()
    gameOverSound.play()

    drawText('GAME OVER', font, windowSurface, (WINDOWWIDTH / 3), (WINDOWHEIGHT / 3))
    drawText('Press a key to play again.', font, windowSurface, (WINDOWWIDTH / 3) - 80, (WINDOWHEIGHT / 3) + 50)
    pygame.display.update()
    waitForPlayerToPressKey()

    gameOverSound.stop()