from flask import json, request
from flask_restful import Resource
from sqlalchemy import text

from flaskr.model import db


class CharacterConnections(Resource):

    def get(self, cid):
        depth = request.args.get('degree')


        rows = db.session.execute(text('''
WITH RECURSIVE

-- start character
start_char AS (
  SELECT :cid AS id
),

-- expand to N degrees (depth)
related(id, depth) AS (
  SELECT id, 0 FROM start_char
  UNION
  SELECT pp2.character_id, r.depth + 1
  FROM related r
  JOIN partnership_participants pp1 ON pp1.character_id = r.id
  JOIN partnership_participants pp2
       ON pp2.partnership_id = pp1.partnership_id
      AND pp2.character_id != pp1.character_id
  WHERE r.depth < :depth  -- e.g. 1 for direct, 3 for social graph
),

-- all partnerships involving any related character
all_partnerships AS (
  SELECT DISTINCT p.*
  FROM partnerships p
  JOIN partnership_participants pp ON pp.partnership_id = p.id
  WHERE pp.character_id IN (SELECT id FROM related)
)

-- output each partnership as JSON with nested participants
SELECT 
  json_object(
    'id', p.id,
    'type', p.type,
    'name', p.name,
    'is_primary', p.is_primary,
    'legitimate', p.legitimate,
    'participants',
      (
        SELECT json_group_array(
          json_object(
            'id', c.id,
            'name', c.name,
            'sex', c.sex,
            'role', pp.role
          )
        )
        FROM partnership_participants pp
        JOIN character c ON c.id = pp.character_id
        WHERE pp.partnership_id = p.id
      )
) AS partnerships_json
FROM all_partnerships p;

            '''), {'cid': cid, 'depth': int(depth)}).mappings().all()
        return [json.loads(row['partnerships_json']) for row in rows]
