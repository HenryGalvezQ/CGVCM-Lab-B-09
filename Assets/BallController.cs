using UnityEngine;

[RequireComponent(typeof(Rigidbody), typeof(SphereCollider))]
public class BallController : MonoBehaviour
{
    [Header("Velocidad constante")]
    [SerializeField] float startSpeed = 12f;

    Rigidbody rb;
    float radius;               // radio real (incluye escala)
    const float EPS = 0.003f;    // pequeño margen de seguridad

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
        radius = GetComponent<SphereCollider>().radius * transform.localScale.x;
    }

    public void Launch()
    {
        transform.position = Vector3.zero;
        int sx = Random.value < .5f ? -1 : 1;
        int sy = Random.value < .5f ? -1 : 1;
        rb.velocity = new Vector3(sx, sy, 0).normalized * startSpeed;
    }

    void OnCollisionEnter(Collision col)
    {
        // 1. Datos del primer contacto
        ContactPoint c = col.contacts[0];
        Vector3 n = c.normal;          // normal ya está normalizada
        if (col.collider.CompareTag("Paddle"))
            AudioManager.I.PlayPaddle();
        // 2. Coloca el centro justo fuera del muro
        Vector3 newPos = c.point + n * (radius + EPS);
        rb.position = newPos;            // evita micro-rebotes

        // 3. Refleja velocidad y fuerza ángulo de 45°
        Vector3 vRef = Vector3.Reflect(rb.velocity.normalized, n);
        int sx = vRef.x >= 0 ? 1 : -1;
        int sy = vRef.y >= 0 ? 1 : -1;

        rb.velocity = new Vector3(sx, sy, 0).normalized * startSpeed;
    }

    void OnTriggerEnter(Collider col)
    {
        if (col.CompareTag("GoalLeft"))
            GameManager.Instance.Score(rightPlayer: true);
        else if (col.CompareTag("GoalRight"))
            GameManager.Instance.Score(rightPlayer: false);
    }

    void FixedUpdate()
    {
        rb.velocity = rb.velocity.normalized * startSpeed;
    }
}
