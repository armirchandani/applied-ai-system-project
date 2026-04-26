
import sys, os
sys.path.insert(0, 'src')
from recommender import load_songs, recommend_songs
from evaluator import score_results, check_consistency

PROFILES = [
    ("Happy Pop Fan", {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False, "favorite_mood_tag": "uplifting", "preferred_decade": 2020}),
    ("Chill Lofi",    {"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.3, "likes_acoustic": True, "favorite_mood_tag": "dreamy", "preferred_decade": 2020}),
    ("Intense Rock",  {"favorite_genre": "metal", "favorite_mood": "intense", "target_energy": 0.9, "likes_acoustic": False, "favorite_mood_tag": "aggressive", "preferred_decade": 2010}),
    ("Conflicted Listener", {"favorite_genre": "jazz", "favorite_mood": "happy", "target_energy": 0.9, "likes_acoustic": True, "favorite_mood_tag": "nostalgic", "preferred_decade": 2000}),
    ("Genre Ghost",   {"favorite_genre": "country", "favorite_mood": "focused", "target_energy": 0.5, "likes_acoustic": False, "favorite_mood_tag": "gritty", "preferred_decade": 1990}),
]
SEP = "-" * 70

def main():
    songs = load_songs("data/songs.csv")
    print("\n" + "=" * 70)
    print("  VibeFinder 2.0 - Reliability Test Harness")
    print("=" * 70)
    evaluations = []
    for name, prefs in PROFILES:
        results = recommend_songs(prefs, songs, k=5)
        ev = score_results(prefs, results)
        consistency = check_consistency(prefs, songs, runs=3)
        status = "PASS" if ev["passed"] else "FAIL"
        print(f"\n{SEP}\n  [{status}]  {name}\n{SEP}")
        for i, (song, score, _) in enumerate(results, 1):
            print(f"  {i}. {song['title']:<24} score={score:.2f}")
        print(f"\n  Confidence : {ev['confidence']:.2f}")
        print(f"  Guardrails : {', '.join(ev['guardrails']) if ev['guardrails'] else 'none'}")
        print(f"  Consistent : {consistency['note']}")
        print(f"  Verdict    : {ev['verdict']}")
        evaluations.append((name, ev))
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    passed = sum(1 for _, e in evaluations if e["passed"])
    avg_conf = sum(e["confidence"] for _, e in evaluations) / len(evaluations)
    for name, e in evaluations:
        status = "PASS" if e["passed"] else "FAIL"
        guards = ", ".join(e["guardrails"]) if e["guardrails"] else "none"
        print(f"  [{status}]  {name:<25} confidence={e['confidence']:.2f}  guardrails={guards}")
    print(f"\n  Result: {passed}/{len(evaluations)} passed | Avg confidence: {avg_conf:.2f}\n")

if __name__ == "__main__":
    main()
