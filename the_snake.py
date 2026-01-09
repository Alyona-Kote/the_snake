from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    def __init__(self):
        self.position = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.body_color = BOARD_BACKGROUND_COLOR

    def draw(self):
        pass


class Apple(GameObject):

    def randomize_position(self):
        return (randint(0, GRID_WIDTH) * GRID_SIZE, randint(0, GRID_HEIGHT) * GRID_SIZE)
    
    def __init__(self):
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position()
    
    def draw(self):
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    def __init__(self):
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    # Метод обновления направления после нажатия на кнопку
    def update_direction(self):
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        if self.direction == UP:
            new_head = (self.positions[0][0], self.positions[0][1] - GRID_SIZE)
        elif self.direction == DOWN:
            new_head = (self.positions[0][0], self.positions[0][1] + GRID_SIZE)
        elif self.direction == LEFT:
            new_head = (self.positions[0][0] - GRID_SIZE, self.positions[0][1])
        elif self.direction == RIGHT:
            new_head = (self.positions[0][0] + GRID_SIZE, self.positions[0][1])

        # Добавляем новую голову в начало списка позиций
        self.positions.insert(0, new_head)

        # Если длина змейки не изменилась, удаляем последний элемент
        if len(self.positions) > self.length:
            self.last = self.positions.pop()


    def draw(self):
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        return self.positions[0]

    def reset(self):
        # сбрасывает змейку в начальное состояние
        self.length = 1
        self.positions = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))
        self.direction = choice([UP, DOWN, LEFT, RIGHT])

# Функция обработки действий пользователя
def handle_keys(game_object):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT




def check_collision(snake, apple):
        # Тут опишите основную логику игры.
        # Проверка столкновения с яблоком
    if snake.get_head_position() == apple.position:
        snake.length += 1
        apple.randomize_position()

        # Проверка столкновений с собственным телом
    for pos in snake.positions[1:]:
        if snake.get_head_position() == pos:
            snake.reset()
            break

def main():
    pygame.init()
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()
        check_collision(snake, apple)
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()