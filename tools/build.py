#!/usr/bin/env python3
"""Build dist/redwand.wad from src/ plus red-recoloured sprites (wand + bow) taken from your HERETIC.WAD.

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

# Red bow (Ethereal Crossbow): green ethereal glow + orange powered bolts -> red
BOW_SPRITES = ['CRBW' + c + '0' for c in 'ABCDEFGH']       # first-person crossbow
BOW_SPRITES += ['WBOWA0', 'AMC1A0', 'AMC2A0', 'AMC2B0', 'AMC2C0']
BOW_PREFIXES = ('FX03', 'FX14')                            # bolts, impacts, powered bolts (all rotations)
BOW_GRAPHICS = ['INAMBOW']

RED_RAMP = [251, 250, 249, 248] + list(range(145, 161)) + [161, 162, 163, 164, 165]  # dark red -> hot pink-white
WARM = list(range(111, 145)) + list(range(241, 248))      # gold/orange/yellow ramps
GREEN = list(range(209, 225))                              # bright green ramp
GREY_GREEN = list(range(225, 241))                         # muted green ramp

def _lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]

def build_remap(pal, groups):
    """groups: list of (source indices, normalise-against indices). Maps by luminance onto RED_RAMP."""
    remap = list(range(256))
    for src, norm in groups:
        lmax = max(_lum(pal[i]) for i in norm)
        for i in src:
            f = min(1.0, _lum(pal[i]) / lmax)
            remap[i] = RED_RAMP[min(len(RED_RAMP) - 1, round(f * (len(RED_RAMP) - 1)))]
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
        # v2: 7 tics per shot (v1 10, vanilla 11)
        st('Fire01', '@next', 'B', 2),
        st('Fire02', '@next', 'C!', 0, 'A_ConsumeAmmo'),
        st('Fire03', '@next', 'C!', 0, 'A_WeaponSound', ['gldhit']),
        st('Fire04', '@next', 'C!', 3, 'A_WeaponBulletAttack', [2.8125, 0, 1, unpow_base, 3, 'GoldWandPuff1']),
        st('Fire05', '@next', 'D', 2),
        st('Fire06', ready, 'D', 0, 'A_ReFire'),

        # v2: 7 tics per powered shot (v1 9)
        st('PFire01', '@next', 'B', 2, 'A_WeaponSound', ['gldchg']),
        st('PFire02', '@next', 'C!', 0, 'A_ConsumeAmmo'),
        st('PFire03', '@next', 'C!', 0, 'A_WeaponProjectile', ['GoldWandFX2', -5.625]),
        st('PFire04', '@next', 'C!', 0, 'A_WeaponProjectile', ['GoldWandFX2', 5.625]),
        st('PFire05', '@next', 'C!', 0, 'A_WeaponSound', ['gldhit']),
        st('PFire06', '@next', 'C!', 3, 'A_WeaponBulletAttack', [5.625, 0, 5, mult, 8, 'GoldWandPuff2']),
        st('PFire07', '@next', 'D', 2),
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

def exdefs_doc(comment, data):
    return {'type': 'exdefs', 'version': '1.0.0',
            'metadata': {'author': 'altanc', 'timestamp': '2026-11-23T00:00:00+00:00', 'application': 'N/A',
                         'comment': comment},
            'data': data}

def exdefs_bow():
    """Red bow: one heavy bolt per shot (vanilla 1 + 2 small), three heavy bolts powered (vanilla 3 + 2 small).

    Fires through the game's own A_FireCrossbowPL1/PL2 so aiming and ammo use behave exactly like the
    original (the generic A_WeaponProjectile aimed off-target in playtest). The two small side bolts
    (CrossbowFX3) are disabled: no damage, no sound, removed after one tic.

    CrossbowFX1: speed 30 -> 40, damage 10 -> 50 (avg 225 per shot; vanilla volley avg 63).
    CrossbowFX2 (powered): speed 32 -> 42, damage 6 -> 40 (3 bolts, avg 540 per shot).
    Fire cycle 12 tics (vanilla 31), powered 10 (vanilla 25).
    """
    p = 'RB_'
    ready = 'S_HERETIC_CRBOW1'
    st = lambda name, nxt, frame, tics, action=None, args=None, sprite='CRBW': dict(
        [('name', p + name), ('next', nxt if nxt.startswith(('@', 'S_')) else p + nxt),
         ('sprite', sprite), ('frame', frame), ('tics', tics)]
        + ([('action', action)] if action else []) + ([('args', args)] if args is not None else []))
    states = [
        st('Fire01', '@next', 'D!', 3, 'A_FireCrossbowPL1'),
        st('Fire02', '@next', 'E', 2),
        st('Fire03', '@next', 'F', 1),
        st('Fire04', '@next', 'G', 1),
        st('Fire05', '@next', 'H', 1),
        st('Fire06', '@next', 'A', 1),
        st('Fire07', '@next', 'B', 1),
        st('Fire08', ready, 'C', 2, 'A_ReFire'),

        st('PFire01', '@next', 'D!', 3, 'A_FireCrossbowPL2'),
        st('PFire02', '@next', 'E', 1),
        st('PFire03', '@next', 'F', 1),
        st('PFire04', '@next', 'G', 1),
        st('PFire05', '@next', 'H', 1),
        st('PFire06', '@next', 'A', 1),
        st('PFire07', '@next', 'B', 1),
        st('PFire08', ready, 'C', 1, 'A_ReFire'),

        st('NoBolt', '@stop', 'A', 1, sprite='FX03'),
    ]
    return exdefs_doc('Red bow', {
        'weapons': [
            {'name': 'Crossbow', 'firestate': p + 'Fire01', 'holdstate': p + 'Fire01'},
            {'name': 'CrossbowPowered', 'firestate': p + 'PFire01', 'holdstate': p + 'PFire01'},
        ],
        'actors': [
            {'name': 'CrossbowFX1', 'speed': 40, 'damage': 50, 'seesound': 'bowsht'},
            {'name': 'CrossbowFX2', 'speed': 42, 'damage': 40},
            {'name': 'CrossbowFX3', 'speed': 1, 'damage': 0, 'seesound': 'None', 'spawnstate': p + 'NoBolt'},
        ],
        'states': states,
    })

def exdefs_ammo(enhanced):
    """Double max ammo and every pickup amount for wand crystals and arrows.
    The enhanced-weapons option changes crossbow ammo (max 30/60, pickups 3/15/6), so that
    variant doubles those values instead of vanilla's (max 50/100, pickups 5/20/10)."""
    if enhanced:
        bow = {'maxammo': 60, 'maxupgradedammo': 120, 'clipammo': 6, 'boxammo': 30, 'backpackammo': 6,
               'weaponammo': 12, 'weaponpieceammo': 12, 'deathmatchweaponammo': 12}
    else:
        bow = {'maxammo': 100, 'maxupgradedammo': 200, 'clipammo': 10, 'boxammo': 40, 'backpackammo': 10,
               'weaponammo': 20, 'weaponpieceammo': 20, 'deathmatchweaponammo': 20}
    ammo = [dict(name='CrossbowAmmo', **bow)]
    if not enhanced:
        ammo.insert(0, {'name': 'GoldWandAmmo', 'maxammo': 200, 'maxupgradedammo': 400,
                        'clipammo': 20, 'boxammo': 100, 'backpackammo': 20})
    return exdefs_doc('Double ammo' + (' (enhanced weapons)' if enhanced else ''), {'ammo': ammo})

def main():
    iwad = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'HERETIC.WAD')
    L = read_wad(iwad)
    pal = palette(L)
    remap = build_remap(pal, [(WARM, WARM)])
    bow_remap = build_remap(pal, [(WARM, WARM), (GREEN + GREY_GREEN, GREEN)])

    text = lambda f: open(os.path.join(SRC, f), 'rb').read()
    lumps = [
        ('EXDEFS', json.dumps(json.load(open(os.path.join(SRC, 'EXDEFS.json'))), indent=2).encode()),
        ('RW_4X', json.dumps(exdefs_variant(4), indent=2).encode()),
        ('RW_8X', json.dumps(exdefs_variant(8), indent=2).encode()),
        ('RB_BOW', json.dumps(exdefs_bow(), indent=2).encode()),
        ('RW_AMMO', json.dumps(exdefs_ammo(False), indent=2).encode()),
        ('RW_AMMOX', json.dumps(exdefs_ammo(True), indent=2).encode()),
        ('ZSCRIPT', text('ZSCRIPT.zs')),
        ('CVARINFO', text('CVARINFO.txt')),
        ('MENUDEF', text('MENUDEF.txt')),
        ('MAPINFO', text('MAPINFO.txt')),
    ]
    for g in GRAPHICS:
        lumps.append((g, recolor_patch(get(L, g), remap)))
    for g in BOW_GRAPHICS:
        lumps.append((g, recolor_patch(get(L, g), bow_remap)))
    lumps.append(('SS_START', b''))
    for s in SPRITES:
        b = get(L, s)
        lumps.append((s, recolor_wand(b, remap) if s.startswith('GWND') else recolor_patch(b, remap)))
    bow = BOW_SPRITES + [n for n, _ in L if n.startswith(BOW_PREFIXES)]
    for s_ in dict.fromkeys(bow):
        lumps.append((s_, recolor_patch(get(L, s_), bow_remap)))
    lumps.append(('SS_END', b''))

    os.makedirs(os.path.join(ROOT, 'dist'), exist_ok=True)
    out = os.path.join(ROOT, 'dist', 'redwand.wad')
    write_wad(out, lumps)
    print('wrote', out, len(lumps), 'lumps')

if __name__ == '__main__':
    main()
