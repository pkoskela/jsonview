jsonview
========

Reads a json from stdin and displays it in a curses window.

Features
--------
- python
- curses
- syntax highlighting
- intelligent navigation
- less-like usage
- reads from stdin

Examples
--------

```
curl -s "headers.jsontest.com" | python jv.py
echo '"string"' | python jv.py
echo '[1,2,3]' | python jv.py
```

![showcase](http://i.imgur.com/Df0vURi.gif)

TODO
----
- folding lists and objects
- string searching
- displaying node paths
