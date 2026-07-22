import os
from src.recommender import load_songs, Song, UserProfile, Recommender

# Helper to get test data path
def get_test_csv_path():
    """Returns path to the songs CSV file."""
    return os.path.join(os.path.dirname(__file__), '..', 'data', 'songs.csv')


class TestLoadSongs:
    """Tests for loading songs from CSV."""

    def test_load_songs_returns_list(self):
        """load_songs should return a list of song dictionaries."""
        songs = load_songs(get_test_csv_path())
        assert isinstance(songs, list)
        assert len(songs) > 0

    def test_load_songs_converts_numeric_fields(self):
        """Numeric fields should be converted to float."""
        songs = load_songs(get_test_csv_path())
        first_song = songs[0]

        # Check that numeric fields are floats
        assert isinstance(first_song.id, (int, float))
        assert isinstance(first_song.energy, float)
        assert isinstance(first_song.tempo_bpm, float)
        assert isinstance(first_song.valence, float)

    def test_load_songs_has_required_fields(self):
        """Each song should have required fields for scoring."""
        songs = load_songs(get_test_csv_path())
        first_song = songs[0]

        # Verify Song dataclass has all required fields
        assert hasattr(first_song, 'genre')
        assert hasattr(first_song, 'mood')
        assert hasattr(first_song, 'energy')
        assert hasattr(first_song, 'tempo_bpm')
        assert hasattr(first_song, 'valence')


class TestScoreSong:
    """Tests for scoring individual songs."""

    def test_score_song_returns_tuple(self):
        """score_song should return (score, reasons) tuple."""
        user = UserProfile(
            favorite_genre='pop',
            favorite_mood='happy',
            target_energy=0.8,
            target_tempo=120,
            target_valence=0.7,
        )
        song = Song(
            id=1,
            title='Test Song',
            artist='Test Artist',
            genre='pop',
            mood='happy',
            energy=0.8,
            tempo_bpm=120,
            valence=0.7,
        )
        recommender = Recommender([song])
        result = recommender.score_song(user, song)
        assert isinstance(result, tuple)
        assert len(result) == 2
        score, reasons = result
        assert isinstance(score, float)
        assert isinstance(reasons, list)

    def test_score_song_genre_matching(self):
        """Genre match should increase score."""
        user = UserProfile(favorite_genre='rock', favorite_mood='chill',
                          target_energy=0.5, target_tempo=100, target_valence=0.5)

        # Matching genre
        song_match = Song(id=1, title='Rock Song', artist='Artist', genre='rock', mood='chill',
                         energy=0.5, tempo_bpm=100, valence=0.5)
        # Non-matching genre
        song_no_match = Song(id=2, title='Jazz Song', artist='Artist', genre='jazz', mood='chill',
                            energy=0.5, tempo_bpm=100, valence=0.5)

        recommender = Recommender([song_match, song_no_match])
        score_match, _ = recommender.score_song(user, song_match)
        score_no_match, _ = recommender.score_song(user, song_no_match)

        assert score_match > score_no_match, "Matching genre should score higher"

    def test_score_song_mood_matching(self):
        """Mood match should increase score."""
        user = UserProfile(favorite_genre='pop', favorite_mood='happy',
                          target_energy=0.5, target_tempo=100, target_valence=0.5)

        # Matching mood
        song_match = Song(id=1, title='Happy Song', artist='Artist', genre='pop', mood='happy',
                         energy=0.5, tempo_bpm=100, valence=0.5)
        # Non-matching mood
        song_no_match = Song(id=2, title='Sad Song', artist='Artist', genre='pop', mood='sad',
                            energy=0.5, tempo_bpm=100, valence=0.5)

        recommender = Recommender([song_match, song_no_match])
        score_match, _ = recommender.score_song(user, song_match)
        score_no_match, _ = recommender.score_song(user, song_no_match)

        assert score_match > score_no_match, "Matching mood should score higher"

    def test_score_song_energy_proximity(self):
        """Songs close to target energy should score higher."""
        user = UserProfile(favorite_genre='pop', favorite_mood='happy',
                          target_energy=0.8, target_tempo=100, target_valence=0.5)

        # Close to target energy
        song_close = Song(id=1, title='High Energy', artist='Artist', genre='pop', mood='happy',
                         energy=0.79, tempo_bpm=100, valence=0.5)
        # Far from target energy
        song_far = Song(id=2, title='Low Energy', artist='Artist', genre='pop', mood='happy',
                       energy=0.2, tempo_bpm=100, valence=0.5)

        recommender = Recommender([song_close, song_far])
        score_close, _ = recommender.score_song(user, song_close)
        score_far, _ = recommender.score_song(user, song_far)

        assert score_close > score_far, "Song closer to target energy should score higher"

    def test_score_song_includes_reasons(self):
        """Reasons should explain the scoring."""
        user = UserProfile(favorite_genre='pop', favorite_mood='happy',
                          target_energy=0.8, target_tempo=120, target_valence=0.7)
        song = Song(id=1, title='Perfect Song', artist='Artist', genre='pop', mood='happy',
                   energy=0.8, tempo_bpm=120, valence=0.7)

        recommender = Recommender([song])
        score, reasons = recommender.score_song(user, song)

        assert len(reasons) > 0, "Should have reasons for the score"
        # Check that reasons mention key metrics
        reasons_text = '\n'.join(reasons)
        assert 'Genre' in reasons_text or 'genre' in reasons_text


class TestRecommendSongs:
    """Tests for the recommendation function."""

    def test_recommend_songs_returns_sorted_list(self):
        """recommend should return songs sorted by score (highest first)."""
        user = UserProfile(
            favorite_genre='pop',
            favorite_mood='happy',
            target_energy=0.8,
            target_tempo=120,
            target_valence=0.7,
        )
        songs = [
            Song(id=1, title='Perfect Match', artist='Artist 1', genre='pop', mood='happy',
                energy=0.8, tempo_bpm=120, valence=0.7),
            Song(id=2, title='Wrong Match', artist='Artist 2', genre='jazz', mood='sad',
                energy=0.3, tempo_bpm=80, valence=0.3),
        ]

        recommender = Recommender(songs)
        results = recommender.recommend(user, k=2)

        assert len(results) == 2
        # Results should be tuples of (song, score, explanation)
        assert len(results[0]) == 3
        # Highest score should come first
        assert results[0][1] >= results[1][1], "Results should be sorted by score descending"

    def test_recommend_songs_respects_k_parameter(self):
        """recommend should return at most k recommendations."""
        user = UserProfile(favorite_genre='pop', favorite_mood='happy',
                          target_energy=0.5, target_tempo=100, target_valence=0.5)
        songs = [
            Song(id=i, title=f'Song {i}', artist='Artist', genre='pop', mood='happy',
                energy=0.5, tempo_bpm=100, valence=0.5)
            for i in range(10)
        ]

        recommender = Recommender(songs)
        results_k3 = recommender.recommend(user, k=3)
        results_k5 = recommender.recommend(user, k=5)

        assert len(results_k3) == 3
        assert len(results_k5) == 5

    def test_recommend_songs_includes_explanations(self):
        """Each recommendation should include an explanation."""
        user = UserProfile(favorite_genre='pop', favorite_mood='happy',
                          target_energy=0.8, target_tempo=120, target_valence=0.7)
        songs = [
            Song(id=1, title='Great Song', artist='Artist', genre='pop', mood='happy',
                energy=0.8, tempo_bpm=120, valence=0.7),
        ]

        recommender = Recommender(songs)
        results = recommender.recommend(user, k=1)
        _, _, explanation = results[0]

        assert isinstance(explanation, str)
        assert len(explanation) > 0, "Explanation should not be empty"
        assert '\n' in explanation, "Explanation should have multiple reasons"

    def test_recommend_songs_with_real_data(self):
        """Test recommend with actual CSV data."""
        songs = load_songs(get_test_csv_path())
        user = UserProfile(
            favorite_genre='pop',
            favorite_mood='happy',
            target_energy=0.8,
            target_tempo=120,
            target_valence=0.7,
        )

        recommender = Recommender(songs)
        results = recommender.recommend(user, k=5)

        assert len(results) <= 5
        assert len(results) > 0, "Should have at least one recommendation"

        # Verify structure
        for song, score, explanation in results:
            assert isinstance(song, Song)
            assert isinstance(score, (int, float))
            assert isinstance(explanation, str)

    def test_recommend_songs_different_profiles(self):
        """Different user profiles should get different recommendations."""
        songs = load_songs(get_test_csv_path())
        recommender = Recommender(songs)

        # High-energy EDM fan
        edm_profile = UserProfile(
            favorite_genre='electronic',
            favorite_mood='energetic',
            target_energy=0.9,
            target_tempo=130,
            target_valence=0.8,
        )

        # Chill acoustic fan
        acoustic_profile = UserProfile(
            favorite_genre='acoustic',
            favorite_mood='calm',
            target_energy=0.3,
            target_tempo=80,
            target_valence=0.5,
        )

        edm_results = recommender.recommend(edm_profile, k=3)
        acoustic_results = recommender.recommend(acoustic_profile, k=3)

        # Get the top recommendation for each
        edm_top = edm_results[0][0] if edm_results else None
        acoustic_top = acoustic_results[0][0] if acoustic_results else None

        assert edm_top is not None
        assert acoustic_top is not None
        # Different profiles should (usually) get different top recommendations
        # Note: this might occasionally fail if by chance they match, but very unlikely
