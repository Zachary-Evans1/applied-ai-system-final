"""
Interactive music recommendation agent.

This runs the agentic workflow version with user feedback loop.
"""

from .recommender import load_songs, Recommender
from .agent import RecommendationAgent


def main() -> None:
    songs = load_songs("data/songs.csv")
    recommender = Recommender(songs)
    agent = RecommendationAgent(recommender)
    agent.start_session()


if __name__ == "__main__":
    main()
