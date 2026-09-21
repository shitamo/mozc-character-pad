#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2010-2018, Google Inc.
# All rights reserved.
#
# Ported from the original Python 2 script shipped with mozc (gui/character_pad)
# to Python 3 for the mozc-standalone build. Behavior is kept identical.

import re
import sys

kBlockPat = re.compile(r'^(.....?)\.\.(.....?); (.+)')


def main():
  print("static const mozc::gui::CharacterPalette::UnicodeBlock "
        "kUnicodeBlockTable[] = {")
  fh = open(sys.argv[1])
  for line in fh.readlines():
    if line[:1] == '#':
      continue
    m = kBlockPat.match(line)
    if m is not None:
      start = int(m.group(1), 16)
      end = int(m.group(2), 16)
      name = m.group(3).strip()
      if start <= 0x2FFFF and end <= 0x2FFFF:
        print("  { \"%s\", { %d, %d } }," % (name, start, end))

  print("  { NULL, { 0, 0 } }")
  print("};")
  print("")


if __name__ == "__main__":
  main()
