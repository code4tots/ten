"""ten.py

Simple text editor in Python3.

---------

For now, basically everything is hardcoded.

--------------------------------------------------------------------  Y0 = 0
|  <dir window>     | line   |   text buffer     | <minimap panel> |
|    30 char        | number |   X char wide     |    20 char      |
|    wide           | 4 char |                   |    wide         |
|                   | wide   |                   |                 |
|    ...            | ...    |   ...             | ...             |
--------------------------------------------------------------------  Y1
|  1 char high ... info (dir, filename, lineno)                    |
|  2 char high ... command (vim style)                             |  Y2
|  ...................................                             |
--------------------------------------------------------------------  Y
X0 = 0             X1       X2                   X3                X
"""

import time
import sys
import curses
import threading

try: import queue
except ImportError: import Queue as queue

# BG_COLOR_CODE1 = 0
PAIR_DEFAULT = 6  # Default text.
PAIR_LINENO  = 7  # line number text.
PAIR_SIDEBAR = 8  # purple text.
PAIR_COMMAND = 9  # empty blocks.

def _scale_color_component(s):
  # return int((255-s) * 1000 / 255)
  return 0

def _scale_color(*args):
  # return tuple(map(_scale_color_component, args))
  return 1000, 1000, 1000

class Editor(object):
  def __init__(self, stdscr):
    self._s = stdscr

  def _init(self):
    curses.raw()
    curses.use_default_colors()
    ## TODO: Consider what to do about colors.
    # curses.init_pair(PAIR_DEFAULT, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # curses.init_pair(PAIR_LINENO, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # curses.init_pair(PAIR_SIDEBAR, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    # curses.init_pair(PAIR_COMMAND, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(PAIR_DEFAULT, -1, -1)
    curses.init_pair(PAIR_LINENO, -1, -1)
    curses.init_pair(PAIR_SIDEBAR, -1, -1)
    curses.init_pair(PAIR_COMMAND, -1, -1)
    self._attr_def = curses.color_pair(PAIR_DEFAULT)|curses.A_NORMAL
    self._attr_ln = curses.color_pair(PAIR_LINENO)|curses.A_DIM
    self._attr_sb = curses.color_pair(PAIR_SIDEBAR)|curses.A_NORMAL
    self._attr_cm = curses.color_pair(PAIR_COMMAND)|curses.A_NORMAL

  def run(self):
    self._check_terminal_capabilities()
    self._init()
    events = queue.Queue()
    threading.Thread(target=self._listen_to_inputs, args=(events,)).start()
    self._draw()
    while True:
      type_, data = events.get()
      self._draw()
      self._s.addstr(4, 5, repr(curses.can_change_color()))
      self._s.addstr(5, 5, repr((type_, data)))
      self._s.addstr(6, 5, repr(curses.COLORS))
      self._s.refresh()
      if data == 3:
        break  # die on '^c'

  def _check_terminal_capabilities(self):
    if not curses.has_colors():
      raise Exception('terminal cannot display colors!')
    if not curses.can_change_color():
      raise Exception('terminal cannot use custom colors!')

  def _listen_to_inputs(self, events):
    while True:
      ch = self._s.getch()
      events.put(('input', ch))
      if ch == 3:
        break  # die on '^c'

  def _draw(self):
    Y, X = self._s.getmaxyx()
    if Y < 4:
      raise Exception('terminal must be at least 4 characters high')
    if X < 50:
      raise Exception('terminal must be at least 50 characters wide')
    X1 = 28
    X2 = 34
    X3 = X-20
    Y1 = Y-3
    Y2 = Y-2

    dirwin = curses.newwin(Y1, X1)
    dirwin.bkgd(' ', self._attr_sb)

    self._draw_line_numbers(Y1, X2-X1, 0, X1, 5, 500)
    self._draw_buffer(Y1, X3-X2, 0, X2, [], 5)

    minimap = curses.newwin(Y1, X-X3, 0, X3)
    minimap.bkgd(' ', self._attr_sb)

    info1 = curses.newwin(Y2-Y1, X, Y1, 0)
    info1.bkgd(' ', self._attr_cm)

    info2 = curses.newwin(Y-Y2, X, Y2, 0)
    info2.bkgd(' ', self._attr_cm)

    dirwin.noutrefresh()
    minimap.noutrefresh()
    info1.noutrefresh()
    info2.noutrefresh()
    curses.doupdate()

  def _draw_line_numbers(self, dy, dx, sy, sx, i, max_i):
    win = curses.newwin(dy, dx, sy, sx)
    win.bkgd(' ', self._attr_ln)
    for p, y in enumerate(range(i, min(i+dy, max_i))):
      win.addstr(p, 0, '|%s ' % str(y).rjust(dx-3), self._attr_ln)
    win.noutrefresh()

  def _draw_buffer(self, dy, dx, sy, sx, lines, sl):
    win = curses.newwin(dy, dx, sy, sx)
    win.bkgd(' ', self._attr_def)
    for p, (ln, line) in enumerate(zip(range(sl, sl+dy), lines[sl:])):
      win.addstr(p, 0, line, self._attr_def)
    win.addstr(0, 0, ' ', self._attr_def|curses.A_REVERSE)
    win.noutrefresh()

def main(stdscr):
  curses.start_color()
  curses.curs_set(0)
  Editor(stdscr).run()

if __name__ == '__main__':
  curses.wrapper(main)


