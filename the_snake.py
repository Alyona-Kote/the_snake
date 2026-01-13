from random import choice, randint

import pygame as pg

"""Игра «Ухожор».
Цель: управлять Ван Гогом, подбирать отрезанные уши и творить шедевры.
"""

pg.init()  # Инициализация библиотеки Pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 40  # я изменила размер (х2), иначе не видно картинок
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
MIDDLE_OF_FIELD = (SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2)

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
SPEED = 20


def load_image(path, size):
    """Загрузка и масштабирование изображений."""
    try:
        image = pg.image.load(path)
        return pg.transform.scale(image, size)
    except pg.error:
        return None


# Откуда берём картинки
SNAKE_HEAD = pg.image.load("images/snake_head.png")
SNAKE_BODY = pg.image.load("images/snake_body.png")
APPLE_IMAGE = pg.image.load("images/apple.png")
background_image = pg.image.load("images/background.jpg")

# Масштабирование изображений под размер ячейки
if SNAKE_HEAD:
    SNAKE_HEAD = pg.transform.scale(SNAKE_HEAD, (GRID_SIZE, GRID_SIZE))
if SNAKE_BODY:
    SNAKE_BODY = pg.transform.scale(SNAKE_BODY, (GRID_SIZE, GRID_SIZE))
if APPLE_IMAGE:
    APPLE_IMAGE = pg.transform.scale(APPLE_IMAGE, (GRID_SIZE, GRID_SIZE))
if background_image:
    background = pg.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption("Ван Ухожор")

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс для игровых объектов (условные "змейка" и "яблоко" -
    на самом деле Ван Гог и уши, названия классов оставлены для удобства
    проверки).
    Атрибуты:
        position: Координаты объекта (x, y).
        body_color: Цвет объекта (используется, если нет изображения).
    """

    def __init__(self, color):
        """Инициализация объекта в центре экрана."""
        self.position = MIDDLE_OF_FIELD
        self.body_color = color
        self.border_color = self.draw()

    def draw(self):
        """Метод для отрисовки объекта, переопределяется в подклассах."""
        raise NotImplementedError("Метод draw должен быть переопределён.")

    #  def draw_cell():
    ###############################################


class Apple(GameObject):
    """Класс, описывающий объект, который нужно собрать. Вместо яблока у нас
    будут уши.
        Наследуется от GameObject.
    """

    def __init__(self, color):
        """Инициализация уха."""
        super().__init__(color)
        self.position = self.randomize_position()

    def randomize_position(self, busy=[MIDDLE_OF_FIELD]):
        """Генерит случайную позицию для уха на поле. Возвращает случайные
        координаты (x, y) в пределах игрового поля.
        """
        if busy is None:
            busy = []
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in busy:
                break

    def draw(self):
        """Отрисовывает ухо на экране."""
        if APPLE_IMAGE:
            screen.blit(APPLE_IMAGE, self.position)
        else:
            rect = pg.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, rect)
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс, описывающий Ван Гога — главного игрока.
    Наследуется от GameObject.
    """

    def __init__(self, color):
        """Инициализация Ван Гога: начальная длина, позиция и направление."""
        super().__init__(color)  # Вызов конструктора родительского класса
        self.length = 1  # Начальная длина
        self.positions = [MIDDLE_OF_FIELD]
        self.direction = RIGHT  # Начальное направление движения
        self.next_direction = None  # Будущее направление

    def update_direction(self):
        """Обновляет направление движения, если нажали на клавишу."""
        if self.next_direction:  # Если есть новое направление
            self.direction = self.next_direction  # Меняем текущее направление
            self.next_direction = None  # Очищаем буфер

    def move(self):
        """Двигает Ван Гога на один шаг в текущем направлении."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию головы с учётом выхода за границы
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT

        new_head = (new_x, new_y)

        # Добавляем новую голову
        self.positions.insert(0, new_head)

        # Если длина не изменилась — удаляем последнюю картину
        if len(self.positions) > self.length:
            self.positions.pop()  # Сохраняем для затирания

    def draw(self):
        """Отрисовывает Ван Гога на экране."""
        # Картины (всё, кроме головы)
        for position in self.positions[1:]:
            if SNAKE_BODY:
                screen.blit(SNAKE_BODY, position)
            else:
                rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
                pg.draw.rect(screen, self.body_color, rect)
                pg.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы Ван Гога
        head_pos = self.get_head_position()
        if SNAKE_HEAD:
            screen.blit(SNAKE_HEAD, head_pos)
        else:
            head_rect = pg.Rect(head_pos, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, self.body_color, head_rect)
            pg.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def get_head_position(self):
        """Возвращает координаты головы Ван Гога."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает Ван Гога в начальное состояние после столкновения:
        удаляем картины и ставим обратно в центр.
        """
        self.length = 1
        self.positions = [MIDDLE_OF_FIELD]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])


def handle_keys(game_object):
    """Обрабатывает ввод с клавиатуры, Ван Гогу передаются команды."""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def check_collision(snake, apple):
    """Проверяет столкновения Ван Гога с ухом и собственными картинами.
    Args:
        snake (Snake): Ван Гог.
        apple (Apple): ухо.
    """
    # Проверка столкновения с ухом, Ван Гог вдохновлён и творит шедевр
    if snake.get_head_position() == apple.position:
        snake.length += 1
        apple.position = apple.randomize_position(snake.positions)

    # Проверка столкновений с выставкой своих картин, сбрасываем игру в начало
    for pos in snake.positions[1:]:
        if snake.get_head_position() == pos:
            snake.reset()
            # Перегенерируем ухо, исключив начальную позицию змеи
            apple.position = apple.randomize_position([MIDDLE_OF_FIELD])
            break


def main():
    """Основная функция игры — запускает игровой цикл."""

    snake = Snake(SNAKE_COLOR)  # Создаём Ван Гога
    apple = Apple(APPLE_COLOR)  # Создаём ухо

    while True:  # Бесконечный игровой цикл
        clock.tick(SPEED)  # Снижаем скорость игры
        screen.fill(BOARD_BACKGROUND_COLOR)  # Полная очистка экрана
        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BOARD_BACKGROUND_COLOR)
        handle_keys(snake)  # Обрабатываем нажатия клавиш
        snake.update_direction()  # Обновляем направление движения Ван Гога
        snake.move()  # Двигаем Ван Гога на один шаг
        check_collision(snake, apple)  # Проверяем столкновения

        apple.draw()  # Отрисовываем ухо
        snake.draw()  # Отрисовываем Ван Гога

        pg.display.update()  # Обновляем содержимое окна


if __name__ == "__main__":
    """Точка входа в программу.Проверяет, запущен ли скрипт напрямую
    (а не импортирован как модуль),
    и вызывает функцию main() для запуска игры.
    """
    main()
