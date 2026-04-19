import json
import os
from typing import Optional
from pathlib import Path


class UserBindingStorage:
    def __init__(self, storage_file: str = "data/user_bindings.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._bindings: dict = {}
        self._load()
    
    def _load(self):
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self._bindings = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._bindings = {}
        else:
            self._bindings = {}
    
    def _save(self):
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self._bindings, f, ensure_ascii=False, indent=2)
    
    def bind(self, qq_openid: str, user_id: str, server: str = "global") -> bool:
        if qq_openid not in self._bindings:
            self._bindings[qq_openid] = {}
        
        if isinstance(self._bindings[qq_openid], str):
            old_user_id = self._bindings[qq_openid]
            self._bindings[qq_openid] = {"global": old_user_id}
        
        self._bindings[qq_openid][server] = user_id
        self._save()
        return True
    
    def unbind(self, qq_openid: str, server: Optional[str] = None) -> bool:
        if qq_openid not in self._bindings:
            return False
        
        if server is None:
            del self._bindings[qq_openid]
        else:
            if server in self._bindings[qq_openid]:
                del self._bindings[qq_openid][server]
                if not self._bindings[qq_openid]:
                    del self._bindings[qq_openid]
        
        self._save()
        return True
    
    def get_user_id(self, qq_openid: str, server: str = "global") -> Optional[str]:
        user_bindings = self._bindings.get(qq_openid)
        if not user_bindings:
            return None
        if isinstance(user_bindings, str):
            return user_bindings if server == "global" else None
        return user_bindings.get(server)
    
    def get_all_bindings(self, qq_openid: str) -> dict:
        return self._bindings.get(qq_openid, {})
    
    def is_bound(self, qq_openid: str, server: Optional[str] = None) -> bool:
        if qq_openid not in self._bindings:
            return False
        if server is None:
            return True
        return server in self._bindings[qq_openid]


user_binding_storage = UserBindingStorage()
