
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

def score_results(user_prefs, results):
    if not results:
        return {"confidence": 0.0, "passed": False, "breakdown": {}, "guardrails": ["no_results"], "verdict": "No results."}
    target_genre  = user_prefs.get("favorite_genre", "").lower()
    target_mood   = user_prefs.get("favorite_mood", "").lower()
    target_energy = user_prefs.get("target_energy", 0.5)
    top_song = results[0][0]
    top_five = [r[0] for r in results[:5]]
    genre_match  = 1.0 if top_song["genre"].lower() == target_genre else 0.0
    mood_match   = 1.0 if top_song["mood"].lower()  == target_mood  else 0.0
    energy_close = 1.0 if abs(top_song["energy"] - target_energy) <= 0.2 else 0.0
    overlap_count = sum(1 for s in top_five if s["genre"].lower() == target_genre or s["mood"].lower() == target_mood)
    overlap_bonus = 1.0 if overlap_count >= 3 else (0.5 if overlap_count >= 1 else 0.0)
    breakdown = {"genre_match_top1": round(genre_match*0.40,3), "mood_match_top1": round(mood_match*0.25,3), "energy_close_top1": round(energy_close*0.20,3), "overlap_top5": round(overlap_bonus*0.15,3)}
    confidence = round(sum(breakdown.values()), 3)
    guardrails = []
    if sum(1 for s in top_five if s["genre"].lower() == target_genre) == 0:
        guardrails.append("genre_gap")
    if sum(1 for s in top_five if s["mood"].lower() == target_mood) == 0:
        guardrails.append("mood_gap")
    if abs(sum(s["energy"] for s in top_five)/len(top_five) - target_energy) > 0.3:
        guardrails.append("energy_drift")
    if len(set(s["genre"].lower() for s in top_five)) == 1:
        guardrails.append("low_diversity")
    passed = confidence >= 0.65
    verdict = f"Good match. Top: {top_song['title']} — confidence {confidence:.2f}." if passed else f"Weak match ({confidence:.2f}). Issues: {', '.join(guardrails) if guardrails else 'weak signal'}."
    return {"confidence": confidence, "passed": passed, "breakdown": breakdown, "guardrails": guardrails, "verdict": verdict}

def check_consistency(user_prefs, songs, runs=3):
    from recommender import recommend_songs
    sets = [tuple(r[0]["title"] for r in recommend_songs(user_prefs, songs, k=5)) for _ in range(runs)]
    all_same = all(r == sets[0] for r in sets)
    return {"consistent": all_same, "runs": runs, "all_same": all_same, "note": "All runs identical — recommender is deterministic." if all_same else "WARNING: results differed."}
