# Global FTLD-CDR Calculator

### Simple app to calculate FTLD-CDR Global for the ReDLat project

[Click here to run it on streamlit](Not yet available)

#### FTLD-CDR Scoring Instructions.

Two scores must be obtained:

- CDR Box Sum (automatically calculated in REDCap): Calculate the sum of values for all responses (including the two additional domains) and enter the total score in the provided space.
- Global CDR: derived from the scores in each of the eight categories ("box scores").
The rules for determining the FTLD-CDR global score are as follows. (Remember, it involves the eight domains or boxes):

1) If all domains are 0, the FTLD-CDR global score is 0.

2) If the maximum domain score is 0.5, the FTLD-CDR global score is 0.5.

3) If the maximum domain score is greater than 0.5 in any domain, the following applies:

  - A) If the maximum domain score is 1 and all other domains are 0, the FTLD-CDR global score is 0.5.
  - B) If the maximum domain score is 2 or 3 and all other domains are 0, the FTLD-CDR global score is 1.
  - C) If the maximum domain score occurs only once, and there is another score other than zero, the FTLD-CDR global score is one level lower than the level corresponding to the maximum impairment (for example, if the maximum = 2, and there is another score other than zero, the FTLD-CDR global score is 1; if the maximum = 1, and there is another score other than zero, the FTLD-CDR global score is 0.5).
  - D)If the maximum domain score occurs more than once (for example, 1 in 2 domains, 2 in 2 domains), then the FTLD-CDR global score is that maximum domain score.

