# 🎧 Model Card — Music Recommender Applied AI System

## 1. Model Name

**VibeFinder 2.0** — Extended from Module 3's rule-based recommender into a Claude-powered agentic system.

---

## 2. Intended Use

VibeFinder 2.0 is an educational demonstration of applied AI system design. It suggests songs from a small 15-track catalog based on either structured preferences or a natural language description of what the user wants to hear. The system is intended for classroom exploration and portfolio demonstration — not for production deployment.

**Two modes:**
- **Rule-based:** accepts explicit preference fields (genre, mood, energy, tempo, valence)
- **AI agentic:** accepts natural language, routes through a 3-step Claude pipeline

---

## 3. How the Model Works

### Rule-Based Core (used in both modes)
Each song in the catalog is assigned a numeric score by comparing it to the user's preferences. The score adds points in five categories:

- **Genre match** — the biggest boost (+2.0 points) if the song's genre exactly matches the user's favorite
- **Mood match** — a moderate boost (+1.0 point) for an exact mood match
- **Energy closeness** — up to +1.0 point depending on how close the song's energy level is to the user's target
- **Tempo closeness** — up to +1.0 point based on how close the tempo is
- **Valence closeness** — up to +1.0 point based on positivity/mood alignment

Songs are then ranked highest to lowest and the top K are returned.

### AI Agentic Extension (3 steps)
1. **Claude parses language** — The user's natural language description is sent to Claude, which extracts the five preference fields as structured data.
2. **Rule engine scores songs** — The extracted preferences are fed into the exact same scoring function as rule-based mode, ensuring deterministic and auditable ranking.
3. **Claude explains results** — The top-K songs and their scores are sent back to Claude, which writes a brief, personalized explanation for why each song fits the user's request.

A **confidence score** measures how much the top result stands out from the rest. High confidence (near 1.0) means the best match is clearly better than the others; low confidence (near 0.5) signals the catalog may not have a great fit.

---

## 4. Data

The catalog (`data/songs.csv`) contains **15 songs** across 11 genres: pop, lofi, rock, ambient, jazz, synthwave, indie pop, folk, electronic, reggae, hip hop, and classical.

Each song has these numeric features alongside title/artist/genre/mood:

| Feature | Range | Meaning |
|---------|-------|---------|
| energy | 0.0–1.0 | Overall intensity |
| tempo_bpm | 60–160 | Beats per minute |
| valence | 0.0–1.0 | Musical positivity |
| danceability | 0.0–1.0 | Rhythmic drivability |
| acousticness | 0.0–1.0 | Acoustic vs. electronic |

The data was hand-crafted for this project to represent diverse listening contexts (studying, working out, relaxing, commuting). Because it was designed by one person, it likely reflects biases in what genres and moods that person considers worth including.

---

## 5. Strengths

- Works well for users whose taste aligns with the catalog's stronger genres (pop, lofi, rock have the most songs).
- The scoring logic is fully transparent — every recommendation comes with point-by-point reasons.
- Genre and mood matching are given more weight than numeric similarity, which mirrors how humans actually talk about music taste.
- The confidence score correctly flags low-certainty situations rather than confidently returning poor matches.
- Graceful fallback: if the Claude API is unavailable, the system reverts to rule-based mode without crashing.

---

## 6. Limitations and Bias

- **Catalog size:** 15 songs is far too small for real use. Several genres have only one song (ambient, reggae, hip hop, classical), so any query for those genres has at most one "correct" answer.
- **Genre bias:** Because genre match carries the largest weight (+2.0), two identical songs from different genres would rank very differently for the same user.
- **No personalization memory:** Every request is treated independently. A real system would learn from listening history.
- **English-only parsing:** Claude's intent parsing works well in English but has not been tested in other languages.
- **Binary genre/mood matching:** A user who likes "indie pop" won't get credit for liking "pop" even though they're closely related.
- **Acoustic preference ignored in scoring function:** The rule-based `score_song` function doesn't use `acousticness`, even though `UserProfile.likes_acoustic` exists. This gap exists in the OOP `Recommender` class but not the functional path.

---

## 7. Evaluation

**Unit tests (7/7 passing):**
All seven pytest tests pass, covering correct sorting by score, explanation quality, genre boost behavior, acoustic preference effects, and edge cases with no matching attributes.

**Evaluation harness (6/6 passing):**
Each of six predefined user profiles was tested. The harness checks:
1. That the top recommended song belongs to an expected genre
2. That the top score exceeds a minimum threshold

Average confidence across all six scenarios: **0.73**

**Notable observation:** The jazz scenario achieved the highest confidence (0.85) because one song ("Coffee Shop Stories") was a near-perfect match on all five dimensions. The ambient scenario had the lowest confidence (0.58) because only one ambient song exists in the catalog — the engine ranked it first, but the rest of the top-5 were mismatches.

**AI mode observation:** Claude's parsing was tested with five queries ranging from specific ("lofi chill study session") to vague ("something relaxing"). It correctly extracted genre/mood/energy in all five cases. It occasionally defaulted `target_valence` to 0.5 for ambiguous queries, which is a reasonable neutral choice.

---

## 8. Future Work

- **Expand the catalog** to at least 100–200 songs to make genre and mood matching meaningful.
- **Learn weights from data** — instead of hand-tuned genre +2/mood +1, use listening history to fit weights per user.
- **Add diversity enforcement** — prevent the top-5 from being all the same artist or genre.
- **Streaming playlist mode** — allow the user to say "add more like this" and grow a playlist iteratively.
- **Multi-language support** — test and improve Claude's intent parsing in Spanish, Hindi, and other languages common among music listeners.
- **Close the acousticness gap** — apply the `likes_acoustic` flag in the functional scoring path, not just the OOP Recommender.

---

## 9. Personal Reflection

Building this system made it concrete why transparency matters in recommenders. When I could see the score breakdown ("+2.0 genre match, +0.98 energy") I could immediately understand why a song ranked where it did — and spot when the weights were wrong. Real recommender systems at Spotify or YouTube hide their scoring, which makes bias much harder to detect.

The most surprising finding was how much the confidence score revealed. A top score of 4.0 can mean very different things: it could be a great match, or it could be the "least bad" option in a thin catalog. The confidence metric distinguished those cases, which changed how I thought about evaluation — a model shouldn't just return results, it should communicate how sure it is.

The AI collaboration was genuinely useful for the explanation step: generating a human-sounding reason for each recommendation would have taken many string-formatting rules to do manually. But I learned that Claude's consistency drops when you ask it to both rank AND explain in a single prompt — separating those into two distinct steps (rule engine ranks, Claude explains) produced much better results.

---

## 10. AI Collaboration Notes

*(Required for final project submission)*

**Helpful instance:** Claude suggested structuring the agentic pipeline as three clearly separated steps rather than one monolithic prompt. This improved both the quality of outputs and the testability of each component independently.

**Flawed instance:** An early experiment had Claude directly rank songs by reading the CSV in a single prompt. The rankings were inconsistent across runs (different orderings for the same input), and the model occasionally hallucinated song titles not in the catalog. Switching to the deterministic rule engine for ranking fixed both problems.

**Overall:** AI was most valuable at the language boundary (parsing input, generating explanation) and least reliable for tasks requiring numerical consistency (scoring, ranking). The best design separates these concerns.
