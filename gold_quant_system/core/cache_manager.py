import os
import json
import pickle
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


class CacheManager:
    """
    缓存管理器 - 管理本地数据缓存
    
    功能：
    - 自动缓存数据到本地
    - 支持多种缓存格式（pickle、json）
    - 自动过期机制
    - 缓存状态查询
    - 缓存清理功能
    """
    
    def __init__(self, cache_dir=None, default_ttl_hours=24):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录路径，默认为 ~/.goldquant/cache/
            default_ttl_hours: 默认缓存过期时间（小时）
        """
        if cache_dir is None:
            self.cache_dir = Path.home() / ".goldquant" / "cache"
        else:
            self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = timedelta(hours=default_ttl_hours)
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self.metadata = self._load_metadata()
        
        logger.info(f"缓存管理器初始化: {self.cache_dir}")
    
    def _load_metadata(self):
        """加载缓存元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存元数据失败: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存元数据失败: {e}")
    
    def _generate_key(self, identifier):
        """生成缓存键"""
        if isinstance(identifier, str):
            key_str = identifier
        else:
            key_str = str(identifier)
        
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, key, format='pickle'):
        """获取缓存文件路径"""
        ext = 'pkl' if format == 'pickle' else 'json'
        return self.cache_dir / f"{key}.{ext}"
    
    def put(self, identifier, data, ttl_hours=None, format='pickle'):
        """
        存入缓存
        
        Args:
            identifier: 缓存标识符
            data: 要缓存的数据
            ttl_hours: 过期时间（小时），使用默认值为None
            format: 缓存格式，'pickle' 或 'json'
        """
        key = self._generate_key(identifier)
        cache_path = self._get_cache_path(key, format)
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self.default_ttl
        expires_at = (datetime.now() + ttl).isoformat()
        
        try:
            if format == 'pickle':
                with open(cache_path, 'wb') as f:
                    pickle.dump(data, f)
            else:
                with open(cache_path, 'w', encoding='utf-8') as f:
                    if isinstance(data, (dict, list)):
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    else:
                        json.dump({'data': str(data)}, f, ensure_ascii=False, indent=2)
            
            self.metadata[key] = {
                'identifier': str(identifier)[:100],
                'created_at': datetime.now().isoformat(),
                'expires_at': expires_at,
                'format': format,
                'size_bytes': cache_path.stat().st_size
            }
            self._save_metadata()
            
            logger.debug(f"缓存已保存: {key} ({identifier})")
            return True
            
        except Exception as e:
            logger.error(f"缓存保存失败: {e}")
            if cache_path.exists():
                cache_path.unlink()
            return False
    
    def get(self, identifier, default=None, format=None):
        """
        获取缓存
        
        Args:
            identifier: 缓存标识符
            default: 缓存不存在或过期时的默认值
            format: 强制指定格式，自动检测为None
            
        Returns:
            缓存的数据或默认值
        """
        key = self._generate_key(identifier)
        
        if key not in self.metadata:
            return default
        
        meta = self.metadata[key]
        
        # 检查是否过期
        try:
            expires_at = datetime.fromisoformat(meta['expires_at'])
            if datetime.now() > expires_at:
                logger.debug(f"缓存已过期: {key}")
                self.invalidate(identifier)
                return default
        except Exception as e:
            logger.warning(f"检查缓存过期时间失败: {e}")
        
        # 确定格式
        cache_format = format or meta.get('format', 'pickle')
        cache_path = self._get_cache_path(key, cache_format)
        
        if not cache_path.exists():
            logger.debug(f"缓存文件不存在: {cache_path}")
            self.metadata.pop(key, None)
            self._save_metadata()
            return default
        
        try:
            if cache_format == 'pickle':
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
            else:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            logger.debug(f"缓存已读取: {key}")
            return data
            
        except Exception as e:
            logger.error(f"缓存读取失败: {e}")
            return default
    
    def invalidate(self, identifier):
        """
        使缓存失效
        
        Args:
            identifier: 缓存标识符
        """
        key = self._generate_key(identifier)
        
        if key in self.metadata:
            meta = self.metadata[key]
            cache_format = meta.get('format', 'pickle')
            cache_path = self._get_cache_path(key, cache_format)
            
            if cache_path.exists():
                cache_path.unlink()
            
            self.metadata.pop(key, None)
            self._save_metadata()
            logger.debug(f"缓存已失效: {key}")
    
    def invalidate_all(self):
        """清除所有缓存"""
        count = 0
        for key in list(self.metadata.keys()):
            meta = self.metadata[key]
            cache_format = meta.get('format', 'pickle')
            cache_path = self._get_cache_path(key, cache_format)
            
            if cache_path.exists():
                cache_path.unlink()
            count += 1
        
        self.metadata = {}
        self._save_metadata()
        logger.info(f"已清除所有缓存: {count} 项")
    
    def get_status(self):
        """
        获取缓存状态
        
        Returns:
            dict: 缓存状态信息
        """
        total_size = 0
        active_count = 0
        expired_count = 0
        
        for key, meta in self.metadata.items():
            try:
                total_size += meta.get('size_bytes', 0)
                expires_at = datetime.fromisoformat(meta['expires_at'])
                if datetime.now() > expires_at:
                    expired_count += 1
                else:
                    active_count += 1
            except Exception:
                pass
        
        return {
            'cache_dir': str(self.cache_dir),
            'total_items': len(self.metadata),
            'active_items': active_count,
            'expired_items': expired_count,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
    
    def list_items(self, include_expired=False):
        """
        列出所有缓存项
        
        Args:
            include_expired: 是否包含过期的缓存项
            
        Returns:
            list: 缓存项列表
        """
        items = []
        for key, meta in self.metadata.items():
            try:
                expires_at = datetime.fromisoformat(meta['expires_at'])
                is_expired = datetime.now() > expires_at
                
                if not include_expired and is_expired:
                    continue
                
                items.append({
                    'key': key,
                    'identifier': meta.get('identifier', ''),
                    'created_at': meta.get('created_at', ''),
                    'expires_at': meta.get('expires_at', ''),
                    'is_expired': is_expired,
                    'format': meta.get('format', ''),
                    'size_bytes': meta.get('size_bytes', 0)
                })
            except Exception:
                pass
        
        return items
    
    def clean_expired(self):
        """清理过期的缓存"""
        cleaned = 0
        for key in list(self.metadata.keys()):
            try:
                meta = self.metadata[key]
                expires_at = datetime.fromisoformat(meta['expires_at'])
                
                if datetime.now() > expires_at:
                    cache_format = meta.get('format', 'pickle')
                    cache_path = self._get_cache_path(key, cache_format)
                    
                    if cache_path.exists():
                        cache_path.unlink()
                    
                    self.metadata.pop(key)
                    cleaned += 1
            except Exception as e:
                logger.warning(f"清理过期缓存失败: {e}")
        
        if cleaned > 0:
            self._save_metadata()
            logger.info(f"已清理过期缓存: {cleaned} 项")
        
        return cleaned


# 全局缓存管理器实例
_cache_manager = None


def get_cache_manager():
    """获取全局缓存管理器实例"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager
