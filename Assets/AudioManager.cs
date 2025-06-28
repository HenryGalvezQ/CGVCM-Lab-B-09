using UnityEngine;

public class AudioManager : MonoBehaviour
{
    public static AudioManager I;          // acceso global sencillo
    public AudioSource paddleSource;
    public AudioSource goalSource;
    public AudioClip paddleHitClip;
    public AudioClip goalScoreClip;

    void Awake() => I = this;

    public void PlayPaddle() => paddleSource.PlayOneShot(paddleHitClip);
    public void PlayGoal() => goalSource.PlayOneShot(goalScoreClip);
}
