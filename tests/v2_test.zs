version "4.10"
class V2Test : EventHandler
{
	int bolts1, bolts2, wandShots;
	Inventory a1, a2, a3, a4, a6; Weapon a5;
	override void WorldThingSpawned(WorldEvent e)
	{
		if (!e.Thing) return;
		String n = e.Thing.GetClassName();
		if (n == "RedBoltFX1") bolts1++;
		else if (n == "RedBoltFX2") bolts2++;
		else if (n == "CrossbowFX1" || n == "CrossbowFX2" || n == "CrossbowFX3") Console.Printf("V2 UNEXPECTED %s", n);
	}
	int Amm(Actor p, Name t) { return p.CountInv(t); }
	int Max(Actor p, Name t) { let a = p.FindInventory(t); return a ? a.MaxAmount : -1; }
	override void WorldTick()
	{
		let p = players[0].mo;
		if (!p) return;
		int t = level.maptime;
		String rw = "none";
		if (players[0].ReadyWeapon) rw = players[0].ReadyWeapon.GetClassName();
		if (t == 10)
		{
			int s2, i2, s3, i3; bool f2, f3;
			[f2, s2, i2] = players[0].weapons.LocateWeapon("RedGoldWand");
			[f3, s3, i3] = players[0].weapons.LocateWeapon("RedCrossbow");
			Console.Printf("V2 start class=%s weapon=%s wandslot=%d bowslot=%d hasStockWand=%d", p.GetClassName(), rw, f2 ? s2 : -1, f3 ? s3 : -1, p.FindInventory("GoldWand", false) != null && p.FindInventory("GoldWand").GetClass() == "GoldWand");
		}
		if (t == 19 || t == 92) Console.Printf("V2 t=%d wandammo=%d", t, Amm(p, 'GoldWandAmmo'));
		if (t == 100) { let c = Inventory(Actor.Spawn("Crossbow", p.pos, ALLOW_REPLACE)); Console.Printf("V2 spawned %s", c ? c.GetClassName() : 'null'); if (c) c.CallTryPickup(p); }
		if (t == 155) Console.Printf("V2 t=%d weapon=%s bowammo=%d", t, rw, Amm(p, 'CrossbowAmmo'));
		if (t == 252) Console.Printf("V2 t=%d bolts1=%d bowammo=%d", t, bolts1, Amm(p, 'CrossbowAmmo'));
		if (t == 260) { p.GiveInventory("ArtiTomeOfPower", 1); p.UseInventory(p.FindInventory("ArtiTomeOfPower")); }
		if (t == 330) Console.Printf("V2 t=%d weapon=%s bolts2=%d bowammo=%d", t, rw, bolts2, Amm(p, 'CrossbowAmmo'));
		if (t == 340) { p.GiveInventory("GoldWandAmmo", 1000); p.GiveInventory("CrossbowAmmo", 1000); }
		if (t == 342) Console.Printf("V2 nobag wand=%d/%d bow=%d/%d", Amm(p,'GoldWandAmmo'), Max(p,'GoldWandAmmo'), Amm(p,'CrossbowAmmo'), Max(p,'CrossbowAmmo'));
		if (t == 344) p.GiveInventory("BagOfHolding", 1);
		if (t == 346) { p.GiveInventory("GoldWandAmmo", 1000); p.GiveInventory("CrossbowAmmo", 1000); }
		if (t == 348) Console.Printf("V2 bag wand=%d/%d bow=%d/%d", Amm(p,'GoldWandAmmo'), Max(p,'GoldWandAmmo'), Amm(p,'CrossbowAmmo'), Max(p,'CrossbowAmmo'));
		if (t == 360)
		{
			vector3 far = p.Vec3Angle(-2000, p.angle);
			a1 = Inventory(Actor.Spawn("GoldWandAmmo", far)); a2 = Inventory(Actor.Spawn("GoldWandHefty", far));
			a3 = Inventory(Actor.Spawn("CrossbowAmmo", far)); a4 = Inventory(Actor.Spawn("CrossbowHefty", far));
			a5 = Weapon(Actor.Spawn("Crossbow", far, ALLOW_REPLACE));
			a6 = Inventory(Actor.Spawn("CrossbowAmmo", far)); if (a6) a6.Amount = 3; // monster-drop style
		}
		if (t == 362) Console.Printf("V2 pickups wand=%d hefty=%d arrows=%d quiver=%d bowgive=%d drop3=%d", a1.Amount, a2.Amount, a3.Amount, a4.Amount, a5.AmmoGive1, a6.Amount);
		if (t == 350) { let d1 = GetDefaultByType("RedBoltFX1"); let d2 = GetDefaultByType("RedBoltFX2"); Console.Printf("V2 fx1 speed=%d dmg=%d  fx2 speed=%d dmg=%d", d1.Speed, d1.GetMissileDamage(0,1), d2.Speed, d2.GetMissileDamage(0,1)); }
	}
}
