import tkinter as tk
import heapq
import random
from time import perf_counter

FONT = "Times New Roman"

# Bright, high-contrast palette
BG = "#F2F7FA"
PANEL = "#FFFFFF"
NAVY = "#17324D"
TEAL = "#087F8C"
TEAL_LIGHT = "#D9F3F2"
GREEN = "#238636"
GREEN_LIGHT = "#DDF6E5"
RED = "#D9485F"
RED_LIGHT = "#FFE1E5"
ORANGE = "#E58A18"
ORANGE_LIGHT = "#FFF0D5"
BLUE = "#3977D5"
BLUE_LIGHT = "#DDEBFF"
PURPLE = "#7256B9"
TEXT = "#23364D"
MUTED = "#62758A"
BORDER = "#D7E2EB"
SAFE = "#E8F1F7"
WALL = "#334155"
ROUTE = "#17BEBB"

ROWS, COLS = 8, 8
CELL_SIZE = 43
GRID_PAD = 8
START = (0, 0)
GOAL = (7, 7)

INITIAL_GRID = [
    [0, 0, 5, 0, 0, 0, 1, 0],
    [0, 1, 5, 0, 1, 0, 1, 0],
    [0, 0, 0, 0, 1, 0, 0, 0],
    [5, 1, 0, 5, 0, 0, 1, 0],
    [0, 0, 0, 1, 0, 5, 0, 0],
    [0, 1, 0, 0, 0, 1, 0, 5],
    [0, 0, 5, 1, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 5, 1, 0]
]

# 0 = safe, 1 = obstacle, 5 = danger
grid = [row[:] for row in INITIAL_GRID]
visited_cells = set()
route_cells = set()
animation_id = None
busy = False


# -------------------- A* SEARCH --------------------
def heuristic(a, b):
    # Manhattan distance; never overestimates movement cost
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar():
    started = perf_counter()
    open_heap = [(heuristic(START, GOAL), 0, START)]
    g_score = {START: 0}
    parent = {START: None}
    closed = set()
    explored = []

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while open_heap:
        _, current_g, current = heapq.heappop(open_heap)

        if current_g != g_score.get(current) or current in closed:
            continue

        closed.add(current)
        explored.append(current)

        if current == GOAL:
            path = []
            node = GOAL
            while node is not None:
                path.append(node)
                node = parent[node]
            path.reverse()
            return {
                "path": path,
                "explored": explored,
                "cost": g_score[GOAL],
                "elapsed": (perf_counter() - started) * 1000
            }

        for dr, dc in directions:
            nr, nc = current[0] + dr, current[1] + dc
            if not (0 <= nr < ROWS and 0 <= nc < COLS):
                continue
            if grid[nr][nc] == 1:
                continue

            neighbor = (nr, nc)
            step_cost = 5 if grid[nr][nc] == 5 else 1
            new_g = current_g + step_cost

            if new_g < g_score.get(neighbor, float("inf")):
                g_score[neighbor] = new_g
                parent[neighbor] = current
                f_score = new_g + heuristic(neighbor, GOAL)
                heapq.heappush(open_heap, (f_score, new_g, neighbor))

    return {
        "path": None,
        "explored": explored,
        "cost": 0,
        "elapsed": (perf_counter() - started) * 1000
    }


# -------------------- WINDOW --------------------
root = tk.Tk()
root.title("RESQ | Disaster Rescue Navigation")
root.geometry("1020x760")
root.minsize(880, 680)
root.configure(bg=BG)

# Header
header = tk.Frame(root, bg=NAVY, padx=20, pady=12)
header.pack(fill="x")

tk.Label(
    header, text="RESQ", font=(FONT, 27, "bold"),
    bg=NAVY, fg="#5EEAD4"
).pack(side="left")

tk.Label(
    header, text="  DISASTER RESCUE NAVIGATION",
    font=(FONT, 15, "bold"), bg=NAVY, fg="white"
).pack(side="left", pady=(7, 0))

tk.Label(
    header, text="A* PATHFINDING",
    font=(FONT, 11, "bold"), bg=NAVY, fg="#A7F3D0"
).pack(side="right", pady=(8, 0))

tk.Label(
    root,
    text="Plan a cost-aware route through a disaster-affected area.",
    font=(FONT, 13), bg=BG, fg=MUTED
).pack(anchor="w", padx=20, pady=(10, 8))


# Compact statistics row
stats = tk.Frame(root, bg=BG)
stats.pack(fill="x", padx=15, pady=(0, 10))


def make_stat(parent, title, value, accent):
    card = tk.Frame(parent, bg=PANEL, highlightbackground=BORDER,
                    highlightthickness=1, padx=12, pady=7)
    card.pack(side="left", fill="both", expand=True, padx=4)
    tk.Label(card, text=title, font=(FONT, 10, "bold"),
             bg=PANEL, fg=MUTED).pack(anchor="w")
    result = tk.Label(card, text=value, font=(FONT, 18, "bold"),
                      bg=PANEL, fg=accent)
    result.pack(anchor="w", pady=(2, 0))
    return result


cost_value = make_stat(stats, "ROUTE COST", "--", TEAL)
length_value = make_stat(stats, "PATH CELLS", "--", GREEN)
explored_value = make_stat(stats, "CELLS EXPLORED", "0", PURPLE)
time_value = make_stat(stats, "SEARCH TIME", "--", ORANGE)


# Main two-column layout. Grid gets a fixed-width area so it never
# gets pushed off-screen by the operation log.
main = tk.Frame(root, bg=BG)
main.pack(fill="both", expand=True, padx=15, pady=(0, 12))

map_panel = tk.Frame(main, bg=PANEL, padx=12, pady=12,
                     highlightbackground=BORDER, highlightthickness=1)
map_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

control_panel = tk.Frame(main, bg=PANEL, width=270, padx=12, pady=12,
                         highlightbackground=BORDER, highlightthickness=1)
control_panel.pack(side="right", fill="y")
control_panel.pack_propagate(False)

tk.Label(map_panel, text="MISSION MAP", font=(FONT, 16, "bold"),
         bg=PANEL, fg=NAVY).pack(anchor="w")

tk.Label(map_panel, text="S = START     T = TARGET",
         font=(FONT, 11), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(2, 8))

canvas_size = COLS * CELL_SIZE + GRID_PAD * 2
canvas = tk.Canvas(
    map_panel, width=canvas_size, height=canvas_size,
    bg=PANEL, highlightthickness=0
)
canvas.pack(anchor="center", pady=(0, 8))


def draw_grid():
    canvas.delete("all")
    for r in range(ROWS):
        for c in range(COLS):
            x1 = GRID_PAD + c * CELL_SIZE
            y1 = GRID_PAD + r * CELL_SIZE
            x2 = x1 + CELL_SIZE - 3
            y2 = y1 + CELL_SIZE - 3
            pos = (r, c)

            if pos == START:
                color, symbol, fg = GREEN, "S", "white"
            elif pos == GOAL:
                color, symbol, fg = RED, "T", "white"
            elif pos in route_cells:
                color, symbol, fg = ROUTE, "●", NAVY
            elif pos in visited_cells:
                color, symbol, fg = BLUE_LIGHT, "·", BLUE
            elif grid[r][c] == 1:
                color, symbol, fg = WALL, "X", "white"
            elif grid[r][c] == 5:
                color, symbol, fg = ORANGE_LIGHT, "!", ORANGE
            else:
                color, symbol, fg = SAFE, "", TEXT

            canvas.create_rectangle(
                x1, y1, x2, y2, fill=color, outline="#FFFFFF", width=2
            )
            if symbol:
                canvas.create_text(
                    (x1 + x2) / 2, (y1 + y2) / 2,
                    text=symbol, font=(FONT, 16, "bold"), fill=fg
                )


# Legend
legend = tk.Frame(map_panel, bg=PANEL)
legend.pack(fill="x", pady=(2, 0))

for color, label in [
    (GREEN, "Start"), (RED, "Target"), (ORANGE, "Danger"),
    (WALL, "Obstacle"), (ROUTE, "Route")
]:
    entry = tk.Frame(legend, bg=PANEL)
    entry.pack(side="left", padx=(0, 8))
    tk.Label(entry, text="●", font=(FONT, 11, "bold"),
             bg=PANEL, fg=color).pack(side="left")
    tk.Label(entry, text=label, font=(FONT, 10),
             bg=PANEL, fg=TEXT).pack(side="left", padx=(3, 0))


# -------------------- CONTROL PANEL --------------------
tk.Label(control_panel, text="MISSION CONTROL",
         font=(FONT, 16, "bold"), bg=PANEL, fg=NAVY).pack(anchor="w")

status_label = tk.Label(
    control_panel, text="● READY",
    font=(FONT, 12, "bold"), bg=PANEL, fg=GREEN
)
status_label.pack(anchor="w", pady=(8, 10))


def set_status(message, color=GREEN):
    status_label.config(text="● " + message, fg=color)


tk.Label(control_panel, text="OPERATION LOG",
         font=(FONT, 12, "bold"), bg=PANEL, fg=MUTED).pack(anchor="w", pady=(2, 5))

log_box = tk.Text(
    control_panel, height=12, wrap="word",
    bg="#F5F9FC", fg=TEXT, insertbackground=TEXT,
    font=(FONT, 11), relief="flat", bd=0,
    padx=8, pady=8
)
log_box.pack(fill="both", expand=True)


def log(message):
    log_box.insert(tk.END, message + "\n")
    log_box.see(tk.END)


def make_button(parent, text, command, color, fg="white"):
    return tk.Button(
        parent, text=text, command=command,
        font=(FONT, 12, "bold"), bg=color, fg=fg,
        activebackground=color, activeforeground=fg,
        relief="flat", bd=0, cursor="hand2",
        padx=8, pady=9
    )


def stop_animation():
    global animation_id, busy
    if animation_id is not None:
        try:
            root.after_cancel(animation_id)
        except tk.TclError:
            pass
        animation_id = None
    busy = False


def finish_mission(result):
    global busy, animation_id, route_cells
    animation_id = None
    busy = False
    path = result["path"]

    if not path:
        set_status("NO ROUTE FOUND", RED)
        log("MISSION FAILED: No route exists.")
        return

    route_cells = set(path)
    draw_grid()
    cost_value.config(text=str(result["cost"]))
    length_value.config(text=str(len(path)))
    explored_value.config(text=str(len(result["explored"])))
    time_value.config(text=f'{result["elapsed"]:.2f} ms')
    set_status("MISSION COMPLETE", GREEN)

    log("")
    log("MISSION SUCCESS!")
    log(f'Route cost: {result["cost"]}')
    log(f'Path cells: {len(path)}')
    log(f'Cells explored: {len(result["explored"])}')
    log(f'Time: {result["elapsed"]:.2f} ms')
    log("Route coordinates:")
    log(" -> ".join(str(cell) for cell in path))


def start_search():
    global busy, animation_id, visited_cells, route_cells
    if busy:
        return

    busy = True
    visited_cells = set()
    route_cells = set()
    cost_value.config(text="...")
    length_value.config(text="...")
    explored_value.config(text="0")
    time_value.config(text="...")
    log_box.delete("1.0", tk.END)
    set_status("SEARCHING", TEAL)
    log("A* search started...")
    log("Exploring available cells.")
    draw_grid()

    result = astar()
    explored = result["explored"]
    index = 0

    def animate_exploration():
        nonlocal index
        global animation_id

        if index < len(explored):
            pos = explored[index]
            if pos not in (START, GOAL):
                visited_cells.add(pos)
            draw_grid()
            explored_value.config(text=str(index + 1))
            if index % 4 == 0:
                log(f"Explored {pos}")
            index += 1
            animation_id = root.after(35, animate_exploration)
        elif result["path"]:
            path = result["path"]
            p_index = 0

            def animate_route():
                nonlocal p_index
                global animation_id
                if p_index < len(path):
                    route_cells.add(path[p_index])
                    draw_grid()
                    p_index += 1
                    animation_id = root.after(55, animate_route)
                else:
                    finish_mission(result)

            animate_route()
        else:
            finish_mission(result)

    animate_exploration()


def reset_map():
    global visited_cells, route_cells
    stop_animation()
    visited_cells.clear()
    route_cells.clear()
    cost_value.config(text="--")
    length_value.config(text="--")
    explored_value.config(text="0")
    time_value.config(text="--")
    log_box.delete("1.0", tk.END)
    set_status("READY", GREEN)
    draw_grid()
    log("Map reset. Ready for a new mission.")


def randomize_map():
    global grid
    stop_animation()
    new_grid = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            if (r, c) in (START, GOAL):
                row.append(0)
            else:
                chance = random.random()
                if chance < 0.13:
                    row.append(1)
                elif chance < 0.30:
                    row.append(5)
                else:
                    row.append(0)
        new_grid.append(row)
    grid = new_grid
    reset_map()
    log("A new map has been generated.")


make_button(control_panel, "▶  START RESCUE SEARCH",
            start_search, TEAL).pack(fill="x", pady=(10, 7))

make_button(control_panel, "↻  RESET MAP",
            reset_map, NAVY).pack(fill="x", pady=7)

make_button(control_panel, "⚡  RANDOMIZE MAP",
            randomize_map, PURPLE).pack(fill="x", pady=7)

tk.Label(
    control_panel,
    text="SAFE: 1 COST   |   DANGER: 5 COST",
    font=(FONT, 10, "bold"), bg=PANEL, fg=MUTED
).pack(anchor="w", pady=(12, 0))

# Footer
tk.Label(
    root,
    text="RESQ  •  A* SEARCH ALGORITHM  •  EDUCATIONAL SIMULATION",
    font=(FONT, 10), bg=BG, fg=MUTED
).pack(pady=(0, 8))

draw_grid()
log("System ready.")
log("Green = Start | Red = Target")
log("Orange = Danger | Dark = Obstacle")
log("Press START to find a route.")

root.mainloop()
