"""
Evaluation Harness for Music Recommender Simulation.

Runs predefined test scenarios and prints a pass/fail summary with
confidence scores. Acts as the stretch-feature reliability component.

Usage:
  python tests/test_harness.py
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.recommender import load_songs, recommend_songs

SONGS = load_songs("data/songs.csv")

TEST_CASES = [
    {
        "name": "Pop Happy High-Energy",
        "prefs": {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.85,
            "target_tempo": 120,
            "target_valence": 0.80,
        },
        "expected_top_genres": ["pop", "indie pop"],
        "min_top_score": 3.5,
    },
    {
        "name": "LoFi Chill Study Session",
        "prefs": {
            "favorite_genre": "lofi",
            "favorite_mood": "chill",
            "target_energy": 0.40,
            "target_tempo": 78,
            "target_valence": 0.60,
        },
        "expected_top_genres": ["lofi"],
        "min_top_score": 4.0,
    },
    {
        "name": "Rock Intense Workout",
        "prefs": {
            "favorite_genre": "rock",
            "favorite_mood": "intense",
            "target_energy": 0.90,
            "target_tempo": 150,
            "target_valence": 0.50,
        },
        "expected_top_genres": ["rock", "electronic"],
        "min_top_score": 3.5,
    },
    {
        "name": "Ambient Chill Relaxation",
        "prefs": {
            "favorite_genre": "ambient",
            "favorite_mood": "chill",
            "target_energy": 0.30,
            "target_tempo": 65,
            "target_valence": 0.65,
        },
        "expected_top_genres": ["ambient", "lofi", "classical"],
        "min_top_score": 3.5,
    },
    {
        "name": "Electronic Energetic Dance",
        "prefs": {
            "favorite_genre": "electronic",
            "favorite_mood": "energetic",
            "target_energy": 0.88,
            "target_tempo": 128,
            "target_valence": 0.75,
        },
        "expected_top_genres": ["electronic", "pop"],
        "min_top_score": 3.0,
    },
    {
        "name": "Jazz Relaxed Evening",
        "prefs": {
            "favorite_genre": "jazz",
            "favorite_mood": "relaxed",
            "target_energy": 0.37,
            "target_tempo": 90,
            "target_valence": 0.71,
        },
        "expected_top_genres": ["jazz", "folk", "lofi"],
        "min_top_score": 3.5,
    },
]


def _compute_confidence(scores: list) -> float:
    if len(scores) < 2:
        return 1.0
    top = scores[0]
    spread = top - scores[-1]
    if spread < 0.01:
        return 0.5
    mean = sum(scores) / len(scores)
    return round(min(1.0, (top - mean) / (spread + 1e-9)), 2)


def run_case(case: dict) -> dict:
    recs = recommend_songs(case["prefs"], SONGS, k=5)
    top = recs[0]
    failures = []

    if top["song"]["genre"] not in case["expected_top_genres"]:
        failures.append(
            f"Top genre '{top['song']['genre']}' not in expected {case['expected_top_genres']}"
        )

    if top["score"] < case["min_top_score"]:
        failures.append(
            f"Top score {top['score']:.2f} < required minimum {case['min_top_score']}"
        )

    scores = [r["score"] for r in recs]
    return {
        "name": case["name"],
        "passed": len(failures) == 0,
        "failures": failures,
        "top_song": f"{top['song']['title']} by {top['song']['artist']}",
        "top_score": top["score"],
        "confidence": _compute_confidence(scores),
    }


def main() -> int:
    print("=" * 62)
    print("  Music Recommender — Evaluation Harness")
    print("=" * 62)

    results = [run_case(c) for c in TEST_CASES]
    passed = sum(1 for r in results if r["passed"])

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        marker = "✓" if r["passed"] else "✗"
        print(f"\n  [{status}] {r['name']}")
        print(f"    {marker} Top pick : {r['top_song']}")
        print(f"    {marker} Score    : {r['top_score']:.2f}  |  Confidence: {r['confidence']:.2f}")
        for f in r["failures"]:
            print(f"    ✗ {f}")

    avg_conf = sum(r["confidence"] for r in results) / len(results)
    print("\n" + "=" * 62)
    print(f"  Results  : {passed}/{len(results)} tests passed")
    print(f"  Avg conf : {avg_conf:.2f}")
    print("=" * 62)

    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
