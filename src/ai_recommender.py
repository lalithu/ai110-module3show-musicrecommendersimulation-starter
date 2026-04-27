"""
AI Agentic Recommendation Pipeline.

Three observable steps:
  Step 1 — Claude parses natural language into structured preferences
  Step 2 — Rule-based engine scores the song catalog (retrieval)
  Step 3 — Claude generates personalized explanations for top results
"""

import os
import json
import logging

logger = logging.getLogger("music_recommender")


def _get_songs_context(songs: list) -> str:
    lines = ["Available songs in catalog:"]
    for s in songs:
        lines.append(
            f'  - "{s["title"]}" by {s["artist"]} | '
            f'genre={s["genre"]} mood={s["mood"]} '
            f'energy={s["energy"]} tempo={s["tempo_bpm"]} valence={s["valence"]}'
        )
    return "\n".join(lines)


def _parse_user_intent(client, query: str) -> dict:
    """Step 1: Claude extracts structured preferences from natural language."""
    logger.info("[Agent Step 1] Parsing intent: %r", query)
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=(
            "You are a music preference parser. Extract structured listening preferences "
            "from the user's natural language request.\n"
            "Available genres: pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, "
            "electronic, reggae, hip hop, classical\n"
            "Available moods: happy, chill, intense, relaxed, focused, moody, calm, energetic, peaceful\n"
            "Return ONLY valid JSON with exactly these keys:\n"
            "  favorite_genre (string), favorite_mood (string),\n"
            "  target_energy (float 0.0-1.0), target_tempo (float 60-160), target_valence (float 0.0-1.0)"
        ),
        messages=[{"role": "user", "content": f"User request: {query}\n\nReturn JSON only:"}],
    )
    raw = response.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    prefs = json.loads(raw.strip())
    logger.info("[Agent Step 1] Parsed: %s", prefs)
    return prefs


def _generate_explanations(client, query: str, recommendations: list) -> str:
    """Step 3: Claude writes personalized explanations for each recommendation."""
    logger.info("[Agent Step 3] Generating AI explanations")
    songs_text = "\n".join(
        f'{i + 1}. "{r["song"]["title"]}" by {r["song"]["artist"]} '
        f"(score: {r['score']:.2f}, top factor: {r['reasons'][0]})"
        for i, r in enumerate(recommendations)
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=700,
        system=(
            "You are a friendly music recommendation assistant. "
            "Write a brief, enthusiastic 1–2 sentence explanation for why each song suits the user's request. "
            "Be specific about the musical qualities that make it a good fit. "
            "Number each explanation to match the list."
        ),
        messages=[{
            "role": "user",
            "content": f'User wanted: "{query}"\n\nTop recommendations:\n{songs_text}\n\nExplain each:',
        }],
    )
    explanation = response.content[0].text.strip()
    logger.info("[Agent Step 3] Explanations generated.")
    return explanation


def _compute_confidence(scores: list) -> float:
    """Confidence = how much the top score stands out from the rest."""
    if len(scores) < 2:
        return 1.0
    top = scores[0]
    spread = top - scores[-1]
    if spread < 0.01:
        return 0.5
    mean = sum(scores) / len(scores)
    return round(min(1.0, (top - mean) / (spread + 1e-9)), 2)


def ai_recommend(query: str, songs: list, k: int = 5) -> dict:
    """
    Full agentic recommendation pipeline.

    Returns a dict with:
      query, parsed_preferences, recommendations, ai_explanations, confidence
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed. Run: pip install anthropic")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY is not set. "
            "Add it to your .env file or export it in your shell."
        )

    client = Anthropic(api_key=api_key)

    # Step 1: Parse intent
    prefs = _parse_user_intent(client, query)

    # Step 2: Score songs using rule-based engine
    logger.info("[Agent Step 2] Scoring %d songs", len(songs))
    from src.recommender import recommend_songs
    recommendations = recommend_songs(prefs, songs, k=k)
    logger.info(
        "[Agent Step 2] Top: %s (score %.2f)",
        recommendations[0]["song"]["title"],
        recommendations[0]["score"],
    )

    # Step 3: Generate explanations
    ai_explanations = _generate_explanations(client, query, recommendations)

    scores = [r["score"] for r in recommendations]
    confidence = _compute_confidence(scores)

    return {
        "query": query,
        "parsed_preferences": prefs,
        "recommendations": recommendations,
        "ai_explanations": ai_explanations,
        "confidence": confidence,
    }
