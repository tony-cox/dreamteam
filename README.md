# Dreamteam

Dreamteam is a pulp-based integer programming formulation for the generalised dream team problem.
It is based on the premise that for a given 'expected score' per player and price per player, acting within the
selection rules of the game and some salary cap requirement, an optimal team exists and can be selected

## Installation

1. Clone or download the repository
2. Install with pip

    ```
    pip install path/to/cloned/repository
    ```

## Usage
To use Dreamteam to create a team:

- Sign up for a dreamteam/fantasy sports account of your choice.
- Scrape or otherwise extract the player data for all players available for selection.  This can often
be done simply by viewing the requests sent on the dreamteam website you are using and finding the one which has json
data for all players.
- Create a new Python 3 virtualenv and install the dreamteam package (see Installation above)
- Create a list of Position objects for each position in the comp that you need to put a specific number of players
into (e.g. forwards, backs, midfielders)

```
from dreamteam import Position
positions = [Position('Forward'), Position('Back')]
```

- Create a list of Squad objects for each squad in the comp that you need to create players for (e.g. Main Team,
Reserves, Bench, etc).  For each squad, provide a multiplier to apply to the expected score for players in that squad.
For example, you may want to have a multiplier of 1.0 for the Main Team and 0.5 for bench players to encourage
the solver to put more emphasis on the selection of players in the Main Team squad.  For each squad, also supply a
dictionary of `Position: int` representing the number of players which are required to be selected for each position
in that squad (for example, the Main Team may need 4 Forwards and 6 Backs).

```
from dreamteam import Squad
squads = [
    Squad('Main Team', value_multiplier=1.0, position_caps = {prositions[0]: 4, positions[1]:6)
]
```

- Create a list of players, which should include every player available for selection (as found in Step 2).  For each
player, you will need to provide a name, the team that the player plays for, the elgible squads the player can play in,
the eligible positions the player can be selected for, and an expected score.  The expected score is something that
you will need to determine via your own methods.  The dream team website may provide an estimate in the json data that
you scrape, or you may wish to use your own advanced machine learning methods to determine this, or anything in between.

```
from dreamteam import Player
players = [
    Player('Jeff', 'Harvey', 'Broncos', 70, positions[1:], squads),
    Player('Brett', 'Jones', 'Cowboys', 85, positions[:1], squads),
    ...
]
```

- Pass your list of positions, squads and players to the engine and wait for it to return.  If your dream team comp
has the concept of a 'captain' who receives a bonus score, you can also pass the `captain_value_bonus` kwarg to
the engine (0.0 is no bonus, 1.0 would be a captain that gets 'double score')

```
from dreamteam import solve
problem = solve(
    players, positions, squads, salary_cap=120000, captain_value_bonus=0.0,
)
```

- Once the engine returns the solved problem, you can inspect the problem object itself (which is returned straight
from Pulp) or simply inspect your player objects which will now have been mutated and have the properties
'selected_in_solution', `solution_position`, `solution_squad` and `solution_captain` set on them
(which will be `False`, `None`, `None`, and `False` respectively for players not selected in the solution)

```
solution_players = [p for p in players if p.selected_in_solution]
for player in solution_players:
    print(player)
```

## License
Dreamteam is supplied as open source under the MIT license.  See LICENSE for details.

## API Documentation
API Documentation is a work in progress.  Please feel free to inspect the code in the meantime (there are only
two fairly small modules)

## Mathematical Formulation
The integer programming (IP) model that is used to solve the Dreamteam problem will be included as part of the API
documentation when it is complete.
