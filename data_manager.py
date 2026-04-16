"""
数据管理模块
功能：
- 数据导入/导出
- 自定义数据源管理
- 数据质量监控
- 数据备份和恢复
"""
import os
import json
import shutil
from datetime import datetime
import pandas as pd
from loguru import logger

class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.backup_dir = os.path.join(self.base_dir, 'data', 'backups')
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def list_data_files(self):
        """列出所有数据文件"""
        data_files = []
        if os.path.exists(self.data_dir):
            for file in os.listdir(self.data_dir):
                if file.endswith('.csv'):
                    file_path = os.path.join(self.data_dir, file)
                    file_size = os.path.getsize(file_path) / 1024  # KB
                    modified_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # 尝试读取文件信息
                    try:
                        df = pd.read_csv(file_path)
                        row_count = len(df)
                        columns = list(df.columns)
                    except Exception as e:
                        row_count = 0
                        columns = []
                    
                    data_files.append({
                        'name': file,
                        'path': file_path,
                        'size': f'{file_size:.2f} KB',
                        'modified_time': modified_time,
                        'row_count': row_count,
                        'columns': columns
                    })
        return data_files
    
    def import_data(self, file_path, target_name=None):
        """导入数据"""
        try:
            # 读取导入的文件
            df = pd.read_csv(file_path)
            
            # 验证数据格式
            if 'date' not in df.columns:
                return {'success': False, 'message': '数据文件缺少date列'}
            
            if 'close' not in df.columns:
                return {'success': False, 'message': '数据文件缺少close列'}
            
            # 处理日期格式
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            if df['date'].isnull().any():
                return {'success': False, 'message': '日期格式错误'}
            
            # 排序并去重
            df = df.sort_values('date').drop_duplicates('date', keep='last')
            
            # 生成目标文件名
            if target_name:
                target_path = os.path.join(self.data_dir, target_name)
            else:
                base_name = os.path.basename(file_path)
                target_path = os.path.join(self.data_dir, base_name)
            
            # 保存数据
            df.to_csv(target_path, index=False, encoding='utf-8')
            logger.info(f"数据导入成功: {target_path}")
            
            return {'success': True, 'message': f'数据导入成功，共 {len(df)} 条记录'}
        except Exception as e:
            logger.error(f"数据导入失败: {e}")
            return {'success': False, 'message': f'导入失败: {str(e)}'}
    
    def export_data(self, file_name, output_path):
        """导出数据"""
        try:
            data_path = os.path.join(self.data_dir, file_name)
            if not os.path.exists(data_path):
                return {'success': False, 'message': '数据文件不存在'}
            
            # 读取数据
            df = pd.read_csv(data_path)
            
            # 保存到输出路径
            df.to_csv(output_path, index=False, encoding='utf-8')
            logger.info(f"数据导出成功: {output_path}")
            
            return {'success': True, 'message': f'数据导出成功，共 {len(df)} 条记录'}
        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            return {'success': False, 'message': f'导出失败: {str(e)}'}
    
    def backup_data(self, file_name=None):
        """备份数据"""
        try:
            backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_folder = os.path.join(self.backup_dir, backup_time)
            os.makedirs(backup_folder, exist_ok=True)
            
            if file_name:
                # 备份单个文件
                src_path = os.path.join(self.data_dir, file_name)
                if not os.path.exists(src_path):
                    return {'success': False, 'message': '数据文件不存在'}
                
                dst_path = os.path.join(backup_folder, file_name)
                shutil.copy2(src_path, dst_path)
                logger.info(f"数据备份成功: {file_name} -> {dst_path}")
            else:
                # 备份所有数据文件
                for file in os.listdir(self.data_dir):
                    if file.endswith('.csv'):
                        src_path = os.path.join(self.data_dir, file)
                        dst_path = os.path.join(backup_folder, file)
                        shutil.copy2(src_path, dst_path)
                logger.info(f"全部数据备份成功: {backup_folder}")
            
            return {'success': True, 'message': f'数据备份成功，备份时间: {backup_time}'}
        except Exception as e:
            logger.error(f"数据备份失败: {e}")
            return {'success': False, 'message': f'备份失败: {str(e)}'}
    
    def restore_data(self, backup_time, file_name=None):
        """恢复数据"""
        try:
            backup_folder = os.path.join(self.backup_dir, backup_time)
            if not os.path.exists(backup_folder):
                return {'success': False, 'message': '备份不存在'}
            
            if file_name:
                # 恢复单个文件
                src_path = os.path.join(backup_folder, file_name)
                if not os.path.exists(src_path):
                    return {'success': False, 'message': '备份文件不存在'}
                
                dst_path = os.path.join(self.data_dir, file_name)
                shutil.copy2(src_path, dst_path)
                logger.info(f"数据恢复成功: {src_path} -> {dst_path}")
            else:
                # 恢复所有数据文件
                for file in os.listdir(backup_folder):
                    if file.endswith('.csv'):
                        src_path = os.path.join(backup_folder, file)
                        dst_path = os.path.join(self.data_dir, file)
                        shutil.copy2(src_path, dst_path)
                logger.info(f"全部数据恢复成功: {backup_folder}")
            
            return {'success': True, 'message': f'数据恢复成功，备份时间: {backup_time}'}
        except Exception as e:
            logger.error(f"数据恢复失败: {e}")
            return {'success': False, 'message': f'恢复失败: {str(e)}'}
    
    def list_backups(self):
        """列出所有备份"""
        backups = []
        if os.path.exists(self.backup_dir):
            for backup in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, backup)
                if os.path.isdir(backup_path):
                    # 统计备份文件数量
                    file_count = len([f for f in os.listdir(backup_path) if f.endswith('.csv')])
                    
                    # 计算备份大小
                    total_size = 0
                    for file in os.listdir(backup_path):
                        file_path = os.path.join(backup_path, file)
                        if os.path.isfile(file_path):
                            total_size += os.path.getsize(file_path)
                    total_size = total_size / 1024  # KB
                    
                    backups.append({
                        'time': backup,
                        'path': backup_path,
                        'file_count': file_count,
                        'size': f'{total_size:.2f} KB'
                    })
            # 按时间倒序排序
            backups.sort(key=lambda x: x['time'], reverse=True)
        return backups
    
    def validate_data_quality(self, file_name):
        """验证数据质量"""
        try:
            data_path = os.path.join(self.data_dir, file_name)
            if not os.path.exists(data_path):
                return {'success': False, 'message': '数据文件不存在'}
            
            df = pd.read_csv(data_path)
            
            # 基本统计
            stats = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'date_range': f"{df['date'].min()} ~ {df['date'].max()}" if 'date' in df.columns else 'N/A',
                'missing_values': df.isnull().sum().to_dict(),
                'duplicate_rows': df.duplicated().sum(),
            }
            
            # 价格统计（如果有close列）
            if 'close' in df.columns:
                stats['price_stats'] = {
                    'min': df['close'].min(),
                    'max': df['close'].max(),
                    'mean': df['close'].mean(),
                    'std': df['close'].std()
                }
            
            logger.info(f"数据质量验证完成: {file_name}")
            return {'success': True, 'stats': stats}
        except Exception as e:
            logger.error(f"数据质量验证失败: {e}")
            return {'success': False, 'message': f'验证失败: {str(e)}'}

# 全局实例
data_manager = DataManager()