"""Hyper monsters for the KEX remaster (EXDEFS generator).

- Monsters move 2x as fast: their walk (See) and pain sequences are cloned with half the tics, so
  A_Chase runs twice as often. That doubles movement *and* how often they decide to attack. Every
  cloned attack/pain sequence returns to the fast walk.
- Monster projectiles fly 3x as fast (capped at PROJ_SPEED_CAP: much faster missiles can pass
  straight through the player in this engine) and do 4x damage.
- Attack sequences run in 1/3 of the time (cloned states, tics / 3) and monsters get RANGEHALF,
  so they decide to shoot more often. Together: roughly 3x the attack rate.
- Pure melee attacks become A_MonsterMeleeAttack with 4x vanilla damage. Enhanced-enemy attacks that
  take damage args (A_MonsterMeleeAttack, A_MonsterComboAttack) get those args x4. Attacks with
  hard-coded damage (e.g. A_KnightAttack's close swing, A_ClinkAttackEX) keep their normal melee damage.

Two variants: vanilla monsters, and the remaster's "Enhanced Enemies" option (heretic_enemies),
whose EX_E* lumps change some speeds, damages and attack chains. The enhanced chains are cloned
from the IWAD at build time.
"""
import json, math

PROJ_SPEED_CAP = 60
PROJ_SPEED_MULT, DAMAGE_MULT, TIC_DIV, SEE_DIV = 3, 4, 3, 2

# Vanilla monster speeds (Heretic info.c / GZDoom).
MONSTER_SPEED = {
    'HereticImp': 10, 'HereticImpLeader': 10,
    'Mummy': 12, 'MummyLeader': 12, 'MummyGhost': 12, 'MummyLeaderGhost': 12,
    'Knight': 12, 'KnightGhost': 12, 'Wizard': 12, 'Clink': 14, 'Beast': 14, 'Snake': 10,
    'Ironlich': 6, 'Sorcerer1': 16, 'Sorcerer2': 14, 'Minotaur': 16,
}
# Vanilla monster projectiles: (speed, damage).
PROJECTILES = {
    'HereticImpBall': (10, 1), 'MummyFX1': (9, 4), 'KnightAxe': (9, 2), 'RedAxe': (9, 7),
    'WizardFX1': (18, 3), 'BeastBall': (12, 4), 'SnakeProjA': (14, 1), 'SnakeProjB': (14, 3),
    'HeadFX1': (13, 1), 'HeadFX2': (8, 3), 'HeadFX3': (10, 5), 'Whirlwind': (10, 1),
    'SorcererFX1': (20, 10), 'Sorcerer2FX1': (20, 1), 'Sorcerer2FX2': (6, 10),
    'MinotaurFX1': (20, 3), 'MinotaurFX2': (14, 4),
}
# Remaster-only monsters / projectiles defined in EX_BASE (always loaded).
NEW_LUMPS = ['EX_EMUM2', 'EX_ETROL', 'EX_EDEMN']
ENHANCED_LUMPS = ['EX_EIMPX', 'EX_EMUMM', 'EX_EKNIG', 'EX_EWZRD', 'EX_ECLNK', 'EX_EBEAS',
                  'EX_ESNKE', 'EX_EHEAD', 'EX_EMNTR', 'EX_ESORC']

def melee(base, dice, sound):
    return ('A_MonsterMeleeAttack', [base, dice, sound])

# Vanilla attack chains: (sprite, frame, tics, action, args). 'next' of the last state is the
# monster's walk state; LOOP marks "Goto <index>" inside the chain.
FT = ('A_FaceTarget', None)
VANILLA = {
    'imp_melee': ('IMPX', 'S_HERETIC_IMP_FLY1', [
        ('D', 6, *FT), ('E', 6, *FT), ('F', 6, *melee(17, 3, 'impat1'))]),       # vanilla 5..12
    'imp_missile': ('IMPX', ('LOOP', 2), [
        ('A', 10, *FT), ('B', 6, 'A_ImpMsAttack', None), ('C', 6, None, None),
        ('B', 6, None, None), ('A', 6, None, None), ('B', 6, None, None)]),
    'impleader_missile': ('IMPX', 'S_HERETIC_IMP_FLY1', [
        ('D', 6, *FT), ('E', 6, *FT), ('F', 6, 'A_ImpMsAttack2', None)]),
    'mummy_melee': ('MUMM', 'S_HERETIC_MUMMY_WALK1', [
        ('E', 6, *FT), ('F', 6, *melee(12, 5, 'mumat2')), ('G', 6, None, None)]),  # vanilla 2..16
    'mummyleader_missile': ('MUMM', 'S_HERETIC_MUMMY_WALK1', [
        ('X', 5, *FT), ('Y!', 5, *FT), ('X', 5, *FT), ('Y!', 5, *FT), ('X', 5, *FT),
        ('Y!', 5, 'A_MummyAttack2', None)]),
    'knight_melee': ('KNIG', 'S_HERETIC_KNIGHT_WALK1', [
        ('E', 10, *FT), ('F', 8, *FT), ('G', 8, *melee(27, 3, 'kgtat2')),          # vanilla 3..24
        ('E', 10, *FT), ('F', 8, *FT), ('G', 8, *melee(27, 3, 'kgtat2'))]),
    'knight_missile': ('KNIG', 'S_HERETIC_KNIGHT_WALK1', [
        ('E', 10, *FT), ('F', 8, *FT), ('G', 8, 'A_KnightAttack', None),
        ('E', 10, *FT), ('F', 8, *FT), ('G', 8, 'A_KnightAttack', None)]),
    'wizard_missile': ('WZRD', 'S_HERETIC_WIZARD_WALK1', [
        ('C', 4, 'A_WizAtk1', None), ('C', 4, 'A_WizAtk2', None), ('C', 4, 'A_WizAtk1', None),
        ('C', 4, 'A_WizAtk2', None), ('C', 4, 'A_WizAtk1', None), ('C', 4, 'A_WizAtk2', None),
        ('C', 4, 'A_WizAtk1', None), ('C', 4, 'A_WizAtk2', None), ('D', 12, 'A_WizAtk3', None)]),
    'clink_melee': ('CLNK', 'S_HERETIC_CLINK_WALK1', [
        ('E', 5, *FT), ('F', 4, *FT), ('G', 7, *melee(8, 5, 'clkatk'))]),        # vanilla 3..9
    'beast_missile': ('BEAS', 'S_HERETIC_BEAST_WALK1', [
        ('H', 10, *FT), ('I', 10, 'A_BeastAttack', None)]),
    'snake_missile': ('SNKE', 'S_HERETIC_SNAKE_WALK1', [
        ('F', 5, *FT), ('F', 5, *FT), ('F', 4, 'A_SnakeAttack', None), ('F', 4, 'A_SnakeAttack', None),
        ('F', 4, 'A_SnakeAttack', None), ('F', 5, *FT), ('F', 5, *FT), ('F', 5, *FT),
        ('F', 4, 'A_SnakeAttack2', None)]),
    'lich_missile': ('LICH', 'S_HERETIC_HEAD_FLOAT', [
        ('A', 5, *FT), ('B', 20, 'A_HeadAttack', None)]),
    'srcr1_missile': ('SRCR', 'S_HERETIC_SRCR1_WALK1', [
        ('Q', 7, *FT), ('R', 6, *FT), ('S', 10, 'A_Srcr1Attack', None)]),
    'sor2_missile': ('SOR2', 'S_HERETIC_SOR2_WALK1', [
        ('R', 9, 'A_Srcr2Decide', None), ('S', 9, *FT), ('T', 20, 'A_Srcr2Attack', None)]),
    'mntr_melee': ('MNTR', 'S_HERETIC_MNTR_WALK1', [
        ('V', 10, *FT), ('W', 7, *FT), ('X', 12, *melee(24, 5, 'stfpow'))]),     # vanilla 4..32
    'mntr_missile': ('MNTR', 'S_HERETIC_MNTR_WALK1', [
        ('V', 10, 'A_MinotaurDecide', None), ('Y', 4, *FT), ('Z', 9, 'A_MinotaurAtk2', None)]),
}
VANILLA_ATTACKS = {   # actor -> {meleestate/missilestate: chain}
    'HereticImp': {'meleestate': 'imp_melee', 'missilestate': 'imp_missile'},
    'HereticImpLeader': {'missilestate': 'impleader_missile'},
    'Mummy': {'meleestate': 'mummy_melee'}, 'MummyGhost': {'meleestate': 'mummy_melee'},
    'MummyLeader': {'meleestate': 'mummy_melee', 'missilestate': 'mummyleader_missile'},
    'MummyLeaderGhost': {'meleestate': 'mummy_melee', 'missilestate': 'mummyleader_missile'},
    'Knight': {'meleestate': 'knight_melee', 'missilestate': 'knight_missile'},
    'KnightGhost': {'meleestate': 'knight_melee', 'missilestate': 'knight_missile'},
    'Wizard': {'missilestate': 'wizard_missile'},
    'Clink': {'meleestate': 'clink_melee'},
    'Beast': {'missilestate': 'beast_missile'},
    'Snake': {'missilestate': 'snake_missile'},
    'Ironlich': {'missilestate': 'lich_missile'},
    'Sorcerer1': {'missilestate': 'srcr1_missile'},
    'Sorcerer2': {'missilestate': 'sor2_missile'},
    'Minotaur': {'meleestate': 'mntr_melee', 'missilestate': 'mntr_missile'},
}

# Vanilla walk (See) loops and pain sequences: sprite, [(frame, tics, action)].
SEE = {
    'imp': ('IMPX', 'S_HERETIC_IMP_FLY1', [(f, 3, 'A_Chase') for f in 'AABBCCBB']),
    'mummy': ('MUMM', 'S_HERETIC_MUMMY_WALK1', [(f, 4, 'A_Chase') for f in 'ABCD']),
    'knight': ('KNIG', 'S_HERETIC_KNIGHT_WALK1', [(f, 4, 'A_Chase') for f in 'ABCD']),
    'wizard': ('WZRD', 'S_HERETIC_WIZARD_WALK1', [(f, t, 'A_Chase') for f, t in
                                                 zip('AAAABBBB', (3, 4, 3, 4, 3, 4, 3, 4))]),
    'clink': ('CLNK', 'S_HERETIC_CLINK_WALK1', [(f, 3, 'A_Chase') for f in 'ABCD']),
    'beast': ('BEAS', 'S_HERETIC_BEAST_WALK1', [(f, 3, 'A_Chase') for f in 'ABCDEF']),
    'snake': ('SNKE', 'S_HERETIC_SNAKE_WALK1', [(f, 4, 'A_Chase') for f in 'ABCD']),
    'lich': ('LICH', 'S_HERETIC_HEAD_FLOAT', [('A', 4, 'A_Chase')]),
    'srcr1': ('SRCR', 'S_HERETIC_SRCR1_WALK1', [(f, 5, 'A_Sor1Chase') for f in 'ABCD']),
    'sor2': ('SOR2', 'S_HERETIC_SOR2_WALK1', [(f, 4, 'A_Chase') for f in 'MNOP']),
    'mntr': ('MNTR', 'S_HERETIC_MNTR_WALK1', [(f, 5, 'A_MinotaurChase') for f in 'ABCD']),
}
PAIN = {
    'imp': [('G', 3, None), ('G', 3, 'A_Pain')], 'mummy': [('H', 4, None), ('H', 4, 'A_Pain')],
    'knight': [('H', 3, None), ('H', 3, 'A_Pain')], 'wizard': [('E', 3, 'A_GhostOff'), ('E', 3, 'A_Pain')],
    'clink': [('H', 3, None), ('H', 3, 'A_Pain')], 'beast': [('G', 3, None), ('G', 3, 'A_Pain')],
    'snake': [('E', 3, None), ('E', 3, 'A_Pain')], 'lich': [('A', 4, None), ('A', 4, 'A_Pain')],
    'srcr1': [('Q', 6, 'A_Sor1Pain')], 'sor2': [('Q', 3, None), ('Q', 6, 'A_Pain')],
    'mntr': [('E', 3, None), ('E', 6, 'A_Pain')],
}
GROUP = {
    'HereticImp': 'imp', 'HereticImpLeader': 'imp', 'Mummy': 'mummy', 'MummyLeader': 'mummy',
    'MummyGhost': 'mummy', 'MummyLeaderGhost': 'mummy', 'Knight': 'knight', 'KnightGhost': 'knight',
    'Wizard': 'wizard', 'Clink': 'clink', 'Beast': 'beast', 'Snake': 'snake', 'Ironlich': 'lich',
    'Sorcerer1': 'srcr1', 'Sorcerer2': 'sor2', 'Minotaur': 'mntr',
}

def spread(tics, div):
    """Divide a chain's tics by div, spreading the rounding so the chain total is right (min 1)."""
    out, acc = [], 0.0
    for t in tics:
        if t <= 0:
            out.append(t)
            continue
        acc += t / div
        n = max(1, int(round(acc)))
        acc -= n
        out.append(n)
    return out

def fast(t):
    return t if t <= 0 else max(1, math.ceil(t / TIC_DIV))

def proj_speed(s):
    return min(s * PROJ_SPEED_MULT, max(s, PROJ_SPEED_CAP))

def doc(comment, data):
    return {'type': 'exdefs', 'version': '1.0.0',
            'metadata': {'author': 'altanc', 'timestamp': '2026-11-24T00:00:00+00:00',
                         'application': 'N/A', 'comment': comment},
            'data': data}

def vanilla_chain_states(key):
    sprite, end, chain = VANILLA[key]
    p = 'RH_%s_' % key
    out = []
    new_tics = spread([c[1] for c in chain], TIC_DIV)
    for i, (frame, _, action, args) in enumerate(chain):
        tics = new_tics[i]
        last = i == len(chain) - 1
        if not last:
            nxt = '@next'
        elif isinstance(end, tuple):
            nxt = p + '%02d' % end[1]
        else:
            nxt = end
        s = {'name': p + '%02d' % i, 'next': nxt, 'sprite': sprite, 'frame': frame, 'tics': tics}
        if action:
            s['action'] = action
        if args:
            s['args'] = args
        out.append(s)
    return out, p + '00'

def simple_chain(prefix, sprite, chain, div, end):
    """end: state name for the last 'next', or None to loop back to the first state."""
    tics = spread([c[1] for c in chain], div)
    out = []
    for i, (frame, _, action) in enumerate(chain):
        last = i == len(chain) - 1
        s = {'name': prefix + '%02d' % i, 'next': (end or prefix + '00') if last else '@next',
             'sprite': sprite, 'frame': frame, 'tics': tics[i]}
        if action:
            s['action'] = action
        out.append(s)
    return out

def scale_args(action, args):
    """x4 the damage args of attack functions that take them."""
    if not args:
        return args
    args = list(args)
    if action == 'A_MonsterMeleeAttack' and isinstance(args[0], (int, float)):
        args[0] *= DAMAGE_MULT
    elif action == 'A_MonsterComboAttack' and len(args) > 1 and isinstance(args[1], (int, float)):
        args[1] *= DAMAGE_MULT
    elif action == 'A_ClinkAttackEX' and len(args) == 4 and all(isinstance(x, (int, float)) for x in args[2:]):
        args[2] *= DAMAGE_MULT   # min damage (Troll: 10..20)
        args[3] *= DAMAGE_MULT   # max damage
    return args

STOP_WORDS = ('See', 'Spawn', 'Pain', 'Death', 'Look', 'Walk', 'Raise')

def clone_chain(lump_states, start, prefix, stop=(), div=TIC_DIV, stopwords=None):
    """Clone an EXDEFS state chain (following @next, explicit next and A_RandomJump targets)."""
    order = [s['name'] for s in lump_states]
    by = {s['name']: s for s in lump_states}
    todo, seen = [start], []
    while todo:
        n = todo.pop()
        words = STOP_WORDS if stopwords is None else stopwords
        if n in seen or n not in by or n in stop or any(k in n for k in words):
            continue
        seen.append(n)
        s = by[n]
        nxt = s['next']
        if nxt == '@next':
            i = order.index(n)
            if i + 1 < len(order):
                todo.append(order[i + 1])
        elif not nxt.startswith('@'):
            todo.append(nxt)
        for a in s.get('args', []) or []:
            if isinstance(a, str) and a in by:
                todo.append(a)
    rename = {n: prefix + n for n in seen}
    out = []
    for n in order:
        if n not in rename:
            continue
        s = dict(by[n])
        i = order.index(n)
        if s['next'] == '@next':
            s['next'] = rename.get(order[i + 1], order[i + 1]) if i + 1 < len(order) else '@stop'
        else:
            s['next'] = rename.get(s['next'], s['next'])
        s['name'] = rename[n]
        s['tics'] = max(1, round(s['tics'] / div)) if s['tics'] > 0 else s['tics']
        if 'args' in s:
            s['args'] = [rename.get(a, a) if isinstance(a, str) else a
                         for a in scale_args(s.get('action'), s['args'])]
        out.append(s)
    return out, rename[start]

def lump_json(L, get, name):
    return json.loads(get(L, name))['data']

def build(L, get):
    """Returns {lumpname: exdefs dict} for the hyper-monster lumps."""
    # --- vanilla ---------------------------------------------------------------
    states, actors = [], []
    see_map = {}                                   # vanilla walk state -> fast walk clone
    for g, (sprite, walk, chain) in SEE.items():
        states += simple_chain('RH_see_%s_' % g, sprite, chain, SEE_DIV, None)
        see_map[walk] = 'RH_see_%s_00' % g
        states += simple_chain('RH_pain_%s_' % g, sprite, PAIN[g], SEE_DIV, see_map[walk])
    starts = {}
    for key in VANILLA:
        st, first = vanilla_chain_states(key)
        for x in st:
            x['next'] = see_map.get(x['next'], x['next'])
        states += st
        starts[key] = first
    for name in MONSTER_SPEED:
        g = GROUP[name]
        a = {'name': name, 'addflags': ['RANGEHALF'],
             'seestate': 'RH_see_%s_00' % g, 'painstate': 'RH_pain_%s_00' % g}
        for field, key in VANILLA_ATTACKS.get(name, {}).items():
            a[field] = starts[key]
        actors.append(a)
    for name, (spd, dmg) in PROJECTILES.items():
        actors.append({'name': name, 'speed': proj_speed(spd), 'damage': dmg * DAMAGE_MULT})
    out = {'RH_VAN': doc('Hyper monsters - vanilla', {'actors': actors, 'states': states})}

    # --- enhanced enemies (heretic_enemies option) and remaster-only monsters -----
    def from_lumps(lumps, tag):
        states, actors = [], []
        for lump in lumps:
            d = lump_json(L, get, lump)
            lstates = d.get('states', [])
            for a in d.get('actors', []):
                name = a['name']
                flags = a.get('flags', [])
                patch = {'name': name}
                if name in PROJECTILES or 'MISSILE' in flags or a.get('inherits') in PROJECTILES:
                    base_spd, base_dmg = PROJECTILES.get(name, PROJECTILES.get(a.get('inherits'), (None, None)))
                    spd = a.get('speed', base_spd)
                    dmg = a.get('damage', base_dmg)
                    if spd:
                        patch['speed'] = proj_speed(spd)
                    if dmg:
                        patch['damage'] = dmg * DAMAGE_MULT
                elif name in MONSTER_SPEED or 'COUNTKILL' in flags:
                    patch['addflags'] = ['RANGEHALF']
                    # remaster-only monsters: clone their own walk and pain sequences at 2x
                    for field, prefix in (('seestate', 'RH%sS_' % tag), ('painstate', 'RH%sP_' % tag)):
                        if field in a and a[field] in {x['name'] for x in lstates}:
                            stop = {a.get('seestate')} if field == 'painstate' else set()
                            st, first = clone_chain(lstates, a[field], prefix, stop=stop, div=SEE_DIV, stopwords=())
                            if field == 'seestate':
                                see_map[a[field]] = first
                            have = {x['name'] for x in states}
                            states += [x for x in st if x['name'] not in have]
                            patch[field] = first
                    if 'reactiontime' in a:
                        patch['reactiontime'] = fast(a['reactiontime'])
                    for field in ('meleestate', 'missilestate'):
                        if field in a:
                            st, first = clone_chain(lstates, a[field], 'RH%s_' % tag, stop={a.get('seestate')})
                            have = {s['name'] for s in states}
                            states += [s for s in st if s['name'] not in have]
                            patch[field] = first
                if len(patch) > 1:
                    actors.append(patch)
        # every cloned attack/pain sequence returns to the fast walk
        for x in states:
            if not x['name'].startswith(('RH%sS_' % tag,)):
                x['next'] = see_map.get(x['next'], x['next'])
        return actors, states
    a, s = from_lumps(ENHANCED_LUMPS, 'E')
    out['RH_ENH'] = doc('Hyper monsters - enhanced enemies', {'actors': a, 'states': s})
    a, s = from_lumps(NEW_LUMPS, 'N')
    out['RH_NEW'] = doc('Hyper monsters - remaster-only monsters', {'actors': a, 'states': s})
    out['RH_ROOT'] = doc('Hyper monsters', {'include': [
        {'comment': 'vanilla monsters', 'lumpname': 'RH_VAN'},
        {'comment': 'enhanced enemies overrides', 'lumpname': 'RH_ENH', 'ifoption': 'heretic_enemies'},
        {'comment': 'Draugr, Troll, Chaos Serpent', 'lumpname': 'RH_NEW'},
    ]})
    return out
