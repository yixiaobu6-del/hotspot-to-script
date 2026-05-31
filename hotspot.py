"""热点检测模块

基于关键词、搜索量、社交传播等多维度检测实时热点。
"""

import re
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pathlib import Path


class HotspotStage(Enum):
    """热点发展阶段"""
    RISING = "rising"        # 上升期
    EXPLODING = "exploding"  # 爆发期
    PEAK = "peak"            # 峰值期
    DECLINING = "declining"  # 衰退期
    STABLE = "stable"        # 稳定期


class HotspotCategory(Enum):
    """热点类别"""
    SOCIETY = "社会"
    TECH = "科技"
    FINANCE = "财经"
    ENTERTAINMENT = "娱乐"
    SPORTS = "体育"
    EDUCATION = "教育"
    LIFESTYLE = "生活"
    HEALTH = "健康"
    POLITICS = "时政"


@dataclass
class Hotspot:
    """热点数据结构"""
    title: str
    url: str
    score: int                          # 热度分数 0-100
    stage: HotspotStage
    source: str                         # 来源平台
    category: Optional[HotspotCategory] = None
    keywords: List[str] = field(default_factory=list)
    summary: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    trend_data: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "url": self.url,
            "score": self.score,
            "stage": self.stage.value,
            "source": self.source,
            "category": self.category.value if self.category else None,
            "keywords": self.keywords,
            "summary": self.summary,
            "metrics": self.metrics,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Hotspot":
        return cls(
            title=data["title"],
            url=data["url"],
            score=data["score"],
            stage=HotspotStage(data["stage"]),
            source=data["source"],
            category=HotspotCategory(data["category"]) if data.get("category") else None,
            keywords=data.get("keywords", []),
            summary=data.get("summary", ""),
            metrics=data.get("metrics", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
        )


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    hotspot: Hotspot
    stage: HotspotStage
    growth_rate: float                   # 增长率
    prediction: str                      # 预测描述
    recommendation: str                  # 行动建议
    peak_time: Optional[datetime] = None
    decline_rate: Optional[float] = None
    related_topics: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hotspot": self.hotspot.to_dict(),
            "stage": self.stage.value,
            "growth_rate": self.growth_rate,
            "prediction": self.prediction,
            "recommendation": self.recommendation,
            "peak_time": self.peak_time.isoformat() if self.peak_time else None,
            "decline_rate": self.decline_rate,
            "related_topics": self.related_topics,
        }


class HotspotSource(ABC):
    """热点数据源抽象基类"""

    name: str = "base"
    platforms: List[str] = []

    @abstractmethod
    def fetch(self, keywords: List[str], limit: int = 20) -> List[Hotspot]:
        """抓取热点数据"""
        pass

    @abstractmethod
    def get_trend_data(self, hotspot: Hotspot) -> List[Dict[str, Any]]:
        """获取热点趋势数据"""
        pass


class MockHotspotSource(HotspotSource):
    """模拟热点数据源（用于测试）"""

    name = "mock"
    platforms = ["mock"]

    def fetch(self, keywords: List[str], limit: int = 20) -> List[Hotspot]:
        mock_data = [
            {
                "title": f"{kw}成为热门话题" if kw else "热点话题",
                "url": f"https://mock.example.com/topic/{i}",
                "score": 80 + (i * 2),
                "stage": "rising",
                "source": "mock",
                "keywords": [kw] if kw else [],
                "summary": f"关于{kw}的热门讨论",
            }
            for i, kw in enumerate(keywords[:limit])
        ]
        return [Hotspot.from_dict(d) for d in mock_data]

    def get_trend_data(self, hotspot: Hotspot) -> List[Dict[str, Any]]:
        return [
            {"time": "2024-01-01", "score": hotspot.score - 20},
            {"time": "2024-01-02", "score": hotspot.score - 10},
            {"time": "2024-01-03", "score": hotspot.score},
        ]


@dataclass
class HotspotConfig:
    """热点检测配置"""
    min_score: int = 50
    platforms: List[str] = field(default_factory=lambda: ["weibo", "douyin", "zhihu"])
    keywords: List[str] = field(default_factory=list)
    exclude_keywords: List[str] = field(default_factory=list)
    categories: List[HotspotCategory] = field(default_factory=list)
    max_age_hours: int = 24
    language: str = "zh"


class HotspotDetector:
    """热点检测器"""

    def __init__(self, config: Optional[HotspotConfig] = None):
        self.config = config or HotspotConfig()
        self.sources: Dict[str, HotspotSource] = {}
        self._register_default_sources()

    def _register_default_sources(self):
        """注册默认数据源"""
        self.register_source(MockHotspotSource())

    def register_source(self, source: HotspotSource):
        """注册数据源"""
        self.sources[source.name] = source

    def detect(
        self,
        keywords: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[Hotspot]:
        """检测热点"""
        kw = keywords or self.config.keywords
        all_hotspots = []

        for source in self.sources.values():
            try:
                hotspots = source.fetch(kw, limit)
                all_hotspots.extend(hotspots)
            except Exception as e:
                print(f"数据源 {source.name} 抓取失败: {e}")

        # 过滤和排序
        filtered = self._filter_hotspots(all_hotspots)
        sorted_hotspots = sorted(filtered, key=lambda h: h.score, reverse=True)

        return sorted_hotspots[:limit]

    def detect_realtime(self) -> List[Hotspot]:
        """检测实时热点"""
        return self.detect()

    def _filter_hotspots(self, hotspots: List[Hotspot]) -> List[Hotspot]:
        """过滤热点"""
        filtered = []

        for h in hotspots:
            # 热度阈值过滤
            if h.score < self.config.min_score:
                continue

            # 排除关键词过滤
            if self.config.exclude_keywords:
                if any(kw in h.title for kw in self.config.exclude_keywords):
                    continue

            # 类别过滤
            if self.config.categories and h.category:
                if h.category not in self.config.categories:
                    continue

            filtered.append(h)

        return filtered

    def analyze_trend(self, hotspot: Hotspot) -> TrendAnalysis:
        """分析热点趋势"""
        # 获取趋势数据
        source = self.sources.get(hotspot.source)
        if not source:
            return self._default_trend_analysis(hotspot)

        trend_data = source.get_trend_data(hotspot)

        if len(trend_data) < 2:
            return self._default_trend_analysis(hotspot)

        # 计算增长率
        current = trend_data[-1].get("score", hotspot.score)
        previous = trend_data[-2].get("score", hotspot.score)

        if previous > 0:
            growth_rate = (current - previous) / previous * 100
        else:
            growth_rate = 0

        # 判断阶段
        if growth_rate > 50:
            stage = HotspotStage.EXPLODING
            prediction = "热点正在爆发，建议立即跟进"
            recommendation = "快速创作，抢占流量窗口"
        elif growth_rate > 20:
            stage = HotspotStage.RISING
            prediction = "热度持续上升，有发展空间"
            recommendation = "可以跟进，准备深度内容"
        elif growth_rate < -30:
            stage = HotspotStage.DECLINING
            prediction = "热度正在下降"
            recommendation = "不建议跟进，寻找新热点"
        elif current > 90:
            stage = HotspotStage.PEAK
            prediction = "已到峰值，可能即将下降"
            recommendation = "可以考虑独特角度切入"
        else:
            stage = HotspotStage.STABLE
            prediction = "热度稳定"
            recommendation = "可以做差异化内容"

        return TrendAnalysis(
            hotspot=hotspot,
            stage=stage,
            growth_rate=growth_rate,
            prediction=prediction,
            recommendation=recommendation,
        )

    def _default_trend_analysis(self, hotspot: Hotspot) -> TrendAnalysis:
        """默认趋势分析"""
        return TrendAnalysis(
            hotspot=hotspot,
            stage=hotspot.stage,
            growth_rate=0,
            prediction="暂无足够数据",
            recommendation="建议进一步分析",
        )

    def export(self, hotspots: List[Hotspot], output_path: str):
        """导出热点数据"""
        path = Path(output_path)
        data = [h.to_dict() for h in hotspots]

        if path.suffix == ".json":
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        else:
            # 默认导出为 markdown
            with open(path, "w", encoding="utf-8") as f:
                f.write("# 热点列表\n\n")
                for i, h in enumerate(hotspots, 1):
                    f.write(f"## {i}. {h.title}\n\n")
                    f.write(f"- 热度: {h.score}\n")
                    f.write(f"- 阶段: {h.stage.value}\n")
                    f.write(f"- 来源: {h.source}\n")
                    if h.summary:
                        f.write(f"- 摘要: {h.summary}\n")
                    f.write(f"- 链接: {h.url}\n\n")


# 便捷函数
def detect_hotspots(
    keywords: Optional[List[str]] = None,
    platforms: Optional[List[str]] = None,
    min_score: int = 50,
    limit: int = 20,
) -> List[Hotspot]:
    """检测热点（便捷函数）"""
    config = HotspotConfig(
        platforms=platforms or ["mock"],
        min_score=min_score,
    )
    detector = HotspotDetector(config)
    return detector.detect(keywords, limit)