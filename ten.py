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
import queue
import threading


class Editor(object):
  def __init__(self, stdscr):
    self.stdscr = stdscr

  def draw(self):
    Y, X = self.stdscr.getmaxyx()
    if Y < 4:
      raise Exception('terminal must be at least 4 characters high')
    if X < 50:
      raise Exception('terminal must be at least 50 characters wide')
    X1 = 30
    X2 = 34
    X3 = X-20
    Y1 = Y-3
    Y2 = Y-2

    dirwin = curses.newwin(Y1, X1)
    dirwin.bkgd('_')

    lnwin = curses.newwin(Y1, X2-X1, 0, X1)
    lnwin.bkgd('c')

    textbuf = curses.newwin(Y1, X3-X2, 0, X2)
    textbuf.bkgd('-')

    minimap = curses.newwin(Y1, X-X3, 0, X3)
    minimap.bkgd('m')

    info1 = curses.newwin(Y2-Y1, X, Y1, 0)
    info1.bkgd('1')

    info2 = curses.newwin(Y-Y2, X, Y2, 0)
    info2.bkgd('2')

    dirwin.addstr(0, 0, repr((Y, X)))
    Y, X = lnwin.getmaxyx()
    dirwin.addstr(1, 0, repr((Y, X)))

    dirwin.noutrefresh()
    lnwin.noutrefresh()
    textbuf.noutrefresh()
    minimap.noutrefresh()
    info1.noutrefresh()
    info2.noutrefresh()
    curses.doupdate()

  def run(self):
    events = queue.Queue()
    threading.Thread(target=self._listen_to_inputs, args=(events,)).start()
    self.draw()
    while True:
      type_, data = events.get()
      self.draw()
      self.stdscr.addstr(repr((type_, data)))
      self.stdscr.refresh()
      if data == 3:
        break  # die on '^c'

  def _listen_to_inputs(self, events):
    while True:
      ch = self.stdscr.getch()
      events.put(('input', ch))
      if ch == 3:
        break  # die on '^c'


def main(stdscr):
  curses.raw()
  Editor(stdscr).run()

if __name__ == '__main__':
  curses.wrapper(main)


