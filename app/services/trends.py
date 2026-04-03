import json
from typing import List, Dict, Optional

class TrendsDataService:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.keywords = []
        self.load_data()
    
    def load_data(self):
        """加载 JSONL 数据"""
        try:
            with open(self.data_path, 'r') as f:
                for line in f:
                    data = json.loads(line)
                    self.keywords.append(data)
            print(f"✅ 加载 {len(self.keywords)} 条关键词数据")
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
    
    def search(self, query: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """搜索关键词"""
        if not query:
            return self.get_trending(limit)
        
        results = [
            kw for kw in self.keywords 
            if query.lower() in kw.get('keyword', '').lower()
        ]
        # 按热度排序
        results.sort(key=lambda x: x.get('avg_heat', 0), reverse=True)
        return results[:limit]
    
    def get_trending(self, limit: int = 20) -> List[Dict]:
        """获取热门趋势（按热度排序）"""
        sorted_keywords = sorted(
            self.keywords, 
            key=lambda x: x.get('avg_heat', 0), 
            reverse=True
        )
        return sorted_keywords[:limit]
