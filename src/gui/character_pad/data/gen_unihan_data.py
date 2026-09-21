#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright 2010-2018, Google Inc.
# All rights reserved.
#
# Ported from the original Python 2 script shipped with mozc (gui/character_pad)
# to Python 3 for the mozc-standalone build. Behavior is kept identical, except
# that string_escape (a Python 2-only codec) is replaced with an equivalent
# hand-written C-string escaper that operates on the UTF-8 bytes of the value.

import re
import sys

rs = {}


def CEscapeBytes(data):
  """Escapes a bytes object into a C string literal body (no quotes)."""
  out = []
  for b in data:
    if b == 0x5c:  # backslash
      out.append('\\\\')
    elif b == 0x22:  # double quote
      out.append('\\"')
    elif 0x20 <= b < 0x7f:
      out.append(chr(b))
    else:
      out.append('\\x%02x' % b)
  return ''.join(out)


def Escape(n):
  if n != "NULL":
    return "\"%s\"" % (n)
  else:
    return "NULL"


def GetCode(n):
  if n != "NULL":
    n = n.replace('0-', 'JIS X 0208: 0x')
    n = n.replace('1-', 'JIS X 0212: 0x')
    n = n.replace('3-', 'JIS X 0213: 0x')
    n = n.replace('4-', 'JIS X 0213: 0x')
    n = n.replace('A-', 'Vendors Ideographs: 0x')
    n = n.replace('3A', 'JIS X 0213 2000: 0x')
    return "\"%s\"" % n
  else:
    return "NULL"


def GetRadical(n):
  pat = re.compile(r'^(\d+)\.')
  if n != "NULL":
    m = pat.match(n)
    if m:
      result = rs[m.group(1)]
      escaped = CEscapeBytes(result.encode('utf-8'))
      return "\"%s\"" % (escaped)
    else:
      return "NULL"
  else:
    return "NULL"


def main():
  fh = open(sys.argv[1], encoding='utf-8', errors='replace')
  for line in fh.readlines():
    array = line.split()
    if len(array) < 3:
      continue
    n = array[0]
    id_ = array[1]
    radical = array[2]
    rs[id_] = radical

  dic = {}
  pat = re.compile(
      r'^U\+(\S+)\s+(kTotalStrokes|kJapaneseKun|kJapaneseOn|kRSUnicode|'
      r'kIRG_JSource)\t(.+)')
  fh = open(sys.argv[2], encoding='utf-8', errors='replace')
  for line in fh.readlines():
    m = pat.match(line)
    if m:
      field = m.group(2)
      value = m.group(3).rstrip('\n')
      key = m.group(1)
      n = int(m.group(1), 16)
      if n <= 65536:
        dic.setdefault(key, {}).setdefault(field, value)

  keys = sorted(dic.keys())

  print("struct UnihanData {")
  print("  unsigned int ucs4;")
  # Since the total strokes defined in Unihan data is Chinese-based
  # number, we can't use it.
  # print "  unsigned char total_strokes;"
  print("  const char *japanese_kun;")
  print("  const char *japanese_on;")
  # Since the radical information defined in Unihan data is Chinese-based
  # number, we can't use it.
  # print "  const char *radical;"
  print("  const char *IRG_jsource;")
  print("};")
  print("static const size_t kUnihanDataSize = %d;" % (len(keys)))
  print("static const UnihanData kUnihanData[] = {")

  for key in keys:
    kun = Escape(dic[key].get("kJapaneseKun", "NULL"))
    on = Escape(dic[key].get("kJapaneseOn", "NULL"))
    code = GetCode(dic[key].get("kIRG_JSource", "NULL"))
    print(" { 0x%s, %s, %s, %s }," % (key, kun, on, code))

  print("};")


if __name__ == "__main__":
  main()
