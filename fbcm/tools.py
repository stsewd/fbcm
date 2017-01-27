from .models import Stage, FbcmError


def add_default_stages(championship):
    Stage(
        id=0,
        championship=championship,
        name="Primera etapa",
        num_groups=4,
        algorithm='round-robin',
        num_select=2,
        draw=True
    )

    Stage(
        id=1,
        championship=championship,
        name="Cuartos de final",
        num_groups=4,
        algorithm="first-last",
        num_select=1,
        draw=False
    )

    Stage(
        id=2,
        championship=championship,
        name="Semifinal",
        num_groups=2,
        algorithm="random",
        num_select=1,
        draw=False
    )

    Stage(
        id=3,
        championship=championship,
        name="Final",
        num_groups=1,
        algorithm="random",
        num_select=1,
        draw=False
    )


def get_first_error(form):
    if form.errors:
        return list(form.errors.values())[0][0]
    else:
        return ""


def validate_player(team, player, number):
    error = ""
    if player in team.players:
        error = "El jugador ya se encuentra registrado en el equipo."
    elif player.team:
        error = "El jugador ya pertenece a otro equipo."
    elif team.players.select(lambda player: player.number == number):
        error = "El número {} ya está ocupado.".format(number)

    if error:
        raise FbcmError(error)
