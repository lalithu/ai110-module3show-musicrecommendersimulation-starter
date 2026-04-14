"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Example user profile
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
        "target_tempo": 120,
        "target_valence": 0.85
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\nTop recommendations:\n")
    for rec in recommendations:
        song = rec["song"]
        score = rec["score"]
        reasons = rec["reasons"]
        print(f"{song['title']} by {song['artist']} - Score: {score:.2f}")
        print("Reasons:")
        for reason in reasons:
            print(f"  - {reason}")
        print()

if __name__ == "__main__":
    main()
