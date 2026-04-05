import json
from typing import List, Dict, Optional

class TrendsDataService:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.keywords = []
        self.load_data()

    def load_data(self):
        """加载 JSONL 数据，自动去重"""
        try:
            seen = set()
            raw = []
            with open(self.data_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    kw = data.get('keyword', '').lower()
                    if kw and kw not in seen:
                        seen.add(kw)
                        raw.append(data)
            self.keywords = raw
            print(f"✅ 加载 {len(self.keywords)} 条关键词数据（已去重）")
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            self.keywords = []

    def _format(self, kw: dict) -> dict:
        """标准化输出字段"""
        return {
            "keyword": kw.get("keyword", ""),
            "avg_heat": round(kw.get("avg_heat", 0), 1),
            "trend": kw.get("trend", "stable"),
            "growth_rate": round(kw.get("growth_rate", 0), 1),
            "markets": kw.get("markets", {}),
            "active_markets": kw.get("active_markets", 0),
            "recent_avg": round(kw.get("recent_avg", 0), 1),
            "rising_queries": kw.get("rising_queries", []),
        }

    def search(self, query: Optional[str] = None, limit: int = 20) -> List[Dict]:
        """搜索关键词"""
        if not query:
            return self.get_trending(limit)

        q = query.lower().strip()
        results = [
            kw for kw in self.keywords
            if q in kw.get('keyword', '').lower()
        ]
        results.sort(key=lambda x: x.get('avg_heat', 0), reverse=True)
        return [self._format(r) for r in results[:limit]]

    def get_trending(self, limit: int = 20) -> List[Dict]:
        """获取热门趋势（热度 > 10，按热度排序）"""
        valid = [kw for kw in self.keywords if kw.get('avg_heat', 0) > 10]
        sorted_kws = sorted(valid, key=lambda x: x.get('avg_heat', 0), reverse=True)
        return [self._format(r) for r in sorted_kws[:limit]]

    def get_rising(self, limit: int = 20) -> List[Dict]:
        """获取上升趋势词"""
        rising = [
            kw for kw in self.keywords
            if kw.get('trend') == 'rising' and kw.get('avg_heat', 0) > 10
        ]
        rising.sort(key=lambda x: x.get('growth_rate', 0), reverse=True)
        return [self._format(r) for r in rising[:limit]]
