using NUnit.Framework;
using System.Collections.Generic;

[TestFixture]
public class ILTest
{
	[Test]
	public void AbilityDataTest(){
		AbilityData ab = new AbilityData(new KeyValuePair<string, object>("aaa", "bbb"));

		Assert.AreEqual(ab.name, "aaa");
	}
}