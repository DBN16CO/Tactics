using System;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using System.Threading;

public static class Communication{

	private static WebSocketSharp.WebSocket m_Socket;
	private static Queue<byte[]> m_Messages = new Queue<byte[]>();
	private static bool m_IsConnected;
	private static string m_Error;
	private static int retry;

	private static Uri mUrl;

	public static void SendString(string str)
	{
		Send(Encoding.UTF8.GetBytes (str));
	}

	public static string RecvString()
	{
		byte[] retval = Recv();
		return (retval == null)? null : Encoding.UTF8.GetString(retval);
	}

	public static bool Connect(Uri url)
	{
		//Already connected, just return true
		if (mUrl == url && m_IsConnected && m_Error == null){
			return true;
		}

		mUrl = url;

		string protocol = mUrl.Scheme;
		if (!protocol.Equals("ws") && !protocol.Equals("wss"))
			throw new ArgumentException("Unsupported protocol: " + protocol);

		m_Socket = new WebSocketSharp.WebSocket(mUrl.ToString());

		//Logic to be done when we receive a message through the websocket
		m_Socket.OnMessage += (sender, e) => {
			m_Messages.Enqueue(e.RawData);
			lock(CommunicationManager.responseDictLock){
				Monitor.Pulse(CommunicationManager.responseDictLock);
			}
		};

		//Logic to be done when we successfully connect to the server through the websocket
		m_Socket.OnOpen += (sender, e) => {
			retry = 0;
			m_IsConnected = true;
		};

		//Logic to be done when we hit an error with the websocket connection
		m_Socket.OnError += (sender, e) => {
			m_Error = e.Message;
			m_IsConnected = false;
			Debug.Log("Error Reason: " + e.Message);
			if (retry < 5) {
				Debug.Log("Retrying connection: " + retry);
				retry++;
				Close();
				Connect(url);
			}
			else {
				Debug.Log("Failed to reconnect");
			}
		};

		//Logic to be done when the websocket is closed
		m_Socket.OnClose += (sender, e) => {
			m_IsConnected = false;
			Debug.Log("Websocket closed.");
		};

		m_Socket.ConnectAsync();

		int retryCount = 0;
		const int maxRetries = 10;
		while (!m_IsConnected && m_Error == null && retryCount < maxRetries) {
			//Debug.Log ("Waiting for connection...");
			Thread.Sleep (200);
			retryCount++;
		}

		return m_IsConnected;
	}

	public static bool IsConnected {
		get{return m_Socket != null && m_Socket.IsAlive && m_IsConnected;}
	}

	public static void Send(byte[] buffer)
	{
		m_Socket.Send(buffer);
	}

	public static byte[] Recv()
	{
		return (m_Messages.Count <= 0)? null : m_Messages.Dequeue();
	}

	public static void Close()
	{
		if(m_Socket != null){
			m_Socket.Close();
			m_Socket = null;
		}
	}

	public static string Error
	{
		get {
			return m_Error;
		}
	}
}
