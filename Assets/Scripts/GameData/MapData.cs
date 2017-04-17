using System.Collections.Generic;		// For dictionaries
using System.Linq;						// For Count
using System;

// Class holding game data for each map
public class MapData {

	public string name;
	public int[][] teamPlaceUnit;
	public string[][] terrain;

	public int width;
	public int height;

	public MapData(KeyValuePair<string, object> map) {
		name = map.Key;
		CreateMapData(map.Value.ToString());
	}

	// Creates public arrays from map size and values
	private void CreateMapData(string mapData) {
		char[] newRow = {'n'};
		string[] rows = mapData.Split(newRow, StringSplitOptions.RemoveEmptyEntries);
		//Array.Reverse(rows);
		width = rows[0].Count(x => x == ' ') + 1;
		height = rows.Length;

		teamPlaceUnit = new int[width][];
		terrain = new string[width][];
		for(int x = 0; x < width; x++) {
			teamPlaceUnit[x] = new int[height];
			terrain[x] = new string[height];
		}

		char[] newCol = {' '};
		for(int y = 0; y < height; y++) {
			string[] cols = rows[y].Split(newCol, StringSplitOptions.RemoveEmptyEntries);
			for(int x = 0; x < width; x++) {
				teamPlaceUnit[x][y] = int.Parse(cols[x].Substring(0, 1));
				terrain[x][y] = cols[x].Substring(2,1);
			}
		}

	}

}
