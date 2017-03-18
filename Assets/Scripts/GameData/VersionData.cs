using System.Collections.Generic;
using System;

public class VersionData {

	public int maxFunds;

	public VersionData(Dictionary<string, object> versionData) {
		maxFunds = Int32.Parse(versionData["Price_Max"].ToString());
	}

}
