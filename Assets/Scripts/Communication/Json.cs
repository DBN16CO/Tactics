using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

public static class Json {

	public static string ToString(Dictionary<string, object> map){
        return JsonConvert.SerializeObject(map);
	}

	
	public static Dictionary<string, object> ToDict(string json){
		return JsonConvert.DeserializeObject<Dictionary<string, object>>(json);
	}
}
