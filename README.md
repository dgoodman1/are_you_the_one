# Are You the One?
Simulate the probabilistic model behind the MTV show [Are You the One?](https://en.wikipedia.org/wiki/Are_You_the_One%3F).  This project has three goals:

1. See if you can predict who the matches are before the couples.
2. Determine optimal strategies for the contestants after new information is provided.
3. Test the impacts of changing the rules.


Implementation
----
- On the outset, each combination has a probability of 1/10.
- The number of correct matches, x, tells us the probability of any one of the current matches being correct, i.e. x/10.  The other matches for a given contestant thus have a probability of (1 - x/10)/(# of remaining other matches).
- 
