import pygame
import pyscroll
import pytmx

from sprites.player import Mahé

class Game:

    def __init__(self, screen, player):

        self.screen = screen
        self.player = player

        self.group = pygame.sprite.Group()
        self.group.add(self.player)

        self.clock = pygame.time.Clock()

        self.paused = False
        self.show_help = False

        self.font = pygame.font.Font(None, 40)
        self.big_font = pygame.font.Font(None, 70)


    
    def handle_input(self):

        pressed = pygame.key.get_pressed()

        if pressed[pygame.K_UP]:
            self.player.move_up()

        elif pressed[pygame.K_DOWN]:
            self.player.move_down()

        elif pressed[pygame.K_LEFT]:
            self.player.move_left()

        elif pressed[pygame.K_RIGHT]:
            self.player.move_right()


   
    def draw_pause(self):

        overlay = pygame.Surface((900,600))
        overlay.set_alpha(180)
        overlay.fill((0,0,0))

        self.screen.blit(overlay,(0,0))

        title = self.big_font.render("PAUSE", True, (255,255,255))
        self.screen.blit(title,(380,150))

        lines = [
            "s : reprendre",
            "a : aide",
            "d : menu principal"
        ]

        for i,line in enumerate(lines):

            text = self.font.render(line,True,(255,255,255))
            self.screen.blit(text,(350,300+i*40))


    
    def draw_help(self):

        overlay = pygame.Surface((900,600))
        overlay.set_alpha(200)
        overlay.fill((0,0,0))

        self.screen.blit(overlay,(0,0))

        title = self.big_font.render("AIDE", True, (255,255,255))
        self.screen.blit(title,(400,150))

        lines = [
            "Flèches : déplacement",
            "z : pause",
            "q : reprendre",
            "d : menu principal"
        ]

        for i,line in enumerate(lines):

            text = self.font.render(line,True,(255,255,255))
            self.screen.blit(text,(320,300+i*40))


   
    def run(self):

        running = True

        while running:

            self.clock.tick(60)

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False


                if event.type == pygame.KEYDOWN:

                 
                    if event.key == pygame.K_z:
                        self.paused = not self.paused
                        self.show_help = False

                    if self.paused:

                        if event.key == pygame.K_s:
                            self.paused = False
                            self.show_help = False

                        if event.key == pygame.K_a:
                            self.show_help = not self.show_help

                        if event.key == pygame.K_d:
                            running = False




            
            if not self.paused:

                self.handle_input()
                self.group.update()

                self.screen.fill((0,0,0))
                self.group.draw(self.screen)


            
            else:

                self.screen.fill((0,0,0))
                self.group.draw(self.screen)

                if self.show_help:
                    self.draw_help()
                else:
                    self.draw_pause()


            pygame.display.flip()