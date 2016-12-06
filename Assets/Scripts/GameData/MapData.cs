using System.Collections.Generic;		// For dictionaries
using System.Linq;						// For Count
using System;

// Class holding game data for each map
public class MapData {

	public string name;
	public bool[][] canPlaceUnit;
	public string[][] terrain;

	private int width;
	private int height;

	public MapData(KeyValuePair<string, object> map) {
		name = map.Key;
		CreateMapData(map.Value.ToString());
		//UnityEngine.Debug.Log(int.Parse("1"));
	}

	// Creates public arrays from map size and values
	private void CreateMapData(string mapData) {
		char[] newRow = {'n'};
		string[] rows = mapData.Split(newRow, StringSplitOptions.RemoveEmptyEntries);
		Array.Reverse(rows);
		width = rows[0].Count(x => x == ' ') + 1;
		height = rows.Length;

		canPlaceUnit = new bool[width][];
		terrain = new string[width][];
		for(int x = 0; x < width; x++) {
			canPlaceUnit[x] = new bool[height];
			terrain[x] = new string[height];
		}

		char[] newCol = {' '};
		for(int y = 0; y < height; y++) {
			string[] cols = rows[y].Split(newCol, StringSplitOptions.RemoveEmptyEntries);
			for(int x = 0; x < width; x++) {
				canPlaceUnit[x][y] = (cols[x].Substring(0, 1) == "1");
				terrain[x][y] = cols[x].Substring(2,1);
			}
		}

		/*for(int y = 0; y < height; y++) {
			for(int x = 0; x < width; x++) {
				canPlaceUnit[x][y] = (rows[y].Substring(4*x, 1) == "1");
				terrain[x][y] = rows[y].Substring(3 + 4*x, 1);
			}
		}*/

	}

}
