"""脚本生成模块

基于四模块结构自动生成内容脚本。
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any


class ScriptStyle(Enum):
    """脚本风格"""
    CASUAL = "casual"       # 轻松口语
    FORMAL = "formal"       # 正式严谨
    STORY = "story"         # 故事化
    EDUCATIONAL = "educational"  # 教学式


class ScriptLength(Enum):
    """脚本长度"""
    SHORT = "short"         # 短篇 (500-1000字)
    MEDIUM = "medium"       # 中篇 (1500-3000字)
    LONG = "long"           # 长篇 (3000字以上)


class Platform(Enum):
    """发布平台"""
    DOUYIN = "douyin"
    XIAOHONGSHU = "xiaohongshu"
    BILIBILI = "bilibili"
    WECHAT = "wechat"
    SHIPINHAO = "shipinhao"
    ZHIHU = "zhihu"


@dataclass
class Module:
    """脚本模块"""
    name: str
    purpose: str
    content: str = ""
    techniques: List[str] = field(default_factory=list)
    length_ratio: float = 0.25
    examples: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "purpose": self.purpose,
            "content": self.content,
            "techniques": self.techniques,
            "length_ratio": self.length_ratio,
            "examples": self.examples,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Module":
        return cls(
            name=data["name"],
            purpose=data["purpose"],
            content=data.get("content", ""),
            techniques=data.get("techniques", []),
            length_ratio=data.get("length_ratio", 0.25),
            examples=data.get("examples", []),
        )


@dataclass
class Template:
    """脚本模板"""
    name: str
    description: str
    modules: List[Module]
    platform_adapters: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "modules": [m.to_dict() for m in self.modules],
            "platform_adapters": self.platform_adapters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        return cls(
            name=data["name"],
            description=data["description"],
            modules=[Module.from_dict(m) for m in data["modules"]],
            platform_adapters=data.get("platform_adapters", {}),
        )

    def get_total_length_ratio(self) -> float:
        return sum(m.length_ratio for m in self.modules)


@dataclass
class Script:
    """生成的脚本"""
    topic: str
    template: str
    modules: Dict[str, Module]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    style: ScriptStyle = ScriptStyle.CASUAL
    length: ScriptLength = ScriptLength.MEDIUM
    platform: Optional[Platform] = None

    def to_markdown(self) -> str:
        """转换为 Markdown 格式"""
        lines = [
            f"# {self.topic}",
            "",
            f"> 模板: {self.template} | 风格: {self.style.value} | 长度: {self.length.value}",
            f"> 创建时间: {self.created_at.strftime('%Y-%m-%d %H:%M')}",
            "",
            "---",
            "",
        ]

        for name, module in self.modules.items():
            lines.append(f"## {name}")
            lines.append("")
            lines.append(f"*{module.purpose}*")
            lines.append("")
            lines.append(module.content)
            lines.append("")
            if module.techniques:
                lines.append("**技巧：**")
                for t in module.techniques:
                    lines.append(f"- {t}")
                lines.append("")
            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "topic": self.topic,
            "template": self.template,
            "modules": {k: v.to_dict() for k, v in self.modules.items()},
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "style": self.style.value,
            "length": self.length.value,
            "platform": self.platform.value if self.platform else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Script":
        return cls(
            topic=data["topic"],
            template=data["template"],
            modules={k: Module.from_dict(v) for k, v in data["modules"].items()},
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            style=ScriptStyle(data.get("style", "casual")),
            length=ScriptLength(data.get("length", "medium")),
            platform=Platform(data["platform"]) if data.get("platform") else None,
        )


@dataclass
class ScriptConfig:
    """脚本生成配置"""
    template: str = "four_module"
    style: ScriptStyle = ScriptStyle.CASUAL
    length: ScriptLength = ScriptLength.MEDIUM
    platform: Optional[Platform] = None
    include_examples: bool = True
    include_techniques: bool = True
    word_count: Optional[int] = None


# 预定义模板
DEFAULT_TEMPLATES = {
    "four_module": Template(
        name="四模块结构",
        description="破碎与重构 → 核心洞察 → 解决方案 → 润滑剂",
        modules=[
            Module(
                name="破碎与重构",
                purpose="问题与时代背景，打破默认剧本",
                techniques=["砸碎默认剧本", "时代断层", "自我暴露"],
                length_ratio=0.15,
            ),
            Module(
                name="核心洞察",
                purpose="核心框架（'道'），提供认知升级",
                techniques=["创造新名词", "PAS模型", "跨领域合成"],
                length_ratio=0.25,
            ),
            Module(
                name="解决方案",
                purpose="框架与工具（'术'），可执行步骤",
                techniques=["强结构分章", "独特框架", "清晰主线"],
                length_ratio=0.40,
            ),
            Module(
                name="润滑剂",
                purpose="修辞手法，贯穿全文",
                techniques=["微故事", "隐喻", "金句", "提问驱动"],
                length_ratio=0.20,
            ),
        ],
    ),
    "three_act": Template(
        name="三幕式结构",
        description="开端 → 冲突 → 结局",
        modules=[
            Module(
                name="开端",
                purpose="建立背景，引入角色",
                techniques=["开场钩子", "场景设定", "人物介绍"],
                length_ratio=0.25,
            ),
            Module(
                name="冲突",
                purpose="核心矛盾，推动情节",
                techniques=["矛盾升级", "转折点", "情感爆发"],
                length_ratio=0.50,
            ),
            Module(
                name="结局",
                purpose="解决问题，升华主题",
                techniques=["高潮解决", "余韵收尾", "主题升华"],
                length_ratio=0.25,
            ),
        ],
    ),
    "hero_journey": Template(
        name="英雄之旅",
        description="冒险召唤 → 试炼 → 转变 → 归来",
        modules=[
            Module(
                name="冒险召唤",
                purpose="打破平静，接受召唤",
                techniques=["平凡世界", "冒险召唤", "拒绝召唤"],
                length_ratio=0.20,
            ),
            Module(
                name="试炼之路",
                purpose="面对挑战，获得成长",
                techniques=["跨越门槛", "试炼盟友", "接近洞穴"],
                length_ratio=0.40,
            ),
            Module(
                name="转变归来",
                purpose="终极考验，蜕变归来",
                techniques=["核心考验", "获得奖赏", "返回之路"],
                length_ratio=0.40,
            ),
        ],
    ),
}

# 平台适配配置
PLATFORM_CONFIGS = {
    Platform.DOUYIN: {
        "max_length": 90,  # 秒
        "hook_time": 3,
        "style": "casual",
        "techniques": ["快节奏", "强钩子", "反转", "情绪化"],
    },
    Platform.XIAOHONGSHU: {
        "word_count": 800,
        "style": "casual",
        "techniques": ["图文结合", "种草感", "emoji", "话题标签"],
    },
    Platform.BILIBILI: {
        "min_length": 480,  # 秒
        "style": "educational",
        "techniques": ["深度干货", "UP主个性", "弹幕互动点"],
    },
    Platform.WECHAT: {
        "word_count": 3000,
        "style": "formal",
        "techniques": ["结构化", "可读性", "金句", "引用"],
    },
    Platform.SHIPINHAO: {
        "max_length": 60,  # 秒
        "style": "casual",
        "techniques": ["短平快", "情绪化", "话题性"],
    },
    Platform.ZHIHU: {
        "word_count": 2000,
        "style": "formal",
        "techniques": ["专业深度", "数据支撑", "逻辑严密"],
    },
}


class ScriptGenerator:
    """脚本生成器"""

    def __init__(self, config: Optional[ScriptConfig] = None):
        self.config = config or ScriptConfig()
        self.templates: Dict[str, Template] = DEFAULT_TEMPLATES.copy()

    def register_template(self, template: Template):
        """注册自定义模板"""
        self.templates[template.name] = template

    def load_template(self, path: str) -> Template:
        """从文件加载模板"""
        p = Path(path)
        if p.suffix in [".yaml", ".yml"]:
            import yaml
            with open(p, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        else:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)

        template = Template.from_dict(data)
        self.register_template(template)
        return template

    def generate(
        self,
        topic: str,
        template: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Script:
        """生成脚本"""
        template_name = template or self.config.template

        if template_name not in self.templates:
            raise ValueError(f"未知模板: {template_name}")

        tpl = self.templates[template_name]
        ctx = context or {}

        # 生成各模块内容
        modules = {}
        for module in tpl.modules:
            content = self._generate_module_content(
                module=module,
                topic=topic,
                context=ctx,
            )
            modules[module.name] = Module(
                name=module.name,
                purpose=module.purpose,
                content=content,
                techniques=module.techniques if self.config.include_techniques else [],
                length_ratio=module.length_ratio,
                examples=module.examples if self.config.include_examples else [],
            )

        # 创建脚本对象
        script = Script(
            topic=topic,
            template=template_name,
            modules=modules,
            style=self.config.style,
            length=self.config.length,
            platform=self.config.platform,
            metadata={
                "target_audience": ctx.get("target_audience", ""),
                "key_points": ctx.get("key_points", []),
                "tone": ctx.get("tone", ""),
            },
        )

        return script

    def _generate_module_content(
        self,
        module: Module,
        topic: str,
        context: Dict[str, Any],
    ) -> str:
        """生成模块内容框架"""
        lines = []

        # 模块标题
        lines.append(f"<!-- {module.name}: {module.purpose} -->")
        lines.append("")

        # 根据模块类型生成内容框架
        if module.name == "破碎与重构":
            lines.extend(self._generate_opening(topic, context))
        elif module.name == "核心洞察":
            lines.extend(self._generate_insight(topic, context))
        elif module.name == "解决方案":
            lines.extend(self._generate_solution(topic, context))
        elif module.name == "润滑剂":
            lines.extend(self._generate_rhetoric(topic, context))
        elif module.name == "开端":
            lines.extend(self._generate_act1(topic, context))
        elif module.name == "冲突":
            lines.extend(self._generate_act2(topic, context))
        elif module.name == "结局":
            lines.extend(self._generate_act3(topic, context))
        else:
            # 通用模块框架
            lines.append(f"[在此填写{module.name}的内容]")
            lines.append("")
            lines.append("关键要点：")
            for i, tech in enumerate(module.techniques[:3], 1):
                lines.append(f"{i}. {tech}")

        return "\n".join(lines)

    def _generate_opening(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """生成开场模块"""
        return [
            "### 开场引入",
            "",
            f"【关于{topic}，你可能一直被误导了】",
            "",
            "**时代背景：**",
            "[描述当前时代背景和社会现状]",
            "",
            "**问题呈现：**",
            f"- 你是否遇到过这样的困惑：[与{topic}相关的具体问题]",
            f"- 这个问题正在影响着[目标人群]",
            "",
            "**自我暴露：**",
            "[分享一个真实的个人经历或观察]",
            "",
            "**打破认知：**",
            "今天我想说的是——这一切可能都不是你想的那样。",
            "",
        ]

    def _generate_insight(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """生成核心洞察模块"""
        key_points = context.get("key_points", ["核心要点1", "核心要点2", "核心要点3"])

        return [
            "### 核心洞察",
            "",
            f"**{topic}的本质是什么？**",
            "",
            "[创造一个新名词/概念来描述核心洞察]",
            "",
            "**PAS模型分析：**",
            f"- **P (Problem):** {key_points[0] if len(key_points) > 0 else '[问题定义]'}",
            f"- **A (Agitate):** {key_points[1] if len(key_points) > 1 else '[问题恶化]'}",
            f"- **S (Solution):** {key_points[2] if len(key_points) > 2 else '[解决方案预览]'}",
            "",
            "**跨领域合成：**",
            "- [从其他领域借鉴的思维模型]",
            "- [为什么这个视角能带来新突破]",
            "",
        ]

    def _generate_solution(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """生成解决方案模块"""
        return [
            "### 解决方案",
            "",
            "**框架步骤：**",
            "",
            "#### 第一步：[动作名称]",
            "- 具体操作：[如何执行]",
            "- 注意事项：[避坑指南]",
            "- 示例：[具体案例]",
            "",
            "#### 第二步：[动作名称]",
            "- 具体操作：[如何执行]",
            "- 注意事项：[避坑指南]",
            "- 示例：[具体案例]",
            "",
            "#### 第三步：[动作名称]",
            "- 具体操作：[如何执行]",
            "- 注意事项：[避坑指南]",
            "- 示例：[具体案例]",
            "",
            "**工具清单：**",
            "1. [工具1]：[用途说明]",
            "2. [工具2]：[用途说明]",
            "3. [工具3]：[用途说明]",
            "",
        ]

    def _generate_rhetoric(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """生成修辞模块"""
        return [
            "### 修辞手法库",
            "",
            "**微故事（可插入位置）：**",
            "- 开场后：「记得有一次...」",
            "- 核心观点后：「这让我想起...」",
            "- 结尾前：「最后分享一个故事...」",
            "",
            "**隐喻金句：**",
            f"- 「{topic}就像是...」",
            "- 「这不是X，而是Y」",
            "- 「真正的问题是...」",
            "",
            "**提问驱动：**",
            "- 「你有没有想过...」",
            "- 「为什么会这样？」",
            "- 「答案是什么？」",
            "",
        ]

    def _generate_act1(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """三幕式第一幕"""
        return [
            "### 第一幕：开端",
            "",
            "**场景设定：**",
            f"时间：[时间背景]",
            f"地点：[地点背景]",
            f"人物：[主要人物介绍]",
            "",
            "**开场钩子：**",
            f"「{topic}」",
            "",
        ]

    def _generate_act2(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """三幕式第二幕"""
        return [
            "### 第二幕：冲突",
            "",
            "**矛盾引入：**",
            "[主要矛盾是什么]",
            "",
            "**矛盾升级：**",
            "- [第一次升级]",
            "- [第二次升级]",
            "- [第三次升级]",
            "",
            "**转折点：**",
            "[关键转折]",
            "",
        ]

    def _generate_act3(self, topic: str, context: Dict[str, Any]) -> List[str]:
        """三幕式第三幕"""
        return [
            "### 第三幕：结局",
            "",
            "**高潮：**",
            "[核心冲突的解决]",
            "",
            "**收尾：**",
            "[故事的余韵]",
            "",
            "**主题升华：**",
            f"「{topic}给我们的启示是...」",
            "",
        ]

    def adapt_to_platform(self, script: Script, platform: Platform) -> Script:
        """适配到特定平台"""
        config = PLATFORM_CONFIGS.get(platform, {})

        # 创建适配后的脚本
        adapted = Script(
            topic=script.topic,
            template=script.template,
            modules=script.modules.copy(),
            metadata={**script.metadata, "platform_config": config},
            style=ScriptStyle(config.get("style", "casual")),
            length=script.length,
            platform=platform,
        )

        return adapted

    def export(
        self,
        script: Script,
        output_path: str,
        format: str = "markdown",
    ):
        """导出脚本"""
        path = Path(output_path)

        if format == "markdown" or path.suffix == ".md":
            content = script.to_markdown()
        else:
            content = json.dumps(script.to_dict(), ensure_ascii=False, indent=2)

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


# 便捷函数
def generate_script(
    topic: str,
    template: str = "four_module",
    context: Optional[Dict[str, Any]] = None,
) -> Script:
    """生成脚本（便捷函数）"""
    generator = ScriptGenerator()
    return generator.generate(topic, template, context)