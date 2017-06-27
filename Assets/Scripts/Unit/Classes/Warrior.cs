using UnityEngine;

public class Warrior : Unit {

	public override void Awake() {
		base.Awake();
		GetStat("MoveRange").BaseValue = 3;
		GetStat("AttackRange").BaseValue = 1;
		name = "Swordsman";
	}
}
