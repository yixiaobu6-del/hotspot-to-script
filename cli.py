"""命令行入口"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from hotspot import HotspotDetector, HotspotConfig, detect_hotspots
from script_generator import (
    ScriptGenerator,
    ScriptConfig,
    ScriptStyle,
    ScriptLength,
    Platform,
    generate_script,
)


console = Console()


@click.group()
@click.version_option("1.0.0")
def cli() -> None:
    """热点到脚本生成工具"""
    pass


@cli.command()
@click.option("--keywords", "-k", multiple=True, help="关键词")
@click.option("--platform", "-p", multiple=True, help="平台")
@click.option("--min-score", "-m", default=50, help="最低热度")
@click.option("--limit", "-l", default=20, help="返回数量")
@click.option("--output", "-o", type=click.Path(), help="输出文件")
def detect(keywords: tuple, platform: tuple, min_score: int, limit: int, output: str | None) -> None:
    """检测热点

    示例:
        hotspot detect -k AI -k 人工智能 -p weibo --limit 10
        hotspot detect --output hotspots.md

    Args:
        keywords: 搜索关键词元组
        platform: 平台名称元组
        min_score: 最低热度阈值
        limit: 返回结果数量上限
        output: 输出文件路径（可选）
    """
    console.print("\n[bold blue]正在检测热点...[/bold blue]\n")

    config = HotspotConfig(
        platforms=list(platform) if platform else ["mock"],
        min_score=min_score,
    )

    detector = HotspotDetector(config)
    hotspots = detector.detect(list(keywords) if keywords else None, limit)

    if not hotspots:
        console.print("[yellow]未检测到热点[/yellow]")
        return

    # 显示结果
    table = Table(show_header=True, header_style="bold")
    table.add_column("#", style="dim", width=4)
    table.add_column("热点标题", width=40)
    table.add_column("热度", justify="right")
    table.add_column("阶段", width=10)
    table.add_column("来源", width=10)

    for i, h in enumerate(hotspots, 1):
        stage_color = {
            "exploding": "red",
            "rising": "green",
            "peak": "yellow",
            "declining": "dim",
            "stable": "blue",
        }.get(h.stage.value, "white")

        table.add_row(
            str(i),
            h.title[:40],
            str(h.score),
            f"[{stage_color}]{h.stage.value}[/{stage_color}]",
            h.source,
        )

    console.print(table)

    # 导出
    if output:
        detector.export(hotspots, output)
        console.print(f"\n[green]已导出到: {output}[/green]")


@cli.command()
@click.argument("topic")
@click.option("--template", "-t", default="four_module", help="脚本模板")
@click.option("--style", "-s", type=click.Choice(["casual", "formal", "story", "educational"]), default="casual", help="脚本风格")
@click.option("--platform", "-p", type=click.Choice(["douyin", "xiaohongshu", "bilibili", "wechat", "shipinhao", "zhihu"]), help="目标平台")
@click.option("--output", "-o", type=click.Path(), help="输出文件")
def generate(topic: str, template: str, style: str, platform: str | None, output: str | None) -> None:
    """生成脚本

    示例:
        hotspot generate "年轻人开始反向消费" --template four_module
        hotspot generate "AI创业" -t three_act -s story -p douyin

    Args:
        topic: 脚本主题
        template: 模板名称
        style: 脚本风格（casual/formal/story/educational）
        platform: 目标平台（可选）
        output: 输出文件路径（可选）
    """
    console.print(f"\n[bold blue]正在生成脚本...[/bold blue]")
    console.print(f"  话题: {topic}")
    console.print(f"  模板: {template}")
    console.print(f"  风格: {style}")
    if platform:
        console.print(f"  平台: {platform}")
    console.print()

    config = ScriptConfig(
        template=template,
        style=ScriptStyle(style),
        platform=Platform(platform) if platform else None,
    )

    generator = ScriptGenerator(config)
    script = generator.generate(topic)

    # 显示结果
    console.print(Panel(script.to_markdown(), title=f"脚本: {topic}"))

    # 导出
    if output:
        generator.export(script, output)
        console.print(f"\n[green]已导出到: {output}[/green]")


@cli.command()
@click.argument("topic")
@click.option("--history", "-h", default="7d", help="历史时间范围")
def analyze(topic: str, history: str) -> None:
    """分析热点趋势

    示例:
        hotspot analyze "AI创业" --history 7d

    Args:
        topic: 分析话题
        history: 历史时间范围，如"7d"
    """
    console.print(f"\n[bold blue]分析热点趋势: {topic}[/bold blue]\n")

    # 模拟分析
    console.print("[green]趋势分析结果：[/green]")
    console.print("  阶段: 上升期")
    console.print("  增长率: +35%")
    console.print("  预测: 热度持续上升，有发展空间")
    console.print("  建议: 可以跟进，准备深度内容")


@cli.command("batch")
@click.argument("topics_file", type=click.Path(exists=True))
@click.option("--template", "-t", default="four_module", help="脚本模板")
@click.option("--output-dir", "-o", type=click.Path(), default="./scripts", help="输出目录")
def batch_generate(topics_file: str, template: str, output_dir: str) -> None:
    """批量生成脚本

    示例:
        hotspot batch topics.txt --template four_module --output-dir ./scripts

    Args:
        topics_file: 话题列表文件路径
        template: 脚本模板名称
        output_dir: 输出目录路径
    """
    import pathlib

    topics = pathlib.Path(topics_file).read_text(encoding="utf-8").strip().split("\n")
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold blue]批量生成脚本[/bold blue]")
    console.print(f"  话题数: {len(topics)}")
    console.print(f"  输出目录: {output_dir}\n")

    generator = ScriptGenerator()

    for i, topic in enumerate(topics, 1):
        topic = topic.strip()
        if not topic:
            continue

        script = generator.generate(topic, template)
        output_file = output_path / f"{topic}.md"
        generator.export(script, str(output_file))

        console.print(f"  [{i}/{len(topics)}] {topic} -> {output_file.name}")

    console.print(f"\n[green]完成！共生成 {len(topics)} 个脚本[/green]")


@cli.group()
def template() -> None:
    """模板管理"""
    pass


@template.command("list")
def template_list() -> None:
    """列出所有模板

    示例:
        hotspot template list
    """
    from script_generator import DEFAULT_TEMPLATES

    table = Table(show_header=True, header_style="bold")
    table.add_column("模板名称", width=20)
    table.add_column("描述", width=50)
    table.add_column("模块数", justify="right")

    for name, tpl in DEFAULT_TEMPLATES.items():
        table.add_row(name, tpl.description, str(len(tpl.modules)))

    console.print("\n[bold]可用模板：[/bold]\n")
    console.print(table)


@template.command("export")
@click.argument("template_name")
@click.option("--output", "-o", type=click.Path(), required=True, help="输出文件")
def template_export(template_name: str, output: str) -> None:
    """导出模板配置

    示例:
        hotspot template export four_module --output my_template.yaml

    Args:
        template_name: 模板名称
        output: 输出文件路径
    """
    import json
    import yaml

    from script_generator import DEFAULT_TEMPLATES

    if template_name not in DEFAULT_TEMPLATES:
        console.print(f"[red]错误: 未知模板 '{template_name}'[/red]")
        console.print(f"可用模板: {', '.join(DEFAULT_TEMPLATES.keys())}")
        return

    tpl = DEFAULT_TEMPLATES[template_name]

    output_path = pathlib.Path(output)
    data = tpl.to_dict()

    if output_path.suffix in [".yaml", ".yml"]:
        with open(output_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    console.print(f"[green]模板已导出到: {output}[/green]")


if __name__ == "__main__":
    cli()