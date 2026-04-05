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

        # 分词，过滤停用词
        stopwords = {'a', 'an', 'the', 'and', 'or', 'for', 'to', 'of', 'in', 'on', 'at', 'with', 'free', 'best'}
        all_terms = [t.lower().strip() for t in query.split() if t.strip()]
        terms = [t for t in all_terms if t not in stopwords and len(t) > 1]

        if not terms:
            return self.get_trending(limit)

        # 按长度排序，优先用长词匹配（更精确）
        terms_by_len = sorted(terms, key=len, reverse=True)

        # 策略：用最长的词（核心词）做主匹配，其余词加分
        core_term = terms_by_len[0]
        other_terms = terms_by_len[1:]

        results = []
        for kw in self.keywords:
            kw_lower = kw.get('keyword', '').lower()
            # 核心词必须命中
            if core_term not in kw_lower:
                continue
            # 计算相关度分数（命中的其他词越多越靠前）
            score = kw.get('avg_heat', 0)
            for t in other_terms:
                if t in kw_lower:
                    score += 20  # 额外加分
            results.append((score, kw))

        # 按分数排序
        results.sort(key=lambda x: x[0], reverse=True)
        return [self._format(kw) for _, kw in results[:limit]]

    def get_trending(self, limit: int = 20) -> List[Dict]:
        valid = [kw for kw in self.keywords if kw.get('avg_heat', 0) > 10]
        sorted_kws = sorted(valid, key=lambda x: x.get('avg_heat', 0), reverse=True)
        return [self._format(k) for k in sorted_kws[:limit]]

    def get_rising(self, limit: int = 20) -> List[Dict]:
        rising = [kw for kw in self.keywords if kw.get('trend') == 'rising' and kw.get('avg_heat', 0) > 10]
        rising.sort(key=lambda x: x.get('growth_rate', 0), reverse=True)
        return [self._format(r) for r in rising[:limit]]
