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

	private Dictionary<int, UnitInfo>	_alliedUnits;
	private MatchLeader       			_alliedLeader;
	private List<MatchPerk>   			_alliedPerks;
	private Dictionary<int, UnitInfo>	_enemyUnits;
	private MatchLeader       			_enemyLeader;
	private List<MatchPerk>   			_enemyPerks;
	private List<MatchAction> 			_gameActions;

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
	public Dictionary<int, UnitInfo> AlliedUnits{
		get{return _alliedUnits;}
	}
	public MatchLeader AlliedLeader {
		get{return _alliedLeader;}
	}
	public List<MatchPerk> AlliedPerks {
		get{return _alliedPerks;}
	}
	public Dictionary<int, UnitInfo> EnemyUnits {
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
		_id          = int.Parse(matchData["ID"].ToString());
		_name        = matchData["Name"].ToString();
		_opponent    = matchData["Opponent"].ToString();
    	_round       = int.Parse(matchData["Round"].ToString());
        _userTurn    = (bool)matchData["Your_Turn"];
        _mapName     = matchData["Map"].ToString();
        _finished    = (bool)matchData["Finished"];
		_userTeam    = int.Parse(matchData["Your_Team"].ToString());
		_enemyTeam   = int.Parse(matchData["Enemy_Team"].ToString());

		// Get all the allied units
		_alliedUnits = new Dictionary<int, UnitInfo>();
		foreach(object unitData in Json.ToList(matchData["Your_Units"].ToString())){
			if(unitData != null) {
				Dictionary<string, object> unit = Json.ToDict(unitData.ToString());
				UnitInfo alliedUnit = new UnitInfo(unit);
				_alliedUnits[alliedUnit.ID] = alliedUnit;
			}
		}

		// Get all the allied perks
		_alliedPerks = new List<MatchPerk>();
		foreach(object perkData in Json.ToList(matchData["Your_Perks"].ToString())){
			Dictionary<string, object> perk = Json.ToDict(perkData.ToString());

			MatchPerk alliedPerk = new MatchPerk();

			alliedPerk.Tier = int.Parse(perk["Tier"].ToString());
			alliedPerk.Name = perk["Name"].ToString();

			_alliedPerks.Add(alliedPerk);
		}

		// Allied leader data
		Dictionary<string, object> leaderData = (Dictionary<string, object>)matchData["Your_Leader"];
		_alliedLeader.Name    = leaderData["Name"].ToString();
		_alliedLeader.Ability = leaderData["Ability"].ToString();

		// Get all the enemy units
		_enemyUnits = new Dictionary<int, UnitInfo>();
		foreach(object unitData in Json.ToList(matchData["Enemy_Units"].ToString())){
			if(unitData != null) {
				Dictionary<string, object> unit = Json.ToDict(unitData.ToString());
				UnitInfo enemyUnit = new UnitInfo(unit);
				_enemyUnits[enemyUnit.ID] = enemyUnit;
			}
		}

		// Enemy leader data
		leaderData = (Dictionary<string, object>)matchData["Enemy_Leader"];
		_enemyLeader.Name    = leaderData["Name"].ToString();
		_enemyLeader.Ability = leaderData["Ability"].ToString();

		// Get all the enemy perks
		_enemyPerks = new List<MatchPerk>();
		foreach(object perkData in Json.ToList(matchData["Enemy_Perks"].ToString())){
			Dictionary<string, object> perk = Json.ToDict(perkData.ToString());

			MatchPerk enemyPerk = new MatchPerk();

			enemyPerk.Tier = int.Parse(perk["Tier"].ToString());
			enemyPerk.Name = perk["Name"].ToString();

			_enemyPerks.Add(enemyPerk);
		}

		// Get all of the Action History Data
		_gameActions = new List<MatchAction>();
		foreach(object actionData in Json.ToList(matchData["Action_History"].ToString())){
			Dictionary<string, object> actn = Json.ToDict(actionData.ToString());

			MatchAction currAction = new MatchAction();

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
			if(actn["Target"] != null) {
				currAction.TargetID      = int.Parse(actn["Target"].ToString());
				currAction.TargetOldHP   = int.Parse(actn["Tgt_Old_HP"].ToString());
				currAction.TargetNewHP   = int.Parse(actn["Tgt_New_HP"].ToString());
				currAction.TargetCounter = (bool)actn["Tgt_Counter"];
				currAction.TargetCrit    = (bool)actn["Tgt_Crit"];
				currAction.TargetMiss    = (bool)actn["Tgt_Miss"];
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

