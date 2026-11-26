#!/usr/bin/env python3
"""Check that every sprite/frame used by an EXDEFS state in the mod exists.

The remaster crashes (null read in the sprite renderer) when a thing enters a
state whose sprite or frame isn't defined, so run this before every release:

    python3 tests/check_sprites.py dist/redwand.wad HERETIC.WAD [heretic_ex.wad]

Pass the remaster's heretic_ex.wad too, for the remaster-only monsters' sprites.
"""
import json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import wadlib

def names(path):
    return [l[0] if isinstance(l, tuple) else l['name'] for l in wadlib.read_wad(path)]

mod, wads = sys.argv[1], sys.argv[1:]
frames = {}
for w in wads:
    for n in names(w):
        n = n.upper()
        if re.match(r'^[A-Z0-9]{4}[A-Z\[\]\\]\d([A-Z\[\]\\]\d)?$', n):
            frames.setdefault(n[:4], set()).add(n[4])
            if len(n) == 8:
                frames[n[:4]].add(n[6])

L = wadlib.read_wad(mod)
bad = 0
for lump in names(mod):
    try:
        d = json.loads(wadlib.get(L, lump))
    except Exception:
        continue
    if not isinstance(d, dict) or not isinstance(d.get('data'), dict):
        continue
    for s in d['data'].get('states') or []:
        sp = (s.get('sprite') or '').upper()
        if not sp:
            continue
        for f in s.get('frame', '').replace('!', '').upper():
            if f not in frames.get(sp, ()):
                print('MISSING %s: state %s uses %s %s' % (lump, s['name'], sp, f))
                bad += 1
print('sprite check: %d missing' % bad)
sys.exit(1 if bad else 0)
