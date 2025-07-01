using UnityEngine;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;

public class UDPReceiver : MonoBehaviour
{
    public static UDPReceiver Instance;
    UdpClient client;
    CancellationTokenSource cts;
    Task receiveTask;
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
        cts = new CancellationTokenSource();
        receiveTask = ReceiveLoopAsync(cts.Token);
    }

    async Task ReceiveLoopAsync(CancellationToken token)
    {
        while (!token.IsCancellationRequested)
        {
            UdpReceiveResult res;
            try
            {
                res = await client.ReceiveAsync();
            }
            catch (ObjectDisposedException)
            {
                break;
            }
            var msg = Encoding.UTF8.GetString(res.Buffer);


            var parts = msg.Split(',');
            if (parts.Length >= 2 &&
                float.TryParse(parts[0], out float yL) &&
                float.TryParse(parts[1], out float yR))
            {
                float normL = Mathf.Clamp01(1f - yL / 480f);
                float normR = Mathf.Clamp01(1f - yR / 480f);

                LeftY = normL * 2f - 1f;
                RightY = normR * 2f - 1f;
            }
        }
    }

    void OnApplicationQuit()
    {
        cts?.Cancel();
        client?.Close();
    }

    void OnDestroy() => OnApplicationQuit();
}
