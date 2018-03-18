import json

from typing import Optional, List, Dict


class Position(object):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__()


class Squad(object):
    def __init__(self, name: str, value_multiplier: float, position_caps: Dict[Position, int]) -> None:
        self.name = name
        self.value_multiplier = value_multiplier
        self.position_caps = position_caps
        super().__init__()


class Player(object):
    def __init__(
            self,
            given_name: str,
            surname: str,
            team: str,
            expected_score: float,
            positions: List[Position],
            eligible_squads: List[Squad],
            price: float,
            games_played_prev_year: Optional[int]=None,
    ) -> None:
        assert given_name is not None, 'Player must have a given name'
        self.given_name = given_name
        self.surname = surname
        self.team = team
        self.games_played_prev_year = games_played_prev_year
        self.positions = positions
        self.eligible_squads = eligible_squads
        self.price = price
        self.expected_score = expected_score
        self.selected_in_solution = False
        self.solution_position = None
        self.solution_squad = None
        self.solution_captain = False
        super().__init__()

    @property
    def price_score_ratio(self):
        if self.price and self.expected_score:
            return self.expected_score / self.price * 1000
        return 0

    @property
    def name(self):
        if self.given_name and self.surname:
            return '{} {}'.format(self.given_name, self.surname)
        else:
            return self.given_name

    @property
    def key(self):
        return '_'.join(self.name.split()).lower()

    def as_dict(self):
        return {
            'name': self.name,
            'given_name': self.given_name,
            'surname': self.surname,
            'team_code': self.team,
            'games_played_prev_year': self.games_played_prev_year,
            'expected_score': self.expected_score,
            'positions': self.positions,
            'eligible_squads': self.eligible_squads,
            'price': self.price,
            'solution_position': self.solution_position,
            'solution_main_team': self.solution_main_team,
            'solution_captain': self.solution_captain,
        }

    def __repr__(self) -> str:
        return json.dumps(self.as_dict())