import math
import random

from pony import orm
from pony.orm import select

from . import app


db = orm.Database()
random.seed(4)


class FbcmError(Exception):
    def __init__(self, msg, status_code=None):
        Exception.__init__(self, msg)
        self.msg = msg
        self.status_code = status_code if status_code is not None else 200

    def to_dict(self):
        return {
            'description': self.msg,
            'status': 'error'
        }

    def __str__(self):
        return self.msg


class Person(db.Entity):
    id = orm.PrimaryKey(str, 10)
    name = orm.Required(str, 40)
    lastname = orm.Required(str, 40)


class Player(Person):
    team = orm.Optional('Team')
    position = orm.Optional('Position')
    number = orm.Optional(int)
    goals = orm.Set('Goal')
    orm.composite_key(team, number)


class Position(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, 50, unique=True)
    players = orm.Set(Player)


class Team(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, 90, unique=True)
    championships = orm.Set('TeamChampionship')
    players = orm.Set(Player)


class Championship(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    name = orm.Required(str, 90, unique=True)
    description = orm.Optional(str, 500)
    teams = orm.Set('TeamChampionship')
    stages = orm.Set('Stage')  # Only four
    points_winner = orm.Required(int)
    points_draw = orm.Required(int)
    points_loser = orm.Required(int)

    @property
    def state(self):
        stage = self.stages.select(lambda stage: stage.id == 0)[:1][0]
        if stage.matches.is_empty():
            return "not_started"
        else:
            return (
                "finished"
                if all(s.is_finish for s in self.stages)
                else "started"
            )

    @property
    def top_players(self):
        return select(
            (p, orm.count(g.id))
            for p in Player
            for g in Goal
            if g.team_match.team.championship.id == self.id
            and g.player == p
        ).order_by(orm.desc(2)).limit(10)


class Match(db.Entity):
    id = orm.Required(int)
    stage = orm.Required('Stage')
    group = orm.Required(int)
    round = orm.Required(int)
    team_matches = orm.Set('TeamMatch')  # Just two
    # not_started, started, finished
    state = orm.Required(str, default='not_started')
    orm.PrimaryKey(id, stage, group, round)

    @property
    def goals(self):
        return select(
            (tm.team.team, goal)
            for tm in TeamMatch
            for goal in tm.goals
            if tm.match == self
        ).prefetch(Player)

    @property
    def score(self):
        return select(
            (tm, tm.goals.count())
            for tm in TeamMatch
            if tm.match == self.match
        ).order_by(
            lambda tm_goals: tm_goals[1]
        )

    @property
    def is_draw(self):
        return len(set(
            goals
            for team, goals in self.score
        )) == self.score.count()

    def after_update(self):
        stage = self.stage
        if stage.is_finish:
            n_stage = stage.next_stage
            if n_stage:
                n_stage.create_matches()

    def add_goals(self):
        if self.state == 'finished':
            return
        self.state = 'started'
        na = random.randint(0, 5)
        nb = random.randint(0, 5)
        while self.stage.draw and na == nb:
            na = random.randint(0, 5)
            nb = random.randint(0, 5)
            
        for tm, n in zip(self.team_matches, [na, nb]):
            for _ in range(n):
                tm.goals.create(
                    player=tm.team.team.players.random(1)[:][0]
                )
        self.state = 'finished'


class Goal(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    player = orm.Required(Player)
    team_match = orm.Required('TeamMatch')


class Stage(db.Entity):
    id = orm.Required(int)  # Must be secuential
    championship = orm.Required(Championship)
    name = orm.Required(str)
    num_groups = orm.Required(int)
    algorithm = orm.Required(str)  # Algorithm for make the rounds
    num_select = orm.Required(int)  # number of winners for next stage
    draw = orm.Required(bool, default=True)  # Allow draws?
    matches = orm.Set(Match)
    orm.PrimaryKey(id, championship)

    def create_matches(self):
        if not self.matches.is_empty():
            raise FbcmError("Etapa ya comenzada")
        for group, round, match, teams in self._generate_matches():
            match = self.matches.create(
                id=match,
                group=group,
                round=round
            )
            for team in teams:
                match.team_matches.create(
                    team=team
                )

    def _generate_matches(self):
        for group in range(1, self.num_groups + 1):
            for it in self.pre_generate_matches(group):
                yield it

    def pre_generate_matches(self, group):
        teams = self.get_teams_matches(group)[:]
        n = len(teams)
        generator = self._get_matches_generator()
        for round, match, teams_index in generator(n):
            yield group, round, match, (teams[i] for i in teams_index)

    def _get_matches_generator(self):
        """All generators must be return a:
            - round
            - match and
            - teams
        """
        matches_generators = {
            'round-robin': Stage.round_robin,
            'first-last': Stage.first_last,
            'random': Stage.random
        }
        return matches_generators.get(self.algorithm)

    @staticmethod
    def round_robin(n):
        max_odd = n - 1 if n % 2 == 0 else n
        team_a = 0
        team_b = max_odd - 1
        for round in range(1, n - (n % 2 == 0) + 1):
            for match in range(n//2):
                if match == 0 and n % 2 == 0:
                    yield round, match, (team_a, n - 1)
                else:
                    yield round, match, (team_a, team_b)
                    team_b = (team_b - 1) % max_odd
                team_a = (team_a + 1) % max_odd

    @staticmethod
    def first_last(n):
        # TODO: when n is odd?
        return (
            (1, match, (team_a, n - team_a - 1))
            for match, team_a in enumerate(range(n//2))
        )

    @staticmethod
    def random(n):
        teams = list(range(n))
        random.Random(4).shuffle(teams)
        # TODO: if n is odd?
        i = 0
        for match in range(n//2):
            team_a = teams[i]
            team_b = teams[i + 1]
            i += 2
            yield (1, match, (team_a, team_b))

    def get_table(self, group):
        championship_id = self.championship.id
        stage = self.id

        championship = self.championship
        pwinner = championship.points_winner
        ploser = championship.points_loser
        pdraw = championship.points_draw

        result = db.select("""SELECT * FROM positions_table
            WHERE championship=$championship_id and
            stage=$stage and `group`=$group
            ORDER BY pg * $pwinner + pp * $ploser + pe * $pdraw DESC,
            gf - gc DESC, gf DESC, gc ASC
            """)
        for r in result:
            team, championship, stage, group, pg, pp, pe, gf, gc = r
            yield (
                Team[team],
                pg, pe, pp,
                gf, gc,
                pg*pwinner + pp*ploser + pe*pdraw
            )

    def get_teams_matches(self, group):
        if self.id == 0:
            teams = select(
                tc
                for tc in TeamChampionship
                if tc.championship == self.championship
            )
            return teams.order_by(
                lambda tc: tc.team.name
            ).page(
                group,
                pagesize=math.ceil(len(teams)/self.num_groups)
            )
        else:
            prev_stage = Stage.get(
                id=self.id - 1,
                championship=self.championship
            )
            winners = [
                TeamChampionship.get(
                    team=row[0],
                    championship=self.championship
                )
                for row in prev_stage.get_winners()
            ]
            if self.algorithm == 'first-last':
                n = len(winners)
                if n//2 <= group - 1:
                    return []
                else:
                    first = winners[group - 1]
                    if n//2 >= group:
                        return [first, winners[n - group]]
                    else:
                        return [first]
            elif self.algorithm == 'random':
                random.Random(4).shuffle(winners)
                n = len(winners)//self.num_groups
                l = (group - 1) * n
                r = (group + n)
                return winners[l:r]

    def get_winners(self):
        result = [
            t
            for group in range(1, self.num_groups + 1)
            for i, t in enumerate(self.get_table(group))
            if i < self.num_select
        ]

        result.sort(
            key=lambda t: (t[6], t[4] - t[5], t[4], 9999 - t[5])
        )
        return result

    def get_matches(self, group):
        return select(
            m for m in Match
            if m.group == group and m.stage == self
        ).order_by(
            lambda match: match.round
        )

    def random_marker(self, group):
        for m in self.matches:
            if m.group == group:
                m.add_goals()

    @property
    def is_finish(self):
        return all(
            m.state == 'finished'
            for m in self.matches
        )

    @property
    def is_predictable(self):
        stage = self.prev_stage
        if stage:
            return not stage.is_finish
        return False

    @property
    def prev_stage(self):
        return Stage.get(
            id=self.id - 1,
            championship=self.championship
        )

    @property
    def next_stage(self):
        return Stage.get(
            id=self.id + 1,
            championship=self.championship
        )


class TeamMatch(db.Entity):
    team = orm.Required('TeamChampionship')
    match = orm.Required(Match)
    goals = orm.Set(Goal)
    orm.PrimaryKey(team, match)

    @property
    def is_draw(self):
        return self.match.is_draw

    @property
    def is_winner(self):
        if not self.is_draw:
            return self.match.score[:1] == self.team
        else:
            raise FbcmError("Es un empate!")


class TeamChampionship(db.Entity):
    team = orm.Required(Team)
    championship = orm.Required(Championship)
    matches = orm.Set(TeamMatch)
    orm.PrimaryKey(team, championship)


db.bind(
    'mysql',
    host=app.config['DB_HOST'],
    user=app.config['DB_USER'],
    passwd=app.config['DB_PASSWD'],
    db=app.config['DB_NAME']
)
db.generate_mapping(create_tables=True)
