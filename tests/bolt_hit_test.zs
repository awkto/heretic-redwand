version "4.10"
class HitDummy : Actor
{
	Default { Health 1000000; Radius 16; Height 36; +SHOOTABLE; +SOLID; +NOBLOOD; +DONTTHRUST; +NOGRAVITY; }
	States { Spawn: IMPX A -1; Stop; }
}
class HitTest : EventHandler
{
	HitDummy d; int fired, hits, lastHp; Array<Actor> bolts;
	override void WorldTick()
	{
		let p = players[0].mo; if (!p) return;
		int t = level.maptime;
		if (t == 5) { d = HitDummy(Actor.Spawn("HitDummy", p.Vec3Angle(300, p.angle, 20))); lastHp = d.health; }
		if (!d) return;
		// fire one bolt every 6 tics, sweeping the aim across the dummy's width
		if (t >= 10 && t < 10 + 6*40 && (t - 10) % 6 == 0)
		{
			int k = (t - 10) / 6;
			String cls = (k % 2) ? "RedBoltFX2" : "RedBoltFX1";
			double off = (k % 20 - 9.5) * 1.4; // -13.3 .. +13.3 units sideways at 300
			double ang = p.AngleTo(d) + atan(off / 300.);
			let m = p.SpawnMissileAngleZ(p.pos.z + 32, cls, ang, 0);
			if (m) { m.target = p; fired++; }
		}
		if (d.health != lastHp) { hits++; lastHp = d.health; }
		if (t == 10 + 6*40 + 40) Console.Printf("HIT fired=%d hits=%d", fired, hits);
	}
}
