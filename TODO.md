# TODO
- Codify rules from Excel file example
  - Probability of a specific match is (number of paths in which they're matched)/(total number of paths)
  - Ceremony Results
    - If n_PM = 0
      - Drop paths containing any of the current matches.
    - If n_PM = 10
      - Contestants win; End of game
    - Else (0 < n_PM < 10)
      - Drop paths that do not contain exactly n_PM
  - Truth Booth
    - If PM = True
      - Drop paths that don't contain that match
    - Else
      - Drop paths that do contain that match

Notes
----
- calculate counts and probabilities at all steps
- identify all paths that a match is part of
- might want to use a mask or another array/matrix to store results of ceremonies and truth booths.
- User will interact entirely through Season object.

Objects
-----
Contestant : (object)
  An individual on the show, not grouped into Guys or Girls, which are subclasses of Contestant.
Guy, Girl : (Contestant)
  One member of a "team" of N unique Contestants that has a unique Perfect Match on the other
  "team." Every Guy has one and only one Girl that is a Perfect Match.
Match : (object)
  A pairing of a Guy and a Girl.  At each ceremony, every Guy and Girl have a match (except on Season 2,
  but that's not implemented yet).
Matrix : (object)
  The internal accounting of feasible paths in a Numpy array.  Has methods to update the set of feasible
  paths based on a Ceremony or Truth Booth.
Season : (object)
  State-full object used to walk through events in a season and calculate metrics.
