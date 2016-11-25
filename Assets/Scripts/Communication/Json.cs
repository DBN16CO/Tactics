using System.Collections.Generic;
using Newtonsoft.Json;

using System.Linq;
using Newtonsoft.Json.Linq;
using Newtonsoft.Json.Converters;
using System;

/*
	Custom Dictionary Converter used to deserialize Json Objects to a Dictionary<string, object> type
*/
class DictConverter : CustomCreationConverter<IDictionary<string, object>>
{
    public override IDictionary<string, object> Create(Type objectType)
    {
        return new Dictionary<string, object>();
    }

    public override bool CanConvert(Type objectType)
    {
        return objectType == typeof(object) || base.CanConvert(objectType);
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
    {
        if (reader.TokenType == JsonToken.StartObject
            || reader.TokenType == JsonToken.Null)
            return base.ReadJson(reader, objectType, existingValue, serializer);

        return serializer.Deserialize(reader);
    }
}


/*
	Custom List Converter used to deserialize Json Arrays to a List<object> type
*/
class ListConverter : CustomCreationConverter<IList<object>>
{
    public override IList<object> Create(Type objectType){
    	return new List<object>();
    }

    public override bool CanConvert(Type objectType)
    {
        return objectType == typeof(List<object>) || base.CanConvert(objectType);
    }

    public override object ReadJson(JsonReader reader, Type objectType, object existingValue, JsonSerializer serializer)
    {
        if (reader.TokenType == JsonToken.Null || reader.TokenType == JsonToken.StartArray)
            return base.ReadJson(reader, objectType, existingValue, serializer);

        return serializer.Deserialize(reader);
    }
}

public static class Json {

	public static string ToString(Dictionary<string, object> map){
        return JsonConvert.SerializeObject(map);
	}

	public static Dictionary<string, object> ToDict(string json){
		return JsonConvert.DeserializeObject<Dictionary<string, object>>(json, new JsonConverter[] {new DictConverter()});
	}

	public static List<object> ToList(string json){
		return JsonConvert.DeserializeObject<List<object>>(json, new JsonConverter[] {new ListConverter()});
	}
}
