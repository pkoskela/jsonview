#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, json, curses, os, collections, locale, itertools
reload(sys)
sys.setdefaultencoding('utf-8')

def render(obj, scr, level = 0, isKey=None, wrap=True, levelStep=2):
 if type(obj) in [int, float, bool, str, unicode]:
  if type(obj) in [str, unicode] and wrap: scr.addstr('"', curses.color_pair(1))
  if isKey: scr.attron(curses.color_pair(3) | curses.A_BOLD)
  else: scr.attron(curses.color_pair(2) | curses.A_BOLD)
  p0 = scr.getyx()
  scr.addstr(str(obj))
  p1 = scr.getyx()
  if type(obj) in [str, unicode] and wrap: scr.addstr('"', curses.color_pair(1))
  return (('value', p0, p1), None)
 if type(obj) in [list]:
  p = []
  p0 = scr.getyx()
  scr.addstr('[', curses.color_pair(1))
  for i, v in enumerate(obj):
   sy, sx = scr.getyx()
   scr.move(sy+1, (level+1)*levelStep)
   r = render(v, scr, level=level+1)
   p.append(r)
   if i != len(obj)-1:
    scr.addstr(',', curses.color_pair(1))
  sy, sx = scr.getyx()
  scr.move(sy+1, level*levelStep)
  p1 = scr.getyx()
  scr.addstr(']', curses.color_pair(1))
  return (('list', p0, p1), p)
 if type(obj) in [dict, collections.OrderedDict]:
  p = []
  p0 = scr.getyx()
  scr.addstr('{', curses.color_pair(1))
  for i, kv in enumerate(obj.iteritems()):
   k, v = kv
   sy, sx = scr.getyx()
   scr.move(sy+1, (level+1)*levelStep)
   r = render(k, scr, level=level+1, isKey=True)
   scr.addstr(': ', curses.color_pair(1))
   r2 = render(v, scr, level=level+1)
   p.append( (r[0], r2) )
   if i != len(obj)-1:
    scr.addstr(',', curses.color_pair(1))
  sy, sx = scr.getyx()
  scr.move(sy+1, level*levelStep)
  p1 = scr.getyx()
  scr.addstr('}', curses.color_pair(1))
  return (('object', p0, p1), p)

def looplines(t, lines=None, maxline=None):
 if lines is None: lines = []
 if (type(t) is tuple) and (type(t[0]) is str) and (t[0] in ['value', 'list', 'object']):
  while len(lines) < max(t[1][0], t[2][0])+1: lines.append( [] )
  if t[0] in ['value']:
   for i in range(t[1][0], t[2][0]+1):
    x0, x1 = 0, maxline
    if i == t[1][0]: x0 = t[1][1]
    if i == t[2][0]: x1 = t[2][1]
    lines[i].append( (x0, x1) )
  if t[0] in ['list', 'object']:
   lines[t[1][0]].append( (t[1][1], t[1][1]+1,) )
   lines[t[2][0]].append( (t[2][1], t[2][1]+1,) )
  return
 if type(t) is list:
  for i, v in enumerate(t):
   looplines(v, lines, maxline=maxline)
 if type(t) is tuple:
  if t[0] is not None:
   looplines(t[0], lines, maxline=maxline)
  if t[1] is not None:
   for i, v in enumerate(t[1]):
    looplines(v, lines, maxline=maxline)
 return lines

def view(stdscr, j):
 curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
 curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
 curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)

 tokens = None
 doclen = stdscr.getmaxyx()[0]
 while 1:
  pad = curses.newpad(doclen, stdscr.getmaxyx()[1])
  try:
   tokens = render(j, pad)
  except curses.error:
   doclen *= 2
   continue
  break
 doclen = pad.getyx()[0]+1

 lines = looplines(tokens, maxline=stdscr.getmaxyx()[1])

 scroll = 0
 yx = (0, 0)

 while 1:
  stdscr.move(stdscr.getmaxyx()[0]-1, 0)
  stdscr.addstr('[STDIN]')
  stdscr.refresh()

  if yx[0] - scroll - 1 == stdscr.getmaxyx()[0]-2: scroll += 1
  if yx[0] - scroll + 1 == 0: scroll -= 1

  while yx[0] - scroll > stdscr.getmaxyx()[0]-1: scroll += stdscr.getmaxyx()[0]-1
  while yx[0] - scroll < 0: scroll -= stdscr.getmaxyx()[0]-1

  scroll = max(min(scroll, (doclen - (stdscr.getmaxyx()[0]-1))), 0)
 
  pad.refresh(scroll, 0, 0, 0, stdscr.getmaxyx()[0]-2, stdscr.getmaxyx()[1]-1)

  nyx = list(yx)
  line = list(itertools.chain(*map(lambda x:range(x[0], x[1]), sorted(lines[nyx[0]]))))
  candids = [x for x in line if x <= nyx[1]]
  if len(candids) > 0:
   nyx[1] = candids[-1]
  else:
   nyx[1] = line[0]
  stdscr.move(nyx[0] - scroll, nyx[1])

  ch = stdscr.getch()
  if ch in [113]: break

  if ch in [32, 338, 6]: yx = (yx[0] + (stdscr.getmaxyx()[0]-1), yx[1])
  if ch in [339, 2]: yx = (yx[0] - (stdscr.getmaxyx()[0]-1), yx[1])
  scroll = max(min(scroll, (doclen - (stdscr.getmaxyx()[0]-1))), 0)

  if ch in [258, 106]: yx = (yx[0]+1, yx[1])
  if ch in [259, 107]: yx = (yx[0]-1, yx[1])
  if ch in [260, 104]:
   candids = [x for x in line if x < nyx[1]]
   if len(candids) > 0: yx = (yx[0], candids[-1])
  if ch in [261, 108]:
   candids = [x for x in line if x > nyx[1]]
   if len(candids) > 0: yx = (yx[0], candids[0])
  if yx[0] < 0: yx = (0, yx[1])
  if yx[0] >= doclen: yx = (doclen-1, yx[1])

if __name__ == "__main__":
 locale.setlocale(locale.LC_ALL, '')
 json_input = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(sys.stdin.read())
 os.dup2(os.open('/dev/tty', os.O_RDONLY), 0)
 curses.wrapper(view, json_input)
