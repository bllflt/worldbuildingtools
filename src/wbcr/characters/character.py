class Character():

    def __init__(self, name: str, **kwargs):
        self.name = name

    def get_overview_data(self) -> dict:
        overview = {}
        for elm in ['images', 'name', 'apperance', 'roleplaying',
                    'background']:
            try:
                overview[elm] = getattr(self, elm)
            except:
                continue
        kr = []
        try:
            for rel_type in self.key_relationships:
                for rel in self.key_relationships[rel_type]:
                    kr.append(rel)
        except:
            pass
        overview['kr_list'] = kr
        return overview
