import pygame
import sys
import numpy as np
import os
import csv
import tkinter as tk
from tkinter import filedialog

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 1000, 600
GRID_COLOR = (200, 200, 200)
NUMBERS_COLOR = (0, 0, 0)
BG_COLOR = (255, 255, 255)
CELL_SIZE = 40
UI_WIDTH = 200

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Room Designer")

icon_image = pygame.image.load("twinturbochibi.png")
pygame.display.set_icon(icon_image)

# Initialize grid
rows, cols = 15, 15
grid = np.zeros((rows, cols), dtype=int)

# Zoom and Pan variables
zoom = 1.0
offset_x = (WINDOW_WIDTH - UI_WIDTH - cols * CELL_SIZE) // 2 + UI_WIDTH
offset_y = (WINDOW_HEIGHT - rows * CELL_SIZE) // 2

# Current value to place in grid
placing_value = 1

custom_value_button_clicked = False

def draw_grid():
    for row in range(rows):
        for col in range(cols):
            cell_value = grid[row][col]
            rect = pygame.Rect(col * CELL_SIZE * zoom + offset_x, row * CELL_SIZE * zoom + offset_y, CELL_SIZE * zoom,
                               CELL_SIZE * zoom)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)
            if cell_value != 0:
                font = pygame.font.Font(None, int(36 * zoom))
                text = font.render(str(cell_value), True, NUMBERS_COLOR)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)


def export_room_view(filename="room_view"):
    # Check for existing files and generate unique filenames
    jpg_filename = find_unique_filename(filename + ".jpg")
    csv_filename = find_unique_filename(filename + ".csv")

    # Save room view as JPG
    room_surface = pygame.Surface((cols * CELL_SIZE, rows * CELL_SIZE))
    room_surface.fill(BG_COLOR)
    for row in range(rows):
        for col in range(cols):
            cell_value = grid[row][col]
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(room_surface, GRID_COLOR, rect, 1)
            if cell_value != 0:
                font = pygame.font.Font(None, 36)
                text = font.render(str(cell_value), True, NUMBERS_COLOR)
                text_rect = text.get_rect(center=rect.center)
                room_surface.blit(text, text_rect)
    pygame.image.save(room_surface, jpg_filename)

    # Save room information as CSV
    with open(csv_filename, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for row in grid:
            writer.writerow(row)

def find_unique_filename(filename):
    suffix = 0
    original_filename = filename
    while os.path.exists(filename):
        suffix += 1
        filename = f"{os.path.splitext(original_filename)[0]}_{suffix}{os.path.splitext(original_filename)[1]}"
    return filename

def resize_grid(new_rows, new_cols):
    global grid, rows, cols, offset_x, offset_y, zoom
    old_rows, old_cols = rows, cols
    rows, cols = new_rows, new_cols
    new_grid = np.zeros((rows, cols), dtype=int)
    min_rows, min_cols = min(old_rows, rows), min(old_cols, cols)
    new_grid[:min_rows, :min_cols] = grid[:min_rows, :min_cols]
    grid = new_grid
    offset_x = (WINDOW_WIDTH - UI_WIDTH - cols * CELL_SIZE) // 2 + UI_WIDTH
    offset_y = (WINDOW_HEIGHT - rows * CELL_SIZE) // 2
    # Adjust zoom to fit the new grid within the screen
    zoom_x = (WINDOW_WIDTH - UI_WIDTH) / (cols * CELL_SIZE)
    zoom_y = WINDOW_HEIGHT / (rows * CELL_SIZE)
    zoom = min(zoom_x, zoom_y, 1.0)


def add_row_above():
    global grid, rows
    new_grid = np.zeros((rows + 1, cols), dtype=int)
    new_grid[1:, :] = grid
    grid = new_grid
    rows += 1


def add_row_below():
    global grid, rows
    new_grid = np.zeros((rows + 1, cols), dtype=int)
    new_grid[:-1, :] = grid
    grid = new_grid
    rows += 1


def add_col_left():
    global grid, cols
    new_grid = np.zeros((rows, cols + 1), dtype=int)
    new_grid[:, 1:] = grid
    grid = new_grid
    cols += 1


def add_col_right():
    global grid, cols
    new_grid = np.zeros((rows, cols + 1), dtype=int)
    new_grid[:, :-1] = grid
    grid = new_grid
    cols += 1

def remove_row_above():
    global grid, rows
    if rows > 1:
        new_grid = np.zeros((rows - 1, cols), dtype=int)
        new_grid[:] = grid[1:]
        grid = new_grid
        rows -= 1

def remove_row_below():
    global grid, rows
    if rows > 1:
        new_grid = np.zeros((rows - 1, cols), dtype=int)
        new_grid[:] = grid[:-1]
        grid = new_grid
        rows -= 1

def remove_col_left():
    global grid, cols
    if cols > 1:
        new_grid = np.zeros((rows, cols - 1), dtype=int)
        new_grid[:, :] = grid[:, 1:]
        grid = new_grid
        cols -= 1

def remove_col_right():
    global grid, cols
    if cols > 1:
        new_grid = np.zeros((rows, cols - 1), dtype=int)
        new_grid[:, :] = grid[:, :-1]
        grid = new_grid
        cols -= 1


def display_custom_value_popup(input_text):
    popup_width, popup_height = 200, 100
    popup_x = (WINDOW_WIDTH - popup_width) // 2
    popup_y = (WINDOW_HEIGHT - popup_height) // 2
    pygame.draw.rect(screen, BG_COLOR, pygame.Rect(popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(screen, GRID_COLOR, pygame.Rect(popup_x, popup_y, popup_width, popup_height), 2)

    font = pygame.font.Font(None, 24)
    label = font.render("Enter custom value:", True, NUMBERS_COLOR)
    screen.blit(label, (popup_x + 10, popup_y + 10))
    input_box = pygame.Rect(popup_x + 10, popup_y + 40, 180, 30)
    pygame.draw.rect(screen, GRID_COLOR, input_box, 2)

    input_surface = font.render(input_text, True, NUMBERS_COLOR)
    screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

    cancel_button = pygame.Rect(popup_x + 10, popup_y + 80, 180, 30)
    pygame.draw.rect(screen, (255, 0, 0), cancel_button)
    cancel_text = font.render("Cancel", True, NUMBERS_COLOR)
    screen.blit(cancel_text, (cancel_button.x + 60, cancel_button.y + 5))

    return cancel_button

def draw_ui():
    pygame.draw.rect(screen, BG_COLOR, pygame.Rect(0, 0, UI_WIDTH, WINDOW_HEIGHT))
    font = pygame.font.Font(None, 24)

    buttons = [
        ("Save (Alt + S)", 10, 10),
        ("Clear All (Alt + C)", 10, 40),
        ("Resize (Alt + R)", 10, 70),
        ("Value 1", 10, 100),
        ("Value 2", 10, 130),
        ("Value 3", 10, 160),
        ("Clear Tile (0)", 10, 190),
        ("Add Row Above (Ctrl + W)", 10, 220),
        ("Add Row Below (Ctrl + S)", 10, 250),
        ("Add Col Left (Ctrl + A)", 10, 280),
        ("Add Col Right (Ctrl + D)", 10, 310),
        ("Remove Row Above (Shift + W)", 10, 340),
        ("Remove Row Below (Shift + S)", 10, 370),
        ("Remove Col Left (Shift + A)", 10, 400),
        ("Remove Col Right (Shift + D)", 10, 430),
        (f"Custom Value (Alt + V): {placing_value}", 10, 460),
        ("Load CSV (Alt + L)", 10, 490),
        ("(Shift + left mouse) or", 10, 560),
        ("(right mouse) to drag", 10, 580)
    ]

    for text, x, y in buttons:
        label = font.render(text, True, NUMBERS_COLOR)
        screen.blit(label, (x, y))


def draw_resize_popup(input_text, width_collected):
    popup_width, popup_height = 300, 150
    popup_x = (WINDOW_WIDTH - popup_width) // 2
    popup_y = (WINDOW_HEIGHT - popup_height) // 2
    pygame.draw.rect(screen, BG_COLOR, pygame.Rect(popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(screen, GRID_COLOR, pygame.Rect(popup_x, popup_y, popup_width, popup_height), 2)

    font = pygame.font.Font(None, 24)
    if width_collected:
        label = font.render("Enter new height:", True, NUMBERS_COLOR)
    else:
        label = font.render("Enter new width:", True, NUMBERS_COLOR)
    screen.blit(label, (popup_x + 10, popup_y + 10))
    input_box = pygame.Rect(popup_x + 10, popup_y + 40, 280, 30)
    pygame.draw.rect(screen, GRID_COLOR, input_box, 2)

    input_surface = font.render(input_text, True, NUMBERS_COLOR)
    screen.blit(input_surface, (input_box.x + 5, input_box.y + 5))

    cancel_button = pygame.Rect(popup_x + 10, popup_y + 80, 280, 30)
    pygame.draw.rect(screen, (255, 0, 0), cancel_button)
    cancel_text = font.render("Cancel", True, NUMBERS_COLOR)
    screen.blit(cancel_text, (cancel_button.x + 110, cancel_button.y + 5))

    return cancel_button

def import_room_view():
    # Create a Tkinter root window
    root = tk.Tk()
    root.iconbitmap("twinturbochibi.ico")
    root.withdraw()  # Hide the root window

    # Prompt the user to select a CSV file
    file_path = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])

    # Read data from the selected CSV file and update the game grid
    if file_path:
        with open(file_path, mode='r') as csv_file:
            reader = csv.reader(csv_file)
            imported_grid = [list(map(int, row)) for row in reader]

        # Update the game grid with the imported data
        global grid, rows, cols
        rows, cols = len(imported_grid), len(imported_grid[0])
        grid = np.array(imported_grid)

        # Ensure the grid dimensions are compatible with the screen size
        resize_grid(rows, cols)

        # Close the Tkinter root window
        root.destroy()

def main():
    global zoom, offset_x, offset_y, grid, placing_value

    running = True
    input_active = False
    custom_value_button_clicked = False
    input_text = ''
    shift_held = False
    ctrl_held = False
    alt_held = False
    width_collected = False
    new_width, new_height = None, None

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = event.pos
                    if input_active:
                        cancel_button = draw_resize_popup(input_text, width_collected)
                        if cancel_button.collidepoint(x, y):
                            input_active = False
                            input_text = ''
                            width_collected = False
                            new_width, new_height = None, None
                    elif custom_value_button_clicked:
                        cancel_button = display_custom_value_popup(input_text)
                        if cancel_button.collidepoint(x, y):
                            custom_value_button_clicked = False
                            input_text = ''
                    elif x > UI_WIDTH:
                        col = int((x - offset_x) / (CELL_SIZE * zoom))
                        row = int((y - offset_y) / (CELL_SIZE * zoom))
                        if 0 <= col < cols and 0 <= row < rows and not shift_held:
                            grid[row][col] = placing_value
                    else:
                        # Handle UI button clicks
                        if 10 <= y <= 30:
                            export_room_view()
                        elif 40 <= y <= 60:
                            grid = np.zeros((rows, cols), dtype=int)
                        elif 70 <= y <= 90:
                            input_active = True
                            input_text = ''
                        elif 100 <= y <= 120:
                            placing_value = 1
                        elif 130 <= y <= 150:
                            placing_value = 2
                        elif 160 <= y <= 180:
                            placing_value = 3
                        elif 190 <= y <= 210:
                            placing_value = 0
                        elif 220 <= y <= 240:
                            add_row_above()
                        elif 250 <= y <= 270:
                            add_row_below()
                        elif 280 <= y <= 300:
                            add_col_left()
                        elif 310 <= y <= 330:
                            add_col_right()
                        elif 340 <= y <= 360:
                            remove_row_above()
                        elif 370 <= y <= 390:
                            remove_row_below()
                        elif 400 <= y <= 420:
                            remove_col_left()
                        elif 430 <= y <= 450:
                            remove_col_right()
                        elif 460 <= y <= 480:
                            custom_value_button_clicked = True
                        if 490 <= y <= 520:  # Check if "Load CSV" button is clicked
                            import_room_view()
                elif event.button == 4:  # Scroll up
                    zoom += 0.1
                elif event.button == 5:  # Scroll down
                    zoom = max(0.1, zoom - 0.1)
            elif event.type == pygame.KEYDOWN:
                if not input_active and not custom_value_button_clicked:
                    if event.key == pygame.K_s and not ctrl_held and not shift_held and alt_held:
                        export_room_view()
                    elif event.key == pygame.K_c and alt_held:
                        grid = np.zeros((rows, cols), dtype=int)
                    elif event.key == pygame.K_r and alt_held:
                        input_active = True
                        input_text = ''
                    elif event.key == pygame.K_1:
                        placing_value = 1
                    elif event.key == pygame.K_2:
                        placing_value = 2
                    elif event.key == pygame.K_3:
                        placing_value = 3
                    elif event.key == pygame.K_0:
                        placing_value = 0
                    elif event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                        ctrl_held = True
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        shift_held = True
                    elif event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                        alt_held = True
                    elif event.key == pygame.K_a:
                        if ctrl_held and not shift_held:
                            add_col_left()
                        elif shift_held:
                            remove_col_left()
                    elif event.key == pygame.K_d:
                        if ctrl_held and not shift_held:
                            add_col_right()
                        elif shift_held:
                            remove_col_right()
                    elif event.key == pygame.K_w:
                        if ctrl_held and not shift_held:
                            add_row_above()
                        elif shift_held:
                            remove_row_above()
                    elif event.key == pygame.K_s:
                        if ctrl_held and not shift_held:
                            add_row_below()
                        elif shift_held:
                            remove_row_below()
                    elif event.key == pygame.K_v and alt_held:
                        custom_value_button_clicked = True
                    elif event.key == pygame.K_l and alt_held:
                        import_room_view()
                elif input_active:
                    if event.key == pygame.K_RETURN:
                        if not width_collected:
                            try:
                                new_width = int(input_text)
                                input_text = ''
                                width_collected = True
                            except ValueError:
                                pass
                        else:
                            try:
                                new_height = int(input_text)
                                resize_grid(new_height, new_width)
                                input_active = False
                                input_text = ''
                                width_collected = False
                                new_width, new_height = None, None
                            except ValueError:
                                pass
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode
                elif custom_value_button_clicked:
                    if event.key == pygame.K_RETURN:
                        try:
                            placing_value = int(input_text)
                            custom_value_button_clicked = False
                            input_text = ''
                        except ValueError:
                            pass
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    elif event.unicode.isdigit():
                        input_text += event.unicode
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL or event.key == pygame.K_RCTRL:
                    ctrl_held = False
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    shift_held = False
                if event.key == pygame.K_LALT or event.key == pygame.K_RALT:
                    alt_held = False
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[2]:  # Right click and drag
                    offset_x += event.rel[0]
                    offset_y += event.rel[1]
                elif event.buttons[0]:  # Left click and drag
                    if shift_held:
                        offset_x += event.rel[0]
                        offset_y += event.rel[1]

        screen.fill(BG_COLOR)
        draw_grid()
        draw_ui()
        if input_active:
            draw_resize_popup(input_text, width_collected)
        elif custom_value_button_clicked:  # Display the custom value popup if button is clicked
            display_custom_value_popup(input_text)
        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
