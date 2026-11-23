version "4.10"
class RWFire : EventHandler
{
	override void WorldTick()
	{
		let p = players[0].mo;
		if (!p) return;
		int t = level.maptime;
		if (t == 5) { let m = Actor.Spawn("HereticImp", p.Vec3Angle(160, p.angle)); if (m) { m.bDormant = true; m.angle = m.AngleTo(p); } }
		if (t == 60) p.GiveInventory("ArtiTomeOfPower", 1);
		if (t == 61) p.UseInventory(p.FindInventory("ArtiTomeOfPower"));

		if (t == 100) Console.Printf("RWFIRE ammo=%d weapon=%s", p.CountInv("GoldWandAmmo"), players[0].ReadyWeapon ? players[0].ReadyWeapon.GetClassName() : 'none');
	}
}
