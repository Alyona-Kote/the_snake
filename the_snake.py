from random import choice, randint
import pygame

"""Игра «Ухожор».
Цель: управлять Ван Гогом, подбирать отрезанные уши и творить шедевры.
"""


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

# Цвета БУДУТ МЕНЯТЬСЯ на изображения:
BOARD_BACKGROUND_COLOR = (51, 153, 102)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (204, 153, 51)
SNAKE_COLOR = (153, 51, 0)


# Скорость движения змейки:
SPEED = 3

# Загрузка изображений (поместите файлы в ту же папку, что и скрипт)
try:
    SNAKE_HEAD = pygame.image.load("snake_head.png").convert_alpha()
    SNAKE_BODY = pygame.image.load("snake_body.png").convert_alpha()
    APPLE_IMAGE = pygame.image.load("apple.png").convert_alpha()
except pygame.error as e:
    print(f"Ошибка загрузки изображений: {e}")
    print("Используются цветные квадраты вместо изображений.")
    SNAKE_HEAD = None
    SNAKE_BODY = None
    APPLE_IMAGE = None


# Масштабирование изображений под размер ячейки
if SNAKE_HEAD:
    SNAKE_HEAD = pygame.transform.scale(SNAKE_HEAD, (GRID_SIZE, GRID_SIZE))
if SNAKE_BODY:
    SNAKE_BODY = pygame.transform.scale(SNAKE_BODY, (GRID_SIZE, GRID_SIZE))
if APPLE_IMAGE:
    APPLE_IMAGE = pygame.transform.scale(APPLE_IMAGE, (GRID_SIZE, GRID_SIZE))


# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption("УХОЖОР")

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов (условные "змейка" и "яблоко" -
    на самом деле Ван Гог и уши, названия классов оставлены для удобства
    проверки).
    Атрибуты:
        position: Координаты объекта (x, y).
        body_color: Цвет объекта (используется, если нет изображения).
    """

    def __init__(self):
        """Инициализация объекта в центре экрана."""
        self.position = (SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)
        self.body_color = BOARD_BACKGROUND_COLOR

    def draw(self):
        """Метод для отрисовки объекта, переопределяется в подклассах."""
        pass


class Apple(GameObject):
    """Класс, описывающий объект, который нужно собрать. Вместо яблока у нас
    будут уши.
        Наследуется от GameObject.
    """

    def randomize_position(self):
        """Генерит случайную позицию для уха на поле. Возвращает случайные
        координаты (x, y) в пределах игрового поля.
        """
        pos = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )
        return pos

    def __init__(self):
        """Инициализация уха."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.position = self.randomize_position()

    def draw(self):
        """Отрисовывает ухо на экране."""
        if APPLE_IMAGE:
            screen.blit(APPLE_IMAGE, self.position)
        else:
            rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий Ван Гога — главного игрока.
    Наследуется от GameObject.
    """

    def __init__(self):
        """Инициализация Ван Гога: начальная длина, позиция и направление."""
        super().__init__()  # Вызов конструктора родительского класса
        self.length = 1  # Начальная длина
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = RIGHT  # Начальное направление движения
        self.next_direction = None  # Будущее направление
        self.body_color = SNAKE_COLOR
        self.last = None  # Последняя позиция удалённой картины(для затирания)

    def update_direction(self):
        """Обновляет направление движения, если нажали на клавишу."""
        if self.next_direction:  # Если есть новое направление
            self.direction = self.next_direction  # Меняем текущее направление
            self.next_direction = None  # Очищаем буфер

    def move(self):
        """Двигает Ван Гога на один шаг в текущем направлении."""
        head_x, head_y = self.positions[0]
        dx, dy = self.direction

        # Вычисляем новую позицию головы с учётом выхода за границы
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT

        new_head = (new_x, new_y)

        # Добавляем новую голову
        self.positions.insert(0, new_head)

        # Если длина не изменилась — удаляем последнюю картину
        if len(self.positions) > self.length:
            self.last = self.positions.pop()  # Сохраняем для затирания
        else:
            self.last = None

    def draw(self):
        """Отрисовывает Ван Гога на экране."""
        # Картины (всё, кроме головы)
        for position in self.positions[1:]:
            if SNAKE_BODY:
                screen.blit(SNAKE_BODY, position)
            else:
                rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, self.body_color, rect)
                pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы Ван Гога
        head_pos = self.positions[0]
        if SNAKE_HEAD:
            screen.blit(SNAKE_HEAD, head_pos)
        else:
            head_rect = pygame.Rect(head_pos, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, head_rect)
            pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Возвращает координаты головы Ван Гога."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает Ван Гога в начальное состояние после столкновения:
        удаляем картины и ставим обратно в центр."""
        self.length = 1
        self.positions = [((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.last = None


def handle_keys(game_object):
    """Обрабатывает ввод с клавиатуры.
    Args:
        game_object (Snake): Ван Гог, которому передаются команды.
    """
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
    """Проверяет столкновения Ван Гога с ухом и собственными картинами.
    Args:
        snake (Snake): Ван Гог.
        apple (Apple): ухо.
    """
    # Проверка столкновения с ухом, Ван Гог вдохновён и творит шедевр
    if snake.get_head_position() == apple.position:
        snake.length += 1
        apple.position = apple.randomize_position()

    # Проверка столкновений с выставкой своих картин, сбрасываем игру в начало
    for pos in snake.positions[1:]:
        if snake.get_head_position() == pos:
            snake.reset()
            break


def main():
    """Основная функция игры — запускает игровой цикл."""
    pygame.init()  # Инициализация библиотеки Pygame
    screen.fill(BOARD_BACKGROUND_COLOR)  # Заливаем экран фоновым цветом
    snake = Snake()  # Создаём Ван Гога
    apple = Apple()  # Создаём ухо

    while True:  # Бесконечный игровой цикл
        clock.tick(SPEED)  # Снижаем скорость игры
        handle_keys(snake)  # Обрабатываем нажатия клавиш
        snake.update_direction()  # Обновляем направление движения Ван Гога
        snake.move()  # Двигаем Ван Гога на один шаг
        check_collision(snake, apple)  # Проверяем столкновения
        screen.fill(BOARD_BACKGROUND_COLOR)  # Очищаем экран (заливаем фоном)
        apple.draw()  # Отрисовываем ухо
        snake.draw()  # Отрисовываем Ван Гога
        pygame.display.update()  # Обновляем содержимое окна


if __name__ == "__main__":
    """Точка входа в программу.Проверяет, запущен ли скрипт напрямую
    (а не импортирован как модуль),
    и вызывает функцию main() для запуска игры.
    """
    main()
