# Hotspot to Script - 热点追踪与脚本生成

> 热点检测到脚本生成的自动化框架，实时热点自动转化为结构化内容脚本

---

## Features / 功能特点

| 功能 | 说明 |
|------|------|
| 热点检测 | 基于关键词、搜索量、社交传播等多维度检测 |
| 趋势分析 | 识别热点的发展阶段（上升期/爆发期/衰退期） |
| 脚本生成 | 自动生成符合四模块结构的脚本框架 |
| 多平台适配 | 支持抖音、小红书、B站、公众号等平台模板 |
| CLI 命令行 | 完整的命令行操作接口 |
| 扩展开发 | 支持自定义热点源和模板 |
| 批量生成 | 支持批量话题脚本生成 |

## Installation / 安装

```bash
# 通过 pip 安装
pip install hotspot-to-script

# 或从源码安装
git clone https://github.com/yourusername/hotspot-to-script.git
cd hotspot-to-script
pip install -e .
```

## Usage / 使用方法

### 热点检测

```bash
hotspot detect --keywords "AI,人工智能" --platform weibo
```

```python
from hotspot_to_script import HotspotDetector

detector = HotspotDetector()
hotspots = detector.detect(keywords=["AI", "人工智能"])

for h in hotspots:
    print(f"{h.title} - 热度: {h.score}, 阶段: {h.stage}")
```

### 脚本生成

```bash
hotspot generate "年轻人开始反向消费" --template four_module --platform douyin
```

```python
from hotspot_to_script import ScriptGenerator

generator = ScriptGenerator()
script = generator.generate(
    topic="年轻人开始反向消费",
    template="four_module",
    platform="douyin"
)

print(script.to_markdown())
```

### CLI 命令大全

```bash
# 检测热点
hotspot detect --keywords "AI" --platform weibo --limit 10

# 分析趋势
hotspot analyze "热点标题" --history 7d

# 生成脚本
hotspot generate "话题" --template four_module --platform douyin

# 批量生成
hotspot batch topics.txt --output ./scripts/

# 导出模板
hotspot template list
hotspot template export four_module --output my_template.yaml
```

### 四模块结构模板

| 模块 | 内容 | 占比 | 技巧 |
|------|------|:----:|------|
| 破碎与重构 | 问题与时代背景 | 15% | 砸碎默认剧本、时代断层、自我暴露 |
| 核心洞察 | 核心框架（"道"） | 25% | 创造新名词、PAS模型、跨领域合成 |
| 解决方案 | 框架与工具（"术"） | 40% | 强结构分章、独特框架、清晰主线 |
| 润滑剂 | 修辞手法（贯穿全文） | 20% | 微故事、隐喻、金句、提问驱动 |

### 平台适配

| 平台 | 特点 | 推荐长度 |
|------|------|----------|
| 抖音 | 快节奏、强钩子 | 60-90秒 |
| 小红书 | 图文结合、种草 | 500-800字 |
| B站 | 深度、干货 | 8-15分钟 |
| 公众号 | 结构化、可读性 | 2000-4000字 |
| 视频号 | 短平快、情绪化 | 30-60秒 |

### 扩展开发

```python
from hotspot import HotspotSource, Hotspot

class MyHotspotSource(HotspotSource):
    name = "my_platform"

    def fetch(self, keywords):
        return [
            Hotspot(
                title="热点标题",
                url="https://...",
                score=85,
                stage="rising",
                source=self.name,
            )
        ]

# 注册
detector = HotspotDetector()
detector.register_source(MyHotspotSource())
```

## Contributing / 贡献

参见 [CONTRIBUTING.md](CONTRIBUTING.md)

欢迎贡献：
- 添加新热点源
- 改进检测算法
- 新增模板类型
- 报告问题

## License / 许可证

MIT License - 参见 [LICENSE](LICENSE)

---

> 版本：1.0.0 | 更新日期：2026-05-30