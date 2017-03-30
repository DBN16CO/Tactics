using System.Collections.Generic;
using System;

public class MatchData {

	public int maxFunds;


	// QGU properties
	public string name;
	public int round;
	public bool yourTurn;
	public string map;
	public bool finished;

	public List<MatchUnit> units;
	public MatchLeader leader;
	public List<MatchPerk> perks;


	public MatchData(Dictionary<string, object> matchData) {
		//Dictionary<string, object> matchData = (Dictionary<string, object>)match.Value;
		name = matchData["Name"].ToString();
		round = int.Parse(matchData["Round"].ToString());
		yourTurn = (bool)matchData["Your_Turn"];
		map = matchData["Map"].ToString();
		finished = (bool)matchData["Finished"];

		units = new List<MatchUnit>();
		leader = new MatchLeader();
		perks = new List<MatchPerk>();
	}

}

public struct MatchUnit {
	private int ID;
	public string name;
	private int HP;
	private int prevHP;
	private int X;
	private int Y;
}
public struct MatchLeader {
	public string name;
	private string ability;
}
public struct MatchPerk {
	private string perk;
	private int tier;
}
