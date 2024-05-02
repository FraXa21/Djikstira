import pygame as pg
from os import environ
from sprites import *
from settings import *

environ['SDL_VIDEO_CENTERED'] = '1'


class CommandListPopup:
    def __init__(self):
        self.width = 400
        self.height = 200
        self.font = pg.font.Font(None, 24)
        self.surface = pg.Surface((self.width, self.height))
        self.surface.fill(WHITE)
        self.commands = [
            "Command List:",
            "- Press 'S' to set the start point.",
            "- Press 'E' to set the end point.",
            "- Press 'Ctrl + R' to run the algorithm.",
            "- Press 'Ctrl + C' to clear the board.",
            "- Press 'H' to show this command list.",
            "- Click left mouse button to place walls.",
            "- Click right mouse button to remove walls."
        ]
        self.show_popup()

    def show_popup(self):
        pg.display.set_caption("Command List")
        screen = pg.display.set_mode((self.width, self.height))
        clock = pg.time.Clock()
        running = True

        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_ESCAPE:
                        running = False

            # Draw commands on the popup surface
            y_offset = 10
            for command in self.commands:
                text_surface = self.font.render(command, True, BLACK)
                self.surface.blit(text_surface, (10, y_offset))
                y_offset += 25

            screen.blit(self.surface, (0, 0))
            pg.display.flip()
            clock.tick(FPS)

        pg.display.quit()


class Dijkstra:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption("Dijkstra")
        self.clock = pg.time.Clock()
        self.running = True
        self.start, self.end = None, None
        self.algo_run, self.algo_end = False, False

        self.command_list_popup = None

    def new(self):
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.visited, self.path = pg.sprite.Group(), pg.sprite.Group()
        self.graph = Graph(self)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    if self.start:
                        self.clear_board()
                        self.graph.distances[self.graph.start[0]][self.graph.start[1]] = float('inf')
                        self.start.kill()
                    self.start = Start(self, *(pg.mouse.get_pos()))
                if event.key == pg.K_e:
                    if self.end:
                        self.clear_board()
                        self.end.kill()
                    self.end = End(self, *(pg.mouse.get_pos()))
                if event.key == pg.K_r and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.algo_run, self.algo_end = True, True
                    self.algo_time = pg.time.get_ticks()
                    self.graph.dijkstra(self.graph.start, self.graph.end)
                if event.key == pg.K_c and pg.key.get_mods() & pg.KMOD_CTRL:
                    self.clear_board()
                if event.key == pg.K_h:
                    self.show_command_list()

            if pg.mouse.get_pressed()[0]:
                Wall(self, *(pg.mouse.get_pos()))

    def update(self):
        self.all_sprites.update()

        if self.algo_run and pg.time.get_ticks() - self.algo_time > 15:
            self.algo_time = pg.time.get_ticks()
            a = self.graph.dijkstra(self.graph.start, self.graph.end)
            if a is False:
                self.algo_run = False

        if self.algo_end and not self.algo_run and pg.time.get_ticks() - self.algo_time - 300 > 500:
            node = (self.end.rect.topleft[1] // 16, self.end.rect.topleft[0] // 16)
            while node != (self.start.rect.topleft[1] // 16, self.start.rect.topleft[0] // 16):
                Shortest(self, node[1], node[0])
                node = self.graph.prev[(node[0], node[1])]

    def draw(self):
        self.screen.fill(GREY)
        self.all_sprites.draw(self.screen)

        for i in range(1, 48):
            pg.draw.line(self.screen, WHITE, (i * TILE_SIZE, 0), (i * TILE_SIZE, HEIGHT))
        for j in range(1, 32):
            pg.draw.line(self.screen, WHITE, (0, j * TILE_SIZE), (WIDTH, j * TILE_SIZE))

        pg.display.flip()

    def clear_board(self):
        self.algo_end = False
        for sprite in self.visited:
            sprite.kill()
        for sprite in self.path:
            sprite.kill()
        for sprite in self.walls:
            sprite.kill()
        self.graph.distances = [[float('inf')] * 48 for i in range(32)]
        self.graph.prev, self.graph.walls = {}, []
        self.graph.start = (self.start.rect.topleft[1] // 16, self.start.rect.topleft[0] // 16)
        self.graph.pq = [[0, self.graph.start]]
        self.graph.distances[self.graph.start[0]][self.graph.start[1]] = 0

    def show_command_list(self):
        self.command_list_popup = CommandListPopup()


# main loop
g = Dijkstra()
g.new()
while g.running:
    g.run()

pg.quit()
