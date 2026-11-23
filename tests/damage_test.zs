version "4.10"
class RWDummy : Actor
{
	Default { Health 100000; Radius 24; Height 56; +SHOOTABLE; +SOLID; +NOBLOOD; +DONTTHRUST; +NOGRAVITY; }
	States { Spawn: IMPX A -1; Stop; }
}
class RWTest : EventHandler
{
	RWDummy dummy;
	int last;
	void Hit(Actor p, Name puff, int dmg, String label)
	{
		last = dummy.health;
		p.LineAttack(p.AngleTo(dummy), 2048, 0, dmg, 'Hitscan', puff);
		Console.Printf("RWTEST %s base=%d dealt=%d", label, dmg, last - dummy.health);
	}
	override void WorldTick()
	{
		let p = players[0].mo;
		if (!p) return;
		int t = level.maptime;
		if (t == 20)
		{
			dummy = RWDummy(Actor.Spawn("RWDummy", p.Vec3Angle(96, p.angle)));
			Console.Printf("RWTEST mult=%d hasboost=%d dummy=%d", CVar.FindCVar("redwand_mult") ? CVar.FindCVar("redwand_mult").GetInt() : -1, p.FindInventory((class<Inventory>)("RedWandBoost")) != null, dummy != null);
		}
		if (!dummy) return;
		if (t == 21) Hit(p, "GoldWandPuff1", 10, "wand-unpowered");
		if (t == 22) Hit(p, "GoldWandPuff2", 10, "wand-powered");
		if (t == 23) Hit(p, "StaffPuff", 10, "staff(control)");
		if (t == 24) { last = dummy.health; let m = p.SpawnMissileAngle("GoldWandFX2", p.AngleTo(dummy), 0); if (m) m.target = p; }
		if (t == 50) Console.Printf("RWTEST fx2-missile dealt=%d (vanilla range 1..8)", last - dummy.health);
	}
}
