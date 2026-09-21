#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2010-2018, Google Inc.
# All rights reserved.
#
# Ported from the original Python 2 script shipped with mozc (gui/character_pad)
# to Python 3 for the mozc-standalone build. Behavior is kept identical.

import re
import sys

kUnicodePat = re.compile(r'[0-9A-Fa-f]{2,4}')


def IsValidUnicode(n):
  return kUnicodePat.match(n)


def LoadJISX0201(filename):
  fh = open(filename)
  result = []
  for line in fh.readlines():
    if line[:1] == '#':
      continue
    array = line.split()
    if len(array) < 2:
      continue
    jis = array[0].replace('0x', '')
    ucs2 = array[1].replace('0x', '')
    if len(jis) == 2:
      jis = "00" + jis

    if IsValidUnicode(ucs2):
      result.append([jis, ucs2])

  return ["JISX0201", result]


def LoadJISX0208(filename):
  fh = open(filename)
  result = []
  for line in fh.readlines():
    if line[:1] == '#':
      continue
    array = line.split()
    if len(array) < 3:
      continue
    jis = array[1].replace('0x', '')
    ucs2 = array[2].replace('0x', '')
    if IsValidUnicode(ucs2):
      result.append([jis, ucs2])

  return ["JISX0208", result]


def LoadJISX0212(filename):
  fh = open(filename)
  result = []
  for line in fh.readlines():
    if line[:1] == '#':
      continue
    array = line.split()
    if len(array) < 2:
      continue
    jis = array[0].replace('0x', '')
    ucs2 = array[1].replace('0x', '')
    if IsValidUnicode(ucs2):
      result.append([jis, ucs2])

  return ["JISX0212", result]


def LoadCP932(filename):
  fh = open(filename)
  result = []
  for line in fh.readlines():
    if line[:1] == '#':
      continue
    array = line.split()
    if len(array) < 2:
      continue
    sjis = array[0].replace('0x', '')
    ucs2 = array[1].replace('0x', '')
    if int(sjis, 16) < 32:
      continue
    if len(sjis) == 2:
      sjis = "00" + sjis

    if IsValidUnicode(ucs2):
      result.append([sjis, ucs2])

  return ["CP932", result]


def Output(arg):
  name = arg[0]
  result = arg[1]
  print("static const size_t k%sMapSize = %d;" % (name, len(result)))
  print("static const mozc::gui::CharacterPalette::LocalCharacterMap k%sMap[] = {" % (name))
  for n in result:
    print("  { 0x%s, 0x%s }," % (n[0], n[1]))
  print("  { 0, 0 }")
  print("};")
  print("")


if __name__ == "__main__":
  Output(LoadJISX0201(sys.argv[1]))
  Output(LoadJISX0208(sys.argv[2]))
  Output(LoadJISX0212(sys.argv[3]))
  Output(LoadCP932(sys.argv[4]))
