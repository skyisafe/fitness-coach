#!/usr/bin/env python3
"""fitness-coach 自动生成测试（SCK Phase 4.6）

覆盖 validate/audit 盲区：路由一致性、领域约束（起始重量/跑步机参数/周期规则）、
边界用例、输出模板完整性。运行：python3 tests/test.py
"""

import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
passed = 0
failed = 0


def ok(msg):
    global passed
    passed += 1
    print(f"  ✅ {msg}")


def fail(msg):
    global failed
    failed += 1
    print(f"  ❌ {msg}")


def check(cond, msg):
    ok(msg) if cond else fail(msg)


def section(title):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


def read(p):
    return (SKILL_ROOT / p).read_text(encoding="utf-8")


# ---------- T1 文件完整性 ----------
section("T1 文件完整性")
DECLARED = [
    "SKILL.md", "README.md", "DESIGN.md", "CHANGELOG.md",
    "references/goals.md", "references/venues.md", "references/body-data.md",
    "references/nutrition.md", "references/programs.md", "references/adjustments.md",
]
for f in DECLARED:
    check((SKILL_ROOT / f).is_file(), f"存在: {f}")

readme = read("README.md")
check("├──" in readme or "└──" in readme, "README.md 含树形结构（文件表委托）")
tree_files = [m.rstrip("/") for m in re.findall(r"(?:├──|└──)\s+(\S+)", readme)]
missing_in_tree = [f for f in DECLARED
                   if f not in tree_files and Path(f).name not in tree_files]
check(not missing_in_tree, f"README 树覆盖全部声明文件（缺: {missing_in_tree or '无'}）")
check("tests" in readme, "README 树含 tests/（自动化测试）")

# ---------- T2 Frontmatter 质量 ----------
section("T2 Frontmatter 质量")
skill = read("SKILL.md")
fm = skill.split("---")[1]
name_m = re.search(r"^name:\s*(\S+)", fm, re.M)
ver_m = re.search(r"^version:\s*(\S+)", fm, re.M)
desc_m = re.search(r"^description:\s*(.+)", fm, re.M)
check(name_m and name_m.group(1) == "fitness-coach", "name = fitness-coach")
check(ver_m is not None, "version 存在")
check(desc_m is not None and "Use when" in desc_m.group(1), "description 含 Use when 触发语")
check(desc_m and len(desc_m.group(1)) <= 200, f"description ≤200 字符（实际 {len(desc_m.group(1)) if desc_m else '?'}）")

changelog = read("CHANGELOG.md")
latest_ver = re.search(r"^## \[(\d+\.\d+\.\d+)\]", changelog, re.M)
check(ver_m and latest_ver and ver_m.group(1) == latest_ver.group(1),
      f"SKILL.md 版本与 CHANGELOG 最新条目一致（{ver_m.group(1) if ver_m else '?'} vs {latest_ver.group(1) if latest_ver else '?'}）")

# ---------- T3 路由一致性 ----------
section("T3 路由一致性（SKILL.md ↔ references）")
# SKILL.md 引用的 § 锚点必须能解析到对应文件的实际标题（标题前缀匹配）
CITED_SECTIONS = {
    "references/goals.md": ["减脂", "增肌", "局部塑形", "减脂增肌"],
    "references/venues.md": ["家庭健身", "无器材健身", "健身房", "跑步机", "户外与跑步", "游泳", "徒步"],
    "references/nutrition.md": ["宏量营养素分配", "三餐模板", "补给品"],
    "references/adjustments.md": ["第一步：反馈分类", "第二步：按层级调整", "调整输出格式", "训练日志模板"],
}
for path, anchors in CITED_SECTIONS.items():
    body = read(path)
    headings = re.findall(r"^#{1,3}\s+(.+)", body, re.M)
    check(f"references/{path.split('/')[-1]}" in skill, f"SKILL.md 引用了 {path}")
    for a in anchors:
        hit = [h for h in headings if h.startswith(a)]
        check(bool(hit), f"{path} 锚点「§{a}」解析到标题: {hit[0] if hit else '未找到'}")

# 运动状态两级路由（v2.2.0）
venues = read("references/venues.md")
check("### 第 4 步：按运动状态读对应参考文件" in skill, "SKILL.md 第 4 步按运动状态路由")
check(all(h in venues for h in ["## 健身房健身", "## 非健身房健身 · 室内", "## 非健身房健身 · 室外运动"]),
      "venues.md 三大运动状态章节（健身房 / 非健身房室内 / 室外运动）")
check("### 健身房（器械与自由重量）" in venues and "### 无器材健身（纯自重）" in venues
      and "### 跑步机（健身房 / 家用）" in venues, "原小节保留为三级锚点")
check("## 混合状态排期原则" in venues and "混合状态排期原则" in skill, "混合状态排期原则（venues + SKILL 引用一致）")

# 综合运动教练定位与无器材一等公民（v2.3.0）
programs = read("references/programs.md")
check("综合运动锻炼教练" in skill, "SKILL.md 定位为综合运动锻炼教练")
check("排期四" in skill and "无器材版" in skill and "自重进阶四板斧" in skill,
      "推荐模板含排期四（无器材版 + 自重进阶四板斧）")
check("自重 / 无器材适配" in programs, "programs.md 含自重/无器材适配注记")
check("无器械" in (desc_m.group(1) if desc_m else ""), "description 含无器械触发词")

# 其余 L2 关键内容存在
programs = read("references/programs.md")
check("7 项" in read("references/body-data.md") and "标准格式" in read("references/body-data.md"),
      "body-data.md 含 7 项标准格式")
check("常见训练分化方式" in programs and "渐进超负荷" in programs, "programs.md 含分化库与渐进超负荷")

# 反向：6 个 L2 文件都被 SKILL.md 提及
for f in ["goals", "venues", "body-data", "nutrition", "programs", "adjustments"]:
    check(f in skill, f"SKILL.md 提及 references/{f}.md")

# 跨文件引用有效：venues.md 指向 programs.md 的双重渐进法
venues = read("references/venues.md")
programs = read("references/programs.md")
check("渐进超负荷 · 双重渐进法" in venues and "双重渐进法" in programs,
      "venues.md → programs.md「双重渐进法」引用有效")

# ---------- T4 路径引用 ----------
section("T4 路径引用（references/*.md 均存在）")
all_md = {p.relative_to(SKILL_ROOT).as_posix() for p in SKILL_ROOT.rglob("*.md")
          if "_backups" not in p.parts and "tests" not in p.parts}
bad_refs = []
for f in all_md:
    if f == "CHANGELOG.md":
        continue
    for ref in re.findall(r"references/([\w-]+\.md)", read(f)):
        if not (SKILL_ROOT / "references" / ref).is_file():
            bad_refs.append(f"{f} → references/{ref}")
check(not bad_refs, f"无悬空路径引用（坏引用: {bad_refs or '无'}）")

# ---------- T5 领域特定完整性 ----------
section("T5 领域完整性（v1.5.0 三项优化落地）")
# 跑步机：坡度 + 配速
check("### 跑步机（健身房 / 家用）" in venues, "venues.md 含 §跑步机 小节")
check("慢跑 1%" in venues and "8~12%" in venues, "跑步机坡度默认（慢跑 1% / 坡走 8~12%）")
check(re.search(r"\d\.\d~\d\.\d km/h", venues) and "Zone 2" in venues, "跑步机配速表与心率区间")
check("谈话测试" in venues or "能完整说句子" in venues or "还能完整说话" in venues, "谈话测试校准")
# 力量起始重量
check("起始重量参考" in venues and "×BW" in venues, "起始重量按 BW 折算表存在")
check("单边" in venues, "起始重量标注单边/总重")
check("宁轻勿重" in venues and "12 次" in venues, "自校准规则（12 次余力法 + 宁轻勿重）")
# 周期规则
check("默认一周" in skill, "SKILL.md 周期默认一周")
check("按 4 周滚动" in skill and "按 4 周滚动" in programs, "超四周按 4 周滚动（SKILL.md + programs.md）")
check("按月滚动" not in skill and "按月滚动" not in programs and "一个月计划" not in programs
      and "一个月渐进计划" not in skill, "周期单位统一为周（无按月滚动/一个月计划表述）")
check("1 个月 = 4 周" in skill and "1 个月 = 4 周" in programs, "月→周换算规则（SKILL.md + programs.md）")
check("第 2 个月" not in venues, "venues.md 升级路径以周表述")
check("### 第 5 步：按周期搭建计划骨架（默认一周，以周为单位延长）" in skill, "第 5 步标题体现默认一周与周单位")
check("三阶段结构" not in skill and "12~13 周" not in programs, "独立三个月骨架已移除")
check("4 周渐进" in skill and "W1 适应周" in programs, "四周 = 4 周渐进结构")
# 输出格式强制携带
check("起始重量" in skill.split("## 输出格式")[1], "输出格式强制起始重量")
check("坡度与配速" in skill.split("## 输出格式")[1], "输出格式强制跑步机坡度配速")
# 动态调整（v1.6.0）
adjustments = read("references/adjustments.md")
check("### 第 7 步：动态调整（回访触发）" in skill, "SKILL.md 含第 7 步动态调整")
check("不重走第 1~5 步" in skill, "回访不重走采集与计划搭建")
check(all(k in adjustments for k in ["执行反馈", "进度数据", "条件变化", "疼痛与伤病"]), "反馈四分类齐全")
check(all(k in adjustments for k in ["L1 参数", "L2 结构", "L3 目标重估"]), "三级调整层级（L1/L2/L3）")
check("4 周为决策窗口" in adjustments, "进度调整锁 4 周决策窗口")
check("本周调整" in adjustments and "下次反馈点" in adjustments, "变化对比表 + 下次反馈点输出")
check("训练日志模板" in skill, "计划交付附训练日志模板（§六）")
check("双重渐进" in adjustments and "退回上一重量" in adjustments, "力量回调细则（渐进/退阶）")
check("停 / 换 / 降 / 就医" in adjustments, "伤病安全红线处理规则")
# 逐日课表输出（v1.6.1）
check("逐日排表" in skill, "SKILL.md 输出格式强制逐日排表")
check("不按「力量训练」「有氧训练」" in skill or "不要拆成「力量训练」「有氧训练」" in skill,
      "SKILL.md 禁止按训练类型分块")
example = skill.split("输出示例")[1]
for d in ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]:
    check(f"| {d} " in example, f"输出示例含{d}行")
check("主动恢复" in example and "完全休息" in example, "示例含周末恢复/休息行")
check("逐日课表" in programs, "programs.md 一周计划节强制逐日课表")

# ---------- T6 边界用例 ----------
section("T6 边界用例")
check("周末可以训练时才" in skill and "仅当用户明确表示周末可以训练" in programs, "周末默认不排训练（两处一致）")
check("BMI < 18.5" in skill and "未成年人" in skill, "安全红线（偏瘦减脂沟通 / 未成年人）")
check("≤10%" in venues, "周跑量增幅 ≤10%")
check("每周 ≤1 次" in venues, "间歇日每周 ≤1 次")
check("TDEE − 300~500" in skill or "TDEE − 300~500" in read("references/goals.md"), "减脂缺口上限约束")
check("不构成医疗建议" in skill, "医疗免责声明")

# ---------- T7 模板有效性 ----------
section("T7 输出格式模板")
out_fmt = skill.split("## 输出格式")[1]
for sec_name in ["一、身体数据分析", "二、目标可行性", "三、训练计划", "四、有氧与日常消耗",
                 "五、恢复与注意事项", "六、进度追踪与调整规则", "七、补给建议", "八、饮食安排"]:
    check(sec_name in out_fmt, f"输出模板含「{sec_name}」")
check("星期 | 训练内容 | 动作(组×次·起始重量)" in out_fmt, "课表列含起始重量")

# ---------- Summary ----------
section("SUMMARY")
total = passed + failed
print(f"  Score: {passed}/{total} ({passed / total * 100:.0f}%)")
sys.exit(0 if failed == 0 else 1)
