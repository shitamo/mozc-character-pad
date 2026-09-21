#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2010-2018, Google Inc.
# All rights reserved.
#
# Ported from the original Python 2 script shipped with mozc (gui/character_pad)
# to Python 3 for the mozc-standalone build. Behavior is kept identical.

import re
import sys

kUnicodePat = re.compile(r'0x[0-9A-Fa-f]{2,4}')


def IsValidUnicode(n):
  return kUnicodePat.match(n)


def main():
  fh = open(sys.argv[1])
  result = {}
  for line in fh.readlines():
    if line[:1] == '#':
      continue
    array = line.split()
    if len(array) < 2:
      continue
    sjis = array[0]
    ucs2 = array[1]
    if eval(sjis) < 32 or not IsValidUnicode(ucs2):
      continue
    result.setdefault(ucs2, sjis)

  keys = sorted(result.keys())

  print("struct CP932MapData {")
  print("  unsigned int ucs4;")
  print("  unsigned short int sjis;")
  print("};")
  print("")
  print("static const size_t kCP932MapDataSize = %d;" % (len(keys)))
  print("static const CP932MapData kCP932MapData[] = {")
  for n in keys:
    print("  { %s, %s }," % (n, result[n]))
  print("  { 0, 0 }")
  print("};")


if __name__ == "__main__":
  main()
