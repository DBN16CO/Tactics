using System.Collections.Generic;		// For dictionaries

// Holds all data about a match
public class MatchData {

	// QGU properties
	private int 	_id;
	private string 	_name;
	private string 	_opponent;
	private int 	_round;
	private bool 	_userTurn;
	private string 	_mapName;
	private bool 	_finished;
	private int 	_userTeam;
	private int 	_enemyTeam;

	private Dictionary<int, Unit>	_alliedUnits;
	private MatchLeader       		_alliedLeader;
	private List<MatchPerk>   		_alliedPerks;
	private Dictionary<int, Unit>	_enemyUnits;
	private MatchLeader       		_enemyLeader;
	private List<MatchPerk>   		_enemyPerks;
	private List<MatchAction> 		_gameActions;

#region // Public properties
	public int ID {
		get{return _id;}
	}
	public string Name {
		get{return _name;}
	}
	public string Opponent {
		get{return _opponent;}
	}
	public int Round {
		get{return _round;}
	}
	public bool UserTurn {
		get{return _userTurn;}
	}
	public string MapName {
		get{return _mapName;}
	}
	public bool Finished {
		get{return _finished;}
	}
	public int UserTeam {
		get{return _userTeam;}
	}
	public int EnemyTeam {
		get{return _enemyTeam;}
	}
	public Dictionary<int, Unit> AlliedUnits{
		get{return _alliedUnits;}
	}
	public MatchLeader AlliedLeader {
		get{return _alliedLeader;}
	}
	public List<MatchPerk> AlliedPerks {
		get{return _alliedPerks;}
	}
	public Dictionary<int, Unit> EnemyUnits {
		get{return _enemyUnits;}
	}
	public MatchLeader EnemyLeader {
		get{return _enemyLeader;}
	}
	public List<MatchPerk> EnemyPerks {
		get{return _enemyPerks;}
	}
	public List<MatchAction> GameActions {
		get{return _gameActions;}
	}
#endregion


	// Default constructor
	// Parses all fields necessary to describe the game to the front end
	public MatchData(Dictionary<string, object> matchData) {
		// General match information
		_id          = Parse.Int(matchData["ID"]);
		_name        = Parse.String(matchData["Name"]);
		_opponent    = Parse.String(matchData["Opponent"]);
    	_round       = Parse.Int(matchData["Round"]);
        _userTurn    = Parse.Bool(matchData["Your_Turn"]);
        _mapName     = Parse.String(matchData["Map"]);
        _finished    = Parse.Bool(matchData["Finished"]);
		_userTeam    = Parse.Int(matchData["Your_Team"]);
		_enemyTeam   = Parse.Int(matchData["Enemy_Team"]);

		// Get all the allied units
		_alliedUnits = new Dictionary<int, Unit>();
		foreach(object unitData in Json.ToList(Parse.String(matchData["Your_Units"]))){
			Dictionary<string, object> unitInfo = Json.ToDict(Parse.String(unitData));
			Unit alliedUnit = new Unit(unitInfo, Unit.ALLY_TEAM);
			_alliedUnits[alliedUnit.ID] = alliedUnit;
		}

		// Allied leader data
		Dictionary<string, object> leaderData = (Dictionary<string, object>)matchData["Your_Leader"];
		_alliedLeader.Name    = Parse.String(leaderData["Name"]);
		_alliedLeader.Ability = Parse.String(leaderData["Ability"]);

		// Get all the allied perks
		_alliedPerks = new List<MatchPerk>();
		foreach(object perkData in Json.ToList(Parse.String(matchData["Your_Perks"]))){
			Dictionary<string, object> perk = Json.ToDict(Parse.String(perkData));

			MatchPerk alliedPerk = new MatchPerk();
			alliedPerk.Tier = Parse.Int(perk["Tier"]);
			alliedPerk.Name = Parse.String(perk["Name"]);

			_alliedPerks.Add(alliedPerk);
		}

		// Get all the enemy units
		_enemyUnits = new Dictionary<int, Unit>();
		foreach(object unitData in Json.ToList(Parse.String(matchData["Enemy_Units"]))){
			Dictionary<string, object> unitInfo = Json.ToDict(Parse.String(unitData));
			Unit enemyUnit = new Unit(unitInfo, Unit.ENEMY_TEAM);
			_enemyUnits[enemyUnit.ID] = enemyUnit;
		}

		// Enemy leader data
		leaderData = (Dictionary<string, object>)matchData["Enemy_Leader"];
		_enemyLeader.Name    = Parse.String(leaderData["Name"]);
		_enemyLeader.Ability = Parse.String(leaderData["Ability"]);

		// Get all the enemy perks
		_enemyPerks = new List<MatchPerk>();
		foreach(object perkData in Json.ToList(Parse.String(matchData["Enemy_Perks"]))){
			Dictionary<string, object> perk = Json.ToDict(Parse.String(perkData));

			MatchPerk enemyPerk = new MatchPerk();
			enemyPerk.Tier = Parse.Int(perk["Tier"]);
			enemyPerk.Name = Parse.String(perk["Name"]);

			_enemyPerks.Add(enemyPerk);
		}

		// Get all of the Action History Data
		_gameActions = new List<MatchAction>();
		foreach(object actionData in Json.ToList(Parse.String(matchData["Action_History"]))){
			Dictionary<string, object> actn = Json.ToDict(Parse.String(actionData));

			MatchAction currAction = new MatchAction();

			currAction.Order         = Parse.Int(actn["Order"]);
			currAction.Turn          = Parse.Int(actn["Turn"]);
			currAction.YourAction    = Parse.Bool(actn["Your_Action"]);
			currAction.Action        = Parse.String(actn["Action"]);
			currAction.UnitID        = Parse.Int(actn["Unit"]);
			currAction.UnitOldX      = Parse.Int(actn["Old_X"]);
			currAction.UnitNewX      = Parse.Int(actn["New_X"]);
			currAction.UnitOldY      = Parse.Int(actn["Old_Y"]);
			currAction.UnitNewY      = Parse.Int(actn["New_Y"]);
			currAction.UnitOldHP     = Parse.Int(actn["Old_HP"]);
			currAction.UnitNewHP     = Parse.Int(actn["New_HP"]);
			currAction.UnitCrit      = Parse.Bool(actn["Crit"]);
			currAction.UnitMiss      = Parse.Bool(actn["Miss"]);
			if(actn["Target"] != null) {
				currAction.TargetID      = Parse.Int(actn["Target"]);
				currAction.TargetOldHP   = Parse.Int(actn["Tgt_Old_HP"]);
				currAction.TargetNewHP   = Parse.Int(actn["Tgt_New_HP"]);
				currAction.TargetCounter = Parse.Bool(actn["Tgt_Counter"]);
				currAction.TargetCrit    = Parse.Bool(actn["Tgt_Crit"]);
				currAction.TargetMiss    = Parse.Bool(actn["Tgt_Miss"]);
			}

			_gameActions.Add(currAction);
		}
	}

#region // Public methods
	public void EndTurn() {
		_userTurn = false;
	}
	public void StartTurn() {
		_userTurn = true;
	}
#endregion

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

public struct MatchLeader {
	public string Name;
	public string Ability;
}

public struct MatchPerk {
	public string Name;
	public int    Tier;
}
