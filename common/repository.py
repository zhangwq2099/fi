"""
统一数据存储层 - 基于内存的数据管理
"""
from typing import Dict, List, Optional, Any
from datetime import datetime


class BaseRepository:
    """数据仓库基类"""
    
    def __init__(self):
        """初始化数据存储"""
        self._storage: Dict[str, Dict[str, Any]] = {}
    
    def _generate_id(self, prefix: str = '') -> str:
        """生成唯一ID"""
        import uuid
        return f"{prefix}{uuid.uuid4().hex[:16]}"
    
    def create(self, table_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """创建记录"""
        if table_name not in self._storage:
            self._storage[table_name] = {}
        
        primary_key = data.get('id') or data.get(f'{table_name}_id')
        if not primary_key:
            raise ValueError(f"缺少主键字段: {table_name}")
        
        if primary_key in self._storage[table_name]:
            raise ValueError(f"记录已存在: {primary_key}")
        
        self._storage[table_name][primary_key] = data.copy()
        return data
    
    def get(self, table_name: str, primary_key: str) -> Optional[Dict[str, Any]]:
        """获取记录"""
        if table_name not in self._storage:
            return None
        return self._storage[table_name].get(primary_key)
    
    def update(self, table_name: str, primary_key: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新记录"""
        if table_name not in self._storage:
            return None
        if primary_key not in self._storage[table_name]:
            return None
        
        self._storage[table_name][primary_key].update(data)
        return self._storage[table_name][primary_key]
    
    def delete(self, table_name: str, primary_key: str) -> bool:
        """删除记录"""
        if table_name not in self._storage:
            return False
        if primary_key not in self._storage[table_name]:
            return False
        
        del self._storage[table_name][primary_key]
        return True
    
    def list(self, table_name: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """列出记录"""
        if table_name not in self._storage:
            return []
        
        records = list(self._storage[table_name].values())
        
        if filters:
            filtered = []
            for record in records:
                match = True
                for key, value in filters.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(record)
            return filtered
        
        return records
    
    def exists(self, table_name: str, primary_key: str) -> bool:
        """检查记录是否存在"""
        if table_name not in self._storage:
            return False
        return primary_key in self._storage[table_name]


# 全局单例
_repository_instance = None


def get_repository() -> BaseRepository:
    """获取仓库实例（单例）"""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = BaseRepository()
    return _repository_instance


