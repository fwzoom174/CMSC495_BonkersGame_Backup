"""
LEVELS GUIDE

You can build levels in two ways:

1. Basic numbers:
   0 = empty
   1 = normal brick (1 HP)
   2 = strong brick (2 HP, uses the square brick image)

   Colors for this mode are chosen automatically by the row.

2. Advanced mode (choose type AND color):
   (type, colorIndex)

   type:
       1 = normal brick
       2 = strong brick

   colorIndex:
       0 = red
       1 = orange
       2 = yellow
       3 = green
       4 = blue
       5 = purple
       6 = cyan

You can mix both styles in the same level.

Notes:
    - Each level must be a list of rows.
"""

# ---------- LEVEL 1 ----------
level_1 = [
    [(1, 0)] * 16,
    [(1, 1)] * 16,
    [(1, 2)] * 16,
    [(1, 3)] * 16,
]

# ---------- LEVEL 2 ----------
level_2 = [
    [0,0,0,0,(1,6),(1,6),0,0,0,0,(1,6),(1,6),0,0,0,0],
    [0,0,0,(1,4),(1,4),(1,4),(1,4),0,0,(1,4),(1,4),(1,4),(1,4),0,0,0],
    [0,0,(1,4),(2,3),(2,3),(1,4),(1,4),(1,4),(1,4),(1,4),(1,4),(2,3),(2,3),(1,4),0,0],
    [0,(1,2),(1,2),(1,2),(1,4),(1,4),(1,4),(2,3),(2,3),(1,4),(1,4),(1,4),(1,2),(1,2),(1,2),0],
    [0,0,(1,2),0,0,(1,4),(1,4),(1,4),(1,4),(1,4),0,0,(1,2),0,0,0],
]

# ---------- LEVEL 3 ----------
level_3 = [
    [0, (2, 0), (2, 0), (2, 0), (2, 0), (2, 0), 0],
    [(2, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0)],
    [(2, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0)],
    [(2, 0), (1, 6), (1, 6), 0, (1, 6), (1, 6), (2, 0)],
    [(2, 0), (1, 6), (1, 6), 0, (1, 6), (1, 6), (2, 0)],
    [(2, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0), (2, 0)],
    [0, (2, 0), 0, 0, 0, (2, 0), 0],
]

# ---------- LEVEL 4 ----------
level_4 = [
    [0, (2, 6), (2, 6), (2, 6), (2, 6), (2, 6), 0],
    [(2, 6), 0, 0, 0, 0, 0, (2, 6)],
    [(2, 6), (1, 6), (1, 6), 0, (1, 6), (1, 6), (2, 6)],
    [(2, 6), 0, 0, 0, 0, 0, (2, 6)],
    [0, (2, 6), (2, 6), (2, 6), (2, 6), (2, 6), 0],
    [0, 0, (2, 6), 0, (2, 6), 0, 0],
]

# ---------- LEVEL 5 (UMGC) ----------
level_5 = [
    # U
    [(1,4),0,(1,4),     0,   (2,3),0,(2,3),     0,   (1,2),(1,2),(1,2),   0,   (1,0),(1,0),(1,0)],
    [(1,4),0,(1,4),     0,   (2,3),(1,3),(2,3), 0,   (1,2),0,0,           0,   (2,0),0,0],
    [(1,4),0,(1,4),     0,   (2,3),0,(2,3),     0,   (1,2),(2,2),(1,2),   0,   (2,0),0,0],
    [(1,4),0,(1,4),     0,   (2,3),0,(2,3),     0,   (1,2),0,(1,2),       0,   (2,0),0,0],
    [(1,4),(1,4),(1,4), 0,   (2,3),0,(2,3),     0,   (1,2),(1,2),(1,2),   0,   (1,0),(1,0),(1,0)],
]

# ---------- FINAL LEVEL LIST ----------
LEVEL_LAYOUTS = [
    level_1,
    level_2,
    level_3,
    level_4,
    level_5
]
# Settings for each level
LEVEL_SETTINGS = [
    {"timer": "stopwatch"},                        # Level 1
    {"timer": "stopwatch"},                        # Level 2
    {"timer": "stopwatch"},                        # Level 3
    {"timer": "stopwatch"},                        # Level 4
    {"timer": "countdown", "time_limit": 60}       # Level 5 (Final boss)
]


# ---------- LEVEL HELPERS ----------
# Return how many levels exist.
def get_level_count():
    return len(LEVEL_LAYOUTS)


# Return the brick pattern for a given level number.
def get_level_pattern(level_number):
    if level_number < 1:
        level_number = 1
    if level_number > len(LEVEL_LAYOUTS):
        level_number = len(LEVEL_LAYOUTS)
    return LEVEL_LAYOUTS[level_number - 1]


# Return the settings (timer rules) for a given level number.
def get_level_settings(level_number):
    if level_number < 1:
        level_number = 1
    if level_number > len(LEVEL_SETTINGS):
        level_number = len(LEVEL_SETTINGS)
    return LEVEL_SETTINGS[level_number - 1]