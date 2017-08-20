using System.Diagnostics;				// For stackframe

// Generalized parsing class that extends Parse to check for nulls and default values
public static class Parse {

	// Converts an object to a string if valid, otherwise defaults
	public static string String(object obj, string defaultOverride = "") {
		if(obj == null){
			WriteError(new StackFrame(1, true));
			return defaultOverride;
		}
		return obj.ToString();
	}

	// Converts an object to a bool if valid, otherwise defaults
	public static bool Bool(object obj, bool defaultOverride = false) {
		if(obj == null){
			WriteError(new StackFrame(1, true));
			return defaultOverride;
		}
		return (bool)obj;
	}

	// Converts an object to an int if valid, otherwise defaults
	public static int Int(object obj, int defaultOverride = -1) {
		if(obj == null){
			WriteError(new StackFrame(1, true));
			return defaultOverride;
		}
		int parsedInt;
		return (int.TryParse(obj.ToString(), out parsedInt))? parsedInt : defaultOverride;
	}

	// Logs the error message when an input is null
	private static void WriteError(StackFrame error) {
		string message;
		message = "Error parsing - null value at " + error.GetMethod().Name + ": " + error.GetFileLineNumber();
		UnityEngine.Debug.Log(message);
	}
}
