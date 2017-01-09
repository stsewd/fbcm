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
    position = orm.Optional(str)
    number = orm.Optional(int)
    goals = orm.Set('Goal')
    orm.composite_key(team, number)


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


class Match(db.Entity):
    id = orm.PrimaryKey(int, auto=True)
    round = orm.Required(int)  # Depends on num_rounds of Stage
    group = orm.Required('Group')
    team_matches = orm.Set('TeamMatch')  # Just two
    is_finish = orm.Required(bool, default=False)


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
    groups = orm.Set('Group')  # Number defined by each stage
    orm.PrimaryKey(id, championship)


class Group(db.Entity):
    id = orm.Required(int)
    stage = orm.Required(Stage)
    matches = orm.Set(Match)
    orm.PrimaryKey(id, stage)


class TeamMatch(db.Entity):
    team = orm.Required('TeamChampionship')
    match = orm.PrimaryKey(Match)
    goals = orm.Set(Goal)


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
