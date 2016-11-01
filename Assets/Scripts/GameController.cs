using UnityEngine;
using System.Threading;
using System;

public class GameController : MonoBehaviour {

	void Start() {
		Grid grid = gameObject.AddComponent<Grid>();
		grid.CreateGrid(8);


		//Example sending and receiving data synchronously
		Communication.Connect(new Uri("ws://localhost:8000"));
		Communication.SendString ("{\"PING\":\"PING\"}");
		string response = null;
		while (response == null) {
			response = Communication.RecvString ();
		}

		Debug.Log ("Received: " + response);		


		//Example sending and receiving data asynchronously and doing something with the response
		new Thread(GameController.PingServerPrintResponse).Start();

		Debug.Log("Continuing on...");
		

	}

	public static void PingServerPrintResponse(){
		Communication.Connect(new Uri("ws://localhost:8000"));
		Communication.SendString("{\"PING\":\"PING\"}");

		string response = null;
		while (response == null) {
			response = Communication.RecvString ();
		}

		Debug.Log ("Received in pingServerPrintResponse: " + response);
	}

}
