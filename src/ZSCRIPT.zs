version "4.10"

// Red Elven Wand + Red Bow - GZDoom / UZDoom side.
//
// Wand damage: every player carries a hidden item whose ModifyDamage()
// multiplies damage dealt through the wand's puffs and projectiles
// (CVar redwand_mult, default 4).
// v2: the wand and bow are replaced by faster subclasses, handed out by a
// small player class (RedHereticPlayer) so start items and weapon slots stay
// right; max ammo for wand crystals and arrows is doubled.

// ---------------------------------------------------------------------------
// Player

class RedHereticPlayer : HereticPlayer
{
	Default
	{
		// The first StartItem in a subclass clears the inherited list.
		Player.StartItem "RedGoldWand";
		Player.StartItem "Staff";
		Player.StartItem "GoldWandAmmo", 50;
		Player.WeaponSlot 1, "Staff", "Gauntlets";
		Player.WeaponSlot 2, "RedGoldWand";
		Player.WeaponSlot 3, "RedCrossbow";
		Player.WeaponSlot 4, "RedBlaster";
		Player.WeaponSlot 5, "SkullRod";
		Player.WeaponSlot 6, "PhoenixRod";
		Player.WeaponSlot 7, "Mace";
	}
}

class RedWandHandler : EventHandler
{
	override void PlayerEntered(PlayerEvent e)   { GiveBoost(e.PlayerNumber); }
	override void PlayerRespawned(PlayerEvent e) { GiveBoost(e.PlayerNumber); }

	static void GiveBoost(int pnum)
	{
		if (pnum < 0 || pnum >= MAXPLAYERS || !playeringame[pnum]) return;
		let mo = players[pnum].mo;
		if (mo && !mo.FindInventory("RedWandBoost")) mo.GiveInventory("RedWandBoost", 1);
	}

	// Pickups are doubled one tic after they spawn, so amounts set by the
	// spawner (monster drops) are doubled too.
	Array<Inventory> fresh;

	override void WorldThingSpawned(WorldEvent e)
	{
		let item = Inventory(e.Thing);
		if (item && !item.Owner && (item is "GoldWandAmmo" || item is "CrossbowAmmo" || item is "Crossbow"
			|| item is "BlasterAmmo" || item is "Blaster"))
			fresh.Push(item);

		if (redwand_hyper && e.Thing)
		{
			if (e.Thing.bIsMonster && !e.Thing.player) MakeHyper(e.Thing);
			else if (e.Thing.bMissile) freshMissiles.Push(e.Thing);
		}
	}

	// --- Hyper monsters -----------------------------------------------------------
	// Walk and pain sequences run at 1.6x (more A_Chase calls: 1.6x movement and
	// chances to attack), attack sequences at 3x, plus MISSILEMORE /
	// MISSILEEVENMORE so they decide to shoot more often. 4x damage (DamageMultiply
	// covers melee and their projectiles). Projectiles 2.4x faster (capped at 60, same
	// as the remaster).
	Array<Actor> hyper;
	Array<State> hyperLast;
	Array<double> hyperCarry;
	Array<Actor> freshMissiles;

	void MakeHyper(Actor mo)
	{
		mo.bMissileMore = true;
		mo.bMissileEvenMore = true;
		mo.DamageMultiply *= 4;
		hyper.Push(mo);
		hyperLast.Push(null);
		hyperCarry.Push(0);
	}

	static void SpeedUpMissile(Actor m)
	{
		if (!m || !m.target || !m.target.bIsMonster || m.target.player || m.Speed <= 0) return;
		double ns = min(m.Speed * 2.4, max(m.Speed, 60.));
		double f = ns / m.Speed;
		m.Speed = ns;
		m.Vel *= f;
	}

	void TickHyper()
	{
		for (int i = 0; i < freshMissiles.Size(); i++) SpeedUpMissile(freshMissiles[i]);
		freshMissiles.Clear();

		for (int i = hyper.Size() - 1; i >= 0; i--)
		{
			let mo = hyper[i];
			if (!mo || mo.health <= 0)
			{
				hyper.Delete(i);
				hyperLast.Delete(i);
				hyperCarry.Delete(i);
				continue;
			}
			let cur = mo.CurState;
			if (cur == hyperLast[i]) continue;
			hyperLast[i] = cur;
			if (mo.tics <= 0) continue;
			double div = 1;
			if ((mo.MissileState && mo.InStateSequence(cur, mo.MissileState))
				|| (mo.MeleeState && mo.InStateSequence(cur, mo.MeleeState)))
				div = 3;
			else if ((mo.SeeState && mo.InStateSequence(cur, mo.SeeState))
				|| mo.InStateSequence(cur, mo.FindState("Pain")))
				div = 1.6;
			if (div == 1) continue;
			// carry the rounding so a chain of 3-tic frames averages 1.5, not 2
			double want = mo.tics / div + hyperCarry[i];
			int n = max(1, int(want + 0.5));
			hyperCarry[i] = want - n;
			mo.tics = n;
		}
	}

	static void DoublePickup(Inventory item)
	{
		if (!item || item.Owner) return;
		let w = Weapon(item);
		if (w) w.AmmoGive1 *= 2;
		else item.Amount *= 2;
	}

	override void WorldTick()
	{
		for (int i = 0; i < fresh.Size(); i++) DoublePickup(fresh[i]);
		fresh.Clear();
		TickHyper();

		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo) continue;
			DoubleAmmo(players[i].mo, "GoldWandAmmo");
			DoubleAmmo(players[i].mo, "CrossbowAmmo");
			DoubleAmmo(players[i].mo, "BlasterAmmo");
		}
	}

	// Doubles the per-player limits on the ammo item itself, so pickups and
	// the Bag of Holding (which raises MaxAmount to BackpackMaxAmount) just work.
	static void DoubleAmmo(Actor mo, class<Ammo> type)
	{
		let a = Ammo(mo.FindInventory(type));
		if (!a) return;
		let def = GetDefaultByType(type);
		int bagMax = def.BackpackMaxAmount * 2;
		if (a.BackpackMaxAmount < bagMax) a.BackpackMaxAmount = bagMax;
		if (a.BackpackAmount < def.BackpackAmount * 2) a.BackpackAmount = def.BackpackAmount * 2;
		bool hasBag = mo.FindInventory("BackpackItem", true) != null;
		int target = hasBag ? bagMax : def.MaxAmount * 2;
		if (a.MaxAmount < target) a.MaxAmount = target;
	}
}

class RedWandBoost : Inventory
{
	Default
	{
		Inventory.MaxAmount 1;
		+INVENTORY.UNDROPPABLE
		+INVENTORY.UNTOSSABLE
		+INVENTORY.UNCLEARABLE
	}

	static bool IsWandDamage(Actor inflictor)
	{
		// GoldWandPuff2 and GoldWandFX2 both inherit from GoldWandFX1.
		return inflictor && (inflictor is "GoldWandPuff1" || inflictor is "GoldWandFX1");
	}

	static bool IsClawDamage(Actor inflictor)
	{
		return inflictor && (inflictor is "BlasterPuff" || inflictor is "BlasterFX1" || inflictor is "Ripper");
	}

	override void ModifyDamage(int damage, Name damageType, out int newdamage, bool passive, Actor inflictor, Actor source, int flags)
	{
		if (passive || damage <= 0) return;
		if (IsWandDamage(inflictor)) newdamage = damage * clamp(redwand_mult, 1, 64);
		else if (IsClawDamage(inflictor)) newdamage = damage * 2;
	}
}

// ---------------------------------------------------------------------------
// Wand: same shots, faster cycle (7 tics, vanilla 11; powered 7, vanilla 9)

class RedGoldWand : GoldWand replaces GoldWand
{
	Default
	{
		Weapon.SisterWeapon "RedGoldWandPowered";
	}
	States
	{
	Fire:
		GWND B 2;
		GWND C 3 A_FireGoldWandPL1;
		GWND D 2;
		GWND D 0 A_ReFire;
		Goto Ready;
	}
}

class RedGoldWandPowered : GoldWandPowered
{
	Default
	{
		Weapon.SisterWeapon "RedGoldWand";
	}
	States
	{
	Fire:
		GWND B 2;
		GWND C 3 A_FireGoldWandPL2;
		GWND D 2;
		GWND D 0 A_ReFire;
		Goto Ready;
	}
}

// ---------------------------------------------------------------------------
// Red bow: one heavy bolt (vanilla: 1 + 2 small), powered three heavy bolts
// (vanilla: 3 + 2 small). Cycle 12 tics (vanilla 31), powered 10 (vanilla 25).

class RedCrossbow : Crossbow replaces Crossbow
{
	Default
	{
		Weapon.SisterWeapon "RedCrossbowPowered";
	}
	States
	{
	Fire:
		CRBW D 3 A_FireRedBow;
		CRBW E 2;
		CRBW FGHAB 1;
		CRBW C 2 A_ReFire;
		Goto Ready;
	}

	action void A_FireRedBow()
	{
		if (player == null) return;
		Weapon weapon = player.ReadyWeapon;
		if (weapon != null && !weapon.DepleteAmmo(weapon.bAltFire)) return;
		SpawnPlayerMissile("RedBoltFX1");
	}
}

class RedCrossbowPowered : CrossbowPowered
{
	Default
	{
		Weapon.SisterWeapon "RedCrossbow";
	}
	States
	{
	Fire:
		CRBW D 3 A_FireRedBowPL2;
		CRBW EFGHABC 1;
		CRBW C 0 A_ReFire;
		Goto Ready;
	}

	action void A_FireRedBowPL2()
	{
		if (player == null) return;
		Weapon weapon = player.ReadyWeapon;
		if (weapon != null && !weapon.DepleteAmmo(weapon.bAltFire)) return;
		SpawnPlayerMissile("RedBoltFX2");
		SpawnPlayerMissile("RedBoltFX2", angle - 4.5);
		SpawnPlayerMissile("RedBoltFX2", angle + 4.5);
	}
}

class RedBoltFX1 : CrossbowFX1
{
	Default
	{
		Speed 40;
		Damage 50;
	}
}

class RedBoltFX2 : CrossbowFX2
{
	Default
	{
		Speed 42;
		Damage 40;
	}
}

// ---------------------------------------------------------------------------
// Red Dragon Claw: bursts of 9 shots in ~1 second (one every 4 tics), then a
// 1 second cool-off. 2x damage (RedWandBoost.ModifyDamage). Powered fire is the
// stock BlasterPowered one, also 2x.

class RedBlaster : Blaster replaces Blaster
{
	Default
	{
		Weapon.SisterWeapon "RedBlasterPowered";
	}
	States
	{
	Fire:
	Hold:
		BLSR BC 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR D 2 Bright A_FireBlasterPL1;
		BLSR C 2 Bright;
		BLSR B 3 Bright;
		BLSR A 32;
		BLSR A 0 A_ReFire;
		Goto Ready;
	}
}

class RedBlasterPowered : BlasterPowered
{
	Default
	{
		Weapon.SisterWeapon "RedBlaster";
	}
}
