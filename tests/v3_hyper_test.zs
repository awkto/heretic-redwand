version "4.10"
class V3W : EventHandler
{
	int fx; Actor wz;
	override void WorldThingSpawned(WorldEvent e) { if (e.Thing && e.Thing.GetClassName() == "WizardFX1") fx++; }
	override void WorldTick()
	{
		let p = players[0].mo; if (!p) return;
		int t = level.maptime;
		if (t == 10) { wz = Actor.Spawn("Wizard", p.Vec3Angle(300, p.angle)); wz.target = p; wz.angle = wz.AngleTo(p); wz.SetState(wz.SeeState); }
		if (t == 14 && wz) Console.Printf("V3W wizard speed=%d dmgmult=%.1f missilemore=%d", int(wz.Speed), wz.DamageMultiply, wz.bMissileMore);
		if (t == 10 + 350) Console.Printf("V3W bolts in 10s=%d volleys=%d", fx, fx / 3);
	}
}
