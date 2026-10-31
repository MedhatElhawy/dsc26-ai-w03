# AI usage · dsc26-dsa-w03

Keep the three headings below exactly as written. The grader checks that they exist; if this file is
missing or a heading is missing or renamed, the grader stops and reports 0. Your Track Mentor reads the
content, and the W8 defence can ask about it.

## Tools

<!-- Which AI tools you used, and for which parts of the task (e.g. "Claude: first draft of the money parser"). Write "None" if you used none. -->
- Gemini / GitHub Copilot: Used for structuring the statistical module and verifying SciPy bootstrap signatures.

## What AI got wrong

<!-- At least one thing an assistant got wrong that you changed, and how you noticed: a test, the docs, running it. -->
- The initial bootstrap implementation used deprecated SciPy syntax for percentile confidence intervals, which was caught and fixed when running local tests.

## In my own words

<!-- Answer without AI, one or two sentences each. -->

1. In the sample, the pilot couriers have a higher overall failure rate but a lower one in each slot. Which number would you show Sherif, and what would you tell him about the pilot?

- I would show Sherif the slot-stratified failure rates and explain Simpson's Paradox: the pilot couriers appeared worse overall only because they were disproportionately assigned to harder delivery slots, even though they outperform regular couriers within every individual slot.

2. Why might a zone that really is worse not be flagged by your screen?

- A genuinely worse zone might not be flagged due to a small sample size ($n < 30$) or because the Benjamini-Hochberg false-discovery correction adjusted its p-value upward to control for multiple testing across all zones.