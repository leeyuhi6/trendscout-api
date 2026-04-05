import json
import os
from typing import List, Dict, Optional

class TrendsDataService:
    def __init__(self, data_path: str):
        self.data_path = data_path
        self.keywords = []
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(self.data_path) and os.path.getsize(self.data_path) > 10000:
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
                print(f"✅ 从文件加载 {len(self.keywords)} 条关键词")
                return
        except Exception as e:
            print(f"⚠️ 文件加载失败: {e}")

        try:
            from app.data_embedded import load_embedded_keywords
            raw_list = load_embedded_keywords()
            seen = set()
            raw = []
            for data in raw_list:
                kw = data.get('keyword', '').lower()
                if kw and kw not in seen:
                    seen.add(kw)
                    raw.append(data)
            self.keywords = raw
            print(f"✅ 从内嵌数据加载 {len(self.keywords)} 条关键词")
        except Exception as e:
            print(f"❌ 内嵌数据加载失败: {e}")
            self.keywords = []

    def _format(self, kw: dict) -> dict:
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
        if not query:
            return self.get_trending(limit)
        
        # 分词，过滤停用词（太短或太通用的词不参与匹配）
        stopwords = {'a', 'an', 'the', 'and', 'or', 'for', 'to', 'of', 'in', 'on', 'at', 'vs', 'with'}
        terms = [t.lower().strip() for t in query.split() 
                 if t.strip() and t.lower().strip() not in stopwords and len(t.strip()) > 1]
        
        if not terms:
            return self.get_trending(limit)
        
        # 纯 AND 逻辑：所有词都必须在关键词里
        results = []
        for kw in self.keywords:
            kw_lower = kw.get('keyword', '').lower()
            if all(term in kw_lower for term in terms):
                results.append(kw)
        
        results.sort(key=lambda x: x.get('avg_heat', 0), reverse=True)
        return [self._format(r) for r in results[:limit]]

    def get_trending(self, limit: int = 20) -> List[Dict]:
        valid = [kw for kw in self.keywords if kw.get('avg_heat', 0) > 10]
        sorted_kws = sorted(valid, key=lambda x: x.get('avg_heat', 0), reverse=True)
        return [self._format(k) for k in sorted_kws[:limit]]

    def get_rising(self, limit: int = 20) -> List[Dict]:
        rising = [kw for kw in self.keywords if kw.get('trend') == 'rising' and kw.get('avg_heat', 0) > 10]
        rising.sort(key=lambda x: x.get('growth_rate', 0), reverse=True)
        return [self._format(r) for r in rising[:limit]]
