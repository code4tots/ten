"""ten.py

Simple text editor in Python 2/3.

"""

import curses
import string

DEFAULT_COLOR_PAIR = 1
PRINTABLE = set(ord(c) for c in string.printable)

class Editor(object):
  def __init__(self, lines=None, attrs=None, cursors=None, path=None):
    self._l = lines or ['']
    self._a = attrs
    self._c = cursors or [(0, 0)]
    self._p = path

  def draw(self, window, start_line):
    dy, dx = window.getmaxyx()
    end_line = min(start_line + dy, len(self._l))
    end_view_line = start_line + dy
    window.bkgd(' ', self._a)

    #* Draw text.
    for y in range(end_line - start_line):
      window.addstr(y, 0, self._l[start_line + y][:dx], self._a)

    #* Draw cursors.
    for pos in self._c:
      row, col = pos
      if start_line <= row < end_view_line and 0 <= col < dx:
        y = row - start_line
        x = col
        window.addstr(y, x, self[pos], self._a|curses.A_REVERSE)

  def __getitem__(self, pos):
    row, col = pos
    if row < len(self._l):
      line = self._l[row]
      if col < len(line):
        return line[col]
    return ' '

  def add(self, s):
    for c in s:
      if c == '\n':
        self._add_newline()
      else:
        self._add_char(c)

  def _add_char(self, c):
    for pos in self._c:
      row, col = pos
      #* Modify the buffer
      while row >= len(self._l):
        self._l.append('')
      while col >= len(self._l[row]):
        self._l[row] += ' '
      self._l[row] = self._l[row][:col] + c + self._l[row][col+1:]
      #* Update the cursors positions.
      new_cursors = []
      for cursor in self._c:
        if cursor[0] == row and cursor[1] >= col:
          new_cursors.append((cursor[0], cursor[1]+1))
        else:
          new_cursors.append(cursor)
      self._c = _norepeat(new_cursors)

  def _add_newline(self):
    for pos in self._c:
      row, col = pos
      #* Modify the buffer
      while row >= len(self._l):
        self._l.append('')
      self._l = (
          self._l[:row] +
          [self._l[row][:col], self._l[row][col:]] +
          self._l[row+1:])
      #* Update the cursors positions.
      new_cursors = []
      for cursor in self._c:
        if cursor[0] == row and cursor[1] >= col:
          new_cursors.append((cursor[0]+1, cursor[1]-col))
        elif cursor[0] >= row:
          new_cursors.append((cursor[0]+1, cursor[1]))
        else:
          new_cursors.append(cursor)
      self._c = _norepeat(new_cursors)

  def backspace(self):
    for pos in self._c:
      row, col = pos
      if col == 0:
        self._backspace_newline_one(pos)
      else:
        self._backspace_char_one(pos)

  def _backspace_char_one(self, pos):
    row, col = pos
    #* Modify the buffer
    while row >= len(self._l):
      self._l.append('')
    while col >= len(self._l[row]):
      self._l[row] += ' '
    self._l[row] = self._l[row][:col-1] + self._l[row][col:]
    #* Update the cursors positions.
    new_cursors = []
    for cursor in self._c:
      if cursor[0] == row and cursor[1] >= col:
        new_cursors.append((cursor[0], cursor[1]-1))
      else:
        new_cursors.append(cursor)
    self._c = _norepeat(new_cursors)

  def _backspace_newline_one(self, pos):
    row, col = pos
    if row == 0:
      return
    #* Modify the buffer
    while row >= len(self._l):
      self._l.append('')
    self._l = (
        self._l[:row] +
        [self._l[row][:col], self._l[row][col:]] +
        self._l[row+1:])
    #* Update the cursor positions.
    new_cursors = []
    for cursor in self._c:
      if cursor[0] == row:
        nrow = cursor[0]-1
        new_cursors.append((nrow, cursor[1]+len(self._l[nrow])))
      elif cursor[0] >= row:
        new_cursors.append((cursor[0]+1, cursor[1]))
      else:
        new_cursors.append(cursor)
    self._c = _norepeat(new_cursors)

  def move_up(self):
    new_cursors = []
    for cursor in self._c:
      row, col = cursor
      if row == 0:
        new_cursors.append(cursor)
      else:
        new_cursors.append((row-1, min(col, len(self._l[row-1]))))
    self._c = _norepeat(new_cursors)

  def move_down(self):
    new_cursors = []
    for cursor in self._c:
      row, col = cursor
      if row+1 >= len(self._l):
        new_cursors.append(cursor)
      else:
        new_cursors.append((row+1, min(col, len(self._l[row+1]))))
    self._c = _norepeat(new_cursors)

  def move_left(self):
    new_cursors = []
    for cursor in self._c:
      row, col = cursor
      if row == 0 and col == 0:
        new_cursors.append(cursor)
      elif col > 0:
        new_cursors.append((row, col-1))
      else:
        new_cursors.append((row-1, len(self._l[row-1])))
    self._c = _norepeat(new_cursors)

  def move_right(self):
    new_cursors = []
    for cursor in self._c:
      row, col = cursor
      if row >= len(self._l)-1 and col >= len(self._l[row]):
        new_cursors.append(cursor)
      elif col < len(self._l[row]):
        new_cursors.append((row, col+1))
      else:
        new_cursors.append((row+1, 0))
    self._c = _norepeat(new_cursors)

  def clone_up(self):
    cursors = self._c
    self.move_up()
    self._c = _norepeat(cursors + self._c)

  def clone_down(self):
    cursors = self._c
    self.move_down()
    self._c = _norepeat(cursors + self._c)

def _norepeat(xs):
  l = []
  for x in xs:
    if x not in l:
      l.append(x)
  return l


def main(window):
  curses.curs_set(0)
  curses.raw()
  curses.use_default_colors()
  curses.init_pair(DEFAULT_COLOR_PAIR, -1, -1)
  e = Editor(attrs=curses.color_pair(DEFAULT_COLOR_PAIR)|curses.A_NORMAL)
  e.draw(window, 0)
  while True:
    c = window.getch()
    if c == 3:  # break on '^c'
      break
    elif c == 127:  # backspace
      e.backspace()
    # elif c == 10:  # '^j'
    #   e.clone_down()
    # elif c == 11:  # '^k'
    #   e.clone_up()
    elif c == curses.KEY_LEFT:
      e.move_left()
    elif c == curses.KEY_RIGHT:
      e.move_right()
    elif c == curses.KEY_UP:
      e.move_up()
    elif c == curses.KEY_DOWN:
      e.move_down()
    elif c in PRINTABLE:
      e.add(chr(c))
    else:
      raise Exception('Non-printable char: ' + repr(c))
    e.draw(window, 0)
    window.refresh()

if __name__ == '__main__':
  curses.wrapper(main)

