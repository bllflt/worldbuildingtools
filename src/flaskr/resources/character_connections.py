from flask import json
from flask_restful import Resource
from sqlalchemy import text

from flaskr.model import db


class CharacterConnections(Resource):
    def get(self, cid):

        rows = db.session.execute(text('''
WITH my_partnerships AS (
  -- All partnerships the character participates in OR is a child of
  SELECT partnership_id AS pid FROM partnership_participants WHERE character_id = :cid
  UNION
  SELECT partnership_id AS pid FROM offspring WHERE character_id = :cid
)

SELECT
  p.id AS id,
  p.type AS type,

  -- participants as JSON array text
  (
    SELECT
      '[' || GROUP_CONCAT(json_obj, ',') || ']'
    FROM (
      SELECT DISTINCT
        '{"id":' || c.id ||
        ',"name":"' || REPLACE(c.name, '"', '\"') ||
        '","sex":' || c.sex || '}' AS json_obj
      FROM partnership_participants pp
      JOIN character c ON c.id = pp.character_id
      WHERE pp.partnership_id = p.id
      ORDER BY c.id
    )
  ) AS participants,

  -- children as JSON array text
  (
    SELECT
      '[' || GROUP_CONCAT(json_obj, ',') || ']'
    FROM (
      SELECT DISTINCT
        '{"id":' || c.id ||
        ',"name":"' || REPLACE(c.name, '"', '\"') ||
        '","sex":' || c.sex || '}' AS json_obj
      FROM offspring o
      JOIN character c ON c.id = o.character_id
      WHERE o.partnership_id = p.id
      ORDER BY c.id
    )
  ) AS children

FROM partnerships p
JOIN my_partnerships m ON m.pid = p.id
ORDER BY p.id;

            
            '''), {'cid': cid}).mappings().all()
        rv = []
        for row in rows:
            rv.append({'id': row['id'],
                       'type': row['type'],
                       'participants': json.loads(row['participants']),
                       'children': json.loads(row['children']) if row['children'] is not None else []
            })
        return rv

