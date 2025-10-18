from flask_restful import Resource
from sqlalchemy import text

from flaskr.model import db


class CharacterConnections2(Resource):
    def get(self, cid):

        rv = {}
        seen_pid = {}
        seen_pcid = {}
        rows = db.session.execute(text('''
            with cte as (
                select 
                    partnership_id as pid
                from
                    partnership_participants
                where
                    partnership_participants.character_id = :cid
            )
            select
                partnerships.id  as pid,
                partnerships.type as ptype,
                pc.id as pcid,
                pc.name as pcname,
                pc.sex as pcsex,
                cc.id as ccid,
                cc.name as ccname,
                cc.sex as ccsex
            from
                partnerships
            join
                cte on cte.pid = partnerships.id
            join
                partnership_participants as pp on pp.partnership_id = partnerships.id
            join
                character as pc on pp.character_id = pc.id
            left join
                offspring as o on o.partnership_id = partnerships.id
            left join
                character as cc on o.character_id = cc.id
            where
                pc.id <> :cid
            '''), {'cid': cid}).mappings().all()
        for row in rows:
            if not row['pid'] in seen_pid:
                rv[row['pid']] = {'id': row['pid'], 'type': row['ptype'], 'with': [], 'children': []}
                seen_pid[row['pid']] = True
            if not row['pcid'] in seen_pcid:
                rv[row['pid']]['with'].append({'id': row['pcid'], 'name': row['pcname'], 'sex': row['pcsex']})
                seen_pcid[row['pcid']] = True
            if row['ccid'] is not None:
                rv[row['pid']]['children'].append({'id': row['ccid'], 'name': row['ccname'], 'sex': row['ccsex']})
        return list(rv.values())
 

           