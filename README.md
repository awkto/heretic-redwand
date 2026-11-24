# Red Elven Wand

A Heretic mod that turns the Elven Wand, the Ethereal Crossbow and the Dragon Claw red and makes them hit harder. It also makes the monsters much faster and deadlier.
One file, `dist/redwand.wad`, works in both engines. Each engine ignores the other's lumps.

- **Red Elven Wand:** does **4x** (default) or **8x** damage, and fires about 1.5x as fast as vanilla. Its crystal, shots, puffs and ammo are **red** instead of gold.
- **Red bow:** fires **one** heavy bolt (vanilla fires one plus two small ones), or three heavy bolts when powered. Bolts fly about 1.3x as fast and hit far harder, and the bow fires about 2.5x as fast. The bow, bolts and quiver are **red** instead of green.
- **Red Dragon Claw:** fires in **bursts of 9** shots within about a second, then cools off for a second. Each shot does **2x** damage. Its blue magic is **red**.
- **Hyper monsters** (on by default, can be switched off): monsters move **2x** as fast, attack about **3x** as often, their projectiles fly **3x** as fast, and their attacks do **4x** damage.
- **Double ammo** for wand crystals, arrows and claw orbs: double the max (and the Bag of Holding max), and every pickup gives twice as much.

| Engine | How the damage works | 4x / 8x switch |
|---|---|---|
| **Heretic + Hexen (2025 KEX remaster)** | `EXDEFS` re-points the GoldWand fire states at `A_WeaponBulletAttack` / `A_WeaponProjectile` with explicit damage | Options menu → *Red Elven Wand: 8x damage* (off = 4x) |
| **GZDoom / UZDoom** | Stock wand code is kept. A hidden inventory item multiplies all damage dealt through the wand's puffs and missiles (`ModifyDamage`) | Options menu → *Red Elven Wand damage* (1/2/4/8/16x), or console `redwand_mult 8` |

## Download

Grab `redwand.wad` from the [latest release](https://github.com/awkto/heretic-redwand/releases/latest), or build it yourself (below).

## Install

- **Remaster (GOG/Steam):** make a shortcut to `heretic_gog.exe` with `-iwad heretic.wad -file "C:\path\to\redwand.wad"` after the target, or put those arguments in the store's launch options.
  - Steam: *Properties → Launch options*.
- **GZDoom/UZDoom:** `gzdoom -iwad HERETIC.WAD -file redwand.wad`, or drag the WAD onto the exe.

## Damage numbers

| | Vanilla | 4x | 8x |
|---|---|---|---|
| Unpowered shot | 7–14 (avg 10.5) | avg 42 | avg 84 |
| Tome of Power: 5 hitscans each | 1–8 | 4–32 | 8–64 |
| Tome of Power: 2 seeker balls | 1×(1–8) | 4×(1–8) | 8×(1–8) |

- **GZDoom:** every number is exactly vanilla × N.
- **Remaster:** unpowered shots are `21×(1–3)` at 4x and `42×(1–3)` at 8x. The averages match exactly, but the spread is a little wider than vanilla. The engine's bullet function only does `base × random(1..dice)`.
- **Remaster accuracy:** the unpowered shot always has a small ±2.8° spread, where vanilla's first shot is perfectly accurate. The powered shot is a random ±5.6° spread rather than vanilla's fixed fan.

## Fire rates

| | Vanilla | Red mod |
|---|---|---|
| Wand cycle | 11 tics (powered 9) | 7 tics (powered 7) |
| Bow cycle | 31 tics (powered 25) | 12 tics (powered 10) |
| Dragon Claw | a shot every 6 tics while held | 9 shots, one every 4 tics, then a 35-tic (1 s) cool-off |

## Red Dragon Claw

- **Damage:** each shot does `8 × random(1..8)` (avg 36), twice vanilla's `4 × random(1..8)`.
- **Bursts:** one press fires the whole burst of 9. During the 1-second cool-off you can't fire or switch weapons. Holding fire starts the next burst right after the cool-off.
- **Powered (Tome of Power):** uses the game's own powered shot. The claw ball and its rippers do 2x damage.
- **Remaster quirk:** a burst started with fewer than 9 orbs still fires all 9 shots. The engine has no "out of ammo" check mid-sequence, and ammo stops at 0. In GZDoom the burst just stops firing when you run dry.
- **Red parts:** the claw's sparks, shots, puffs, orbs and ammo icon. The ripper death sparks (`FX18 O–S`) stay blue, because the remaster's Tempest Wand uses those frames too.

## Hyper monsters

| | Vanilla | Hyper |
|---|---|---|
| Movement | 1x | 2x: walk animation at double speed |
| Attack rate | 1x | about 3x: attack animations at 1/3 the time, double the chances to attack, and the "shoot more often" flag |
| Projectile speed | 1x | 3x, capped at 60 (faster missiles can pass straight through the player) |
| Damage | 1x | 4x |

- **Toggle:** remaster Options → *Red mod: hyper monsters*. GZDoom Options → *Red mod: hyper monsters*, or the console command `redwand_hyper 0`.
- **Measured in GZDoom:** a Disciple fired 9 volleys on average in 10 seconds, against 3.5 vanilla (4 runs each).
- **Remaster (KEX):**
  - Monsters get faster copies of their walk, pain and attack sequences. With *Enhanced Enemies* on, the game's enhanced attacks are copied and sped up instead.
  - Pure melee attacks become `A_MonsterMeleeAttack` at 4x vanilla damage. Enhanced attacks that take damage arguments get those x4.
  - A few attacks have damage fixed in the engine, so their melee hits stay at normal damage: the Undead Warrior's close swing in its throwing attack, the enhanced Sabreclaw and Maulotaur melee, and the Weredragon / Iron Lich / D'Sparil / leader close-range hits. All their projectiles are 4x.
  - Remaster-only monsters (Draugr, Troll, Chaos Serpent) are included.
- **GZDoom:** done in script for any monster. `DamageMultiply` 4x covers every attack.


## Red bow numbers

| | Vanilla | Red bow |
|---|---|---|
| Shot | 1 bolt (speed 30, dmg 10) + 2 small (speed 20, dmg 2) | 1 bolt (speed 40, dmg 50) |
| Powered shot | 3 bolts (speed 32, dmg 6) + 2 small | 3 bolts (speed 42, dmg 40) |

Projectile damage in Heretic is `damage × random(1..8)`. A red-bow shot averages 225 (powered 540 if all three hit), against vanilla's 63 for all three bolts.

In the remaster the bow fires through the game's own `A_FireCrossbowPL1` / `PL2`, so aiming matches the original. The two small side bolts are disabled (no damage, no sound, gone after one tic). An earlier build used the generic `A_WeaponProjectile`, and autoaim sent the bolt off target.

## Ammo

| | Vanilla max (with bag) | Red mod max (with bag) | Vanilla pickups | Red mod pickups |
|---|---|---|---|---|
| Wand crystals | 100 (200) | 200 (400) | 10 / 50 geode | 20 / 100 geode |
| Arrows | 50 (100) | 100 (200) | 5 / 20 quiver, crossbow 10 | 10 / 40 quiver, crossbow 20 |
| Arrows, remaster with *Enhanced Weapons* on | 30 (60) | 60 (120) | 3 / 15, crossbow 6 | 6 / 30, crossbow 12 |
| Claw orbs | 200 (400) | 400 (800) | 10 / 25 (30 enhanced), claw 30 | 20 / 50 (60 enhanced), claw 60 |

The Bag of Holding's ammo bonus is doubled too. In GZDoom, pickups are doubled when they spawn, so monster drops are doubled as well.

## Build

```
python3 tools/build.py /path/to/HERETIC.WAD     # -> dist/redwand.wad
```

`build.py` copies the sprites from your IWAD and palette-remaps them to red:
- **Wand** (`GWND`, `FX01`, `PUF2`, `AMG1/2`, `INAMGLD`): the gold and orange ramps. The first-person wand's wooden handle is left alone.
- **Bow** (`CRBW`, `WBOW`, `FX03`, `FX14`, `AMC1/2`, `INAMBOW`): the green and orange ramps.
- **Claw** (`BLSR`, `FX17`, `FX18 A–N`, `AMB1/2`, `INAMBST`): the blue ramp.

The hyper-monster EXDEFS lumps (`RH_*`) come from `tools/hyper.py`. It holds a table of vanilla walk, pain and attack sequences, and copies the remaster's enhanced and new monster sequences out of your IWAD at build time.

The remaster's EXDEFS lumps (`RW_4X`, `RW_8X`, `RB_BOW`, `RC_CLAW`, `RW_AMMO`, `RW_AMMOX`) are generated by `build.py`. The rest is hand-written in `src/`.

In GZDoom the wand, bow and claw are subclasses (`RedGoldWand`, `RedCrossbow`, `RedBlaster`) that replace the originals. A small player class (`RedHereticPlayer`) starts you with the red wand and puts the new weapons in the usual slots. Because of that, mods that bring their own player class won't combine with this one.

## Testing

- **GZDoom 4.14.2 (tested headless):**
  - `tests/damage_test.zs` produced wand hits ×4 / ×8, powered hits ×4 / ×8, FX2 missile ×N, and staff unchanged.
  - `tests/fire_test.zs` plus screenshots (`docs/gzdoom-ingame.png`) cover real firing, ammo use and the Tome of Power.
  - `tests/v2_test.zs` covers the v2 changes. A crossbow pickup becomes the red bow in slot 3. Holding fire gave 9 single bolts in 88 tics; powered fire gives 3 bolts per shot. The wand fired 10 shots in 72 tics. Ammo pickups, a crossbow pickup's arrows and monster-style drops came out doubled. In a hit test at an earlier, faster bolt speed (60), 40 of 40 bolts hit a gargoyle-sized target at 300 units. No stock bolts spawned. Ammo maxes doubled with and without the bag. Screenshot: `docs/gzdoom-redbow.png`.
  - `tests/v3_claw_test.zs`: one tap fires the full burst of 9, one shot every 4 tics, then stops. Claw hits do 2x damage.
  - `tests/v3_hyper_test.zs`: Disciple volleys in 10 seconds, hyper on vs off.
- **Remaster: v1, v2 and v3 playtested on Windows (GOG build).** The wand, red bow (aim, speed, damage), red claw bursts, hyper monsters and doubled ammo all work as intended. The EXDEFS was built from what the game itself contains:
  - the IWAD's own `EX_WEAP*` lumps;
  - the argument table that `heretic_gog.exe` registers for `A_WeaponBulletAttack`: `hspread, vspread, numbullets, damagebase, damagedice, puff`.
- **Remaster caveat:** the mod's `EXDEFS` loads *on top of* the base game's, which needs a game build from Update 2 or later. On an older build it could switch off the remaster's new enemies and the Tempest Wand.

## License

The code (`src/`, `tools/`, `tests/`) is MIT. The sprites in the released WAD are recoloured from Heretic (© id Software / Raven Software). You need your own copy of Heretic to play.
