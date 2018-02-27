using System;
using System.Collections;
using System.Collections.Generic;
using System.Threading;
using UnityEngine;

public class ParentController : MonoBehaviour {
	public static readonly bool REQUEST_IS_READY = true;
	public static readonly bool REQUEST_IS_NOT_READY = false;

	// Mapping of the request ID to the type of request it is
	// Key: Request ID Value: The type of request (GUI, TA, etc.)
	public Dictionary<string, RequestType> RequestToType = new Dictionary<string, RequestType>();

	// Mapping of requests made to whether they are ready or not to be processed
	// Key: Request ID Value: True if the request is ready to process
	private Dictionary<string, bool> RequestsAreReady = new Dictionary<string, bool>();

	private static readonly object _readyRequestLock = new object();

	// Runs when the app is closed - attempt to close the websocket cleanly
	void OnApplicationQuit() {
		CommunicationManager.OnDisable();
	}

	public void SetRequestReadiness(string rid, bool isReady){
		lock(_readyRequestLock){
			RequestsAreReady[rid] = isReady;
		}
	}

	protected void ProcessResponses(){
		// Check if any requests that have been made have returned
		if (Monitor.TryEnter(_readyRequestLock)) {
			try {
				string[] retKeys = null;
				Dictionary<string, bool>.KeyCollection keyset = RequestsAreReady.Keys;
				retKeys = new string[RequestsAreReady.Count];
				keyset.CopyTo(retKeys, 0);

				foreach(string rid in retKeys){
					if(!RequestsAreReady[rid]){
						continue;
					}

					if(!_functionMapping.ContainsKey(RequestToType[rid])){
						Debug.Log("ERROR: Missing mapping for RequestType value: " + RequestToType[rid].ToString());
					}
					else{
						StartCoroutine(_functionMapping[RequestToType[rid]](Server.GetResponse(rid)));
					}

					RequestsAreReady.Remove(rid);
					RequestToType.Remove(rid);
				}
			}
			finally {
			  // Ensure that the lock is released.
			  Monitor.Exit(_readyRequestLock);
			}
		}
	}

	protected Dictionary<RequestType, Func<Dictionary<string, object>, IEnumerator>> _functionMapping =
			new Dictionary<RequestType, Func<Dictionary<string, object>, IEnumerator>>();
}
