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
		Player.WeaponSlot 4, "Blaster";
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
		if (item && !item.Owner && (item is "GoldWandAmmo" || item is "CrossbowAmmo" || item is "Crossbow"))
			fresh.Push(item);
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

		for (int i = 0; i < MAXPLAYERS; i++)
		{
			if (!playeringame[i] || !players[i].mo) continue;
			DoubleAmmo(players[i].mo, "GoldWandAmmo");
			DoubleAmmo(players[i].mo, "CrossbowAmmo");
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

	override void ModifyDamage(int damage, Name damageType, out int newdamage, bool passive, Actor inflictor, Actor source, int flags)
	{
		if (passive || damage <= 0 || !IsWandDamage(inflictor)) return;
		int mult = clamp(redwand_mult, 1, 64);
		newdamage = damage * mult;
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
