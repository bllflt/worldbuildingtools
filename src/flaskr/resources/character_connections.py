from flask import json
from flask_restful import Resource
from sqlalchemy import text

from flaskr.model import db


class CharacterConnections(Resource):
    def get(self, cid):

        rows = db.session.execute(text('''
WITH my_partnerships AS (
  SELECT partnership_id AS pid
  FROM partnership_participants
  WHERE character_id = :cid
)
SELECT
  p.id AS partnership_id,
  p.type AS partnership_type,
  p.name AS partnership_name,
  p.is_primary AS partnership_is_primary,
  p.legitimate AS partnership_legitimate,        
  '[' || GROUP_CONCAT(
    '{"id":' || c.id ||
    ',"name":"' || REPLACE(c.name, '"','\"') ||
    '","sex":' || c.sex ||
    ',"role":' || pp.role || '}'
  , ',') || ']' AS participants
FROM partnerships p
JOIN my_partnerships m ON m.pid = p.id
JOIN partnership_participants pp ON pp.partnership_id = p.id
JOIN character c ON c.id = pp.character_id
GROUP BY p.id, p.type
ORDER BY p.id            
            '''), {'cid': cid}).mappings().all()
        rv = []
        for row in rows:
            rv.append({'id': row['partnership_id'],
                       'type': row['partnership_type'],
                       'name': row['partnership_name'],
                       'is_primary': row['partnership_is_primary'],
                       'legitimate': row['partnership_legitimate'],
                       'participants': json.loads(row['participants']),
            })
        return rv

