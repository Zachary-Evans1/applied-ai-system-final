import pytest
from src.recommender import load_songs, Recommender
from src.agent import RecommendationAgent, ParseStatus


def get_test_csv_path():
    """Returns path to the songs CSV file."""
    import os

    return os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")


class TestAnalyzeFeedback:
    """Tests for feedback parsing and analysis."""

    @pytest.fixture
    def agent(self):
        """Create a RecommendationAgent for testing."""
        songs = load_songs(get_test_csv_path())
        recommender = Recommender(songs)
        return RecommendationAgent(recommender)

    def test_clear_single_command(self, agent):
        """Single clear command should return CLEAR status."""
        result = agent._analyze_feedback("more energetic")

        assert result.status == ParseStatus.CLEAR
        assert len(result.commands) == 1
        assert result.commands[0][1] == "energy"  # param
        assert result.commands[0][2] == 0.1  # change
        assert result.reason == ""

    def test_clear_command_with_alias(self, agent):
        """Command aliases should be recognized."""
        result = agent._analyze_feedback("increase energy")

        assert result.status == ParseStatus.CLEAR
        assert len(result.commands) == 1
        assert result.commands[0][1] == "energy"

    def test_multiple_non_conflicting_commands(self, agent):
        """Multiple commands for different parameters should be CLEAR."""
        result = agent._analyze_feedback("more energetic and happier")

        assert result.status == ParseStatus.CLEAR
        assert len(result.commands) == 2

        # Check that we have both energy and valence changes
        params = [cmd[1] for cmd in result.commands]
        assert "energy" in params
        assert "valence" in params

    def test_conflicting_commands(self, agent):
        """Conflicting commands for same parameter should be AMBIGUOUS."""
        result = agent._analyze_feedback("faster and slower")

        assert result.status == ParseStatus.AMBIGUOUS
        assert "Conflicting commands" in result.reason
        assert len(result.commands) == 2

    def test_conflicting_energy_commands(self, agent):
        """Conflicting energy commands should be detected."""
        result = agent._analyze_feedback("more energetic but calmer")

        assert result.status == ParseStatus.AMBIGUOUS
        assert "Conflicting commands" in result.reason

    def test_negation_detection(self, agent):
        """Negations should trigger AMBIGUOUS status."""
        result = agent._analyze_feedback("don't make it faster")

        assert result.status == ParseStatus.AMBIGUOUS
        assert "Negation detected" in result.reason

    def test_negation_with_alternative(self, agent):
        """Negation with alternative instruction should be AMBIGUOUS."""
        result = agent._analyze_feedback("please don't make it faster, I want it slower")

        assert result.status == ParseStatus.AMBIGUOUS
        # When negation comes with conflicting commands, conflict takes precedence
        assert "Conflicting commands" in result.reason or "Negation detected" in result.reason
        assert len(result.commands) >= 1

    def test_unsupported_feedback(self, agent):
        """Unknown commands should return UNSUPPORTED status."""
        result = agent._analyze_feedback("make it mysterious")

        assert result.status == ParseStatus.UNSUPPORTED
        assert len(result.commands) == 0
        assert result.reason != ""

    def test_unsupported_with_partial_match(self, agent):
        """Completely unknown feedback should be UNSUPPORTED."""
        result = agent._analyze_feedback("give me something like my childhood memories")

        assert result.status == ParseStatus.UNSUPPORTED
        assert len(result.commands) == 0

    def test_empty_feedback(self, agent):
        """Empty feedback should return UNSUPPORTED."""
        result = agent._analyze_feedback("")

        assert result.status == ParseStatus.UNSUPPORTED

    def test_case_insensitive_parsing(self, agent):
        """Feedback parsing should be case insensitive."""
        result1 = agent._analyze_feedback("MORE ENERGETIC")
        result2 = agent._analyze_feedback("more energetic")
        result3 = agent._analyze_feedback("MoRe EnErGeTiC")

        assert result1.status == result2.status == result3.status == ParseStatus.CLEAR
        assert result1.commands[0][1] == result2.commands[0][1] == result3.commands[0][1]

    def test_command_in_sentence(self, agent):
        """Commands should be recognized within sentences."""
        result = agent._analyze_feedback("hey, I want to feel more energetic please")

        assert result.status == ParseStatus.CLEAR
        assert len(result.commands) == 1
        assert result.commands[0][1] == "energy"

    def test_multiple_same_command_recognized_once(self, agent):
        """Duplicate commands should not be added twice."""
        result = agent._analyze_feedback("more energetic, I really want more energetic vibes")

        assert result.status == ParseStatus.CLEAR
        assert len(result.commands) == 1
        assert result.commands[0][1] == "energy"


class TestParseResultStructure:
    """Tests for ParseResult data structure."""

    @pytest.fixture
    def agent(self):
        """Create a RecommendationAgent for testing."""
        songs = load_songs(get_test_csv_path())
        recommender = Recommender(songs)
        return RecommendationAgent(recommender)

    def test_parse_result_has_commands_list(self, agent):
        """ParseResult should always have commands as a list."""
        result = agent._analyze_feedback("more energetic")

        assert isinstance(result.commands, list)
        assert all(isinstance(cmd, tuple) and len(cmd) == 3 for cmd in result.commands)

    def test_parse_result_has_status_enum(self, agent):
        """ParseResult should have status as ParseStatus enum."""
        result = agent._analyze_feedback("more energetic")

        assert isinstance(result.status, ParseStatus)
        assert result.status in [
            ParseStatus.CLEAR,
            ParseStatus.AMBIGUOUS,
            ParseStatus.UNSUPPORTED,
        ]

    def test_parse_result_has_reason_string(self, agent):
        """ParseResult should have reason as string."""
        result = agent._analyze_feedback("more energetic")

        assert isinstance(result.reason, str)


class TestAgentWorkflow:
    """Integration tests for agent workflow and profile updates."""

    @pytest.fixture
    def agent_with_profile(self):
        """Create agent with initial profile."""
        songs = load_songs(get_test_csv_path())
        recommender = Recommender(songs)
        agent = RecommendationAgent(recommender)
        from src.recommender import UserProfile

        agent.profile = UserProfile(
            favorite_genre="pop",
            favorite_mood="happy",
            target_energy=0.5,
            target_tempo=100,
            target_valence=0.5,
        )
        return agent

    def test_single_command_increases_energy(self, agent_with_profile):
        """Single clear command should update profile."""
        original_energy = agent_with_profile.profile.target_energy
        parsed = agent_with_profile._analyze_feedback("more energetic")

        assert parsed.status == ParseStatus.CLEAR
        assert len(parsed.commands) == 1

        # Apply the command
        _, param, change = parsed.commands[0]
        _, new_value = agent_with_profile._plan_profile_update(param, change)
        agent_with_profile._act_update_profile(param, new_value)

        assert agent_with_profile.profile.target_energy > original_energy
        assert agent_with_profile.profile.target_energy == 0.6

    def test_single_command_decreases_tempo(self, agent_with_profile):
        """Decrease command should reduce tempo."""
        original_tempo = agent_with_profile.profile.target_tempo
        parsed = agent_with_profile._analyze_feedback("slower")

        assert parsed.status == ParseStatus.CLEAR

        _, param, change = parsed.commands[0]
        _, new_value = agent_with_profile._plan_profile_update(param, change)
        agent_with_profile._act_update_profile(param, new_value)

        assert agent_with_profile.profile.target_tempo < original_tempo
        assert agent_with_profile.profile.target_tempo == 90

    def test_multiple_commands_all_applied(self, agent_with_profile):
        """Multiple non-conflicting commands should all be applied."""
        original_energy = agent_with_profile.profile.target_energy
        original_valence = agent_with_profile.profile.target_valence

        parsed = agent_with_profile._analyze_feedback("more energetic and happier")

        assert parsed.status == ParseStatus.CLEAR
        assert len(parsed.commands) == 2

        # Apply all commands
        for _, param, change in parsed.commands:
            _, new_value = agent_with_profile._plan_profile_update(param, change)
            agent_with_profile._act_update_profile(param, new_value)

        assert agent_with_profile.profile.target_energy > original_energy
        assert agent_with_profile.profile.target_valence > original_valence

    def test_profile_bounded_at_maximum(self, agent_with_profile):
        """Profile values should not exceed maximum bounds."""
        agent_with_profile.profile.target_energy = 1.0

        parsed = agent_with_profile._analyze_feedback("more energetic")
        _, param, change = parsed.commands[0]
        old_value, new_value = agent_with_profile._plan_profile_update(param, change)

        # Should be capped at 1.0
        assert new_value == 1.0
        assert old_value == new_value  # No change should occur

    def test_profile_bounded_at_minimum(self, agent_with_profile):
        """Profile values should not go below minimum bounds."""
        agent_with_profile.profile.target_energy = 0.0

        parsed = agent_with_profile._analyze_feedback("calmer")
        _, param, change = parsed.commands[0]
        old_value, new_value = agent_with_profile._plan_profile_update(param, change)

        # Should be capped at 0.0
        assert new_value == 0.0
        assert old_value == new_value  # No change should occur

    def test_tempo_bounded_minimum(self, agent_with_profile):
        """Tempo should not go below 60 BPM."""
        agent_with_profile.profile.target_tempo = 60

        parsed = agent_with_profile._analyze_feedback("slower")
        _, param, change = parsed.commands[0]
        old_value, new_value = agent_with_profile._plan_profile_update(param, change)

        # Should be capped at 60
        assert new_value == 60
        assert old_value == new_value

    def test_tempo_bounded_maximum(self, agent_with_profile):
        """Tempo should not exceed 200 BPM."""
        agent_with_profile.profile.target_tempo = 200

        parsed = agent_with_profile._analyze_feedback("faster")
        _, param, change = parsed.commands[0]
        old_value, new_value = agent_with_profile._plan_profile_update(param, change)

        # Should be capped at 200
        assert new_value == 200
        assert old_value == new_value

    def test_conflicting_commands_not_applied_without_confirmation(
        self, agent_with_profile
    ):
        """Conflicting commands should require confirmation."""
        parsed = agent_with_profile._analyze_feedback("faster and slower")

        # Should be marked as ambiguous
        assert parsed.status == ParseStatus.AMBIGUOUS
        assert "Conflicting" in parsed.reason

        # In real usage, _ask_user_confirmation would be called
        # Here we just verify the commands are marked as needing confirmation
        assert not (parsed.status == ParseStatus.CLEAR)

    def test_get_profile_value_correct(self, agent_with_profile):
        """_get_profile_value should return correct values."""
        assert agent_with_profile._get_profile_value("energy") == 0.5
        assert agent_with_profile._get_profile_value("tempo") == 100
        assert agent_with_profile._get_profile_value("valence") == 0.5

    def test_act_updates_all_params(self, agent_with_profile):
        """_act_update_profile should handle all parameter types."""
        agent_with_profile._act_update_profile("energy", 0.8)
        assert agent_with_profile.profile.target_energy == 0.8

        agent_with_profile._act_update_profile("valence", 0.9)
        assert agent_with_profile.profile.target_valence == 0.9

        agent_with_profile._act_update_profile("tempo", 150)
        assert agent_with_profile.profile.target_tempo == 150
