using System.Collections.Generic;		// For dictionaries
using System.Linq;						// For Count
using System;							// For StringSplitOptions

// Holds game data for each map
public class MapData {

	private string 		_name;
	private int[][] 	_teamPlaceUnit;
	private string[][] 	_terrain;
	private int 		_width;
	private int 		_height;

#region // Public properties
	public string Name {
		get{return _name;}
	}
	public int[][] TeamPlaceUnit {
		get{return _teamPlaceUnit;} 
	}
	public string[][] Terrain {
		get{return _terrain;} 
	}
	public int Width {
		get{return _width;}
	}
	public int Height {
		get{return _height;}
	}
#endregion


	// Constructor when starting from IL Server call
	public MapData(KeyValuePair<string, object> map) {
		_name = map.Key;
		CreateMapData(Parse.String(map.Value));
	}

	// Creates public arrays from map size and values
	private void CreateMapData(string mapData) {
		char[] newRow = {'n'};
		string[] rows = mapData.Split(newRow, StringSplitOptions.RemoveEmptyEntries);
		_width = rows[0].Count(x => x == ' ') + 1;
		_height = rows.Length;

		_teamPlaceUnit = new int[_width][];
		_terrain = new string[_width][];
		for(int x = 0; x < _width; x++) {
			_teamPlaceUnit[x] = new int[_height];
			_terrain[x] = new string[_height];
		}

		char[] newCol = {' '};
		for(int y = 0; y < _height; y++) {
			string[] cols = rows[y].Split(newCol, StringSplitOptions.RemoveEmptyEntries);
			for(int x = 0; x < _width; x++) {
				_teamPlaceUnit[x][y] = int.Parse(cols[x].Substring(0, 1));
				_terrain[x][y] = cols[x].Substring(2,1);
			}
		}

	}

}
