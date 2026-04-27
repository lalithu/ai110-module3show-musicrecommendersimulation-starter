from src.recommender import Song, UserProfile, Recommender


def _make_songs():
    return [
        Song(id=1, title="Test Pop Track", artist="Test Artist",
             genre="pop", mood="happy", energy=0.8, tempo_bpm=120,
             valence=0.9, danceability=0.8, acousticness=0.2),
        Song(id=2, title="Chill Lofi Loop", artist="Test Artist",
             genre="lofi", mood="chill", energy=0.4, tempo_bpm=80,
             valence=0.6, danceability=0.5, acousticness=0.9),
        Song(id=3, title="Rock Anthem", artist="Test Band",
             genre="rock", mood="intense", energy=0.95, tempo_bpm=150,
             valence=0.45, danceability=0.65, acousticness=0.1),
    ]


def make_small_recommender() -> Recommender:
    return Recommender(_make_songs()[:2])


# ── Original required tests ─────────────────────────────────────────────────

def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# ── Additional tests ─────────────────────────────────────────────────────────

def test_recommend_respects_k():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = Recommender(_make_songs())
    assert len(rec.recommend(user, k=1)) == 1
    assert len(rec.recommend(user, k=3)) == 3


def test_recommend_genre_boost():
    """Genre-matching song should rank first over a slightly better energy match."""
    songs = [
        Song(id=1, title="Pop A", artist="X", genre="pop", mood="happy",
             energy=0.75, tempo_bpm=120, valence=0.8, danceability=0.7, acousticness=0.2),
        Song(id=2, title="Rock B", artist="Y", genre="rock", mood="happy",
             energy=0.80, tempo_bpm=120, valence=0.8, danceability=0.7, acousticness=0.2),
    ]
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = Recommender(songs)
    results = rec.recommend(user, k=2)
    assert results[0].genre == "pop"


def test_explain_contains_title():
    user = UserProfile(favorite_genre="pop", favorite_mood="happy",
                       target_energy=0.8, likes_acoustic=False)
    rec = make_small_recommender()
    song = rec.songs[0]
    explanation = rec.explain_recommendation(user, song)
    assert song.title in explanation


def test_explain_no_match_still_returns_string():
    """When nothing matches, explanation should still be non-empty."""
    user = UserProfile(favorite_genre="jazz", favorite_mood="relaxed",
                       target_energy=0.5, likes_acoustic=False)
    rec = make_small_recommender()
    explanation = rec.explain_recommendation(user, rec.songs[0])
    assert isinstance(explanation, str)
    assert len(explanation) > 0


def test_acoustic_preference_affects_ranking():
    songs = [
        Song(id=1, title="Acoustic Folk", artist="A", genre="folk", mood="calm",
             energy=0.4, tempo_bpm=90, valence=0.6, danceability=0.4, acousticness=0.95),
        Song(id=2, title="Electronic Hit", artist="B", genre="electronic", mood="energetic",
             energy=0.9, tempo_bpm=130, valence=0.7, danceability=0.9, acousticness=0.05),
    ]
    user_acoustic = UserProfile(favorite_genre="folk", favorite_mood="calm",
                                target_energy=0.4, likes_acoustic=True)
    user_digital = UserProfile(favorite_genre="folk", favorite_mood="calm",
                               target_energy=0.4, likes_acoustic=False)
    rec = Recommender(songs)
    assert rec.recommend(user_acoustic, k=1)[0].title == "Acoustic Folk"
    assert rec.recommend(user_digital, k=1)[0].title == "Acoustic Folk"  # genre+mood still dominate
