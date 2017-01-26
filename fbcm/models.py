import math
import random

from pony import orm

from . import app


db = orm.Database()


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
            return "started"
        return "finished"  # TODO


class Match(db.Entity):
    id = orm.Required(int)
    stage = orm.Required('Stage')
    group = orm.Required(int)
    round = orm.Required(int)
    team_matches = orm.Set('TeamMatch')  # Just two
    is_finish = orm.Required(bool, default=False)
    orm.PrimaryKey(id, stage, group, round)


class Goal(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    player = orm.Required(Player)  # Reverse to player of CompetinTeam
    team_match = orm.Required('TeamMatch')


class Stage(db.Entity):
    id = orm.Required(int)  # Must be secuential
    championship = orm.Required(Championship)
    name = orm.Required(str)
    num_groups = orm.Required(int)
    algorithm = orm.Required(str)  # Algorithm for make the rounds
    num_select = orm.Required(int)  # number of winners for next stage
    draw = orm.Required(bool, default=True)  # Permitir empates?
    matches = orm.Set(Match)
    orm.PrimaryKey(id, championship)

    def create_matches(self):
        if not self.matches.is_empty():
            raise FbcmError("Etapa ya comenzada")
        for group, round, match, teams in self._generate_matches():
            print(group, round, teams)
            match = self.matches.create(
                id=match,
                group=group,
                round=round,
                is_finish=False
            )
            for team in teams:
                match.team_matches.create(
                    team=team
                )

    def _generate_matches(self):
        for group in range(1, self.num_groups + 1):
            teams = self.get_teams(group)[:]
            n = len(teams)
            generator = self._get_matches_generator()
            for round, match, teams_index in generator(n):
                yield group, round, match, (teams[i] for i in teams_index)

    def _get_matches_generator(self):
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
        teams = set(range(n))
        # TODO: if n is odd?
        for match in range(n//2):
            team_a = random.select(teams)
            teams.remove(team_a)
            team_b = random.select(teams)
            teams.remove(team_b)
            yield (1, match, (team_a, team_b))

    def get_teams(self, group):
        if self.id == 0:
            teams = self.championship.teams
            return teams.order_by(
                lambda team_match: team_match.team.name
            ).page(group, pagesize=math.ceil(len(teams)/self.num_groups))
        else:
            # TODO
            return []

    def get_matches(self, group):
        return self.matches.select(
            lambda match: match.group == group
        ).order_by(
            lambda match: match.round
        )


class TeamMatch(db.Entity):
    team = orm.Required('TeamChampionship')
    match = orm.Required(Match)
    goals = orm.Set(Goal)
    orm.PrimaryKey(team, match)


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
