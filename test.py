import curses

def main(stdscr):
  if not curses.can_change_color():
    raise Exception('Cannot change color')

  stdscr.addstr(1, 0, repr(curses.color_content(curses.COLOR_BLACK)))
  curses.init_color(curses.COLOR_BLACK, 999,   0,   0)
  curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
  curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
  stdscr.addstr(0, 0, 'hello', curses.color_pair(1))
  stdscr.addstr(' world', curses.color_pair(2))
  stdscr.addstr(2, 0, repr(curses.color_content(curses.COLOR_BLACK)))
  stdscr.getch()

curses.wrapper(main)

