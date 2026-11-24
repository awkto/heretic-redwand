version "4.10"
class RWDummy3 : Actor
{
	Default { Health 1000000; Radius 20; Height 56; +SHOOTABLE; +SOLID; +NOBLOOD; +DONTTHRUST; +NOGRAVITY; }
	States { Spawn: IMPX A -1; Stop; }
}
class V3Test : EventHandler
{
	int axes, axeSpeedSeen; Knight kn; RWDummy3 dum;
	Array<Actor> newMissiles;
	override void WorldThingSpawned(WorldEvent e)
	{
		if (e.Thing && e.Thing.GetClassName() == "KnightAxe") { axes++; newMissiles.Push(e.Thing); }
		if (e.Thing && e.Thing.GetClassName() == "RedAxe") { axes++; newMissiles.Push(e.Thing); }
	}
	override void WorldTick()
	{
		let p = players[0].mo; if (!p) return;
		int t = level.maptime;
		for (int i = 0; i < newMissiles.Size(); i++) if (newMissiles[i] && axeSpeedSeen == 0 && level.maptime > 0) { axeSpeedSeen = int(newMissiles[i].Vel.Length()); }
		if (t == 3) { let b = Inventory(Actor.Spawn("Blaster", p.pos, ALLOW_REPLACE)); if (b) { Console.Printf("V3 claw class=%s", b.GetClassName()); b.CallTryPickup(p); } }
		if (t >= 30 && t <= 130 && t % 4 == 0) Console.Printf("V3 t=%d orbs=%d weapon=%s", t, p.CountInv("BlasterAmmo"), players[0].ReadyWeapon ? players[0].ReadyWeapon.GetClassName() : 'none');
		if (t == 140)
		{
			dum = RWDummy3(Actor.Spawn("RWDummy3", p.Vec3Angle(200, p.angle)));
			int h = dum.health; p.LineAttack(p.AngleTo(dum), 2048, 0, 10, 'Hitscan', "BlasterPuff");
			Console.Printf("V3 clawpuff base=10 dealt=%d", h - dum.health);
			dum.Destroy();
		}
		if (t == 150)
		{
			kn = Knight(Actor.Spawn("Knight", p.Vec3Angle(384, p.angle)));
			if (kn) { kn.target = p; kn.angle = kn.AngleTo(p); kn.SetState(kn.SeeState); }
			Console.Printf("V3 cvar=%d", CVar.FindCVar("redwand_hyper") ? CVar.FindCVar("redwand_hyper").GetInt() : -9); Console.Printf("V3 knight speed=%d dmgmult=%.1f missilemore=%d", kn ? int(kn.Speed) : -1, kn ? kn.DamageMultiply : -1., kn ? kn.bMissileMore : 0);
		}
		if (t == 150 + 350) Console.Printf("V3 axes thrown in 10s=%d first axe speed=%d", axes, axeSpeedSeen);
	}
}
