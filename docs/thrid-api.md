1. 中文翻译。
接口： GET https://pokev9.52kx.net/locales/zh/translation.json
我下载了一份样例数据帮你了解数据格式和意义，位置 `resources\translation\translation-example.json` 。我希望调用接口后在本地保存一份json文件，这样就不用反复查询。要求保留下载的日期。懒加载每日更新，即发现数据的日期＜今天时，重新拉取数据保存到本地。注意要清理历史文件。
其中pkm是pokemon的缩写，意思是宝可梦，也是游戏的队伍成员。

2. 环境数据。
接口： GET https://www.pokemon-auto-chess.com/meta-v2
关键数据：
- count：环境数量
- winrate：胜率
- mean_rank：平均排名
- synergies： 共鸣组合
- mean_team：平均团队

我希望这个接口的数据也做成本地文件缓存，文件名是 `resources\meta-v2\meta-v2.json` 。要求保留下载的日期。懒加载每日更新，即发现数据的日期＜今天时，重新拉取数据保存到本地。注意要清理历史文件。

另外支持QQ机器人指令“/env -page 页码” 或者 “/env -p 页码”， “/env -h” 或者 “/env -help”时显示指令的帮助信息。
指令返回关键数据，要求按平均排名排序，每页显示10条数据。没有页码参数时默认返回第一页(前10条)，以此类推。

我下载了一份样例数据帮你了解数据格式和意义，位置 `resources\meta-v2\meta-v2-example.json`, 简洁版如下
 - response：
```json
[
    {
        "_id": "69aa4bbad0fc6f3002f8c4cf",
        "cluster_id": "40",
        "count": 168,
        "ratio": 0.88491,
        "winrate": 15.47619,
        "mean_rank": 4.10714,
        "synergies": {
            "dark": 5,
            "monster": 2
        },
        "mean_team": {
            "cluster_id": "40",
            "rank": 4.11,
            "pokemons": {
                "PUPITAR": {
                    "frequency": 0.554,
                    "mean_items": 0.63,
                    "items": [
                        "FLAME_ORB"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca2"
                },
                "DUSCLOPS": {
                    "frequency": 0.399,
                    "mean_items": 0.09,
                    "items": [],
                    "_id": "69ab1a0978b4dd1ffb183ca3"
                },
                "BISHARP": {
                    "frequency": 0.351,
                    "mean_items": 2.07,
                    "items": [
                        "RAZOR_FANG",
                        "SHELL_BELL"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca4"
                },
                "GUZZLORD": {
                    "frequency": 0.345,
                    "mean_items": 2.03,
                    "items": [
                        "REAPER_CLOTH",
                        "ASSAULT_VEST"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca5"
                },
                "TORRACAT": {
                    "frequency": 0.315,
                    "mean_items": 0.55,
                    "items": [
                        "SHELL_BELL"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca6"
                },
                "TYRANITAR": {
                    "frequency": 0.315,
                    "mean_items": 2.06,
                    "items": [
                        "RAZOR_FANG",
                        "SAFETY_GOGGLES"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca7"
                },
                "KROOKODILE": {
                    "frequency": 0.179,
                    "mean_items": 2.1,
                    "items": [
                        "MUSCLE_BAND",
                        "RAZOR_FANG"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca8"
                },
                "PAWNIARD": {
                    "frequency": 0.173,
                    "mean_items": 0.86,
                    "items": [
                        "RAZOR_FANG"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183ca9"
                },
                "CHI_YU": {
                    "frequency": 0.173,
                    "mean_items": 2.38,
                    "items": [
                        "REAPER_CLOTH",
                        "SOUL_DEW"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183caa"
                },
                "ZWEILOUS": {
                    "frequency": 0.167,
                    "mean_items": 0.75,
                    "items": [
                        "REAPER_CLOTH"
                    ],
                    "_id": "69ab1a0978b4dd1ffb183cab"
                }
            },
            "synergies": {
                "elo": 1170.61,
                "field": 0.02,
                "dark": 6.73,
                "ground": 0.31,
                "grass": 0.42,
                "fire": 0.46,
                "ghost": 0.86,
                "rock": 1.13,
                "monster": 2.32,
                "wild": 0.29,
                "poison": 0.02,
                "electric": 0.02,
                "ice": 0.08,
                "flying": 0.12,
                "psychic": 0.09,
                "water": 0.02,
                "aquatic": 0.19,
                "dragon": 0.05,
                "normal": 0.05,
                "bug": 0.05,
                "light": 0.04,
                "sound": 0.01,
                "human": 0.04,
                "fighting": 0.1,
                "steel": 0.23,
                "fossil": 0.01
            },
            "_id": "69ab1a0978b4dd1ffb183cac"
        },
        "mean_items": [
            {
                "_id": "69ab1a0978b4dd1ffb183cad",
                "item": "RAZOR_FANG",
                "frequency": 0.092
            },
            {
                "_id": "69ab1a0978b4dd1ffb183cae",
                "item": "REAPER_CLOTH",
                "frequency": 0.06
            },
            {
                "_id": "69ab1a0978b4dd1ffb183caf",
                "item": "SCOPE_LENS",
                "frequency": 0.056
            },
            {
                "_id": "69ab1a0978b4dd1ffb183cb0",
                "item": "SHELL_BELL",
                "frequency": 0.051
            },
            {
                "_id": "69ab1a0978b4dd1ffb183cb1",
                "item": "DUSK_STONE",
                "frequency": 0.049
            }
        ],
        "top_teams": [
            {
                "_id": "69ab1a0978b4dd1ffb183cb2",
                "rank": 1,
                "elo": 1121,
                "pokemons": [
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb3",
                        "name": "ABSOL",
                        "items": [
                            "RAZOR_FANG",
                            "RED_ORB",
                            "MAX_REVIVE"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb4",
                        "name": "GRENINJA",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb5",
                        "name": "ROARING_MOON",
                        "items": [
                            "SOUL_DEW",
                            "SCOPE_LENS",
                            "UPGRADE"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb6",
                        "name": "TORRACAT",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb7",
                        "name": "KROOKODILE",
                        "items": [
                            "RAZOR_FANG",
                            "LOADED_DICE",
                            "MAX_REVIVE"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb8",
                        "name": "PUPITAR",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cb9",
                        "name": "BISHARP",
                        "items": [
                            "POKE_DOLL",
                            "SCOPE_LENS"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cba",
                        "name": "ZWEILOUS",
                        "items": []
                    }
                ]
            },
            {
                "_id": "69ab1a0978b4dd1ffb183cbb",
                "rank": 1,
                "elo": 1100,
                "pokemons": [
                    {
                        "_id": "69ab1a0978b4dd1ffb183cbc",
                        "name": "ABSOL",
                        "items": [
                            "BLACK_GLASSES"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cbd",
                        "name": "PUPITAR",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cbe",
                        "name": "CHI_YU",
                        "items": [
                            "SOUL_DEW",
                            "REAPER_CLOTH",
                            "DEEP_SEA_TOOTH"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cbf",
                        "name": "RHYHORN",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc0",
                        "name": "TORRACAT",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc1",
                        "name": "TEDDIURSA",
                        "items": [
                            "DUSK_STONE"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc2",
                        "name": "KROOKODILE",
                        "items": [
                            "MUSCLE_BAND",
                            "RAZOR_CLAW",
                            "POKE_DOLL"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc3",
                        "name": "GRENINJA",
                        "items": [
                            "SHELL_BELL",
                            "LOADED_DICE",
                            "AQUA_EGG"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc4",
                        "name": "HUNTAIL",
                        "items": []
                    }
                ]
            },
            {
                "_id": "69ab1a0978b4dd1ffb183cc5",
                "rank": 1,
                "elo": 1164,
                "pokemons": [
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc6",
                        "name": "COMFEY",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc7",
                        "name": "SNEASEL",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc8",
                        "name": "BISHARP",
                        "items": [
                            "RAZOR_CLAW",
                            "RAZOR_FANG",
                            "LOADED_DICE"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cc9",
                        "name": "CHI_YU",
                        "items": [
                            "REAPER_CLOTH",
                            "RAZOR_CLAW",
                            "AQUA_EGG"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cca",
                        "name": "TORRACAT",
                        "items": [
                            "SHINY_CHARM"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ccb",
                        "name": "LOKIX",
                        "items": [
                            "ROCKY_HELMET",
                            "KINGS_ROCK"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ccc",
                        "name": "DUSCLOPS",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ccd",
                        "name": "TYRANITAR",
                        "items": [
                            "SHINY_CHARM",
                            "CHOICE_SPECS"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cce",
                        "name": "TOTODILE",
                        "items": []
                    }
                ]
            },
            {
                "_id": "69ab1a0978b4dd1ffb183ccf",
                "rank": 1,
                "elo": 1128,
                "pokemons": [
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd0",
                        "name": "LUNATONE",
                        "items": [
                            "WONDER_BOX",
                            "AQUA_EGG"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd1",
                        "name": "GLALIE",
                        "items": [
                            "DUSK_STONE",
                            "LOADED_DICE",
                            "COMET_SHARD"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd2",
                        "name": "DARKRAI",
                        "items": [
                            "RAZOR_FANG",
                            "REAPER_CLOTH",
                            "SCOPE_LENS"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd3",
                        "name": "WEAVILE",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd4",
                        "name": "TORRACAT",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd5",
                        "name": "TYRANITAR",
                        "items": [
                            "ABILITY_SHIELD"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd6",
                        "name": "POOCHYENA",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd7",
                        "name": "KINGAMBIT",
                        "items": [
                            "ASSAULT_VEST",
                            "KINGS_ROCK",
                            "MAGMARIZER"
                        ]
                    }
                ]
            },
            {
                "_id": "69ab1a0978b4dd1ffb183cd8",
                "rank": 1,
                "elo": 1229,
                "pokemons": [
                    {
                        "_id": "69ab1a0978b4dd1ffb183cd9",
                        "name": "SHIFTRY",
                        "items": [
                            "RAZOR_FANG",
                            "SCOPE_LENS",
                            "PROTECTIVE_PADS"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cda",
                        "name": "GUZZLORD",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cdb",
                        "name": "CRAWDAUNT",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cdc",
                        "name": "BISHARP",
                        "items": [
                            "FLAME_ORB",
                            "KINGS_ROCK",
                            "GRACIDEA_FLOWER"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cdd",
                        "name": "MALAMAR",
                        "items": [
                            "SMOKE_BALL"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cde",
                        "name": "SNEASEL",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cdf",
                        "name": "TOTODILE",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce0",
                        "name": "TYRANITAR",
                        "items": [
                            "SOUL_DEW"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce1",
                        "name": "OVERQWIL",
                        "items": [
                            "SHINY_CHARM",
                            "REAPER_CLOTH",
                            "RAZOR_FANG"
                        ]
                    }
                ]
            },
            {
                "_id": "69ab1a0978b4dd1ffb183ce2",
                "rank": 1,
                "elo": 1257,
                "pokemons": [
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce3",
                        "name": "DUSCLOPS",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce4",
                        "name": "GUZZLORD",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce5",
                        "name": "BISHARP",
                        "items": [
                            "XRAY_VISION",
                            "WIDE_LENS",
                            "RED_ORB"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce6",
                        "name": "TYRANITAR",
                        "items": [
                            "SAFETY_GOGGLES",
                            "PROTECTIVE_PADS",
                            "RAZOR_FANG"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce7",
                        "name": "RHYDON",
                        "items": [
                            "RED_ORB",
                            "DUSK_STONE",
                            "LOADED_DICE"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce8",
                        "name": "WEAVILE",
                        "items": [
                            "SMOKE_BALL",
                            "RAZOR_FANG"
                        ]
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ce9",
                        "name": "BISHARP",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183cea",
                        "name": "HAUNTER",
                        "items": []
                    },
                    {
                        "_id": "69ab1a0978b4dd1ffb183ceb",
                        "name": "LITTEN",
                        "items": []
                    }
                ]
            }
        ]
        ],
        "x": 4.457003876566887,
        "y": 51.87217864536104,
        "generated_at": "2026-03-06T03:36:26.621845"
    }
]
```

3. 宝可梦环境数据
接口： GET https://www.pokemon-auto-chess.com/meta/pokemons

我希望这个接口的数据也做成本地文件缓存，文件名是 `resources\meta-pkm\pokemons.json` 。要求保留下载的日期。懒加载每日更新，即发现数据的日期＜今天时，重新拉取数据保存到本地。注意要清理历史文件。



GET 请求返回样例, 下面表示是`LEVEL_BALL`分级，`ABOMASNOW`暴雪王的环境信息

我下载了一份样例数据帮你了解数据格式和意义，位置 `resources\meta-pkm\pokemons-example.json`, 简洁版如下
```json
[{"_id":"6993e287c0bde49f15a077f4","tier":"LEVEL_BALL","pokemons":{"ABOMASNOW":{"items":["MUSCLE_BAND","KINGS_ROCK","WONDER_BOX"],"rank":2.78,"count":1595,"name":"ABOMASNOW","item_count":0.83}]
```
分级信息如下
    ```JSON
    "elorank": {
		"LEVEL_BALL": "等级球 elo>0",
		"NET_BALL": "捕网球 elo>1050",
		"SAFARI_BALL": "狩猎球 elo>1100",
		"LOVE_BALL": "甜蜜球 elo>1150",
		"PREMIER_BALL": "纪念球 elo>1200",
		"QUICK_BALL": "先机球 elo>1250",
		"POKE_BALL": "精灵球 elo>1300",
		"SUPER_BALL": "超级球 elo>1350",
		"ULTRA_BALL": "高级球 elo>1400",
		"MASTER_BALL": "大师球 elo>1500",
		"BEAST_BALL": "究极球 elo>1600"
	}
    ```

另外支持QQ机器人指令“/pkm -n 君主蛇 -r 1200” 支持中文名和英文名，根据翻译文件中的 pkm[] 对照. -n表示name，-r表示rank。允许没有-r，表示不筛选数据,有r的话，就从对应的elo分级中获取数据
“/pkm -h” 或者 “/pkm -help”时显示指令的帮助信息。	
    
要求返回宝可梦的`平均名次rank、出场次数count、平均道具数量item_count、道具items`当然，要全部通过translation.json翻译成中文。映射不到时才用英文缺省返回。


4. 另外补充原来一下“/insight” 命令中 -h 或者 -help时，返回帮助信息。