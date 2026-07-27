from typing import List, Tuple, Optional
from .recommender import Recommender, UserProfile, Song


class RecommendationAgent:
    """Interactive agent that refines music recommendations through user feedback."""

    # Feedback command aliases mapping to (parameter, change_value)
    FEEDBACK_COMMANDS = {
        "more energetic": ("energy", 0.1),
        "increase energy": ("energy", 0.1),
        "higher energy": ("energy", 0.1),
        "calmer": ("energy", -0.1),
        "less energetic": ("energy", -0.1),
        "lower energy": ("energy", -0.1),
        "happier": ("valence", 0.1),
        "more positive": ("valence", 0.1),
        "higher valence": ("valence", 0.1),
        "sadder": ("valence", -0.1),
        "less happy": ("valence", -0.1),
        "lower valence": ("valence", -0.1),
        "faster": ("tempo", 10),
        "higher tempo": ("tempo", 10),
        "slower": ("tempo", -10),
        "lower tempo": ("tempo", -10),
    }

    # Constraints for profile parameters
    CONSTRAINTS = {
        "energy": (0.0, 1.0),
        "valence": (0.0, 1.0),
        "tempo": (60, 200),
    }

    # Map parameter names to UserProfile attribute names
    PARAM_TO_ATTR = {
        "energy": "target_energy",
        "valence": "target_valence",
        "tempo": "target_tempo",
    }

    def __init__(self, recommender: Recommender):
        self.recommender = recommender
        self.profile: Optional[UserProfile] = None
        self.previous_recommendations: List[Song] = []
        self.previous_scores: List[float] = []

    def start_session(self) -> None:
        """Start an interactive recommendation session."""
        print("\n🎵 Welcome to the Interactive Music Recommender!\n")

        # Gather initial preferences
        self.profile = self._get_initial_profile()

        # Show initial recommendations
        print("\n" + "=" * 70)
        print("Initial Recommendations Based on Your Preferences")
        print("=" * 70 + "\n")
        self._show_recommendations()

        # Main feedback loop
        print("\nYou can now provide feedback to refine recommendations.")
        print("\nSupported feedback commands:")
        print("  Energy: 'more energetic', 'calmer'")
        print("  Mood: 'happier', 'sadder'")
        print("  Tempo: 'faster', 'slower'")
        print("  Exit: 'quit'\n")

        while True:
            feedback = input("Your feedback: ").strip().lower()

            if feedback == "quit":
                print("\nThanks for using the Music Recommender! 🎵")
                break

            self._process_feedback(feedback)

    def _get_initial_profile(self) -> UserProfile:
        """Prompt user for initial music preferences."""
        print("Let's start by learning about your music taste.\n")

        genre = input("Favorite genre (e.g., pop, rock, jazz): ").strip()
        mood = input("Favorite mood (e.g., happy, sad, energetic): ").strip()

        energy = self._get_valid_float(
            "Target energy level (0.0-1.0): ", 0.0, 1.0
        )
        tempo = self._get_valid_float(
            "Target tempo in BPM (60-200): ", 60, 200
        )
        valence = self._get_valid_float(
            "Target valence/positivity (0.0-1.0): ", 0.0, 1.0
        )

        return UserProfile(
            favorite_genre=genre,
            favorite_mood=mood,
            target_energy=energy,
            target_tempo=tempo,
            target_valence=valence,
        )

    def _get_valid_float(
        self, prompt: str, min_val: float, max_val: float
    ) -> float:
        """Get valid float input from user within range."""
        while True:
            try:
                value = float(input(prompt))
                if min_val <= value <= max_val:
                    return value
                print(f"Please enter a value between {min_val} and {max_val}.")
            except ValueError:
                print("Please enter a valid number.")

    def _process_feedback(self, feedback: str) -> None:
        """Process user feedback through the agentic workflow."""
        # Step 1: Analyze
        param, change, command = self._analyze_feedback(feedback)
        if param is None:
            self._show_unsupported_feedback()
            return

        # Step 2: Plan
        old_value, new_value = self._plan_profile_update(param, change)

        # Step 3: Act
        self._act_update_profile(param, new_value)

        # Step 4: Evaluate
        old_avg_score, new_avg_score, songs_changed = self._evaluate_changes()

        # Step 5: Explain
        assert command is not None
        self._explain_changes(
            param,
            old_value,
            new_value,
            command,
            old_avg_score,
            new_avg_score,
            songs_changed,
        )

        # Show new recommendations
        print()
        self._show_recommendations()

    def _analyze_feedback(
        self, feedback: str
    ) -> Tuple[Optional[str], float, Optional[str]]:
        """Step 1: Analyze user feedback and recognize commands."""
        for command, (param, change) in self.FEEDBACK_COMMANDS.items():
            if command in feedback:
                return param, change, command
        return None, 0.0, None

    def _plan_profile_update(
        self, param: str, change: float
    ) -> Tuple[float, float]:
        """Step 2: Plan the profile update with bounds checking."""
        assert self.profile is not None
        old_value = self._get_profile_value(param)
        min_val, max_val = self.CONSTRAINTS[param]
        new_value = max(min_val, min(max_val, old_value + change))
        return old_value, new_value

    def _act_update_profile(self, param: str, new_value: float) -> None:
        """Step 3: Act by updating the UserProfile."""
        attr_name = self.PARAM_TO_ATTR[param]
        setattr(self.profile, attr_name, new_value)

    def _evaluate_changes(self) -> Tuple[float, float, int]:
        """Step 4: Evaluate if recommendations changed after update."""
        assert self.profile is not None
        recommendations = self.recommender.recommend(self.profile, k=5)
        new_songs = [song for song, _, _ in recommendations]
        new_scores = [score for _, score, _ in recommendations]

        # Calculate score averages
        old_avg_score = (
            sum(self.previous_scores) / len(self.previous_scores)
            if self.previous_scores
            else 0.0
        )
        new_avg_score = (
            sum(new_scores) / len(new_scores) if new_scores else 0.0
        )

        # Count how many songs changed in top 5
        songs_changed = sum(
            1 for i, song in enumerate(new_songs)
            if i >= len(self.previous_recommendations)
            or song != self.previous_recommendations[i]
        )

        self.previous_recommendations = new_songs
        self.previous_scores = new_scores

        return old_avg_score, new_avg_score, songs_changed

    def _explain_changes(
        self,
        param: str,
        old_value: float,
        new_value: float,
        command: str,
        old_avg_score: float,
        new_avg_score: float,
        songs_changed: int,
    ) -> None:
        """Step 5: Explain what was changed and why."""
        param_name = {
            "energy": "energy",
            "valence": "positivity",
            "tempo": "tempo",
        }[param]

        # Show the user's request
        print(f"\nYou requested:")
        print(f'"{command}"')
        print()

        # Explain the change
        if old_value == new_value:
            print(f"✓ Your target {param_name} is already at its limit ({old_value:.2f}).")
        else:
            direction = "increased" if new_value > old_value else "decreased"
            print(f"I {direction} your target {param_name}")
            print(f"from {old_value:.2f} → {new_value:.2f}.")

        # Report impact on recommendations
        print()
        score_change = new_avg_score - old_avg_score
        if songs_changed > 0:
            print(f"📊 {songs_changed} of the top 5 songs changed.")
        else:
            print(f"📊 Top 5 songs remain the same.")

        if score_change > 0:
            print(
                f"   Average recommendation score improved by {score_change:.1f} points."
            )
        elif score_change < 0:
            print(
                f"   Average recommendation score decreased by {abs(score_change):.1f} points."
            )
        else:
            print(f"   Average recommendation score unchanged.")

    def _get_profile_value(self, param: str) -> float:
        """Get current parameter value from profile."""
        attr_name = self.PARAM_TO_ATTR[param]
        return getattr(self.profile, attr_name)

    def _show_recommendations(self) -> None:
        """Display top 5 recommendations."""
        assert self.profile is not None
        recommendations = self.recommender.recommend(self.profile, k=5)
        self.previous_recommendations = [
            song for song, _, _ in recommendations
        ]
        self.previous_scores = [score for _, score, _ in recommendations]

        for idx, (song, score, explanation) in enumerate(recommendations, 1):
            print(f"{idx}. {song.title} - {song.artist}")
            print(f"   Score: {score:.1f}/100")
            print("   " + "─" * 66)
            for reason in explanation.split("\n"):
                print(f"   {reason}")
            print()

    def _show_unsupported_feedback(self) -> None:
        """Show message when feedback is not recognized."""
        print("\n❌ I didn't recognize that command.")
        print("\nSupported feedback commands:")
        print("  Energy: 'more energetic', 'calmer'")
        print("  Mood: 'happier', 'sadder'")
        print("  Tempo: 'faster', 'slower'")
        print("  Exit: 'quit'\n")
        print("Try again with one of these commands:\n")
