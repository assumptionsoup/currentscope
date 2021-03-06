# -*- coding: utf-8 -*-
"""
    CurrentScope is a Sublime Text 2 plugin which shows the current
    scope in the status bar.

    https://github.com/gumuz/currentscope/

    Created by Guyon Moree http://gumuz.nl/

    Notes:

        * Currently only Python is supported.
"""

import re

import sublime, sublime_plugin


DEF = re.compile(r'^(\s*)def\s+(.+)\s*\(.*\):')
CLS1 = re.compile(r'^(\s*)class\s+(.+)\(.*\)\s*:')
CLS2 = re.compile(r'^(\s*)class\s+(.+)\s*:')
WS = re.compile(r'^(\s*)(.*)')


class CurrentScope(sublime_plugin.EventListener):
    def on_selection_modified(self, view):
        try:
            # find the last, empty region
            region = [r for r in view.sel() if r.empty()].pop()
            # check for python syntax
            assert view.scope_name(region.end()).startswith('source.python')
        except (IndexError, AssertionError):
            # no suitable region found
            view.erase_status('CurrentScope')
            return

        scopes = []

        # get current indent
        line = view.substr(view.line(region))
        current_indent, _ = WS.match(line).groups()

        # reverse iterate through rows from current row
        row, col = view.rowcol(region.end())
        for row in reversed(range(row)):
            line = view.substr(view.line(sublime.Region(view.text_point(row, 0))))

            if not line.strip():
                # skip empty lines
                continue

            for pattern in (DEF, CLS1, CLS2):
                # check function/method/class definitions
                match = pattern.match(line)
                if match:
                    indent, name = match.groups()

                    if len(indent) < len(current_indent):
                        scopes.append(name)
                        current_indent = indent
                    break

        # Status messages are ordered by key-name, so making this key
        # the first character should make it the first message to
        # appear.
        scopeKey = chr(0)
        if scopes:
            scope = ".".join(reversed(scopes))
            view.set_status(scopeKey, '--%s--' % scope)
        else:
            view.erase_status(scopeKey)
