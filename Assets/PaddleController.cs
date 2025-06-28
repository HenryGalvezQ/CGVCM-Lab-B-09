using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class PaddleController : MonoBehaviour
{
    public bool isLeft;          // asócialo desde el Inspector
    [SerializeField] float speed = 25f;
    const float LIMIT_Y = 5.5f;

    void FixedUpdate()
    {
        float input = isLeft
            ? UDPReceiver.Instance.LeftY   // valor normalizado –1..1
            : UDPReceiver.Instance.RightY;

        transform.position = new Vector3(
            transform.position.x,
            input * LIMIT_Y,
            transform.position.z);
    }
}
