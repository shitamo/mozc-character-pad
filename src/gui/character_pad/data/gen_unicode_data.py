#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2010-2018, Google Inc.
# All rights reserved.
#
# Ported from the original Python 2 script shipped with mozc (gui/character_pad)
# to Python 3 for the mozc-standalone build. Behavior is kept identical.

import re
import sys


def main():
  results = []
  fh = open(sys.argv[1])
  for line in fh.readlines():
    array = re.split(r';', line)
    if len(array) < 11:
      continue
    code = array[0]
    desc = array[1]
    # the description for control character is placed at different place.
    if desc == "<control>":
      desc = array[10]
    code = int(code, 16)
    if code < 0x2FFFF:
      results.append("  { %d, \"%s\" }," % (code, desc))

  print("struct UnicodeData {")
  print("  char32 ucs4;")
  print("  const char *description;")
  print("};")
  print("")
  print("static const size_t kUnicodeDataSize = %d;" % (len(results)))
  print("static const UnicodeData kUnicodeData[] = {")
  for line in results:
    print(line)
  print("  { 0, NULL }")
  print("};")


if __name__ == "__main__":
  main()
