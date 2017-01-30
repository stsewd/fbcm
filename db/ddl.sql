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


create or replace view `positions_table` as
select
    w.team,
    w.championship,
    w.stage,
    w.`group`,
    count(w.goals) as pg,
    count(Null) as pp,
    count(Null) as pe,
    sum(w.goals) as gf,
    sum(l.goals) as gc
from
    winners as w
    left join losers l
    on
        w.championship = l.championship and
        w.`match` = l.`match` and
        w.stage = l.stage and
        w.`group` = l.`group` and
        w.`round` = l.`round` and
        w.goals > l.goals
group by
    w.team,
    w.championship,
    w.stage,
    w.`group`

UNION
    
select
    l.team,
    l.championship,
    l.stage,
    l.`group`,
    count(Null) as pg,
    count(l.goals) as pp,
    count(Null) as pe,
    sum(l.goals) as gf,
    sum(w.goals) as gc
from
    losers as l
    left join winners w
    on
        l.championship = w.championship and
        l.`match` = w.`match` and
        l.stage = w.stage and
        l.`group` = w.`group` and
        l.`round` = w.`round` and
        l.goals < w.goals
group by
    l.team,
    l.championship,
    l.stage,
    l.`group`

UNION

select
    d.team,
    d.championship,
    d.stage,
    d.`group`,
    count(Null) as pg,
    count(Null) as pp,
    count(d.goals) as pe,
    sum(d.goals) as gf,
    sum(d.goals) as gc
from
    draws as d
group by
    d.team,
    d.championship,
    d.stage,
    d.`group`;


CREATE DEFINER=`root`@`localhost` PROCEDURE `get_position_table`(
	IN championship_id varchar(10),
    IN stage_id varchar(10),
    IN group_id varchar(10))
BEGIN
	SELECT
		@pwinner := points_winner,
        @pdraw := points_draw,
        @ploser := points_loser
	FROM
		championship
	WHERE
		id = championship_id;
	
	SELECT 
		*
	FROM
		positions_table
	WHERE
		championship = championship_id AND
		stage = stage_id AND `group` = group_id
	ORDER BY
		pg * @pwinner + pp * @ploser + pe * @pdraw DESC,
		gf - gc DESC, gf DESC, gc ASC;
END
