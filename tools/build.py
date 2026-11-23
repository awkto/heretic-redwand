#!/usr/bin/env python3
"""Build dist/redwand.wad from src/ plus red-recoloured sprites taken from your HERETIC.WAD.

    python3 tools/build.py /path/to/HERETIC.WAD

The WAD works in both the Heretic + Hexen remaster (KEX, via EXDEFS) and
GZDoom/UZDoom (via ZSCRIPT). Each engine ignores the other's lumps.
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wadlib import read_wad, get, palette, recolor_patch, decode_patch, write_wad

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')

# --- sprites to recolour -------------------------------------------------------
SPRITES = ['FX01' + c + '0' for c in 'ABCDEFGH']          # wand projectiles / powered puff
SPRITES += ['PUF2' + c + '0' for c in 'ABCDE']             # unpowered hit puff
SPRITES += ['GWND' + c + '0' for c in 'ABCD']              # first-person wand
SPRITES += ['AMG1A0', 'AMG2A0', 'AMG2B0', 'AMG2C0']        # wand crystal ammo pickups
GRAPHICS = ['INAMGLD']                                     # status bar ammo icon

def build_remap(pal):
    lum = lambda c: 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]
    warm = list(range(111, 145)) + list(range(241, 248))   # gold/orange/yellow ramps
    ramp = [251, 250, 249, 248] + list(range(145, 161)) + [161, 162, 163, 164, 165]  # dark red -> hot pink-white
    lmax = max(lum(pal[i]) for i in warm)
    remap = list(range(256))
    for i in warm:
        f = lum(pal[i]) / lmax
        remap[i] = ramp[min(len(ramp) - 1, round(f * (len(ramp) - 1)))]
    return remap

def recolor_wand(b, remap):
    """Recolour only the crystal on the first-person wand, not the wooden handle."""
    import struct
    w, h, lo, to = struct.unpack('<hhhh', b[:8])
    cut = int(h * 0.72)
    b = bytearray(b)
    cols = struct.unpack('<%di' % w, b[8:8 + 4 * w])
    for c in cols:
        while b[c] != 255:
            top, ln = b[c], b[c + 1]
            for i in range(ln):
                if top + i < cut:
                    b[c + 3 + i] = remap[b[c + 3 + i]]
            c += ln + 4
    return bytes(b)

# --- KEX EXDEFS ---------------------------------------------------------------
def exdefs_variant(mult):
    """GoldWand fire states built from engine functions with explicit damage.

    Vanilla unpowered: one hitscan, 7..14 (avg 10.5).
      -> A_WeaponBulletAttack base*(1..3): base 21 @4x (avg 42), 42 @8x (avg 84).
    Vanilla powered: five hitscans 1..8 (avg 4.5) + two GoldWandFX2 (damage 1).
      -> five bullets base*(1..8) with base = mult (exactly vanilla x mult),
         two GoldWandFX2 with damage = mult.
    A_WeaponBulletAttack args: hspread, vspread, numbullets, damagebase, damagedice, puff.
    """
    p = 'RW%d_' % mult
    unpow_base = {4: 21, 8: 42}[mult]
    ready = 'S_HERETIC_GOLDWANDREADY'
    st = lambda name, nxt, frame, tics, action=None, args=None: dict(
        [('name', p + name), ('next', nxt if nxt.startswith(('@', 'S_')) else p + nxt),
         ('sprite', 'GWND'), ('frame', frame), ('tics', tics)]
        + ([('action', action)] if action else []) + ([('args', args)] if args is not None else []))
    states = [
        st('Fire01', '@next', 'B', 3),
        st('Fire02', '@next', 'C!', 0, 'A_ConsumeAmmo'),
        st('Fire03', '@next', 'C!', 0, 'A_WeaponSound', ['gldhit']),
        st('Fire04', '@next', 'C!', 4, 'A_WeaponBulletAttack', [2.8125, 0, 1, unpow_base, 3, 'GoldWandPuff1']),
        st('Fire05', '@next', 'D', 3),
        st('Fire06', ready, 'D', 0, 'A_ReFire'),

        st('PFire01', '@next', 'B', 3, 'A_WeaponSound', ['gldchg']),
        st('PFire02', '@next', 'C!', 0, 'A_ConsumeAmmo'),
        st('PFire03', '@next', 'C!', 0, 'A_WeaponProjectile', ['GoldWandFX2', -5.625]),
        st('PFire04', '@next', 'C!', 0, 'A_WeaponProjectile', ['GoldWandFX2', 5.625]),
        st('PFire05', '@next', 'C!', 0, 'A_WeaponSound', ['gldhit']),
        st('PFire06', '@next', 'C!', 3, 'A_WeaponBulletAttack', [5.625, 0, 5, mult, 8, 'GoldWandPuff2']),
        st('PFire07', '@next', 'D', 3),
        st('PFire08', ready, 'D', 0, 'A_ReFire'),
    ]
    return {
        'type': 'exdefs', 'version': '1.0.0',
        'metadata': {'author': 'altanc', 'timestamp': '2026-11-10T00:00:00+00:00', 'application': 'N/A',
                     'comment': 'Red Elven Wand - %dx damage' % mult},
        'data': {
            'weapons': [
                {'name': 'GoldWand', 'firestate': p + 'Fire01', 'holdstate': p + 'Fire01'},
                {'name': 'GoldWandPowered', 'firestate': p + 'PFire01', 'holdstate': p + 'PFire01'},
            ],
            'actors': [{'name': 'GoldWandFX2', 'damage': mult}],
            'states': states,
        },
    }

def main():
    iwad = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'HERETIC.WAD')
    L = read_wad(iwad)
    pal = palette(L)
    remap = build_remap(pal)

    text = lambda f: open(os.path.join(SRC, f), 'rb').read()
    lumps = [
        ('EXDEFS', json.dumps(json.load(open(os.path.join(SRC, 'EXDEFS.json'))), indent=2).encode()),
        ('RW_4X', json.dumps(exdefs_variant(4), indent=2).encode()),
        ('RW_8X', json.dumps(exdefs_variant(8), indent=2).encode()),
        ('ZSCRIPT', text('ZSCRIPT.zs')),
        ('CVARINFO', text('CVARINFO.txt')),
        ('MENUDEF', text('MENUDEF.txt')),
        ('MAPINFO', text('MAPINFO.txt')),
    ]
    for g in GRAPHICS:
        lumps.append((g, recolor_patch(get(L, g), remap)))
    lumps.append(('SS_START', b''))
    for s in SPRITES:
        b = get(L, s)
        lumps.append((s, recolor_wand(b, remap) if s.startswith('GWND') else recolor_patch(b, remap)))
    lumps.append(('SS_END', b''))

    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    out = os.path.join(ROOT, 'dist', 'redwand.wad')
    write_wad(out, lumps)
    print('wrote', out, len(lumps), 'lumps')

if __name__ == '__main__':
    main()
