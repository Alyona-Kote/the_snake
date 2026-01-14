from random import choice, randint
import pygame as pg

"""Игра «Ухожор».
Цель: управлять Ван Гогом, подбирать отрезанные уши и творить шедевры.
"""

pg.init()  # Инициализация библиотеки Pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480  # размеры поля в пикселях
GRID_SIZE = 40  # увеличенный размер ячейки (х2), иначе не видно картинок
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE  # количество ячеек по горизонтали
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE  # количество ячеек по вертикали

MIDDLE_OF_FIELD = ((SCREEN_WIDTH // 2), (SCREEN_HEIGHT // 2))  # середина поля
SCREEN_TOPLEFT = (0, 0)  # Начало координат - левый верхний угол

# Направления движения:
UP = (0, -1)  # Вверх
DOWN = (0, 1)  # Вниз
LEFT = (-1, 0)  # Влево
RIGHT = (1, 0)  # Вправо

# Цвета БУДУТ МЕНЯТЬСЯ на изображения:
BOARD_BACKGROUND_COLOR = (51, 153, 102)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (204, 153, 51)
SNAKE_COLOR = (153, 51, 0)

SPEED = 3  # Скорость движения змейки
clock = pg.time.Clock()  # контроль частоты кадров


# Настройка игрового окна: размер окна, заголовок, фавиконка
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption("Ван Ухожор")  # Заголовок окна
icon = pg.image.load("images/snake_body.png")
pg.display.set_icon(icon)  # Установка фавиконки окна


def load_image(path, size):
    """Загрузка и масштабирование изображений. При ошибке выводит сообщение."""
    try:
        image = pg.image.load(path)
        return pg.transform.scale(image, size)
    except pg.error as e:
        print(f"Ошибка загрузки {path}: {e}")
        return None


# откуда берём картинки
BACKGROUND_IMAGE = load_image("images/background.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
APPLE_IMAGE = load_image("images/apple.png", (GRID_SIZE, GRID_SIZE))
SNAKE_HEAD = load_image("images/snake_head.png", (GRID_SIZE, GRID_SIZE))
SNAKE_BODY = load_image("images/snake_body.png", (GRID_SIZE, GRID_SIZE))


class GameObject:
    """Базовый класс для всех игровых объектов."""

    def __init__(self, color):
        """Инициализирует объект."""
        self.position = MIDDLE_OF_FIELD
        self.body_color = color

    def draw_cell(self, image, position, surface):
        """Отрисовывает ячейку с изображением или цветной заливкой."""
        if image:  # Если изображение доступно, то рисуем его
            surface.blit(image, position)
        else:  # Иначе рисуем цветной прямоугольник с границей
            rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(surface, self.body_color, rect)
            pg.draw.rect(surface, BORDER_COLOR, rect, 1)

    def draw(self, surface):
        """Абстрактный метод отрисовки объекта.
        Переопределяется в подклассах.
        """
        raise NotImplementedError("Переопределяется в подклассах")


class Apple(GameObject):
    """Класс яблока (отрезанного уха), это объект для сбора."""

    def __init__(self, color, busy=[]):
        """Инициализирует ухо."""
        super().__init__(color)
        self.position = self.randomize_position(busy)

    def randomize_position(self, busy):
        """Генерирует случайную позицию, не занятую другими объектами."""
        while True:
            self.position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if self.position not in busy:
                break
        return self.position

    def draw(self, surface):
        """Отрисовывает ухо."""
        self.draw_cell(APPLE_IMAGE, self.position, surface)


class Snake(GameObject):
    """Класс змейки (Ван Гога) — управляемого игрового объекта."""

    def __init__(self, color):
        """Инициализирует Ван Гога."""
        super().__init__(color)  # Вызов конструктора родительского класса
        self.positions = [self.position]  # Список позиций всех картин и головы
        self.length = 1  # Текущая длина
        self.direction = RIGHT  # Начальное направление движения
        self.next_direction = None  # Будущее направление

    def draw(self, surface):
        """Отрисовывает Ван Гога. Рисует голову одним изображением, а картины -
        другим.
        """
        self.draw_cell(SNAKE_HEAD, self.get_head_position(), surface)
        for position in self.positions[1:]:
            self.draw_cell(SNAKE_BODY, position, surface)

    def update_direction(self):
        """Обновляет направление движения."""
        if self.next_direction:  # Если есть новое направление
            self.direction = self.next_direction  # Меняем текущее направление
            self.next_direction = None  # Очищаем буфер

    def get_head_position(self):
        """Возвращает позицию головы Ван Гога."""
        return self.positions[0]

    def move(self):
        """Перемещает Ван Гога. Телепорт (нет стен)."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        # Вычисляем новую позицию головы с учётом выхода за границы
        new_x = (head_x + dx * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)

        self.positions.insert(0, new_head)  # Добавляем новую голову
        # Если длина не изменилась, то удаляем последнюю картину
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        """Сбрасывает состояние Ван Гога к начальному.
        Используется при столкновении с выставкой картин.
        """
        self.length = 1
        self.positions = [MIDDLE_OF_FIELD]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])


def handle_keys(game_object):
    """Обрабатывает ввод с клавиатуры, Ван Гогу передаются команды.
    Нельзя пойти назад.
    """
    for event in pg.event.get():  # Перебираем события
        if event.type == pg.QUIT:  # На выход шагом марш
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:  # Если нажата клавиша..
            if event.key == pg.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pg.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pg.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pg.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def check_collision(snake, apple):
    """Проверяет столкновения Ван Гога с ухом и с выставкой картин.
    - Если Ван Гог подбирает ухо: приходит вдохновение, он творит новый шедевр.
    Появляется новое ухо.
    - Если Ван Гог попал на свою выставку: сбрасываются все картины.
    Появляется новое ухо.
    """
    if snake.get_head_position() == apple.position:
        snake.length += 1  # Ван Гог написал новую картину
        apple.position = apple.randomize_position(snake.positions)

    if snake.get_head_position() in snake.positions[1:]:
        snake.reset()  # Сброс картин
        apple.position = apple.randomize_position(snake.positions)


def main():
    """Основная функция игры — запускает и поддерживает игровой цикл.
    Содержит:
    - инициализацию объектов (Ван Гог, ухо);
    - цикл обработки событий и обновления состояния;
    - отрисовку всех элементов;
    - контроль скорости игры.
    """
    snake = Snake(SNAKE_COLOR)  # Создаём Ван Гога
    apple = Apple(APPLE_COLOR, snake.positions)  # Создаём ухо
    while True:  # Бесконечный игровой цикл
        clock.tick(SPEED)  # Снижаем скорость игры
        if BACKGROUND_IMAGE:  # Отрисовываем фон
            screen.blit(BACKGROUND_IMAGE, SCREEN_TOPLEFT)
        else:
            screen.fill(BOARD_BACKGROUND_COLOR)

        apple.draw(screen)  # Отрисовываем ухо
        snake.draw(screen)  # Отрисовываем Ван Гога
        handle_keys(snake)  # Обрабатываем нажатия клавиш
        snake.update_direction()  # Обновляем направление движения Ван Гога
        snake.move()  # Двигаем Ван Гога на один шаг
        check_collision(snake, apple)  # Проверяем столкновения
        pg.display.update()  # Обновляем содержимое окна


if __name__ == "__main__":
    """Точка входа в программу. Проверяет, запущен ли скрипт напрямую,
    а не импортирован как модуль,
    и вызывает функцию main() для запуска игры.
    После завершения игры закрывает Pygame.
    """
    main()
    pg.quit()
