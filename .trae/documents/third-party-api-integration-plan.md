# 第三方API集成开发计划

## 需求概览

根据 `docs/thrid-api.md` 文档，需要集成3个第三方API并新增2个QQ机器人命令。

---

## 功能需求

### 1. 中文翻译缓存
- **接口**: `GET https://pokev9.52kx.net/locales/zh/translation.json`
- **本地缓存**: `resources/translation/translation.json`
- **更新策略**: 懒加载每日更新（数据日期 < 今天时重新拉取）
- **清理策略**: 清理历史文件

### 2. 环境数据缓存与查询
- **接口**: `GET https://www.pokemon-auto-chess.com/meta-v2`
- **本地缓存**: `resources/meta-v2/meta-v2.json`
- **更新策略**: 懒加载每日更新
- **清理策略**: 清理历史文件
- **QQ命令**: 
  - `/env -page 页码` 或 `/env -p 页码` - 查询环境数据
  - `/env -h` 或 `/env -help` - 显示帮助
- **返回数据**: 按平均排名排序，每页10条，默认第1页
- **关键字段**: count(环境数量)、winrate(胜率)、mean_rank(平均排名)、synergies(共鸣组合)、mean_team(平均团队)

### 3. 宝可梦环境数据缓存与查询
- **接口**: `GET https://www.pokemon-auto-chess.com/meta/pokemons`
- **本地缓存**: `resources/meta-pkm/pokemons.json`
- **更新策略**: 懒加载每日更新
- **清理策略**: 清理历史文件
- **QQ命令**:
  - `/pkm -n 君主蛇 -r 1200` - 查询宝可梦数据
  - `/pkm -h` 或 `/pkm -help` - 显示帮助
- **参数说明**:
  - `-n`: 宝可梦名称（支持中文/英文，通过translation.json映射）
  - `-r`: elo分级（可选，不填则不筛选）
- **返回数据**: 平均名次rank、出场次数count、平均道具数量item_count、道具items
- **翻译**: 所有返回内容通过translation.json翻译成中文

### 4. /insight 命令帮助补充
- `/insight -h` 或 `/insight -help` 时返回帮助信息

---

## 技术实现计划

### 第一步：创建通用缓存模块
创建 `cache_manager.py`，实现：
- 带日期标记的JSON文件缓存
- 懒加载检查（比较日期）
- 自动清理历史文件
- 统一的缓存读写接口

### 第二步：创建第三方API客户端
创建 `third_party_api.py`，实现：
- 翻译API调用与缓存
- 环境数据API调用与缓存
- 宝可梦数据API调用与缓存
- 翻译映射功能

### 第三步：新增命令处理器
修改 `command_handler.py`，新增：
- `parse_env_command()` - 解析/env命令
- `handle_env()` - 处理环境数据查询
- `parse_pkm_command()` - 解析/pkm命令
- `handle_pkm()` - 处理宝可梦数据查询
- 修改 `parse_chess_insight_command()` 支持 -h/-help 参数

### 第四步：集成到主服务
修改 `main.py`，新增：
- `/env` 命令路由处理
- `/pkm` 命令路由处理
- `/insight -h` 帮助响应

### 第五步：测试验证
- 测试API缓存功能
- 测试懒加载更新机制
- 测试QQ命令响应

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `cache_manager.py` | 新建 | 通用缓存管理模块 |
| `third_party_api.py` | 新建 | 第三方API客户端 |
| `command_handler.py` | 修改 | 新增/env和/pkm命令处理 |
| `main.py` | 修改 | 集成新命令路由 |

---

## 待确认事项

1. **环境数据返回格式**: 每条数据需要展示哪些字段？建议格式：
   ```
   📊 队伍组合 #40
   📈 平均排名: 4.11 | 胜率: 15.5% | 场次: 168
   🔥 共鸣: 暗(5) 怪兽(2)
   👥 核心成员: 班基拉斯、三首恶龙...
   ```

2. **宝可梦数据返回格式**: 建议格式：
   ```
   🎮 暴雪王 (ABOMASNOW)
   📊 平均排名: 2.78 | 出场: 1595次
   🎒 平均道具: 0.83个
   💎 推荐道具: 肌肉绑带、王者之证、奇迹箱
   ```

3. **elo分级筛选**: 当指定 `-r 1200` 时，应该返回哪个分级的数据？
   - 根据文档分级表，1200对应"纪念球(PREMIER_BALL)"范围(elo>1200)
   - 是否返回该分级及以上的数据？还是精确匹配？

---

请确认以上需求和实现计划是否正确，如有调整请告知。
