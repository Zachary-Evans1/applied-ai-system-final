from typing import List, Tuple
from dataclasses import dataclass
import csv


@dataclass
class Song:
    """A song with its attributes for recommendation scoring."""
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float


@dataclass
class UserProfile:
    """A user's music taste preferences for generating recommendations."""
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    target_tempo: float
    target_valence: float


class Recommender:
    """
    OOP implementation of the recommendation logic.
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a song against user preferences, returning score and reasons."""
        score = 0.0
        reasons = []

        # Genre match: +40 points
        if song.genre == user.favorite_genre:
            score += 40
            reasons.append(f"✓ Genre match: {song.genre}")

        # Mood match: +30 points
        if song.mood == user.favorite_mood:
            score += 30
            reasons.append(f"✓ Mood match: {song.mood}")

        # Energy proximity: up to +15 points
        energy_distance = abs(song.energy - user.target_energy)
        energy_points = 15 * max(0, 1 - energy_distance)
        score += energy_points
        reasons.append(f"Energy: {energy_points:.1f}/15 (target {user.target_energy}, song {song.energy})")

        # Tempo proximity: up to +10 points
        tempo_distance = abs(song.tempo_bpm - user.target_tempo)
        max_tempo_distance = 50
        tempo_points = 10 * max(0, 1 - (tempo_distance / max_tempo_distance))
        score += tempo_points
        reasons.append(f"Tempo: {tempo_points:.1f}/10 (target {user.target_tempo}, song {song.tempo_bpm})")

        # Valence proximity: up to +5 points
        valence_distance = abs(song.valence - user.target_valence)
        valence_points = 5 * max(0, 1 - valence_distance)
        score += valence_points
        reasons.append(f"Valence: {valence_points:.1f}/5 (target {user.target_valence}, song {song.valence})")

        return (score, reasons)

    def recommend(self, user: UserProfile, k: int = 5) -> List[Tuple[Song, float, str]]:
        """Score all songs and return top k recommendations sorted by score."""
        scored_songs = []
        for song in self.songs:
            score, reasons = self.score_song(user, song)
            scored_songs.append((song, score, '\n'.join(reasons)))

        return sorted(scored_songs, key=lambda x: x[1], reverse=True)[:k]


def load_songs(csv_path: str) -> List[Song]:
    """Load songs from a CSV file and convert to Song dataclass instances."""
    songs = []

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            song = Song(
                id=int(row['id']),
                title=row['title'],
                artist=row['artist'],
                genre=row['genre'],
                mood=row['mood'],
                energy=float(row['energy']),
                tempo_bpm=float(row['tempo_bpm']),
                valence=float(row['valence'])
            )
            songs.append(song)

    print(f"Loaded {len(songs)} songs from {csv_path}")
    return songs

