using NUnit.Framework;
using System.Collections.Generic;

[TestFixture]
public class ILTest
{
	private string testNameVal = "test_name";
	private Dictionary<string, object> testDict;
	private string testDescVal = "test_description";

	[SetUp]
	public void BeforeTest(){
		testDict = new Dictionary<string, object>();
		testDict.Add("Description", testDescVal);
	}

	[Test]
	public void AbilityDataTest(){
		AbilityData ab = new AbilityData(new KeyValuePair<string, object>(testNameVal, testDescVal));

		Assert.AreEqual(ab.name, testNameVal);
		Assert.AreEqual(ab.description, testDescVal);
	}

	[Test]
	public void ActionDataTest(){
		ActionData ad = new ActionData(new KeyValuePair<string, object>(testNameVal, testDict));

		Assert.AreEqual(ad.name, testNameVal);
		Assert.AreEqual(ad.description, testDescVal);
	}

	[Test]
	public void MapDataTest(){
		string mapText = "1,F 1,Gn0,G 0,Fn2,F 2,G";
		MapData md = new MapData(new KeyValuePair<string, object>(testNameVal, mapText));

		Assert.AreEqual(md.name, testNameVal);

		Assert.AreEqual(md.width, 2);
		Assert.AreEqual(md.height, 3);

		Assert.AreEqual(md.teamPlaceUnit[0][0], 1);
		Assert.AreEqual(md.teamPlaceUnit[1][0], 1);
		Assert.AreEqual(md.teamPlaceUnit[0][1], 0);
		Assert.AreEqual(md.teamPlaceUnit[1][1], 0);
		Assert.AreEqual(md.teamPlaceUnit[0][2], 2);
		Assert.AreEqual(md.teamPlaceUnit[1][2], 2);

		Assert.AreEqual(md.terrain[0][0], "F");
		Assert.AreEqual(md.terrain[1][0], "G");
		Assert.AreEqual(md.terrain[0][1], "G");
		Assert.AreEqual(md.terrain[1][1], "F");
		Assert.AreEqual(md.terrain[0][2], "F");
		Assert.AreEqual(md.terrain[1][2], "G");
	}
}