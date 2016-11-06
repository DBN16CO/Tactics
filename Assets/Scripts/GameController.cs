using UnityEngine;
using System.Threading;
using System;
using System.Collections.Generic;

public class GameController : MonoBehaviour {

	void Start() {
		Grid grid = gameObject.AddComponent<Grid>();
		grid.CreateGrid(8);

		var request = new Dictionary<string, object>();
		request["PING"] = "PING";
		
		//Example sending and receiving data synchronously
		Communication.Connect(new Uri("ws://localhost:8000"));
		Communication.SendString (Json.ToString(request));
		string response = null;
		while (response == null) {
			response = Communication.RecvString ();
		}

		Debug.Log ("Received: " + response);
		Debug.Log("Response toDict: " + Json.ToDict(response)["PONG"]);

		//Example sending and receiving data asynchronously and doing something with the response
		new Thread(GameController.PingServerPrintResponse).Start();

		Debug.Log("Continuing on...");
		

	}

	public static void PingServerPrintResponse(){
		var request = new Dictionary<string, object>();
		request["PING"] = "PING";

		Communication.Connect(new Uri("ws://localhost:8000"));
		Communication.SendString(Json.ToString(request));

		string response = null;
		while (response == null) {
			response = Communication.RecvString ();
		}

		Debug.Log ("Received in pingServerPrintResponse: " + response);

		Debug.Log("Response in pingServerPrintResponse - toDict: " + Json.ToDict(response)["PONG"]);
	}

}
