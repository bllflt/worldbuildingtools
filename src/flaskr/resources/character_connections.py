from flask_restful import Resource
from flaskr.model import db
from sqlalchemy import text


class CharacterConnections(Resource):
    def get(self, cid):

        rv = []
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
            union all
            select
              null as pid,
              null as ptype,
              id as pcid,
              name as pcname,
              sex as pcsex,
              null as ccid,
              null as ccname,
              null as ccsex
            from
              character
            where
              id = :cid
            '''), {'cid': cid}).mappings().all()
        person = rows.pop()
        rv.append({
            'data': {'id': person['pcid'],
                     'label': person['pcname'],
                     'gender': person['pcsex']}})
        for row in rows:
            if not row['pid'] in seen_pid:
                rv.append({'data': {'id': f'p{row["pid"]}',
                                    'type': f'{row["ptype"]}'}})
                seen_pid[row['pid']] = True
            if not row['ccid'] in seen_pcid:
                rv.extend([{
                    'data': {
                        'id': row['pcid'],
                        'label': row['pcname'],
                        'gender': row['pcsex']
                    }}, {
                    'data': {
                        'source': row['pcid'],
                        'target': f'p{row["pid"]}',
                        'type': row['ptype']
                    }}, {
                    'data': {
                        'source': person['pcid'],
                        'target': f'p{row["pid"]}',
                        'type': row['ptype']
                    }
                }])
                seen_pcid[row['pcid']] = True
            if row['ccid'] is not None:
                rv.extend([{
                    'data': {
                        'id': row['ccid'],
                        'label': row['ccname'],
                        'gender': row['ccsex']
                    }}, {
                    'data': {
                        'source': f'p{row["pid"]}',
                        'target': row['ccid'],
                        'type': 'parent_child'
                    }
                }])
        return rv
