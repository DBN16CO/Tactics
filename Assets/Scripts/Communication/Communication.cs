using System;
using System.Collections.Generic;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Collections;
using UnityEngine;
using System.Runtime.InteropServices;
using System.Threading;

public class Communication{

	static WebSocketSharp.WebSocket m_Socket;
	static Queue<byte[]> m_Messages = new Queue<byte[]>();
	static bool m_IsConnected = false;
	static string m_Error = null;

	private static Uri mUrl;

	public static void SendString(string str)
	{
		Send(Encoding.UTF8.GetBytes (str));
	}

	public static string RecvString()
	{
		byte[] retval = Recv();
		if (retval == null)
			return null;
		return Encoding.UTF8.GetString (retval);
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
		m_Socket.OnMessage += (sender, e) => m_Messages.Enqueue (e.RawData);
		m_Socket.OnOpen += (sender, e) => m_IsConnected = true;
		m_Socket.OnError += (sender, e) => m_Error = e.Message;
		m_Socket.ConnectAsync();

		while (!m_IsConnected && m_Error == null) {
			Debug.Log ("Waiting for connection...");
			Thread.Sleep (1000);
		}

		if (m_IsConnected) {
			return true;
		}
		else {
			return false;
		}


	}

	public static void Send(byte[] buffer)
	{
		if (m_IsConnected) {
			Debug.Log ("Connected!");
		}
		Debug.Log (buffer.Length);
		m_Socket.Send(buffer);
	}

	public static byte[] Recv()
	{
		if (m_Messages.Count == 0)
			return null;
		return m_Messages.Dequeue();
	}

	public static void Close()
	{
		m_Socket.Close();
	}

	public static string error
	{
		get {
			return m_Error;
		}
	}
}
