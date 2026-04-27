from typing import List
from dataclasses import dataclass


@dataclass
class Song:
    """Represents a song and its attributes."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """Represents a user's taste preferences."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """OOP implementation of the recommendation logic."""

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score(self, user: UserProfile, song: Song) -> float:
        s = 0.0
        if song.genre == user.favorite_genre:
            s += 2.0
        if song.mood == user.favorite_mood:
            s += 1.0
        s += max(0.0, 1.0 - abs(song.energy - user.target_energy))
        if user.likes_acoustic:
            s += song.acousticness * 0.5
        else:
            s += (1.0 - song.acousticness) * 0.5
        return s

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        return sorted(self.songs, key=lambda song: self._score(user, song), reverse=True)[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        reasons = []
        if song.genre == user.favorite_genre:
            reasons.append(f"matches your favorite genre ({song.genre})")
        if song.mood == user.favorite_mood:
            reasons.append(f"fits your preferred mood ({song.mood})")
        if abs(song.energy - user.target_energy) < 0.2:
            reasons.append(f"has energy close to your target ({song.energy:.1f})")
        if user.likes_acoustic and song.acousticness > 0.6:
            reasons.append(f"has a strong acoustic quality ({song.acousticness:.1f})")
        if not reasons:
            reasons.append("is a balanced match for your overall taste profile")
        return f"{song.title} by {song.artist} — " + "; ".join(reasons) + "."


def load_songs(file_path: str) -> list:
    """Load songs from a CSV file and return a list of dicts."""
    import csv
    songs = []
    with open(file_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["energy"] = float(row["energy"])
            row["tempo_bpm"] = float(row["tempo_bpm"])
            row["valence"] = float(row["valence"])
            row["danceability"] = float(row["danceability"])
            row["acousticness"] = float(row["acousticness"])
            songs.append(row)
    return songs


def score_song(user_prefs: dict, song: dict) -> tuple:
    """Calculate a score for a song based on user preferences."""
    score = 0.0
    reasons = []

    if song["genre"] == user_prefs["favorite_genre"]:
        score += 2.0
        reasons.append("Genre match (+2.0)")

    if song["mood"] == user_prefs["favorite_mood"]:
        score += 1.0
        reasons.append("Mood match (+1.0)")

    energy_diff = abs(song["energy"] - user_prefs["target_energy"])
    energy_score = max(0.0, 1.0 - energy_diff)
    score += energy_score
    reasons.append(f"Energy similarity (+{energy_score:.2f})")

    tempo_diff = abs(song["tempo_bpm"] - user_prefs["target_tempo"]) / 100.0
    tempo_score = max(0.0, 1.0 - tempo_diff)
    score += tempo_score
    reasons.append(f"Tempo similarity (+{tempo_score:.2f})")

    valence_diff = abs(song["valence"] - user_prefs["target_valence"])
    valence_score = max(0.0, 1.0 - valence_diff)
    score += valence_score
    reasons.append(f"Valence similarity (+{valence_score:.2f})")

    return score, reasons


def recommend_songs(user_prefs: dict, songs: list, k: int = 5) -> list:
    """Recommend the top K songs based on user preferences."""
    scored = [{"song": s, "score": sc, "reasons": r} for s, (sc, r) in
              ((s, score_song(user_prefs, s)) for s in songs)]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:k]
