// Minimal stand-in for the generated base/character_set.inc.
//
// The original file is produced by base/gen_character_set.py from the
// CP932/JISX0201/JISX0208/JISX0212/JISX0213 mapping tables and provides a
// precise per-codepoint classification used by Util::GetCharacterSet().
// None of the character_palette / hand_writing tools in this standalone
// build call Util::GetCharacterSet(), so a simplified implementation is
// sufficient here: it only distinguishes ASCII from everything else,
// which keeps base/util.cc self-contained without porting the (Python 2)
// generator script.
Util::CharacterSet Util::GetCharacterSet(char32 ucs4) {
  if (ucs4 <= 0x7F) {
    return Util::ASCII;
  }
  return Util::UNICODE_ONLY;
}
