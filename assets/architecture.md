# System Architecture Diagram (Mermaid source)

Export this via https://mermaid.live → Save as PNG → name it `architecture.png`

```mermaid
flowchart TD
    A([User]) -->|natural language query| B[main.py\n--mode ai]
    A -->|structured prefs| C[main.py\n--mode rule]

    subgraph AI["AI Agentic Pipeline (ai_recommender.py)"]
        B --> D["Step 1 — Claude API\nParse intent → structured JSON prefs"]
        D --> E["Step 2 — Rule Engine\nscore_song() scores every song in catalog"]
        E --> F["Step 3 — Claude API\nGenerate personalized explanations"]
        F --> G[Confidence Scorer\nHow strongly top result stands out]
    end

    subgraph Rule["Rule-Based Pipeline (recommender.py)"]
        C --> H[score_song()\nGenre +2 · Mood +1 · Energy/Tempo/Valence similarity]
        H --> I[Top-K Sort]
    end

    subgraph Data["Data Layer"]
        J[(songs.csv\n15 songs)] --> E
        J --> H
    end

    subgraph Reliability["Reliability & Testing"]
        K[tests/test_recommender.py\n7 pytest unit tests]
        L[tests/test_harness.py\n6 scenario evaluations\npass/fail + confidence]
    end

    G --> M([Ranked Recommendations\n+ AI Explanations])
    I --> M

    subgraph Observability
        N[logger.py\nInfo to recommender.log\nWarnings to console]
    end

    B --> N
    C --> N
```
