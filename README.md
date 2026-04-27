# 🎵 Music Recommender — Applied AI System

> **Base project:** Module 3 — Music Recommender Simulation  
> This final project extends the original rule-based music recommender into a full applied AI system featuring a Claude-powered agentic workflow, confidence scoring, structured logging, and an automated evaluation harness.

---

## Summary

The original Module 3 project built a rule-based music recommender that scores songs against a user's structured preferences (genre, mood, energy, tempo, valence) using weighted heuristics. It demonstrated how data-driven scoring rules could surface relevant music without any machine learning.

This extended version adds a **3-step Claude agentic pipeline**: the user types a natural language request ("I want chill lofi for studying"), Claude parses it into structured preferences, the rule engine scores the song catalog, and Claude generates personalized explanations for each recommendation. The result is a system that accepts human language, reasons about it, and produces explainable outputs — all testable and logged.

---

## Architecture Overview

```
User Natural Language
        │
        ▼
  ┌─────────────────────────────────────────┐
  │        AI Agentic Pipeline              │
  │                                         │
  │  Step 1: Claude (Haiku)                 │
  │    Parse intent → structured JSON prefs │
  │          │                              │
  │          ▼                              │
  │  Step 2: Rule Engine (score_song)       │
  │    Score all songs in catalog           │
  │          │                              │
  │          ▼                              │
  │  Step 3: Claude (Haiku)                 │
  │    Generate personalized explanations   │
  │          │                              │
  │          ▼                              │
  │  Confidence Scorer                      │
  └─────────────────────────────────────────┘
        │
        ▼
  Ranked Songs + AI Explanations

  ─── Also available ───────────────────────
  Rule-Based Pipeline (no API key required)
  → score_song() → top-K sort → reasons
```

See [assets/architecture.md](assets/architecture.md) for the full Mermaid diagram source.

**Components:**

| File | Role |
|------|------|
| `src/recommender.py` | `Song`, `UserProfile`, `Recommender` classes + `score_song`, `recommend_songs` |
| `src/ai_recommender.py` | 3-step Claude agentic pipeline |
| `src/main.py` | CLI entry point (`--mode rule\|ai`, `--query`, `--k`) |
| `src/logger.py` | Structured logging to file + console |
| `tests/test_recommender.py` | 7 pytest unit tests |
| `tests/test_harness.py` | 6-scenario evaluation harness with confidence scoring |
| `data/songs.csv` | 15-song catalog with audio features |

---

## Setup Instructions

### 1. Clone and enter the project
```bash
git clone <your-repo-url>
cd music-recommender-applied-ai
```

### 2. Create a virtual environment
```bash
python -m venv .venv
source .venv/bin/activate        # Mac / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. (AI mode only) Add your Anthropic API key
```bash
cp .env.example .env
# Edit .env and paste your key:  ANTHROPIC_API_KEY=sk-ant-...
```

---

## Running the System

### Rule-based mode (no API key required)
```bash
python -m src.main
```

### AI agentic mode
```bash
python -m src.main --mode ai --query "chill lofi for late-night studying"
python -m src.main --mode ai --query "upbeat pop for a morning run" --k 3
python -m src.main --mode ai --query "mellow jazz for a quiet evening"
```

### Run unit tests
```bash
pytest tests/test_recommender.py -v
```

### Run evaluation harness
```bash
python tests/test_harness.py
```

---

## Sample Interactions

### Example 1 — Rule-Based Mode

```
[MODE: Rule-Based Recommender]
  genre=pop  mood=happy  energy=0.8  tempo=120

Top 5 Recommendations:

  Sunrise City by Neon Echo  —  Score: 5.96
    • Genre match (+2.0)
    • Mood match (+1.0)
    • Energy similarity (+0.98)
    • Tempo similarity (+0.82)
    • Valence similarity (+0.99)

  Rooftop Lights by Indigo Parade  —  Score: 4.90
    • Energy similarity (+0.94)
    • Tempo similarity (+0.96)
    ...
```

### Example 2 — AI Agentic Mode (studying)

```
[MODE: AI Agentic Recommender — 3-Step Pipeline]
  Your request: "chill lofi for late-night studying"

━━━ Step 1: Parsed Preferences (Claude) ━━━
  favorite_genre: lofi
  favorite_mood: chill
  target_energy: 0.38
  target_tempo: 75.0
  target_valence: 0.58

━━━ Step 2: Scored Recommendations (Rule Engine) ━━━
  1. Midnight Coding by LoRoom  (score: 4.96)
  2. Library Rain by Paper Lanterns  (score: 4.87)
  3. Focus Flow by LoRoom  (score: 4.72)
  4. Spacewalk Thoughts by Orbit Bloom  (score: 3.44)
  5. Coffee Shop Stories by Slow Stereo  (score: 3.28)

━━━ Step 3: AI Explanations (Claude) ━━━
  1. Midnight Coding perfectly captures that late-night focus energy with its low-tempo, 
     chill vibe—exactly what you need to stay in the zone.
  2. Library Rain's soft, acoustic texture makes it ideal background music for studying 
     without distraction.
  ...

  Confidence Score: 0.82
```

### Example 3 — AI Agentic Mode (workout)

```
[MODE: AI Agentic Recommender — 3-Step Pipeline]
  Your request: "high energy rock for a workout"

━━━ Step 1: Parsed Preferences (Claude) ━━━
  favorite_genre: rock
  favorite_mood: intense
  target_energy: 0.92
  target_tempo: 148.0
  target_valence: 0.5

━━━ Step 2: Scored Recommendations (Rule Engine) ━━━
  1. Storm Runner by Voltline  (score: 5.84)
  2. Gym Hero by Max Pulse  (score: 4.07)
  3. Electric Pulse by Neon Echo  (score: 3.96)
  ...

  Confidence Score: 0.89
```

---

## Design Decisions

**Why Claude Haiku for both parsing and explanation?**  
Haiku is fast and cheap enough for interactive use. The parsing task (structured JSON extraction) doesn't need a larger model, and explanations benefit from being snappy rather than elaborate.

**Why keep the rule-based engine as Step 2 instead of having Claude rank songs directly?**  
Determinism and transparency. The scoring weights (genre +2, mood +1, etc.) are auditable and consistent. Claude handles language understanding; the rule engine handles ranking. This separation makes each component independently testable.

**Why a confidence score?**  
If all songs score similarly, the top result isn't meaningfully better than the others — that's a signal the catalog doesn't match the user's taste. Confidence surfaces this uncertainty rather than silently returning results.

**Graceful fallback:**  
If `ANTHROPIC_API_KEY` is missing, the system falls back to rule-based mode with a clear error message rather than crashing.

---

## Testing Summary

**Unit tests (`pytest tests/test_recommender.py`): 7/7 passing**

| Test | Result |
|------|--------|
| `test_recommend_returns_songs_sorted_by_score` | PASS |
| `test_explain_recommendation_returns_non_empty_string` | PASS |
| `test_recommend_respects_k` | PASS |
| `test_recommend_genre_boost` | PASS |
| `test_explain_contains_title` | PASS |
| `test_explain_no_match_still_returns_string` | PASS |
| `test_acoustic_preference_affects_ranking` | PASS |

**Evaluation harness (`python tests/test_harness.py`): 6/6 passing**

Average confidence score: **0.64**. The system showed high confidence (0.71–0.74) for rock, electronic, and jazz — genres with one very strong match. Confidence was lower (0.41–0.57) for lofi and pop where many catalog songs score similarly, which correctly signals that the catalog is dense in those styles rather than pointing to a clear winner.

The confidence metric revealed a real insight: low confidence doesn't mean a bad recommendation, it means the top result isn't dramatically better than runner-ups — useful information for the user.

---

## Reflection & Ethics

**Limitations:**
- The catalog has only 15 songs, so genre diversity is thin — "ambient" returns non-ambient fallbacks.
- Scoring weights are hand-tuned (genre +2, mood +1). A real system would learn these from click data, which introduces its own feedback-loop bias.
- The system has no memory of past interactions; every request starts cold.

**Potential misuse:**
- If deployed at scale, the genre/mood weighting could create filter bubbles — users only ever hear the same slice of music.
- Claude parsing could be manipulated with adversarial inputs to extract non-music preferences; input should always be validated.

**Surprises during testing:**
- Claude's intent parsing was robust to vague queries ("something chill") but occasionally mapped "energetic" to "electronic" rather than the intended genre, leading to unexpected but not unreasonable results.
- Confidence scores were more informative than raw scores — a top score of 4.0 could mean "great match" or "best of a poor catalog," and confidence distinguished those cases.

**AI Collaboration:**
- **Helpful:** Claude suggested separating intent-parsing from explanation-generation into two distinct API calls, which improved both accuracy and testability.
- **Flawed:** An early suggestion to have Claude directly rank songs via a single prompt produced inconsistent orderings across runs — the deterministic rule engine proved more reliable for the ranking step.

---

## Video Walkthrough

> 🎬 [(https://www.youtube.com/watch?v=5adsVe8XNk)]

---

## Repository Structure

```
.
├── assets/
│   └── architecture.md        # Mermaid diagram source
├── data/
│   └── songs.csv              # 15-song catalog
├── src/
│   ├── ai_recommender.py      # Claude agentic pipeline
│   ├── logger.py              # Structured logging
│   ├── main.py                # CLI entry point
│   └── recommender.py         # Core scoring logic + OOP classes
├── tests/
│   ├── test_harness.py        # Evaluation harness (stretch feature)
│   └── test_recommender.py    # Unit tests
├── .env.example               # API key template
├── model_card.md
├── README.md
└── requirements.txt
```
