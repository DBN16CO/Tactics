using System.Collections.Generic;

public class MatchData {

	// QGU properties
	public int               			ID;
	public string            			Name;
	public string            			Opponent;
	public int               			Round;
	public bool              			UserTurn;
	public string            			MapName;
	public bool             		 	InGameQueue;
	public bool              			Finished;
	public int               			UserTeam;
	public int               			EnemyTeam;
	public Dictionary<int, MatchUnit> 	AlliedUnits;
	public MatchLeader       			AlliedLeader;
	public List<MatchPerk>   			AlliedPerks;
	public Dictionary<int, MatchUnit>   EnemyUnits;
	public MatchLeader       			EnemyLeader;
	public List<MatchPerk>   			EnemyPerks;
	public List<MatchAction> 			GameActions;

	// Default constructor
	// Parses all fields necessary to describe the game to the front end
	public MatchData(Dictionary<string, object> matchData) {
		// General match information
		ID          = int.Parse(matchData["ID"].ToString());
		Name        = matchData["Name"].ToString();
		Opponent    = matchData["Opponent"].ToString();
    	Round       = int.Parse(matchData["Round"].ToString());
        UserTurn    = (bool)matchData["Your_Turn"];
        MapName     = matchData["Map"].ToString();
        Finished    = (bool)matchData["Finished"];
		//InGameQueue = (bool)matchData["In_Game_Queue"];
		UserTeam    = int.Parse(matchData["Your_Team"].ToString());
		EnemyTeam   = int.Parse(matchData["Enemy_Team"].ToString());

		// Get all the allied units
		AlliedUnits = new Dictionary<int, MatchUnit>();
		foreach(object unitData in Json.ToList(matchData["Your_Units"].ToString())){
			Dictionary<string, object> unit = Json.ToDict(unitData.ToString());

			MatchUnit alliedUnit;

			alliedUnit.ID     = int.Parse(unit["ID"].ToString());
			alliedUnit.Name   = unit["Name"].ToString();
			alliedUnit.HP     = int.Parse(unit["HP"].ToString());
			alliedUnit.PrevHP = 0;		// TODO - QGU doesn't send it
			alliedUnit.X      = int.Parse(unit["X"].ToString());
			alliedUnit.Y      = int.Parse(unit["Y"].ToString());
			alliedUnit.Acted  = (bool)unit["Acted"];

			AlliedUnits[alliedUnit.ID] = alliedUnit;
		}

		// Get all the allied perks
		AlliedPerks = new List<MatchPerk>();
		foreach(object perkData in Json.ToList(matchData["Your_Perks"].ToString())){
			Dictionary<string, object> perk = Json.ToDict(perkData.ToString());

			MatchPerk alliedPerk;

			alliedPerk.Tier = int.Parse(perk["Tier"].ToString());
			alliedPerk.Name = perk["Name"].ToString();

			AlliedPerks.Add(alliedPerk);
		}

		// Allied leader data
		Dictionary<string, object> leaderData = (Dictionary<string, object>)matchData["Your_Leader"];
		AlliedLeader.Name    = leaderData["Name"].ToString();
		AlliedLeader.Ability = leaderData["Ability"].ToString();

		// Get all the enemy units
		EnemyUnits = new Dictionary<int, MatchUnit>();
		foreach(object unitData in Json.ToList(matchData["Enemy_Units"].ToString())){
			Dictionary<string, object> unit = Json.ToDict(unitData.ToString());

			MatchUnit enemyUnit;

			enemyUnit.ID     = int.Parse(unit["ID"].ToString());
			enemyUnit.Name   = unit["Name"].ToString();
			enemyUnit.HP     = int.Parse(unit["HP"].ToString());
			enemyUnit.PrevHP = 0;		// TODO - QGU doesn't send it
			enemyUnit.X      = int.Parse(unit["X"].ToString());
			enemyUnit.Y      = int.Parse(unit["Y"].ToString());
			enemyUnit.Acted  = (bool)unit["Acted"];

			EnemyUnits[enemyUnit.ID] = enemyUnit;
		}

		// Enemy leader data
		leaderData = (Dictionary<string, object>)matchData["Enemy_Leader"];
		EnemyLeader.Name    = leaderData["Name"].ToString();
		EnemyLeader.Ability = leaderData["Ability"].ToString();

		// Get all the enemy perks
		EnemyPerks = new List<MatchPerk>();
		foreach(object perkData in Json.ToList(matchData["Enemy_Perks"].ToString())){
			Dictionary<string, object> perk = Json.ToDict(perkData.ToString());

			MatchPerk enemyPerk;

			enemyPerk.Tier = int.Parse(perk["Tier"].ToString());
			enemyPerk.Name = perk["Name"].ToString();

			EnemyPerks.Add(enemyPerk);
		}

		// Get all of the Action History Data
		GameActions = new List<MatchAction>();
		foreach(object actionData in Json.ToList(matchData["Action_History"].ToString())){
			Dictionary<string, object> actn = Json.ToDict(actionData.ToString());

			MatchAction currAction;

			currAction.Order         = int.Parse(actn["Order"].ToString());
			currAction.Turn          = int.Parse(actn["Turn"].ToString());
			currAction.YourAction    = (bool)actn["Your_Action"];
			currAction.Action        = actn["Action"].ToString();
			currAction.UnitID        = int.Parse(actn["Unit"].ToString());
			currAction.UnitOldX      = int.Parse(actn["Old_X"].ToString());
			currAction.UnitNewX      = int.Parse(actn["New_X"].ToString());
			currAction.UnitOldY      = int.Parse(actn["Old_Y"].ToString());
			currAction.UnitNewY      = int.Parse(actn["New_Y"].ToString());
			currAction.UnitOldHP     = int.Parse(actn["Old_HP"].ToString());
			currAction.UnitNewHP     = int.Parse(actn["New_HP"].ToString());
			currAction.UnitCrit      = (bool)actn["Crit"];
			currAction.UnitMiss      = (bool)actn["Miss"];
			// This is likely an inconsistency on the backend - but for now this fixes QGU errors
			currAction.TargetID      = (actn["Target"] == null)? -1 : int.Parse(actn["Target"].ToString());
			currAction.TargetOldHP   = int.Parse(actn["Tgt_Old_HP"].ToString());
			currAction.TargetNewHP   = int.Parse(actn["Tgt_New_HP"].ToString());
			currAction.TargetCounter = (bool)actn["Tgt_Counter"];
			currAction.TargetCrit    = (bool)actn["Tgt_Crit"];
			currAction.TargetMiss    = (bool)actn["Tgt_Miss"];

			GameActions.Add(currAction);
		}
	}

	public Unit GetUnit(int ID) {
		foreach(Unit unit in GameController.Units) {
			if(ID == unit.Info.ID) {
				return unit;
			}
		}
		return null;
	}

}

public struct MatchAction {
	public int    Order;
	public int    Turn;
	public bool   YourAction;
	public string Action;
	public int    UnitID;
	public int    UnitOldX;
	public int    UnitOldY;
	public int    UnitNewX;
	public int    UnitNewY;
	public int    UnitOldHP;
	public int    UnitNewHP;
	public bool   UnitCrit;
	public bool   UnitMiss;
	public int    TargetID;
	public int    TargetOldHP;
	public int    TargetNewHP;
	public bool   TargetCounter;
	public bool   TargetCrit;
	public bool   TargetMiss;
}

public struct MatchUnit {
	public int    ID;
	public string Name;
	public int    HP;
	public int    PrevHP;
	public int    X;
	public int    Y;
	public bool   Acted;
}

public struct MatchLeader {
	public string Name;
	public string Ability;
}

public struct MatchPerk {
	public string Name;
	public int    Tier;
}

