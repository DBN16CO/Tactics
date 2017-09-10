using NUnit.Framework;
using System.Collections.Generic;

///<summary>
/// This class tests that all Game Data is properly loaded.
///</summary>
///<remarks>
/// When the IL command is called several Game Data objects are created.
/// This test fixture should ensure that they are each individually properly
/// populated when the expected IL response is received.
///</remarks>
[TestFixture]
public class ILTest
{
	private string testNameVal = "test_name";
	private Dictionary<string, object> testDict;
	private string testDescVal = "test_description";

	[SetUp]
	public void BeforeTest(){
		// Dictionary for all IL constructors that need a dictionary of values
		testDict = new Dictionary<string, object>();
		testDict.Add("Description", testDescVal);
	}

	[Test]
	public void AbilityDataTest(){
		AbilityData ab = new AbilityData(new KeyValuePair<string, object>(testNameVal, testDescVal));

		Assert.AreEqual(ab.Name, testNameVal);
		Assert.AreEqual(ab.Description, testDescVal);
	}

	[Test]
	public void ActionDataTest(){
		ActionData ad = new ActionData(new KeyValuePair<string, object>(testNameVal, testDescVal));

		Assert.AreEqual(ad.Name, testNameVal);
		Assert.AreEqual(ad.Description, testDescVal);
	}

	[Test]
	public void MapDataTest(){
		string mapText = "1,F 1,Gn0,G 0,Fn2,F 2,G";
		MapData md = new MapData(new KeyValuePair<string, object>(testNameVal, mapText));

		Assert.AreEqual(md.Name, testNameVal);

		// Ensure that the grids are the appropriate size
		Assert.AreEqual(md.Width, 2);
		Assert.AreEqual(md.Height, 3);
		Assert.AreEqual(md.TeamPlaceUnit.Length, 2);
		Assert.AreEqual(md.TeamPlaceUnit[0].Length, 3);
		Assert.AreEqual(md.Terrain.Length, 2);
		Assert.AreEqual(md.Terrain[0].Length, 3);

		// Ensure that each team's possible placement locations are valid
		Assert.AreEqual(md.TeamPlaceUnit[0][0], 1);
		Assert.AreEqual(md.TeamPlaceUnit[1][0], 1);
		Assert.AreEqual(md.TeamPlaceUnit[0][1], 0);
		Assert.AreEqual(md.TeamPlaceUnit[1][1], 0);
		Assert.AreEqual(md.TeamPlaceUnit[0][2], 2);
		Assert.AreEqual(md.TeamPlaceUnit[1][2], 2);

		// Ensure that the terrain type for each token is valid
		Assert.AreEqual(md.Terrain[0][0], "F");
		Assert.AreEqual(md.Terrain[1][0], "G");
		Assert.AreEqual(md.Terrain[0][1], "G");
		Assert.AreEqual(md.Terrain[1][1], "F");
		Assert.AreEqual(md.Terrain[0][2], "F");
		Assert.AreEqual(md.Terrain[1][2], "G");
	}
}