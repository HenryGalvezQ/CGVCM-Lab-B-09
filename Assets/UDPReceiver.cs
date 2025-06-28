using UnityEngine;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

public class UDPReceiver : MonoBehaviour
{
    public static UDPReceiver Instance;
    UdpClient client;
    Thread receiveThread;
    public float LeftY { get; private set; }
    public float RightY { get; private set; }

    void Awake()
    {
        if (Instance == null) Instance = this; else { Destroy(gameObject); return; }
        DontDestroyOnLoad(gameObject);
    }

    void Start()
    {
        client = new UdpClient(5065);
        receiveThread = new Thread(ReceiveLoop) { IsBackground = true };
        receiveThread.Start();
    }

    void ReceiveLoop()
    {
        var anyIP = new IPEndPoint(IPAddress.Any, 0);
        while (true)
        {
            var data = client.Receive(ref anyIP);
            var msg = Encoding.UTF8.GetString(data);
            var parts = msg.Split(',');
            if (parts.Length < 2) continue;

            if (float.TryParse(parts[0], out float yL) &&
                float.TryParse(parts[1], out float yR))
            {
                float normL = Mathf.Clamp01(1f - yL / 480f);
                float normR = Mathf.Clamp01(1f - yR / 480f);

                LeftY = normL * 2f - 1f;
                RightY = normR * 2f - 1f;
            }
        }
    }

    void OnApplicationQuit() => receiveThread?.Abort();
}
