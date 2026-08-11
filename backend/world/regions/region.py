class Region:
    def __init__(self, rid, title="", visible_desc="", hidden_desc=""):
        self.rid = rid
        self.title = title
        self.visible_desc = visible_desc
        self.hidden_desc = hidden_desc

    def to_dict(self):
        return {
            "rid": self.rid,
            "title": self.title,
            "visible_desc": self.visible_desc,
            "hidden_desc": self.hidden_desc,
        }
        