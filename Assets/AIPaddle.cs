using UnityEngine;

[RequireComponent(typeof(Rigidbody))]
public class AIPaddle : MonoBehaviour
{
    public BallController ball;
    [SerializeField] float speed = 8f;
    const float LIMIT_Y = 5.5f;

    void FixedUpdate()
    {
        if (ball == null) return;
        float targetY = Mathf.Clamp(ball.transform.position.y, -LIMIT_Y, LIMIT_Y);
        float newY = Mathf.MoveTowards(transform.position.y, targetY, speed * Time.fixedDeltaTime);
        transform.position = new Vector3(transform.position.x, newY, transform.position.z);
    }
}
