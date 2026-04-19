import logging
from typing import Optional, Dict, List, Any

from cache_manager import cache_manager

logger = logging.getLogger(__name__)


TRANSLATION_URL = "https://pokev9.52kx.net/locales/zh/translation.json"
META_V2_URL = "https://www.pokemon-auto-chess.com/meta-v2"
META_POKEMONS_URL = "https://www.pokemon-auto-chess.com/meta/pokemons"

ELO_RANKS = {
    "LEVEL_BALL": "等级球 (elo>0)",
    "NET_BALL": "捕网球 (elo>1050)",
    "SAFARI_BALL": "狩猎球 (elo>1100)",
    "LOVE_BALL": "甜蜜球 (elo>1150)",
    "PREMIER_BALL": "纪念球 (elo>1200)",
    "QUICK_BALL": "先机球 (elo>1250)",
    "POKE_BALL": "精灵球 (elo>1300)",
    "SUPER_BALL": "超级球 (elo>1350)",
    "ULTRA_BALL": "高级球 (elo>1400)",
    "MASTER_BALL": "大师球 (elo>1500)",
    "BEAST_BALL": "究极球 (elo>1600)"
}

ELO_THRESHOLDS = {
    0: "LEVEL_BALL",
    1050: "NET_BALL",
    1100: "SAFARI_BALL",
    1150: "LOVE_BALL",
    1200: "PREMIER_BALL",
    1250: "QUICK_BALL",
    1300: "POKE_BALL",
    1350: "SUPER_BALL",
    1400: "ULTRA_BALL",
    1500: "MASTER_BALL",
    1600: "BEAST_BALL"
}


def get_elo_tier(elo: int) -> str:
    tier = "LEVEL_BALL"
    for threshold, tier_name in sorted(ELO_THRESHOLDS.items()):
        if elo >= threshold:
            tier = tier_name
        else:
            break
    return tier


class ThirdPartyAPI:
    def __init__(self):
        self._translation_cache: Optional[Dict] = None
    
    async def get_translation(self) -> Optional[Dict]:
        if self._translation_cache:
            return self._translation_cache
        
        data = await cache_manager.fetch_and_cache(
            TRANSLATION_URL,
            "translation",
            "translation.json"
        )
        
        if data:
            self._translation_cache = data
        
        return data
    
    def translate_pokemon(self, name: str, translation: Dict) -> str:
        if not translation:
            return name
        
        pkm_translations = translation.get("pkm", {})
        translated = pkm_translations.get(name, name)
        return translated
    
    def translate_item(self, item: str, translation: Dict) -> str:
        if not translation:
            return item
        
        item_translations = translation.get("item", {})
        translated = item_translations.get(item, item)
        return translated
    
    def translate_synergy(self, synergy: str, translation: Dict) -> str:
        if not translation:
            return synergy
        
        synergy_translations = translation.get("synergy", {})
        if isinstance(synergy_translations, str):
            return synergy
        translated = synergy_translations.get(synergy.upper(), synergy)
        return translated
    
    def get_english_pokemon_name(self, chinese_name: str, translation: Dict) -> Optional[str]:
        if not translation:
            return None
        
        pkm_translations = translation.get("pkm", {})
        for eng_name, cn_name in pkm_translations.items():
            if cn_name == chinese_name:
                return eng_name
        return None
    
    async def search_pokemon_names(self, keyword: str) -> List[Dict[str, str]]:
        translation = await self.get_translation()
        if not translation:
            return []
        
        pkm_dict = translation.get("pkm", {})
        
        results = []
        for en_name, cn_name in pkm_dict.items():
            if keyword in cn_name:
                results.append({
                    "cn": cn_name,
                    "en": en_name
                })
        
        results.sort(key=lambda x: x["cn"])
        return results[:20]
    
    async def get_meta_v2(self) -> Optional[List[Dict]]:
        return await cache_manager.fetch_and_cache(
            META_V2_URL,
            "meta-v2",
            "meta-v2.json"
        )
    
    async def get_meta_pokemons(self) -> Optional[List[Dict]]:
        return await cache_manager.fetch_and_cache(
            META_POKEMONS_URL,
            "meta-pkm",
            "pokemons.json"
        )
    
    async def get_env_data(self, page: int = 1, page_size: int = 10) -> Dict[str, Any]:
        meta_data = await self.get_meta_v2()
        
        if not meta_data:
            return {"success": False, "message": "无法获取环境数据"}
        
        if not isinstance(meta_data, list):
            logger.error(f"meta_data is not a list, type: {type(meta_data)}")
            return {"success": False, "message": "环境数据格式错误"}
        
        sorted_data = sorted(meta_data, key=lambda x: x.get("mean_rank", float("inf")) if isinstance(x, dict) else float("inf"))
        
        total = len(sorted_data)
        total_pages = (total + page_size - 1) // page_size
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = sorted_data[start_idx:end_idx]
        
        translation = await self.get_translation()
        
        formatted_data = []
        for item in page_data:
            synergies = item.get("synergies", {})
            synergy_list = []
            for syn_name, syn_value in synergies.items():
                translated_syn = self.translate_synergy(syn_name, translation)
                synergy_list.append(f"{translated_syn}({syn_value})")
            
            top_teams = item.get("top_teams", [])
            example_pokemons = []
            if top_teams and len(top_teams) > 0:
                first_team = top_teams[0]
                team_pokemons = first_team.get("pokemons", [])
                for pkm in team_pokemons:
                    pkm_name = pkm.get("name", "")
                    if pkm_name:
                        translated_name = self.translate_pokemon(pkm_name, translation)
                        example_pokemons.append(translated_name)
            
            if not example_pokemons:
                mean_team = item.get("mean_team", {})
                pokemons = mean_team.get("pokemons", {})
                core_pokemons = sorted(
                    pokemons.items(),
                    key=lambda x: x[1].get("frequency", 0),
                    reverse=True
                )[:9]
                for pkm_name, _ in core_pokemons:
                    translated_name = self.translate_pokemon(pkm_name, translation)
                    example_pokemons.append(translated_name)
            
            formatted_data.append({
                "cluster_id": item.get("cluster_id", "N/A"),
                "count": item.get("count", 0),
                "winrate": item.get("winrate", 0),
                "mean_rank": item.get("mean_rank", 0),
                "synergies": " ".join(synergy_list) if synergy_list else "无",
                "example_pokemons": "、".join(example_pokemons) if example_pokemons else "无"
            })
        
        return {
            "success": True,
            "data": formatted_data,
            "page": page,
            "total_pages": total_pages,
            "total": total
        }
    
    async def get_pokemon_data(
        self, 
        name: str, 
        elo: Optional[int] = None
    ) -> Dict[str, Any]:
        meta_data = await self.get_meta_pokemons()
        
        if not meta_data:
            return {"success": False, "message": "无法获取宝可梦数据"}
        
        translation = await self.get_translation()
        
        english_name = name.upper()
        if any('\u4e00' <= c <= '\u9fff' for c in name):
            english_name = self.get_english_pokemon_name(name, translation)
            if not english_name:
                return {"success": False, "message": f"未找到宝可梦: {name}"}
            english_name = english_name.upper()
        
        tier = None
        if elo is not None:
            tier = get_elo_tier(elo)
        
        results = []
        for tier_data in meta_data:
            current_tier = tier_data.get("tier")
            
            if tier and current_tier != tier:
                continue
            
            pokemons = tier_data.get("pokemons", {})
            pkm_data = pokemons.get(english_name)
            
            if pkm_data:
                items = pkm_data.get("items", [])
                translated_items = [
                    self.translate_item(item, translation) 
                    for item in items
                ]
                
                results.append({
                    "tier": current_tier,
                    "tier_name": ELO_RANKS.get(current_tier, current_tier),
                    "name": self.translate_pokemon(english_name, translation),
                    "english_name": english_name,
                    "rank": pkm_data.get("rank", 0),
                    "count": pkm_data.get("count", 0),
                    "item_count": pkm_data.get("item_count", 0),
                    "items": translated_items
                })
        
        if not results:
            if tier:
                return {
                    "success": False, 
                    "message": f"在{ELO_RANKS.get(tier, tier)}分级中未找到宝可梦: {name}"
                }
            return {"success": False, "message": f"未找到宝可梦: {name}"}
        
        return {
            "success": True,
            "data": results
        }


third_party_api = ThirdPartyAPI()
