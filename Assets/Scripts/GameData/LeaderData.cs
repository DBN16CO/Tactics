using System.Collections.Generic;		// For dictionaries

// Holds game data for each leader
public class LeaderData {

	public string name;
	public string description;
	public string spritePath;

	private List<StatData> stats;
	private List<AbilityData> abilities;

	public LeaderData(KeyValuePair<string, object> leader) {
		Dictionary<string, object> leaderData = (Dictionary<string, object>)leader.Value;
		name = leader.Key;
		description = leaderData["Description"].ToString();
		spritePath = "Sprites/Units/axeman"; // Testing

		/*stats = new List<StatData>();
		foreach(KeyValuePair<string, object> stat in (Dictionary<string, object>)leaderData["Stats"]) {
			stats.Add(new StatData(stat, true));
		}*/

		abilities = new List<AbilityData>();
		foreach(string ability in Json.ToList(leaderData["Abilities"].ToString())) {
			abilities.Add(new AbilityData(ability));
		}
	}

	public StatData GetStat(string nameKey) {
		return stats.Find(x => x.name == nameKey);
	}

	public List<AbilityData> Abilities {
		get{return abilities;}
		set{abilities = value;}
	}

}
