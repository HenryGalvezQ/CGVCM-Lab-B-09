using UnityEngine;
using TMPro;

public class GameManager : MonoBehaviour
{
    public static GameManager Instance;
    [SerializeField] BallController ball;
    [SerializeField] TMP_Text scoreText;
    int leftScore, rightScore;

    void Awake() => Instance = this;

    void Start() => ball.Launch();

    public void Score(bool rightPlayer)
    {
        if (rightPlayer) rightScore++; else leftScore++;
        scoreText.text = $"{leftScore}  –  {rightScore}";
        AudioManager.I.PlayGoal();

        if (leftScore == 10 || rightScore == 10)
        {
            scoreText.text = leftScore == 10 ? "¡Gana Jugador 1!" : "¡Gana Jugador 2!";
            Invoke(nameof(ResetMatch), 3f);
        }
        else
        {
            ball.Launch();
        }
    }

    void ResetMatch()
    {
        leftScore = rightScore = 0;
        scoreText.text = "0  –  0";
        ball.Launch();
    }
}
