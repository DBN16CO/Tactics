using UnityEngine;
using System;
using System.Threading;
using System.Collections.Generic;
using Common.Cryptography;
using System.Security.Cryptography;
using System.Text.RegularExpressions;
using System.Linq;
using System.Text;

public class CommunicationManager
{
	private static Thread _manager;
	private static bool _threadRunning;

	private static object asyncMessagesLock;
	private static object requestQueueLock;
	private static object responseDictLock;

	private static Queue<Dictionary<string, object>> asyncMessagesQueue;
	private static Queue<Dictionary<string, object>> requestQueue;
	private static Dictionary<string, Dictionary<string, object>> responseDict;

	private static string url = "ws://tactics-dev.ddns.net:8443";
	//private static string url = "ws://localhost:8000";
	//private static string url = ""ws://tactics-production.herokuapp.com/""

	public static void Start()
	{
		Debug.Log("Starting Communication Manager");
		//Create the communication data structures
		asyncMessagesQueue = new Queue<Dictionary<string, object>>();
		requestQueue = new Queue<Dictionary<string, object>>();
		responseDict = new Dictionary<string, Dictionary<string, object>>();

		//Create the communication lock objects
		asyncMessagesLock = new object();
		requestQueueLock = new object();
		responseDictLock = new object();

		//Create the server connection
		Connect();

		//Start the communicator thread
		_manager = new Thread(ProcessRequests);
		_manager.Start();
		Debug.Log("Communication Manager has started successfully");
	}

	static void ProcessRequests(){
		_threadRunning = true;
		Dictionary<string, object> request = null;
		Dictionary<string, object> response = null;
		bool done = false;

		try{
			while (_threadRunning){
				request = null;
				response = null;

				//Take a request off the queue
				lock(requestQueueLock){
					if (requestQueue.Count > 0){
						request = requestQueue.Dequeue();
					}
				}

				string requestID = "";
				if (request != null){
					//Send the request to the server
					requestID = (string)request["Request_ID"];
					Debug.Log("Manager Thread Sending Request: " + requestID);
					SendCommand(request);
				}
				
				done = false;
				while (!done){
					Dictionary<string, object> resp = null;
					try{
						resp = GetNextResponse();
					} catch (Exception e){
						if (e.ToString().Contains("unauthenticated")){
							if (request != null){
								SendCommand(request);
							}
						}
						Debug.Log("Exception getting response: " + e.ToString());
						throw e;
					}
					
					if (resp == null){
						break;
					}

					if (resp.ContainsKey("Request_ID") && (string) resp["Request_ID"] == requestID){
						response = resp;
					}
					else{
						lock(asyncMessagesLock){
							Debug.Log("Found an async message");
							LogDictionary(resp);
							asyncMessagesQueue.Enqueue(resp);
							Debug.Log("Async Queue Size: " + asyncMessagesQueue.Count.ToString());
						}
					}
				}
				
				if (response != null){
					//Add the response to the common dictionary
					lock(responseDictLock){
						responseDict[requestID] = response;
					}
				}
				else if (request == null){
					//No Request or response found, just continue looping
				}
				else{
					//Unable to process request, re-add it to process it later
					lock(requestQueueLock){
						requestQueue.Enqueue(request);
					}
				}
			}
		} catch (Exception e){
			Debug.Log("Manager Thread crashed: " + e.ToString());
		}

		
	}

	public static void OnDisable()
	{
		// If the thread is still running, we should shut it down,
		if (_threadRunning)
		{
			// This forces the while loop of the thread to exit
			_threadRunning = false;

			// This waits until the thread exits
			_manager.Join();
		}

		Disconnect();
	}

	/********************************************
	 * Public Interface functions
	 ********************************************/
	public static string Request(Dictionary<string, object> data)
	{
		//Communication Manager Thread crashed, restart it
		if (!_threadRunning){
			CommunicationManager.Start();
		}

		//Generate a request id
		Guid g = Guid.NewGuid();
		data["Request_ID"] = g.ToString();

		//Put the request id and the request data into the request Queue
		lock (requestQueueLock)
		{
			requestQueue.Enqueue(data);
		}

		//Return the request id
		return g.ToString();
	}

	public static Dictionary<string, object> RequestAndGetResponse(Dictionary<string, object> data){
		string requestID = Request(data);

		return GetResponse(requestID);
	}

	public static Dictionary<string, object> GetResponse(string request_id, bool blocking = true, int timeout = 2, int sleep_time = 100)
	{
		int elapsed_time = 0;
		Dictionary<string, object> response = null;

		if (sleep_time <= 0){
			sleep_time = 100;
		}

		if (!blocking)
		{
			lock (responseDictLock)
			{
				if (responseDict.ContainsKey(request_id))
				{
					response = responseDict[request_id];
					responseDict.Remove(request_id);
				}
			}

			return response;
		}

		while (elapsed_time < timeout)
		{
			lock (responseDictLock)
			{
				//Debug.Log("Checking if a response exists for request: " + request_id.ToString());
				if (responseDict.ContainsKey(request_id))
				{
					response = responseDict[request_id];
					responseDict.Remove(request_id);
				}
			}

			if (response != null)
			{
				return response;
			}
			else
			{
				Thread.Sleep(sleep_time);
				elapsed_time += sleep_time / 1000;
			}
		}

		return response;
	}

	public static Dictionary<string, object> GetNextAsyncMessage(){
		Dictionary<string, object> message = null;
		lock(asyncMessagesLock){
			if (asyncMessagesQueue.Count > 0){
				message = asyncMessagesQueue.Dequeue();
			}
		}

		return message;
	}


	/********************************************
	 * Private communication helper logic
	 ********************************************/
	private static void Connect()
	{
		Communication.Connect(new Uri(url));
	}

	private static void Disconnect()
	{
		Communication.Close();
	}

	private static bool IsUnauthenticated(Dictionary<string, object> response)
	{
		if (!response.ContainsKey("Success")){
			return false;
		}

		bool success = (bool)response["Success"];
		if (!success)
		{
			string error = response["Error"].ToString();
			if (error.Contains("User is not authenticated"))
			{
				Debug.Log("User is not authenticated, retry logging in.");
				return true;
			}
		}

		return false;
	}

	// Used to login to server with cached session token
	public static bool RetryLogin()
	{
		// Create the request, decrypt session token, and send it
		var request = new Dictionary<string, object>();
		string _encryptedToken = PlayerPrefs.GetString("session");
		string _loginToken = AES.Decrypt(_encryptedToken, GenerateAESKey());
		request["Command"] = "LGN";
		request["token"] = _loginToken;
		Communication.SendString(Json.ToString(request));
		// Wait for the response, then parse
		string strResponse = null;
		while (strResponse == null)
		{
			strResponse = Communication.RecvString();
		}
		var response = Json.ToDict(strResponse);
		Debug.Log("Response to Retry Login: " + response.ToString());
		// Error Handling
		bool success = (bool)response["Success"];
		if (success)
		{
			Debug.Log("user re-logged in with token: " + _loginToken);
		}
		else
		{
			Debug.Log("error logging user in with existing token");
			PlayerPrefs.DeleteKey("session");
			PlayerPrefs.Save();
		}
		return success;
	}

	private static bool SendCommand(Dictionary<string, object> request)
	{
		// Verify the websocket is still connected and try to reconnect if it isn't
		if (!Communication.IsConnected())
		{
			Communication.Close();
			Communication.Connect(new Uri(url));
		}

		// Failed to reconnect with the server
		if (!Communication.IsConnected())
		{
			return false;
		}

		// Send the request
		Communication.SendString(Json.ToString(request));

		return true;
	}

	private static Dictionary<string, object> GetNextResponse(){
		// Wait for the response
		string strResponse = null;
		Dictionary<string, object> response = null;

		int retryCount = 0;
		const int maxRetries = 20;
		while (strResponse == null && retryCount < maxRetries)
		{
			strResponse = Communication.RecvString();
			if (strResponse != null)
			{
				response = Json.ToDict(strResponse);
				if (IsUnauthenticated(response))
				{
					// Server says we are not logged in, re-authenticate
					RetryLogin();
					strResponse = null;
					response = null;
					throw new Exception("Response indicates user was unauthenticated please try again");
				}


			}

			if (strResponse == null)
			{
				retryCount++;
				Thread.Sleep(30);
			}
		}

		if (response == null)
		{
			return null;
		}

		return response;
	}

	private static void LogDictionary(Dictionary<string, object> dict){
		Debug.Log("{");
		foreach (KeyValuePair<string, object> kvp in dict)
		{
			Debug.Log(string.Format("Key = {0}, Value = {1}", kvp.Key.ToString(), kvp.Value.ToString()));
			if (kvp.Value.GetType() == typeof(Dictionary<string, object>)){
				LogDictionary((Dictionary<string, object>)kvp.Value);
			}
		}
		Debug.Log("}");
	}

	// Generates the key to use for AES encryption
	public static string GenerateAESKey()
	{
		MD5CryptoServiceProvider md5 = new MD5CryptoServiceProvider();
		byte[] tmpSource;
		byte[] tmpHash;

		// Get unique identifier for device
		string source = SystemInfo.deviceUniqueIdentifier;
		Regex regX = new Regex(@"([<>""'%;()&])");
		source = regX.Replace(source, "");

		// Convert to byte[] and compute MD5 hash
		tmpSource = ASCIIEncoding.ASCII.GetBytes(source);
		tmpHash = md5.ComputeHash(tmpSource);

		// Convert to hexadecimal to ensure valid characters
		StringBuilder sOutput = new StringBuilder(tmpHash.Length);
		for (int i = 0; i < tmpHash.Length; i++)
		{
			sOutput.Append(tmpHash[i].ToString("X2"));  // X2 formats to hexadecimal
		}
		return sOutput.ToString();
	}
}