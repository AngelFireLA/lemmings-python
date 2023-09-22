import pygame
import random
import time

pygame.init()
pygame.mixer.init()


class Jeu:

    def __init__(self, plan_grotte: list):
        # Au moins ça marche dynamiquement pour n'importe quel carte, en prenant la première case libre trouvée comme entrée

        self.index_entree: tuple = None
        self.grotte_visuelle = plan_grotte
        self.grotte = []

        # Remplace les espaces de la grotte pour que de manière interne ça soit plus simple de vérifier sdi la case est occupée ou non
        self.corrige_grotte()
        self.lemmings = []
        self.lemmings_a_demarrer = []
        self.lemmings_en_grotte = []
        self.lemmings_sortis = []

        self.fenetre = pygame.display.set_mode((len(self.grotte[0]) * 50, len(self.grotte) * 50))

    def corrige_grotte(self):
        for i in range(len(self.grotte_visuelle)):
            ligne = self.grotte_visuelle[i]
            self.grotte.append([])
            for j in range(len(ligne)):
                tile = ligne[j]
                if tile == ' ' or tile == '':
                    if not self.index_entree:
                        self.index_entree = (j, i)

                    self.grotte[i].append(None)
                    continue

                self.grotte[i].append(tile)

    def demarrer_pygame(self):
        self.map_to_image()
        self.lemmings_a_demarrer = self.lemmings.copy()

        while True:
            background = pygame.image.load("output.png").convert_alpha()
            self.fenetre.blit(background, (0, 0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    new_lemming = Lemming(self)
                    self.lemmings.append(new_lemming)
                    self.lemmings_a_demarrer.append(new_lemming)
                    print("Nouveau Lemming démarrer")

                elif event.type == pygame.MOUSEBUTTONDOWN:  # Left mouse button click
                    # Get the mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Calculate the tile indexes
                    tile_x = mouse_x // 50
                    tile_y = mouse_y // 50

                    # Ensure the tile indexes are within bounds
                    if 0 <= tile_x < len(self.grotte[0]) and 0 <= tile_y < len(self.grotte):
                        if event.button == 1:
                            tile = self.grotte[tile_y][tile_x]
                            if tile and not isinstance(tile, Lemming):
                                print("Changed le tile", tile_x, tile_y, "a rien")
                                self.grotte[tile_y][tile_x] = None

                                self.map_to_image()
                                background = pygame.image.load("output.png")
                                self.fenetre.blit(background, (0, 0))
                                pygame.display.flip()
                        if event.button == 3:
                            tile = self.grotte[tile_y][tile_x]
                            if not tile:
                                self.grotte[tile_y][tile_x] = "#"
                                print("Changed le tile", tile_x, tile_y, "a #")
                                self.map_to_image()
                                background = pygame.image.load("output.png")
                                self.fenetre.blit(background, (0, 0))
                                pygame.display.flip()

            self.tour()
            pygame.display.flip()
            time.sleep(0.01)

    def map_to_image(self):
        from PIL import Image
        # Calculate the dimensions of the image
        height = 50 * len(self.grotte)
        width = 50 * len(self.grotte[0])

        # Create a blank image with the calculated dimensions
        image = Image.new('RGB', (width, height))

        # Iterate over the list and place tiles on the image
        for row_index, row in enumerate(self.grotte):
            for col_index, tile in enumerate(row):
                if not isinstance(tile, Lemming):
                    # Load the tile image
                    tile_image = Image.open(f"{str(tile)}.png")
                else:
                    tile_image = Image.open("None.png")

                # Calculate the position to place the tile
                x = col_index * 50
                y = row_index * 50

                # Paste the tile onto the image
                image.paste(tile_image, (x, y))

        # Save or display the final image
        image.save('output.png')

    def tour(self):
        if not self.grotte[self.index_entree[1]][self.index_entree[0]] and self.lemmings_a_demarrer:
            self.grotte[self.index_entree[1]][self.index_entree[0]] = self.lemmings_a_demarrer[-1]
            self.lemmings_en_grotte.append(self.lemmings_a_demarrer[-1])
            self.lemmings_a_demarrer.pop()

        for lemming in self.lemmings_en_grotte:
            lemming: Lemming
            self.grotte = lemming.action(self.grotte)
            if lemming.sorti:
                print("enlevé lemming")
                self.lemmings_en_grotte.remove(lemming)
                self.lemmings_sortis.append(lemming)
            image = pygame.image.load("lemming.png")
            rect = image.get_rect()
            rect.x = lemming.pygame_x
            rect.y = lemming.pygame_y
            if lemming.direction == 1:
                image = pygame.transform.flip(image, True, False)
            self.fenetre.blit(image, rect)


class Lemming:
    def __init__(self, jeu: Jeu):
        self.jeu = jeu
        self.pygame_x = self.jeu.index_entree[0] * 50
        self.pygame_y = self.jeu.index_entree[1] * 50
        self.x = self.pygame_x // 50
        self.y = self.pygame_y // 50
        self.sorti = False
        self.prendre_toile = random.choice([True, False])

        self.direction = -1

    def __repr__(self):
        return 'lemming'

    def sortir(self, grotte):
        self.sorti = True
        return grotte

    def le_void(self, grotte):
        print("LE VOID")
        afficher_grotte(grotte)
        pygame.mixer.music.load('roblox-death-sound_1.mp3')
        pygame.mixer.music.set_volume(1)  # Set the volume to 50%
        pygame.mixer.music.play()

        grotte[self.y][self.x] = None
        grotte = self.sortir(grotte)
        return grotte

    def action(self, grotte):

        try:
            if not grotte[self.y + 1][self.x]:
                self.pygame_y += 10

                if self.pygame_y % 50 == 0:
                    grotte[self.y][self.x] = None
                    grotte[self.y + 1][self.x] = None
                    grotte[self.y + 1][self.x] = self
                    self.y += 1
                    afficher_grotte(grotte)

                return grotte
        except IndexError:
            return self.le_void(grotte)

        try:
            if grotte[self.y + 1][self.x] == "toile" and self.prendre_toile and not grotte[self.y + 2][self.x]:
                self.pygame_y += 100
                grotte[self.y][self.x] = None
                grotte[self.y + 2][self.x] = self
                self.y += 2
                afficher_grotte(grotte)
                self.prendre_toile = random.choice([True, False])

                return grotte
        except IndexError:
            return self.le_void(grotte)
        if grotte[self.y + 1][self.x] == "tank":

            return self.le_void(grotte)

        try:
            prochaine_case = grotte[self.y][self.x + self.direction]

        except IndexError:
            prochaine_case = "Hors de la map"

        if not prochaine_case or prochaine_case == 'Sorti':
            if prochaine_case == 'Sorti' and (self.x+self.direction > 0 or self.direction == 1):
                pygame.mixer.music.load('he-he-he-haw.mp3')

                pygame.mixer.music.set_volume(0.1)  # Set the volume to 50%
                pygame.mixer.music.play()
                grotte[self.y][self.x] = None
                grotte = self.sortir(grotte)
                return grotte
            if self.x > 0 or self.direction == 1:
                self.pygame_x += self.direction * 10
                if self.pygame_x % 50 == 0:
                    grotte[self.y][self.x] = None
                    grotte[self.y][self.x + self.direction] = self
                    self.x += self.direction
                    afficher_grotte(grotte)

                return grotte
        self.direction = -self.direction
        self.pygame_y = self.y * 50
        self.pygame_x = self.x * 50
        # pygame.mixer.music.load('ouch.mp3')
        # pygame.mixer.music.set_volume(1)  # Set the volume to 50%
        # pygame.mixer.music.play()
        return grotte


def afficher_grotte(grotte):
    debug = False

    if debug:
        print()
        for g in grotte:
            print(g)
        print()


if __name__ == '__main__':
    grotte_lv_1 = [
        [' ', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['#', '#', '#', '#', 'toile', '#', '#', '#', '#', '#', '#', '#', '#', '#', ' '],
        ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', ''],
        ['', '#', '#', '#', 'tank', '#', ' ', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ''],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', ''],
        ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', ''],
        [' ', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', ' '],
        ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', ''],
        ['', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ''],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', ''],
        ['', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', '', '', '', '', '', ''],
        [' ', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],
        [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', 'Sorti'],
        ['#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#'],


    ]

    jeu1 = Jeu(grotte_lv_1)
    jeu1.demarrer_pygame()
