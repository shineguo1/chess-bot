import re
import logging
from typing import Optional, List
from dataclasses import dataclass
from collections import Counter
from datetime import datetime

from chess_api import pokemon_chess_api, GameRecord
from user_binding import user_binding_storage
from third_party_api import third_party_api

logger = logging.getLogger(__name__)


@dataclass
class ChessInsightCommand:
    user_id: str
    count: int
    server: Optional[str] = None


@dataclass
class BindCommand:
    user_id: str
    server: Optional[str] = None


@dataclass
class EnvCommand:
    page: int


@dataclass
class PkmCommand:
    name: str
    elo: Optional[int] = None


INSIGHT_HELP = """📖 /insight 命令帮助

用法:
  /insight [-u 用户ID] [-c 局数] [-s 服务器]

参数:
  -u 用户ID    指定查询的用户ID（如未绑定则必填）
  -c 局数      查询的局数（默认50局）
  -s 服务器    指定服务器（cn=国服，默认国际服）

示例:
  /insight                    查询绑定的用户最近50局战绩
  /insight -c 100             查询绑定的用户最近100局战绩
  /insight -u ABC123          查询指定用户最近50局战绩
  /insight -u ABC123 -s cn    查询国服用户战绩

提示: 先使用 /bind -u 用户ID 绑定账号"""


ENV_HELP = """📖 /env 命令帮助

用法:
  /env [-p 页码]

参数:
  -p 页码  查询的页码（默认第1页）

功能:
  查询当前环境队伍组合数据，按平均排名排序

示例:
  /env        查询第1页（前10条）
  /env -p 2   查询第2页（第11-20条）"""


PKM_HELP = """📖 /pkm 命令帮助

用法:
  /pkm -n 名称 [-r elo]

参数:
  -n 名称  宝可梦名称（支持中文/英文）
  -r elo   ELO等级分（可选，用于筛选分级）

ELO分级对照:
  等级球(>0) 捕网球(>1050) 狩猎球(>1100)
  甜蜜球(>1150) 纪念球(>1200) 先机球(>1250)
  精灵球(>1300) 超级球(>1350) 高级球(>1400)
  大师球(>1500) 究极球(>1600)

示例:
  /pkm -n 君主蛇        查询君主蛇在所有分级的数据
  /pkm -n Serperior     英文名查询
  /pkm -n 君主蛇 -r 1200  查询纪念球分级的数据"""


BIND_HELP = """📖 /bind 命令帮助

用法:
  /bind -u 用户ID [-s 服务器]

参数:
  -u 用户ID    游戏用户ID
  -s 服务器    指定服务器（cn=国服，默认国际服）

示例:
  /bind -u ABC123           绑定国际服ID
  /bind -u gitee_123 -s cn  绑定国服ID

提示:
  - `用户ID`请在 [个人资料 -> 账号] 处查看，并非`名字`
  - 绑定后使用 /insight 无需再输入用户ID
  - 可同时绑定国服和国际服ID"""


HELP_TEXT = """🤖 QQ机器人命令帮助

📋 可用命令:

  /bind -u 用户ID [-s 服务器]
    绑定游戏ID到QQ账号
    -s cn 绑定国服ID（默认国际服）

  /insight [-u 用户ID] [-c 局数] [-s 服务器]
    查询战绩统计
    -s cn 查询国服数据

  /env [-p 页码]
    查询环境队伍组合数据

  /pkm 名称 [-r elo]
    查询宝可梦环境数据

  /hello
    测试机器人是否在线

💡 提示:
  - 使用 /命令 -h 查看详细帮助
  - 例如: /insight -h
"""


def parse_bind_command(content: str) -> Optional[BindCommand]:
    if re.search(r'/bind\s+(-h|--help)', content):
        return None
    
    pattern = r'/bind\s+-u\s+(\S+)(?:\s+-(?:s|server)\s+(\S+))?'
    match = re.search(pattern, content)
    
    if match:
        user_id = match.group(1)
        server = match.group(2)
        server = server if server == "cn" else "global"
        return BindCommand(user_id=user_id, server=server)
    
    return None


def parse_chess_insight_command(content: str, qq_openid: Optional[str] = None) -> Optional[ChessInsightCommand]:
    if "老吧" in content:
        pattern = r'/insight\s+老吧(?:\s+-c\s+(\d+))?'
        match = re.search(pattern, content)
        if match:
            count_str = match.group(1)
            count = int(count_str) if count_str else 50
            return ChessInsightCommand(user_id="gitee_16656474", count=count, server="cn")
    
    pattern = r'/insight(?:\s+-u\s+(\S+))?(?:\s+-c\s+(\d+))?(?:\s+-(?:s|server)\s+(\S+))?'
    match = re.search(pattern, content)
    
    if match:
        user_id = match.group(1)
        count_str = match.group(2)
        server = match.group(3)
        
        server = server if server == "cn" else "global"
        
        if user_id is None:
            if qq_openid:
                user_id = user_binding_storage.get_user_id(qq_openid, server)
                if user_id is None:
                    return None
            else:
                return None
        
        count = int(count_str) if count_str else 50
        server_param = server if server == "cn" else None
        
        return ChessInsightCommand(user_id=user_id, count=count, server=server_param)
    
    return None


def calculate_rank_statistics(records: List[GameRecord], first_page_records: List[GameRecord] = None) -> str:
    if not records:
        return "未找到游戏记录"
    
    ranks = [r.rank for r in records]
    rank_counter = Counter(ranks)
    
    total_games = len(records)
    avg_rank = sum(ranks) / total_games
    best_rank = min(ranks)
    worst_rank = max(ranks)
    
    top1_count = rank_counter.get(1, 0)
    top3_count = sum(rank_counter.get(i, 0) for i in [1, 2, 3])
    top4_count = sum(rank_counter.get(i, 0) for i in [1, 2, 3, 4])
    
    top1_rate = (top1_count / total_games) * 100
    top3_rate = (top3_count / total_games) * 100
    top4_rate = (top4_count / total_games) * 100
    
    rank_distribution = []
    for rank in sorted(rank_counter.keys()):
        count = rank_counter[rank]
        percentage = (count / total_games) * 100
        rank_distribution.append(f"第{rank}名: {count}局 ({percentage:.1f}%)")
    
    extra_info = ""
    if first_page_records and len(first_page_records) > 0:
        latest_record = first_page_records[0]
        latest_elo = latest_record.elo if latest_record.elo else "N/A"
        latest_time = datetime.fromtimestamp(latest_record.time / 1000).strftime("%Y-%m-%d %H:%M")
        
        recent_10_ranks = [str(r.rank) for r in first_page_records[:10]]
        recent_10_str = "".join(reversed(recent_10_ranks))
        
        extra_info = f"""
📌 最新状态:
   ELO分数: {latest_elo}
   游戏时间: {latest_time}
   最近10局排名: [{recent_10_str}]"""
    
    result = f"""📊 近{total_games}局战绩统计{extra_info}

🏆 平均排名: {avg_rank:.2f}
🥇 最好成绩: 第{best_rank}名
📉 最差成绩: 第{worst_rank}名

📈 排名分布:
{chr(10).join(rank_distribution)}

🎯 吃鸡率: {top1_rate:.1f}% ({top1_count}/{total_games})
🥉 前三率: {top3_rate:.1f}% ({top3_count}/{total_games})
🏅 前四率: {top4_rate:.1f}% ({top4_count}/{total_games})"""
    
    return result


async def handle_bind(content: str, qq_openid: str) -> Optional[str]:
    if re.search(r'/bind\s+(-h|--help)', content):
        return BIND_HELP
    
    command = parse_bind_command(content)
    
    if not command:
        return None
    
    try:
        server_label = "国服" if command.server == "cn" else "国际服"
        user_binding_storage.bind(qq_openid, command.user_id, command.server)
        return f"✅ 绑定成功！您的{server_label}游戏ID已绑定为: {command.user_id}"
    except Exception as e:
        logger.error(f"Failed to bind user: {e}")
        return f"绑定失败: {str(e)}"


async def handle_chess_insight(content: str, qq_openid: Optional[str] = None) -> Optional[str]:
    if re.search(r'/insight\s+(-h|--help)', content):
        return INSIGHT_HELP
    
    command = parse_chess_insight_command(content, qq_openid)
    
    if not command:
        return None
    
    try:
        first_page_records = await pokemon_chess_api.get_game_history(
            user_id=command.user_id,
            page=1,
            server=command.server
        )
        
        records = await pokemon_chess_api.get_multiple_pages(
            user_id=command.user_id,
            total_games=command.count,
            server=command.server
        )
        
        if not records:
            server_name = "国服" if command.server == "cn" else "国际服"
            return f"未找到用户 {command.user_id} 在{server_name}的游戏记录"
        
        statistics = calculate_rank_statistics(records, first_page_records)
        server_label = " [国服]" if command.server == "cn" else ""
        return f"{statistics}{server_label}"
        
    except Exception as e:
        logger.error(f"Failed to handle chess insight: {e}")
        return f"查询失败: {str(e)}"


def parse_env_command(content: str) -> Optional[EnvCommand]:
    if re.search(r'/env\s+(-h|--help)', content):
        return None
    
    pattern = r'/env(?:\s+-(?:p|page)\s+(\d+))?'
    match = re.search(pattern, content)
    
    if match:
        page_str = match.group(1)
        page = int(page_str) if page_str else 1
        return EnvCommand(page=page)
    
    if content.strip() == "/env":
        return EnvCommand(page=1)
    
    return None


async def handle_env(content: str) -> Optional[str]:
    if re.search(r'/env\s+(-h|--help)', content):
        return ENV_HELP
    
    command = parse_env_command(content)
    
    if not command:
        return None
    
    try:
        result = await third_party_api.get_env_data(page=command.page)
        
        if not isinstance(result, dict):
            logger.error(f"result is not a dict: {type(result)}, value: {result}")
            return "查询结果格式错误"
        
        if not result.get("success"):
            return result.get("message", "查询失败")
        
        data = result.get("data", [])
        page = result.get("page", 1)
        total_pages = result.get("total_pages", 1)
        total = result.get("total", 0)
        
        if not data:
            return f"第{page}页无数据"
        
        lines = [f"📊 环境数据 (第{page}/{total_pages}页，共{total}条)\n"]
        
        for i, item in enumerate(data, 1):
            start_rank = (page - 1) * 10 + i
            lines.append(
                f"#{start_rank} 队伍#{item['cluster_id']}\n"
                f"   📈 排名:{item['mean_rank']:.2f} | 胜率:{item['winrate']:.1f}% | 场次:{item['count']}\n"
                f"   🔥 共鸣: {item['synergies']}\n"
                f"   👥 示例: {item['example_pokemons']}\n"
            )
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.error(f"Failed to handle env: {e}")
        import traceback
        traceback.print_exc()
        return f"查询失败: {str(e)}"


def parse_pkm_command(content: str) -> Optional[PkmCommand]:
    if re.search(r'/pkm\s+(-h|--help)', content):
        return None
    
    pattern_with_n = r'/pkm\s+-n\s+(\S+)(?:\s+-r\s+(\d+))?'
    match = re.search(pattern_with_n, content)
    
    if match:
        name = match.group(1)
        elo_str = match.group(2)
        elo = int(elo_str) if elo_str else None
        return PkmCommand(name=name, elo=elo)
    
    pattern_without_n = r'/pkm\s+(\S+)(?:\s+-r\s+(\d+))?'
    match = re.search(pattern_without_n, content)
    
    if match:
        name = match.group(1)
        elo_str = match.group(2)
        elo = int(elo_str) if elo_str else None
        return PkmCommand(name=name, elo=elo)
    
    return None


async def handle_pkm(content: str) -> Optional[str]:
    if re.search(r'/pkm\s+(-h|--help)', content):
        return PKM_HELP
    
    command = parse_pkm_command(content)
    
    if not command:
        return None
    
    try:
        result = await third_party_api.get_pokemon_data(
            name=command.name,
            elo=command.elo
        )
        
        if not result.get("success"):
            return result.get("message", "查询失败")
        
        data = result.get("data", [])
        
        if not data:
            return f"未找到宝可梦: {command.name}"
        
        lines = []
        for item in data:
            items_str = "、".join(item["items"]) if item["items"] else "无推荐"
            lines.append(
                f"🎮 {item['name']} ({item['english_name']})\n"
                f"   📊 分级: {item['tier_name']}\n"
                f"   📈 平均排名: {item['rank']:.2f} | 出场: {item['count']}次\n"
                f"   🎒 平均道具: {item['item_count']:.2f}个\n"
                f"   💎 推荐道具: {items_str}"
            )
        
        return "\n\n".join(lines)
        
    except Exception as e:
        logger.error(f"Failed to handle pkm: {e}")
        return f"查询失败: {str(e)}"
