import httpx
import logging
import time
from typing import Optional, List, Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class PokemonInfo:
    name: str
    avatar: str
    items: List[str]


@dataclass
class GameRecord:
    time: int
    rank: int
    elo: Optional[int] = None
    game_mode: Optional[str] = None
    pokemons: List[PokemonInfo] = None


class PokemonAutoChessAPI:
    def __init__(self):
        self.base_url = "https://pokemon-auto-chess.com"
        self.cn_base_url = "https://daascveqarqwe-dev.workol.cn"
        self._client: Optional[httpx.AsyncClient] = None
    
    async def get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def get_game_history(
        self, 
        user_id: str, 
        page: int = 1,
        server: str = None
    ) -> List[GameRecord]:
        client = await self.get_client()
        
        timestamp = int(time.time())
        
        if server == "cn":
            base_url = self.cn_base_url
        else:
            base_url = self.base_url
        
        url = f"{base_url}/game-history/{user_id}"
        
        params = {
            "page": page,
            "t": timestamp
        }
        
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            records = []
            for item in data:
                pokemons_data = item.get("pokemons", [])
                pokemons = [
                    PokemonInfo(
                        name=p.get("name", ""),
                        avatar=p.get("avatar", ""),
                        items=p.get("items", [])
                    )
                    for p in pokemons_data
                ]

                record = GameRecord(
                    time=item.get("time", 0),
                    rank=item.get("rank", 0),
                    elo=item.get("elo"),
                    game_mode=item.get("gameMode"),
                    pokemons=pokemons
                )
                records.append(record)
            
            logger.info(f"Fetched {len(records)} game records for user {user_id} from {base_url}")
            return records
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to fetch game history: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch game history: {e}")
            raise
    
    async def get_multiple_pages(
        self, 
        user_id: str, 
        total_games: int,
        server: str = None
    ) -> List[GameRecord]:
        all_records = []
        page = 1
        per_page = 10
        
        pages_needed = (total_games + per_page - 1) // per_page
        
        for _ in range(pages_needed):
            records = await self.get_game_history(user_id, page, server=server)
            if not records:
                break
            all_records.extend(records)
            if len(all_records) >= total_games:
                break
            page += 1
        
        return all_records[:total_games]
    
    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


pokemon_chess_api = PokemonAutoChessAPI()
