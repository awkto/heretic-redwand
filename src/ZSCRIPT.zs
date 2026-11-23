version "4.10"

// Red Elven Wand - GZDoom / UZDoom side.
//
// The stock GoldWand code is left alone. Instead every player carries a hidden
// item whose ModifyDamage() multiplies any damage dealt through the wand's
// puffs and projectiles. That keeps the vanilla feel (first-shot accuracy,
// fan pattern when powered, Tome of Power swap) and stays compatible with
// other mods that touch the player class.
//
// Multiplier: CVar redwand_mult (default 4). Options menu -> "Red Elven Wand".

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
