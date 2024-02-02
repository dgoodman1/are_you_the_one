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


- calculate counts and probabilities at all steps
- identify all paths that a match is part of
- might want to use a mask or another array/matrix to store results of ceremonies and truth booths.
- 