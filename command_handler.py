import re
import logging
from typing import Optional, List
from dataclasses import dataclass
from collections import Counter

from chess_api import pokemon_chess_api, GameRecord

logger = logging.getLogger(__name__)


@dataclass
class ChessInsightCommand:
    user_id: str
    count: int


def parse_chess_insight_command(content: str) -> Optional[ChessInsightCommand]:
    pattern = r'/insight\s+-u\s+(\S+)\s+-c\s+(\d+)'
    match = re.search(pattern, content)
    
    if match:
        user_id = match.group(1)
        count = int(match.group(2))
        return ChessInsightCommand(user_id=user_id, count=count)
    
    return None


def calculate_rank_statistics(records: List[GameRecord]) -> str:
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
    
    result = f"""📊 近{total_games}局战绩统计

🏆 平均排名: {avg_rank:.2f}
🥇 最好成绩: 第{best_rank}名
📉 最差成绩: 第{worst_rank}名

📈 排名分布:
{chr(10).join(rank_distribution)}

🎯 吃鸡率: {top1_rate:.1f}% ({top1_count}/{total_games})
🥉 前三率: {top3_rate:.1f}% ({top3_count}/{total_games})
🏅 前四率: {top4_rate:.1f}% ({top4_count}/{total_games})"""
    
    return result


async def handle_chess_insight(content: str) -> Optional[str]:
    command = parse_chess_insight_command(content)
    
    if not command:
        return None
    
    try:
        records = await pokemon_chess_api.get_multiple_pages(
            user_id=command.user_id,
            total_games=command.count
        )
        
        if not records:
            return f"未找到用户 {command.user_id} 的游戏记录"
        
        statistics = calculate_rank_statistics(records)
        return statistics
        
    except Exception as e:
        logger.error(f"Failed to handle chess insight: {e}")
        return f"查询失败: {str(e)}"
