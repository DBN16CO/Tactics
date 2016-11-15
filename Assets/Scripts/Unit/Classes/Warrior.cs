using UnityEngine;

public class Warrior : Unit {

	public override void Awake() {
		base.Awake();
		GetStat("MoveRange").BaseValue = 1f;
		GetStat("AttackRange").BaseValue = 1f;
	}
}
