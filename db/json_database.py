import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import fcntl
from contextlib import contextmanager

from config.settings import settings


class JsonDatabase:
    """JSON文件数据库类"""
    
    def __init__(self):
        self.data_dir = settings.data_dir
        self.enable_backup = settings.enable_backup
        self.enable_file_lock = settings.enable_file_lock
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _get_file_path(self, table_name: str) -> str:
        """获取表对应的JSON文件路径"""
        return os.path.join(self.data_dir, f"{table_name}.json")
    
    @contextmanager
    def _file_lock(self, file_path: str, mode: str = "r"):
        """文件锁上下文管理器"""
        if not self.enable_file_lock:
            with open(file_path, mode, encoding='utf-8') as f:
                yield f
        else:
            with open(file_path, mode, encoding='utf-8') as f:
                try:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    yield f
                finally:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    
    async def _read_table(self, table_name: str) -> List[Dict[str, Any]]:
        """读取表数据"""
        file_path = self._get_file_path(table_name)
        
        if not os.path.exists(file_path):
            return []
        
        try:
            with self._file_lock(file_path, "r") as f:
                content = f.read()
                if not content.strip():
                    return []
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    async def _write_table(self, table_name: str, data: List[Dict[str, Any]]):
        """写入表数据"""
        file_path = self._get_file_path(table_name)
        
        # 备份原文件
        if self.enable_backup and os.path.exists(file_path):
            await self._backup_file(file_path)
        
        with self._file_lock(file_path, "w") as f:
            f.write(json.dumps(data, ensure_ascii=False, indent=2))
    
    async def _backup_file(self, file_path: str):
        """备份文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{file_path}.backup_{timestamp}"
        
        try:
            with open(file_path, "r", encoding='utf-8') as src:
                content = src.read()
            with open(backup_path, "w", encoding='utf-8') as dst:
                dst.write(content)
        except Exception:
            pass  # 备份失败不影响主流程
    
    async def _get_next_id(self, table_name: str) -> int:
        """获取下一个ID"""
        data = await self._read_table(table_name)
        if not data:
            return 1
        return max(item.get("id", 0) for item in data) + 1
    
    async def find_all(self, table_name: str) -> List[Dict[str, Any]]:
        """查找所有记录"""
        return await self._read_table(table_name)
    
    async def find_by_id(self, table_name: str, record_id: int) -> Optional[Dict[str, Any]]:
        """根据ID查找记录"""
        data = await self._read_table(table_name)
        for item in data:
            if item.get("id") == record_id:
                return item
        return None
    
    async def create(self, table_name: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建记录"""
        data = await self._read_table(table_name)
        
        # 自动分配ID
        if "id" not in record_data:
            record_data["id"] = await self._get_next_id(table_name)
        
        # 添加时间戳
        record_data["created_at"] = datetime.now().isoformat()
        record_data["updated_at"] = datetime.now().isoformat()
        
        data.append(record_data)
        await self._write_table(table_name, data)
        
        return record_data
    
    async def update(self, table_name: str, record_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新记录"""
        data = await self._read_table(table_name)
        
        for i, item in enumerate(data):
            if item.get("id") == record_id:
                # 更新字段
                data[i].update(update_data)
                data[i]["updated_at"] = datetime.now().isoformat()
                
                await self._write_table(table_name, data)
                return data[i]
        
        return None
    
    async def delete(self, table_name: str, record_id: int) -> bool:
        """删除记录"""
        data = await self._read_table(table_name)
        
        for i, item in enumerate(data):
            if item.get("id") == record_id:
                data.pop(i)
                await self._write_table(table_name, data)
                return True
        
        return False
    
    async def find_by_field(self, table_name: str, field: str, value: Any) -> List[Dict[str, Any]]:
        """根据字段查找记录"""
        data = await self._read_table(table_name)
        return [item for item in data if item.get(field) == value]


# 全局JSON数据库实例
json_db = JsonDatabase()


async def get_json_db() -> JsonDatabase:
    """获取JSON数据库实例的依赖注入函数"""
    return json_db