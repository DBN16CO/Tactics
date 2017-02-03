using System.Collections.Generic;
using System;

public class MatchData {

	public int maxFunds;

	public MatchData(Dictionary<string, object> matchData) {
		maxFunds = Int32.Parse(matchData["Price_Max"].ToString());
	}

}
