"""
Music Recommender Simulation — Extended with AI Agentic Workflow.

Usage:
  Rule-based mode (default):
    python -m src.main

  AI agentic mode:
    python -m src.main --mode ai --query "upbeat pop for a morning run"

  Choose number of results:
    python -m src.main --k 3
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.recommender import load_songs, recommend_songs
from src.logger import setup_logger

logger = setup_logger()


def _load_dotenv():
    dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
    if os.path.exists(dotenv_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path)
        except ImportError:
            pass


def _print_rule_results(recommendations: list) -> None:
    for rec in recommendations:
        song = rec["song"]
        print(f"  {song['title']} by {song['artist']}  —  Score: {rec['score']:.2f}")
        for reason in rec["reasons"]:
            print(f"    • {reason}")
        print()


def run_rule_based(songs: list, user_prefs: dict, k: int = 5) -> None:
    logger.info("Rule-based mode | genre=%s mood=%s energy=%s",
                user_prefs["favorite_genre"], user_prefs["favorite_mood"], user_prefs["target_energy"])
    print("\n[MODE: Rule-Based Recommender]")
    print(f"  genre={user_prefs['favorite_genre']}  mood={user_prefs['favorite_mood']}  "
          f"energy={user_prefs['target_energy']}  tempo={user_prefs['target_tempo']}\n")
    recs = recommend_songs(user_prefs, songs, k=k)
    print(f"Top {k} Recommendations:\n")
    _print_rule_results(recs)
    logger.info("Top pick: %s (score %.2f)", recs[0]["song"]["title"], recs[0]["score"])


def run_ai_mode(songs: list, query: str, k: int = 5) -> None:
    _load_dotenv()
    logger.info("AI agentic mode | query=%r", query)

    print("\n[MODE: AI Agentic Recommender — 3-Step Pipeline]")
    print(f'  Your request: "{query}"\n')

    try:
        from src.ai_recommender import ai_recommend
        result = ai_recommend(query, songs, k=k)

        print("━━━ Step 1: Parsed Preferences (Claude) ━━━")
        for key, val in result["parsed_preferences"].items():
            print(f"  {key}: {val}")

        print("\n━━━ Step 2: Scored Recommendations (Rule Engine) ━━━")
        for i, rec in enumerate(result["recommendations"], 1):
            song = rec["song"]
            print(f"  {i}. {song['title']} by {song['artist']}  (score: {rec['score']:.2f})")

        print("\n━━━ Step 3: AI Explanations (Claude) ━━━")
        print(result["ai_explanations"])

        print(f"\n  Confidence Score: {result['confidence']:.2f}")
        logger.info("AI mode complete | confidence=%.2f", result["confidence"])

    except (ValueError, RuntimeError) as e:
        logger.error("AI mode failed: %s", e)
        print(f"\n  [Error] {e}")
        print("  Falling back to rule-based mode...\n")
        fallback = {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.7,
            "target_tempo": 110,
            "target_valence": 0.7,
        }
        run_rule_based(songs, fallback, k=k)


def main() -> None:
    parser = argparse.ArgumentParser(description="Music Recommender Simulation")
    parser.add_argument(
        "--mode", choices=["rule", "ai"], default="rule",
        help="Recommendation mode: 'rule' (default) or 'ai' (Claude-powered)",
    )
    parser.add_argument(
        "--query", type=str, default=None,
        help="Natural language request for AI mode (e.g. 'chill lofi for studying')",
    )
    parser.add_argument(
        "--k", type=int, default=5,
        help="Number of recommendations to return (default: 5)",
    )
    args = parser.parse_args()

    songs = load_songs("data/songs.csv")
    logger.info("Loaded %d songs from catalog", len(songs))

    if args.mode == "ai":
        query = args.query or "I want something upbeat and energetic for working out"
        run_ai_mode(songs, query, k=args.k)
    else:
        user_prefs = {
            "favorite_genre": "pop",
            "favorite_mood": "happy",
            "target_energy": 0.8,
            "target_tempo": 120,
            "target_valence": 0.85,
        }
        run_rule_based(songs, user_prefs, k=args.k)


if __name__ == "__main__":
    main()
