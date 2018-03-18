import pulp
import collections as col

from . import structures

from typing import List, Dict, Tuple


class LpPlayerVariable(pulp.LpVariable):

    def __init__(self, name, player, objective_coef, lowBound=0, upBound=1, cat=pulp.LpInteger, e=None):
        super().__init__(name, lowBound, upBound, cat, e)
        self.player = player  # type: structures.Player
        self.objective_coef = objective_coef  # type: float

    def setInitialValue(self, val):
        return 0


# types using above class
PlayerVarMap = Dict[structures.Squad, Dict[structures.Position, Dict[structures.Player, LpPlayerVariable]]]
CaptainVarMap = Dict[structures.Player, LpPlayerVariable]


def _get_player_variables(
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
) -> PlayerVarMap:
    lp_vars = col.defaultdict(lambda: col.defaultdict(dict))

    for pos in positions:
        for squad in squads:
            for p in players:
                lp_vars[squad][pos][p] = LpPlayerVariable(
                    name='{}_{}_{}'.format(squad.name, pos.name, p.name),
                    player=p,
                    objective_coef=squad.value_multiplier * p.expected_score,
                )
    return lp_vars


def _get_captain_variables(
        players: List[structures.Player],
        captain_value_bonus: float,
) -> CaptainVarMap:
    lp_vars = dict()
    for p in players:
        lp_vars[p] = LpPlayerVariable(
            name='captain_{}'.format(p.name),
            player=p,
            objective_coef=captain_value_bonus * p.expected_score,
        )
    return lp_vars


def _get_variables(
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        captain_value_bonus: float,
) -> Tuple[PlayerVarMap, CaptainVarMap]:
    player_vars = _get_player_variables(players, positions, squads)
    captain_vars = _get_captain_variables(players, captain_value_bonus)
    return player_vars, captain_vars


def _get_problem_with_objective(
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
        captain_vars: CaptainVarMap,
) -> pulp.LpProblem:
    problem = pulp.LpProblem('afl_dream_team', pulp.LpMaximize)
    objective = pulp.lpSum([
        pulp.LpAffineExpression(
            {
                var: var.objective_coef
                for squad in squads
                for pos in positions
                for var in player_vars[squad][pos].values()
            }
        ),
        pulp.LpAffineExpression(
            {
                var: var.objective_coef
                for var in captain_vars.values()
            }
        )
    ])
    problem.setObjective(objective)
    return problem


def _add_constraints_for_squad_position_cap(
        problem: pulp.LpProblem,
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
) -> None:
    for squad in squads:
        for pos in positions:
            cap = squad.position_caps[pos]
            problem.addConstraint(pulp.LpConstraint(
                pulp.LpAffineExpression({var: 1 for var in player_vars[squad][pos].values()}),
                pulp.LpConstraintEQ,
                'Choose exactly {} players in position {} in squad {}'.format(cap, pos.name, squad.name),
                cap
            ))


def _add_constraints_for_captain_must_be_on_team(
        problem: pulp.LpProblem,
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
        captain_vars: CaptainVarMap,
) -> None:
    for p in players:
        problem.addConstraint(pulp.LpConstraint(
            pulp.lpSum([
                pulp.LpAffineExpression({
                    player_vars[squad][pos][p]: 1
                    for squad in squads
                    for pos in positions
                }),
                pulp.LpAffineExpression({
                    captain_vars[p]: -1
                })
            ]),
            pulp.LpConstraintGE,
            '{} can only be captain if also in the team'.format(p.name)
        ))


def _add_constraint_for_only_one_captain(
        problem: pulp.LpProblem,
        players: List[structures.Player],
        captain_vars: CaptainVarMap,
) -> None:
    problem.addConstraint(pulp.LpConstraint(
        pulp.LpAffineExpression({
            captain_vars[p]: 1
            for p in players
        }),
        pulp.LpConstraintLE,
        'There can only be one captain selected',
        1,
    ))


def _add_constraints_for_each_player_only_selected_once(
        problem: pulp.LpProblem,
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
) -> None:
    for p in players:
        problem.addConstraint(pulp.LpConstraint(
            pulp.LpAffineExpression({
                player_vars[squad][pos][p]: 1
                for squad in squads
                for pos in positions
            }),
            pulp.LpConstraintLE,
            '{} can only play for one squad and in one position'.format(p.name),
            1
        ))


def _add_constraint_for_salary_cap(
        problem: pulp.LpProblem,
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
        salary_cap: float,
) -> None:
    problem.addConstraint(pulp.LpConstraint(
        pulp.LpAffineExpression({
            player_vars[squad][pos][p]: p.price
            for squad in squads
            for pos in positions
            for p in players
        }),
        pulp.LpConstraintLE,
        'Total cost of all players in team must not exceed the salary cap',
        salary_cap
    ))


def _set_upper_bound_on_ineligible_player_vars_to_zero(
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
) -> None:
    # todo: instead of having this constraint, we can just have less player_vars and the problem is easier for solver
    for p in players:
        for squad in squads:
            for pos in positions:
                if squad not in p.eligible_squads or pos not in p.positions:
                    player_vars[squad][pos][p].upBound = 0


def _add_constraints(
        problem: pulp.LpProblem,
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
        captain_vars: CaptainVarMap,
        salary_cap: float,
) -> None:
    _add_constraints_for_squad_position_cap(problem, positions, squads, player_vars)
    _add_constraints_for_captain_must_be_on_team(problem, players, positions, squads, player_vars, captain_vars)
    _add_constraint_for_only_one_captain(problem, players, captain_vars)
    _add_constraints_for_each_player_only_selected_once(problem, players, positions, squads, player_vars)
    _add_constraint_for_salary_cap(problem, players, positions, squads, player_vars, salary_cap)
    _set_upper_bound_on_ineligible_player_vars_to_zero(players, positions, squads, player_vars)


def _process_result(
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        player_vars: PlayerVarMap,
        captain_vars: CaptainVarMap,
) -> None:
    captain_found = False
    for p in players:
        for squad in squads:
            for pos in positions:
                var_value = player_vars[squad][pos][p].varValue
                if var_value is not None and var_value > 0.0:
                    p.selected_in_solution = True
                    p.solution_position = pos
                    p.solution_squad = squad
                    if captain_vars[p].varValue > 0.0:
                        assert captain_found is False, 'Two captains have been set in solution'
                        p.solution_captain = True
                        captain_found = True


def solve(
        players: List[structures.Player],
        positions: List[structures.Position],
        squads: List[structures.Squad],
        salary_cap: float,
        captain_value_bonus: float=0,
        solver=None,
        **kwargs
) -> pulp.LpProblem:
    """
    Formulates and solves a generic dream team player selection problem

    :param players: players available for selection
    :param positions: positions that players can be put into
    :param squads: squads that players can play for
    :param salary_cap: the total amount that you are allowed to spend on players
    :param captain_value_bonus: the bonus (multiplied by expected score) that a captain is worth. default 0.
    :param solver: the specific solver to be used, defaults to the default solver chosen by pulp.
    :param kwargs: extra kwargs to be passed into pulp.LpProblem.solve()
    :return: The solved pulp.LpProblem
    """
    player_vars, captain_vars = _get_variables(players, positions, squads, captain_value_bonus)
    problem = _get_problem_with_objective(positions, squads, player_vars, captain_vars)
    _add_constraints(problem, players, positions, squads, player_vars, captain_vars, salary_cap)
    problem.solve(solver, **kwargs)
    _process_result(players, positions, squads, player_vars, captain_vars)
    return problem
