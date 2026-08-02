## Original Project: 🎵 Music Recommender Simulation

## Original Goals and Capabilities

This project extends my Music Recommender Simulation. The original Music Recommender Simulation took a group of songs from a CSV file then score and rank them based on a user's preferences. It worked by scoring songs based on there attributes, including genre, mood, energy, tempo/bpm, and valence against a user's desired preferences, and then ranking the top 5 scoring songs and showing them in a list.

## Title: Tunematch 2.0: Interactive Music Recommender Agent

## Project Summary

The Interactive Music Recommender Agent expands the original recommender into an agentic AI system. Instead of generating recommendations only once, the system accepts feedback from the user, updates their music preference profile, and generates new recommendations through a multi-step reasoning process.

The agent analyzes user feedback, applies guardrails to detect ambiguous or unknown/unsupported requests, updates the recommendation profile within given limits, evaluates how the recommendations changed, and explains the results before presenting the updated recommendations. Automated testing and logging were also added to improve the system's reliability.


## Architecture Overview

The systems consists of four primary components:

* Recommendation Engine - Loads songs from a CSV file and scores each song based on genre, mood, energy, tempo, and valence of a song against a user's profile. Then ranks the top five scoring songs and prints them to the terminal.

* Recommendation Agent - Implements an agentic workflow consisting of Analyze → Plan → Act → Evaluate → Explain.

* Reliability & Guardrails - Detects unsupported or ambiguous feedback, requests user confirmation when necessary, enforces bounds for the score, and logs important events.

* Testing & Verification - Automated unit tests that  validate the recommendation algorithm, feedback parsing, workflow behavior, guardrails, and profile updates.


A visual version of this architecture can be found in diagram/diagram.mmd.

## Setup Instructions

### Prerequisites

Python 3.7 or higher
Git (optional) — For cloning the repository

### Installation & Running

1. **Clone or download the project**
   git clone <repository-url>
   cd applied-ai-system-final

2. **Create a virtual environment** (recommended, but optional)

   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate


3. **Install dependencies**

   pip install -r requirements.txt

4. **Run the Interactive Music Recommender Agent**

   python -m src.main
   
   You'll be prompted to enter your music preferences (genre, mood, energy, tempo, valence), then you can provide feedback like "more energetic", "happier", "faster", etc. Type `quit` to exit.

5. **Run the tests**

   pytest tests/

## Sample Interactions

### Example 1 - Increasing Energy

User Input: more energetic

Agent Output:

You requested:
  • "more energetic"

✓ I increased your target energy
  from 0.80 → 0.90.

📊 Top 5 songs remain the same.
   Average recommendation score decreased by 0.3 points.

### Example 2 – Multiple Non-Conflicting Commands

User Input: more energetic and happier

Agent Output:

You requested:
  • "more energetic"
  • "happier"

✓ I increased your target energy
  from 0.90 → 1.00.
✓ I increased your target valence
  from 0.60 → 0.70.

📊 1 of the top 5 songs changed.
   Average recommendation score decreased by 1.0 points.

### Example 3 - Ambiguous Feedback

User Input: please don't make it faster, I want it slower

Agent Output:

Your feedback: please don't make it faster, I want it slower

⚠️  Conflicting commands detected: faster, slower

Commands found:
  • faster (increase tempo)
  • slower (decrease tempo)

Proceed with these changes? (yes/no)

User Input: no

Agent Output:

Understood. Please try again with clearer instructions.

### Example 4 - Unknown Feedback

User Input: make it more danceable

Agent Output:

Your feedback: make it more danceable

❌ I didn't recognize that command.

Supported feedback types:
  Energy: 'more/less energetic', 'increase/decrease energy', etc.
  Valence: 'happier/sadder', 'more/less positive', etc.
  Tempo: 'faster/slower', 'higher/lower tempo', etc.

  💡 Combine non-conflicting types: 'more energetic and happier'
  Exit: 'quit'

Try again with one of these types:

## Design Decisions

The project uses a content-based recommendation system, same as the old Music recommender, because it is appropriate for a small music dataset. Every recommendation includes a score and explanation showing how the song matched a user's preferences.

The largest architectural change was introducing an agentic workflow, rather than immediately applying every user request, the agent follows a structured reasoning process:

1. Analyze the user's feedback.
2. Plan profile updates.
3. Apply validated changes.
4. Evaluate how recommendations changed.
5. Explain the results to the user.

To improve reliability, the system includes guardrails that detect ambiguous commands, unsupported requests, conflicting instructions, and profile values that exceed valid ranges.

## Testing Summary

The project includes automated tests covering both the recommendation engine and the agent workflow.

The tests verify:
* Recommendation scoring and ranking
* CSV loading
* Feedback parsing
* Agent workflow execution
* Ambiguous and unsupported command handling
* Bounds checking for profile values
* Multi-command feedback processing

Logging was also added so important events, like user feedback, parsing decisions, confirmation requests, and profile updates are recorded in logs/agent.log for debugging and evaluation.

Developing these tests helped identify edge cases such as conflicting commands ("faster and slower") and negated requests ("don't make it faster"), which led to the addition of confirmation guardrails before applying profile changes.

### Output From Tests Being Run:
PS C:\Users\evans\Desktop\applied-ai-system-final> pytest tests/
======================================================================================== test session starts =========================================================================================
platform win32 -- Python 3.13.13, pytest-9.0.3, pluggy-1.6.0
rootdir: C:\Users\evans\Desktop\applied-ai-system-final
plugins: anyio-4.13.0
collected 39 items                                                                                                                                                                                    

tests\test_agent.py ..........................                                                                                                                                                  [ 66%]
tests\test_recommender.py .............                                                                                                                                                         [100%]

========================================================================================= 39 passed in 0.06s =========================================================================================

## Reflection

This project showed me that agentic AI does not have to be extremely complicated. Before this project when I heard "agentic AI" I would think of large, complex systems with many parts. Building this project showed me that even a relatively simple application, like updating a user's music preference profile through an Analyze → Plan → Act → Evaluate → Explain workflow, can be an agentic AI system. 

It also helped me understand the importance of adding guardrails, user confirmation, logging, and testing to make an AI system more reliable and easier to trust. Finally, it taught me the importance of a system explaining what it's doing, and how that can improve the user experience by making its decisions more transparent.

## Execution Evidence

PS C:\Users\evans\Desktop\applied-ai-system-final> python -m src.main
Loaded 20 songs from data/songs.csv

🎵 Welcome to the Interactive Music Recommender!

Let's start by learning about your music taste.

Favorite genre (e.g., pop, rock, jazz): pop
Favorite mood (e.g., happy, sad, energetic): happy
Target energy level (0.0-1.0): 0.8
Target tempo in BPM (60-200): 120
Target valence/positivity (0.0-1.0): 0.6

======================================================================
Initial Recommendations Based on Your Preferences
======================================================================

1. Sunrise City - Neon Echo
   Score: 98.1/100
   ──────────────────────────────────────────────────────────────────
   ✓ Genre match: pop
   ✓ Mood match: happy
   Energy: 14.7/15 (target 0.8, song 0.82)
   Tempo: 9.6/10 (target 120.0, song 118.0)
   Valence: 3.8/5 (target 0.6, song 0.84)

2. Gym Hero - Max Pulse
   Score: 64.8/100
   ──────────────────────────────────────────────────────────────────
   ✓ Genre match: pop
   Energy: 13.1/15 (target 0.8, song 0.93)
   Tempo: 7.6/10 (target 120.0, song 132.0)
   Valence: 4.1/5 (target 0.6, song 0.77)

3. Rooftop Lights - Indigo Parade
   Score: 57.6/100
   ──────────────────────────────────────────────────────────────────
   ✓ Mood match: happy
   Energy: 14.4/15 (target 0.8, song 0.76)
   Tempo: 9.2/10 (target 120.0, song 124.0)
   Valence: 3.9/5 (target 0.6, song 0.81)

4. Neon Dreams - SynthMaster
   Score: 27.0/100
   ──────────────────────────────────────────────────────────────────
   Energy: 13.8/15 (target 0.8, song 0.88)
   Tempo: 8.4/10 (target 120.0, song 128.0)
   Valence: 4.8/5 (target 0.6, song 0.65)

5. Night Drive Loop - Neon Echo
   Score: 26.7/100
   ──────────────────────────────────────────────────────────────────
   Energy: 14.2/15 (target 0.8, song 0.75)
   Tempo: 8.0/10 (target 120.0, song 110.0)
   Valence: 4.5/5 (target 0.6, song 0.49)


You can now provide feedback to refine recommendations.

Supported feedback types:
  Energy: 'more/less energetic', 'increase/decrease energy', etc.
  Valence: 'happier/sadder', 'more/less positive', 'higher/lower valence',  etc.
  Tempo: 'faster/slower', 'higher/lower tempo', etc.

  💡 Combine non-conflicting types: 'more energetic and happier'
  Exit: 'quit'

Your feedback: more energetic 

You requested:
  • "more energetic"

✓ I increased your target energy
  from 0.80 → 0.90.

📊 Top 5 songs remain the same.
   Average recommendation score decreased by 0.3 points.

1. Sunrise City - Neon Echo
   Score: 97.2/100
   ──────────────────────────────────────────────────────────────────
   ✓ Genre match: pop
   ✓ Mood match: happy
   Energy: 13.8/15 (target 0.9, song 0.82)
   Tempo: 9.6/10 (target 120.0, song 118.0)
   Valence: 3.8/5 (target 0.6, song 0.84)

2. Gym Hero - Max Pulse
   Score: 66.3/100
   ──────────────────────────────────────────────────────────────────
   ✓ Genre match: pop
   Energy: 14.5/15 (target 0.9, song 0.93)
   Tempo: 7.6/10 (target 120.0, song 132.0)
   Valence: 4.1/5 (target 0.6, song 0.77)

3. Rooftop Lights - Indigo Parade
   Score: 56.1/100
   ──────────────────────────────────────────────────────────────────
   ✓ Mood match: happy
   Energy: 12.9/15 (target 0.9, song 0.76)
   Tempo: 9.2/10 (target 120.0, song 124.0)
   Valence: 3.9/5 (target 0.6, song 0.81)

4. Neon Dreams - SynthMaster
   Score: 27.9/100
   ──────────────────────────────────────────────────────────────────
   Energy: 14.7/15 (target 0.9, song 0.88)
   Tempo: 8.4/10 (target 120.0, song 128.0)
   Valence: 4.8/5 (target 0.6, song 0.65)

5. Night Drive Loop - Neon Echo
   Score: 25.2/100
   ──────────────────────────────────────────────────────────────────
   Energy: 12.8/15 (target 0.9, song 0.75)
   Tempo: 8.0/10 (target 120.0, song 110.0)
   Valence: 4.5/5 (target 0.6, song 0.49)

Your feedback: more energetic and happier      

You requested:
  • "more energetic"
  • "happier"

✓ I increased your target energy
  from 0.90 → 1.00.
✓ I increased your target valence
  from 0.60 → 0.70.

📊 1 of the top 5 songs changed.
   Average recommendation score decreased by 1.0 points.

1. Sunrise City - Neon Echo
   Score: 96.2/100
   ──────────────────────────────────────────────────────────────────
   ✓ Genre match: pop
   ✓ Mood match: happy
   Energy: 12.3/15 (target 1.0, song 0.82)
   Tempo: 9.6/10 (target 120.0, song 118.0)
   Valence: 4.3/5 (target 0.7, song 0.84)

2. Gym Hero - Max Pulse
   Score: 66.2/100
   ──────────────────────────────────────────────────────────────────
   ✓ Genre match: pop
   Energy: 14.0/15 (target 1.0, song 0.93)
   Tempo: 7.6/10 (target 120.0, song 132.0)
   Valence: 4.6/5 (target 0.7, song 0.77)

3. Rooftop Lights - Indigo Parade
   Score: 55.0/100
   ──────────────────────────────────────────────────────────────────
   ✓ Mood match: happy
   Energy: 11.4/15 (target 1.0, song 0.76)
   Tempo: 9.2/10 (target 120.0, song 124.0)
   Valence: 4.4/5 (target 0.7, song 0.81)

4. Neon Dreams - SynthMaster
   Score: 26.4/100
   ──────────────────────────────────────────────────────────────────
   Energy: 13.2/15 (target 1.0, song 0.88)
   Tempo: 8.4/10 (target 120.0, song 128.0)
   Valence: 4.8/5 (target 0.7, song 0.65)

5. Pulsing Lights - ElectroWave
   Score: 23.9/100
   ──────────────────────────────────────────────────────────────────
   Energy: 12.3/15 (target 1.0, song 0.82)
   Tempo: 7.0/10 (target 120.0, song 135.0)
   Valence: 4.6/5 (target 0.7, song 0.78)

Your feedback: please don't make it faster, I want it slower

⚠️  Conflicting commands detected: faster, slower

Commands found:
  • faster (increase tempo)
  • slower (decrease tempo)

Proceed with these changes? (yes/no): no
Understood. Please try again with clearer instructions.

Your feedback: make it more danceable

❌ I didn't recognize that command.

Supported feedback types:
  Energy: 'more/less energetic', 'increase/decrease energy', etc.
  Valence: 'happier/sadder', 'more/less positive', etc.
  Tempo: 'faster/slower', 'higher/lower tempo', etc.

  💡 Combine non-conflicting types: 'more energetic and happier'
  Exit: 'quit'

Try again with one of these types:

Your feedback: quit

Thanks for using the Music Recommender! 🎵