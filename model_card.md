# Reflection and Ethics

## Limitations and Biases

Like the other recommender system, this system uses a small fixed dataset of 20 songs, so the quality and variety of its recommendations are limited by the songs included in the CSV file. This also limits it's ability to discover new user music preferences. As before, the system also relies heavily on genre and mood matches for scoring, which gives those categories a strong influence on the final recommendation scores. The feedback parser also only accepts a predefined set of commands, so it cannot understand all input given to it.

## Potential Misuse and Prevention

This AI could be misused if users assume it understands every prompt or expect it to make decisions beyond changing a user's preference profile. To reduce this risk, it first provides users a list of supported commands so they don't get confused. I also added detection of unsupported, conflicting or ambiguous user input. When feedback is found to be conflicting or ambiguous, the agent first asks the user to confirm the intended action before it applies. The system also enforces bounds on profile values, and records important events in a log file for later review.

## What Surprised Me?

The biggest surprise of this project was how many edge cases I needed to handle. A command like "please don't make it faster, I want it slower" would make the system apply the "faster" command because it was the first matching keyword in the sentence. This led me to need to create guardrails that detect negation, conflicting commands, and unsupported requests. Testing also showed the importance of keeping the profile value scores in bounds so a user could not enter a score so out of bounds that the scoring algorithm for that attribute would always be zero.

## Collaboration With AI

One instance where AI gave a helpful suggestion was at the start of my project, where it helped me plan out the feedback into a Analyze → Plan → Act → Evaluate → Explain agentic workflow, and adding a confirmation step for ambiguous requests.

One suggestion that was flawed was when I was working on explaining the feedback to the user. Initially, the AI suggested simply printing, "Your feedback has been applied." I asked it to improve the explanation by describing which command it applied, how many of the top five songs changed, and how much the average recommendation score changed after the feedback was applied. This made the system much more transparent to the user