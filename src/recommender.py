from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
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
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(file_path):
    """Load songs from a CSV file and return a list of dictionaries."""
    import csv
    songs = []
    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Convert numerical fields to floats
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            songs.append(row)
    return songs

def score_song(user_prefs, song):
    """Calculate a score for a song based on user preferences."""
    score = 0.0
    reasons = []

    # Genre match
    if song['genre'] == user_prefs['favorite_genre']:
        score += 2.0
        reasons.append("Genre match (+2.0)")

    # Mood match
    if song['mood'] == user_prefs['favorite_mood']:
        score += 1.0
        reasons.append("Mood match (+1.0)")

    # Energy similarity
    energy_diff = abs(song['energy'] - user_prefs['target_energy'])
    energy_score = max(0, 1.0 - energy_diff)  # Closer energy gets higher score
    score += energy_score
    reasons.append(f"Energy similarity (+{energy_score:.2f})")

    # Tempo similarity
    tempo_diff = abs(song['tempo_bpm'] - user_prefs['target_tempo']) / 100.0
    tempo_score = max(0, 1.0 - tempo_diff)
    score += tempo_score
    reasons.append(f"Tempo similarity (+{tempo_score:.2f})")

    # Valence similarity
    valence_diff = abs(song['valence'] - user_prefs['target_valence'])
    valence_score = max(0, 1.0 - valence_diff)
    score += valence_score
    reasons.append(f"Valence similarity (+{valence_score:.2f})")

    return score, reasons

def recommend_songs(user_prefs, songs, k=5):
    """Recommend the top K songs based on user preferences."""
    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append({"song": song, "score": score, "reasons": reasons})

    # Sort songs by score in descending order
    scored_songs.sort(key=lambda x: x['score'], reverse=True)

    # Return the top K songs
    return scored_songs[:k]
