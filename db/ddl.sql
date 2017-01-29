create or replace view `team_goals` as
select
    tm.team_team as team,
    tm.team_championship as championship,
    tm.match_id as `match`,
    tm.match_stage_id as stage,
    tm.match_group as `group`,
    tm.match_round as `round`,
    count(g.id) as goals
from
    `match` as m
    join `teammatch` as tm
    on 
        m.id =  tm.match_id and
        m.stage_id = tm.match_stage_id and
        m.stage_championship = tm.team_championship and
        m.`group` = tm.match_group and
        m.`round` = tm.match_round
    left join goal as g
    on
        tm.team_team = g.team_match_team_team and
        tm.match_id = g.team_match_match_id and
        tm.match_stage_id = g.team_match_match_stage_id and
        tm.team_championship = g.team_match_match_stage_championship and
        tm.match_group = g.team_match_match_group and
        tm.match_round = g.team_match_match_round
where
    m.state != 'not_started'
group by
    tm.team_team,
    tm.team_championship,
    tm.match_stage_id,
    tm.match_id,
    tm.match_group,
    tm.match_round;


create or replace view `no_draws` as
select
    championship, `match`, stage, `group`, `round`, goals
from
    team_goals
group by
    championship, `match`, stage, `group`, `round`, goals
having
    count(*) = 1;


create or replace view `winners` as
select
    tg.team, nd.*
from
    team_goals tg
    join (
        select
        championship, `match`, stage, `group`, `round`, max(goals) goals
        from
            no_draws
        group by
            championship, `match`, stage, `group`, `round`
    ) nd
    on
        nd.championship = tg.championship and
        nd.`match` = tg.`match` and
        nd.stage = tg.stage and
        nd.`group` = tg.`group` and
        nd.`round` = tg.`round` and
        nd.goals = tg.goals;


create or replace view `losers` as
select
    tg.team, nd.*
from
    team_goals tg
    join (
        select
        championship, `match`, stage, `group`, `round`, min(goals) goals
        from
            no_draws
        group by
            championship, `match`, stage, `group`, `round`
    ) nd
    on
        nd.championship = tg.championship and
        nd.`match` = tg.`match` and
        nd.stage = tg.stage and
        nd.`group` = tg.`group` and
        nd.`round` = tg.`round` and
        nd.goals = tg.goals;


create or replace view `draws` as
select
    tg_a.team,
    tg_a.championship,
    tg_a.`stage`,
    tg_a.`group`,
    tg_a.`round`,
    tg_a.`match`,
    tg_a.goals
from
    team_goals tg_a
    join team_goals tg_b
    on
        tg_a.championship = tg_b.championship and
        tg_a.`match` = tg_b.`match` and
        tg_a.stage = tg_b.stage and
        tg_a.`group` = tg_b.`group` and
        tg_a.`round` = tg_b.`round` and
        tg_a.goals = tg_b.goals
where
    tg_a.team != tg_b.team;
