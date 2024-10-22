from core.db.structures.abstractions import AbstractDBStructure


class CtrStructure(AbstractDBStructure):
    crs_table = "crostab_razv"
    soato_table = "SOATO"
    users_table = "Users"
    all_tables = [crs_table, soato_table, users_table]

    @staticmethod
    def _get_structure() -> dict:
        return {
            "crostab_razv": {
                "id": {
                    "name": "OBJECTID",
                    "type": ["COUNTER", ]
                },
                "shape_area": {
                    "name": "Shape_Area",
                    "type": ["DOUBLE", ]
                },
                "soato": {
                    "name": "SOATO",
                    "type": ["VARCHAR", ],
                },
                "part_n": {
                    "name": "Part_1",
                    "type": ["DOUBLE", ],
                    "part_name": "Part_",
                },
                "user_n": {
                    "name": "UserN_1",
                    "type": ["INTEGER", "SMALLINT"],
                    "part_name": "UserN_",
                },
                "f22": {
                    "name": "Forma22_1",
                    "type": ["VARCHAR", ],
                    "part_name": "Forma22_",
                },
                "srv_type": {
                    "name": "ServType08",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "sl_nad": {
                    "name": "SLNAD",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "state": {
                    "name": "State",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "lc": {
                    "name": "LANDCODE",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "mc": {
                    "name": "MELIOCODE",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "user_n_sad": {
                    "name": "UserN_Sad",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "category": {
                    "name": "Category",
                    "type": ["INTEGER", "SMALLINT"]
                }
            },
            "SOATO": {
                "name": {
                    "name": "NAME",
                    "type": ["VARCHAR", ],
                },
                "id": {
                    "name": "OBJECTID",
                    "type": ["COUNTER"],
                },
                "pref": {
                    "name": "PREF",
                    "type": ["VARCHAR", ],
                },
                "code": {
                    "name": "KOD",
                    "type": ["VARCHAR", ],
                }
            },
            "Users": {
                "id": {
                    "name": "OBJECTID",
                    "type": ["COUNTER"],
                },
                "user_type": {
                    "name": "UserType",
                    "type": ["INTEGER", "SMALLINT"],
                },
                "us_name": {
                    "name": "UsName",
                    "type": ["VARCHAR", ],
                },
                "user_n": {
                    "name": "UserN",
                    "type": ["INTEGER", "SMALLINT"],
                }
            }
        }
