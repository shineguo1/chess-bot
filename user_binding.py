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
    
    def bind(self, qq_openid: str, user_id: str) -> bool:
        self._bindings[qq_openid] = user_id
        self._save()
        return True
    
    def unbind(self, qq_openid: str) -> bool:
        if qq_openid in self._bindings:
            del self._bindings[qq_openid]
            self._save()
            return True
        return False
    
    def get_user_id(self, qq_openid: str) -> Optional[str]:
        return self._bindings.get(qq_openid)
    
    def is_bound(self, qq_openid: str) -> bool:
        return qq_openid in self._bindings


user_binding_storage = UserBindingStorage()
