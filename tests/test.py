#!/usr/bin/env python3
"""fitness-coach 自动测试（v3.0.0）

覆盖：文件完整性 / 双语 README / frontmatter / 公式系数 / 数值事实 / 路由锚点 /
排期算术 / 输出格式 / 文档一致性 / 证据来源 / 安全边界 / 模板 / evals / 跨文件一致性 / 卫生。
运行：python3 tests/test.py
"""

import json
import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
passed = 0
failed = 0
failures = []


def ok(msg):
    global passed
    passed += 1


def fail(msg):
    global failed
    failed += 1
    failures.append(msg)
    print(f"  ❌ {msg}")


def check(cond, msg):
    ok(msg) if cond else fail(msg)


def section(title):
    print(f"\n{'=' * 60}\n  {title}\n{'=' * 60}")


def read(p):
    return (SKILL_ROOT / p).read_text(encoding="utf-8")


def headings(text):
    return re.findall(r"^#{2,4}\s+(.+)$", text, re.M)


# ---------- T1 文件完整性 / 双语 ----------
section("T1 文件完整性 / 双语 README")
DECLARED = [
    "SKILL.md", "README.md", "README.zh-CN.md", "DESIGN.md", "CHANGELOG.md", "LICENSE",
    "evals/evals.json", "evals/README.md", "tests/test.py", ".github/workflows/test.yml",
    "references/goals.md", "references/venues.md", "references/templates.md",
    "references/technique.md", "references/populations.md", "references/body-data.md",
    "references/nutrition.md", "references/programs.md", "references/adjustments.md",
    "references/evidence.md",
]
for f in DECLARED:
    check((SKILL_ROOT / f).is_file(), f"存在: {f}")

readme = read("README.md")
zh_readme = read("README.zh-CN.md")
check("README.zh-CN.md" in readme and "简体中文" in readme, "README.md 含双语切换入口")
check("README.md" in zh_readme and "English" in zh_readme, "README.zh-CN.md 含双语切换入口")
check("MIT License" in read("LICENSE"), "LICENSE 为 MIT")
check("python3 tests/test.py" in read(".github/workflows/test.yml"), "CI 运行 tests/test.py")

for name, body in (("README.md", readme), ("README.zh-CN.md", zh_readme)):
    tree = [m.rstrip("/") for m in re.findall(r"(?:├──|└──)\s+(\S+)", body)]
    missing = [f for f in DECLARED if Path(f).name not in tree]
    check(not missing, f"{name} 树覆盖全部声明文件（缺: {missing or '无'}）")
    check("tests" in tree and "evals" in tree, f"{name} 树含 tests/ 与 evals/")

# ---------- T2 Frontmatter 质量 ----------
section("T2 Frontmatter 质量")
skill = read("SKILL.md")
fm = skill.split("---")[1]
name_m = re.search(r"^name:\s*(\S+)", fm, re.M)
ver_m = re.search(r"^version:\s*[\"']?([0-9.]+)", fm, re.M)
desc_m = re.search(r"^description:\s*(.+)", fm, re.M)
desc = desc_m.group(1) if desc_m else ""
check(name_m and name_m.group(1) == "fitness-coach", "name = fitness-coach")
check(ver_m is not None, "version 存在")
check(desc_m is not None and "Use when" in desc, "description 含 Use when 触发语")
check(desc_m is not None and len(desc) <= 200, f"description ≤200 字符（实际 {len(desc)}）")
check(180 <= len(desc) <= 200, "description 长度在 180~200（顶格利用预算）")
for w in ["减脂", "减重", "减肥", "增肌", "塑形", "无器械", "跑步", "游泳", "徒步", "训练计划", "体脂"]:
    check(w in desc, f"description 含触发词: {w}")
check(re.search(r"7\s*天|瘦\s*\d+\s*斤|保证|根治|必瘦", desc) is None, "description 无过度承诺")
check(re.search(r"^template:\s*\S+", fm, re.M) is not None, "frontmatter 含 template")
trig_m = re.search(r"^triggers:\s*\n((?:\s+-\s+.+\n?)+)", fm, re.M)
trigger_count = len(re.findall(r"^\s+-\s+", trig_m.group(1), re.M)) if trig_m else 0
check(trigger_count >= 12, f"frontmatter triggers ≥12（实际 {trigger_count}）")
budget_m = re.search(r"^token_budget:\s*\n((?:\s+\w+:\s*\d+\n?)+)", fm, re.M)
for key in ["L0_trigger", "L1_core", "L2_deep", "hard_cap"]:
    check(budget_m is not None and key in budget_m.group(1), f"token_budget 含 {key}")

changelog = read("CHANGELOG.md")
latest_ver = re.search(r"^## \[([0-9.]+)\]", changelog, re.M)
check(ver_m and latest_ver and ver_m.group(1) == latest_ver.group(1),
      f"SKILL 版本 = CHANGELOG 最新（{ver_m.group(1) if ver_m else '?'} vs {latest_ver.group(1) if latest_ver else '?'}）")
check("## [Unreleased]" not in changelog, "CHANGELOG 无 Unreleased 残留")
check("版本 3.0.0" not in readme and "Version 3.0.0" not in readme, "README 不硬编码版本号")
check("当前版本见" in zh_readme and "Current version" in readme, "README 委托版本入口到 SKILL.md")

# ---------- T3 公式与关键数值 ----------
section("T3 公式与关键数值")
check("10×体重 + 6.25×身高 − 5×年龄 + 5" in skill, "BMR 男性公式系数正确")
check("− 161" in skill, "BMR 女性常数 −161")
check("体重 kg / 身高 cm / 年龄岁" in skill, "BMR 公式标注单位")
check("1.20×BMI" in skill and "0.23×年龄" in skill and "10.8×性别" in skill and "5.4" in skill,
      "Deurenberg 成人式系数正确")
check("±4%" in skill, "Deurenberg 误差标注 ±4%")
check("1.51×BMI" in read("references/evidence.md"), "Deurenberg 儿童式在 evidence.md")
check("208−0.7×年龄" in skill, "SKILL 使用 Tanaka 心率公式")
check("208−0.7×年龄" in read("references/venues.md"), "venues 使用 Tanaka 心率公式")
check("208−0.7×年龄" in read("references/adjustments.md"), "adjustments 使用 Tanaka")
check("220−年龄" in read("references/venues.md") and "粗略" in read("references/venues.md"),
      "220−年龄 仅作粗略估计")
check("300~500" in skill and "500~1000" in skill, "减脂缺口 300~500 / 激进 500~1000")
check("1000~1200" in skill and "1200~1500" in skill, "低能量膳食下限区间（女/男）")
check("0.5~1 kg/周" in skill or "0.5~1 kg/周" in read("references/evidence.md"), "减重速度 0.5~1 kg/周")
check("24~27.9" in skill and "≥28" in skill, "BMI 中国标准切点")
check("男 ≥90cm、女 ≥85cm" in skill, "腰围中心型肥胖切点")
check("85~89.9" in skill and "80~84.9" in skill, "腰围中心型肥胖前期档")
for f in ["1.2", "1.375", "1.55", "1.725", "1.9"]:
    check(f in skill, f"TDEE 活动系数 {f}")
check("已包含" in skill and "不再" in skill, "TDEE 系数标注已含运动、不再叠加")
check("久坐 1.2 / 轻度 1.375 / 中度 1.55 / 高度 1.725" in skill, "TDEE 活动系数完整表")
for r in ["1.4~2.0", "1.6~2.2", "1.8~2.4", "2.0~2.4", "2.3~3.1"]:
    check(r in skill or r in read("references/evidence.md"), f"蛋白质分级 {r} g/kg")
check("g/kg 体重" in read("references/evidence.md"), "蛋白质口径明确为 g/kg 体重")
check("体脂偏高者按去脂体重" in skill, "高体脂按去脂体重/目标体重")
check("减脂 1.8~2.4" in skill, "SKILL 减脂蛋白区间唯一")
check("1 + 次数/30" in read("references/programs.md"), "1RM 使用 Epley 估算")
check("不是 ACSM 官方" in read("references/programs.md"), "%1RM 表标注非 ACSM 官方")
check("6~7 个蛋清" in read("references/nutrition.md"), "蛋白粉↔蛋清换算修正")
check("24g 蛋白" in read("references/nutrition.md"), "30g 蛋白粉≈24g 蛋白")
check("6~8 小时" in read("references/nutrition.md"), "咖啡因睡前 6~8h 停用")
check("200mg" in read("references/nutrition.md"), "孕期咖啡因 ≤200mg")
check("3~5g" in read("references/nutrition.md"), "肌酸 3~5g/天")
check("6 周腹部训练" in read("references/goals.md"), "局部减脂有具体证据")
check("10%~20%" in read("references/evidence.md"), "体脂参考区间存在")

# ---------- T4 路由与锚点 ----------
section("T4 路由与锚点")
all_md = {p.relative_to(SKILL_ROOT).as_posix(): p.read_text(encoding="utf-8")
          for p in SKILL_ROOT.rglob("*.md")
          if "_backups" not in p.parts and "evals" not in p.parts}
bad_refs = []
for f, body in all_md.items():
    if f == "CHANGELOG.md":
        continue
    for ref in re.findall(r"references/([\w-]+\.md)", body):
        if not (SKILL_ROOT / "references" / ref).is_file():
            bad_refs.append(f"{f} → references/{ref}")
check(not bad_refs, f"路径引用均有效（坏引用: {bad_refs or '无'}）")

bad_anchors = []
for f, body in all_md.items():
    for m in re.finditer(r"references/([\w-]+\.md)`?\s*§([^\s，。；、）)\]]+)", body):
        target, anchor = m.group(1), m.group(2)
        target_body = all_md.get(f"references/{target}", "")
        hs = headings(target_body)
        if not any(h.startswith(anchor) for h in hs):
            bad_anchors.append((f, target, anchor))
check(not bad_anchors, f"所有 §锚点可解析（坏锚点: {bad_anchors or '无'}）")
for ghost in ["恢复表", "跑步机起步表", "渐进超负荷 · 双重渐进法"]:
    check(ghost not in skill and ghost not in read("references/venues.md"),
          f"无幽灵锚点: {ghost}")

# ---------- T5 排期算术与恢复 ----------
section("T5 排期算术与恢复")
templates = read("references/templates.md")
programs = read("references/programs.md")
venues = read("references/venues.md")
check("共享总则" in templates, "templates 含共享总则")
for s in ["排期一", "排期二", "排期三", "排期四"]:
    check(s in templates and s in skill, f"SKILL 与 templates 均有 {s}")
check("自重进阶四板斧" in templates, "templates 含自重进阶四板斧")
check("0.4~0.5×BW" not in templates, "templates 不重复动作库（无 BW 数值表）")
over_rows = []
for line in templates.splitlines():
    if not line.strip().startswith("|") or "×" not in line:
        continue
    sets = sum(int(n) for n in re.findall(r"(\d+)\s*×\s*\d", line))
    core = sum(int(n) for n in re.findall(r"核心\s*(\d+)\s*组", line))
    total = sets + core
    if total > 20:
        over_rows.append((line[:30], total))
check(not over_rows, f"所有排期行单日组数 ≤20（超限: {over_rows or '无'}）")
for body, label in ((templates, "templates"), (programs, "programs"), (venues, "venues")):
    check("60~90" in body, f"{label} 含孤立休息 60~90s")
    check(("2~3min" in body) or ("2~3 分钟" in body), f"{label} 含复合休息 2~3min")
check("每块肌群每次只选 1 个动作" not in skill, "已删除「每肌群每次只选 1 动作」矛盾规则")
check("10~20 个正式组" in skill or "每周 10~20 组" in skill, "每周容量 10~20 组")
check("≤20 组" in skill and "≤20 组" in programs, "单次容量 ≤20 组")
check("≥48h" in skill or "≥48h" in programs, "同肌群恢复 ≥48h")
p4 = templates.split("## 排期四")[1].split("## 输出范例")[0]
check("| 周三 | 全身 B" in p4, "排期四 周三 = 全身 B")
check("| 周四 | 休息" in p4, "排期四 周四 = 休息（满足 48h）")
check("| 周五 | 全身 C" in p4, "排期四 周五 = 全身 C")
check("| 周四 | 全身 B" not in p4, "排期四 无 B/C 连排")
check("组间 90s，深蹲类" not in skill + templates, "已删除旧组间 90s 规则")
p1 = templates.split("## 排期一")[1].split("## 排期二")[0]
friday = [ln for ln in p1.splitlines() if ln.startswith("| 周五")]
check(bool(friday) and "核心 3 组" in friday[0], "排期一 周五含核心收尾")
bad_sets = []
for line in templates.splitlines():
    if not line.strip().startswith("|") or "×" not in line:
        continue
    for n in re.findall(r"(\d+)\s*×\s*\d", line):
        if not 2 <= int(n) <= 5:
            bad_sets.append((n, line[:30]))
check(not bad_sets, f"每个动作组数在 2~5 组（越界: {bad_sets or '无'}）")
check("## 恢复与休息" in programs, "programs 保留 §恢复与休息 标题")
check("| 游泳 |" in skill, "SKILL 路由表含游泳行")
check("坡走 8~12%" in venues and "慢跑 1%" in venues, "跑步机坡度默认（慢跑 1% / 坡走 8~12%）")

# ---------- T6 输出格式 ----------
section("T6 输出格式")
for sec_name in ["一、身体数据分析", "二、目标可行性", "三、训练计划", "四、有氧与日常消耗",
                 "五、恢复与注意事项", "六、进度追踪与调整规则", "七、补给建议", "八、饮食安排"]:
    check(sec_name in skill, f"输出模板含「{sec_name}」")
check("星期 | 训练内容 | 动作(组×次·起始重量) | 组间休息 | 强度备注" in skill, "课表列名唯一")
check("省略第七、八节" in skill, "未触发时省略补给/饮食节")
check("不构成医疗建议" in skill, "输出含免责声明")
check("本周调整" in read("references/adjustments.md") and "全量周课表" in read("references/adjustments.md"),
      "调整输出=对比表+全量课表")
check("训练日志模板" in read("references/adjustments.md"), "调整协议含训练日志模板")

# ---------- T7 README 质量 ----------
section("T7 README 质量")
for label in ["## Quick start", "## Triggering", "## What it is", "## Installation",
              "## Boundaries & safety", "## Development & testing"]:
    check(label in readme, f"英文 README 含 {label}")
for label in ["## 快速开始", "## 触发方式", "## 核心能力", "## 安装", "## 文件结构", "## 边界与注意事项"]:
    check(label in zh_readme, f"中文 README 含 {label}")
check("一次性追问" not in readme and "一次性追问" not in zh_readme, "README 无「一次性追问」过期表述")
for body in (readme, zh_readme):
    check("ConfigStation" not in body and "/Users/" not in body, "README 无私有绝对路径")
    check("_backups" not in body, "README 树不含 _backups")

# ---------- T8 DESIGN 一致性 ----------
section("T8 DESIGN 一致性")
design = read("references/../DESIGN.md")
check("设计偏离说明" in design, "DESIGN 含设计偏离说明")
check("L1 core" in design and "3,400" in design, "DESIGN 声明 L1 预算 3,400")
check("决策 27" in design, "DESIGN 含决策 27")
for fn in ["goals", "venues", "templates", "technique", "populations", "body-data",
           "nutrition", "programs", "adjustments", "evidence"]:
    check(f"{fn}.md" in design, f"DESIGN 架构提及 {fn}.md")
check("self-improving" not in design, "DESIGN 无死引用")
check("约 280 行" not in design, "DESIGN 无过期行数口径")
check("三个排期差异块" not in design, "DESIGN 排期数量已更新")

# ---------- T9 证据来源 ----------
section("T9 证据来源")
evidence = read("references/evidence.md")
for token in ["WHO", "ACSM", "ISSN", "卫健委", "CDC", "USDA", "ACOG", "ESPEN",
              "中国高血压防治指南", "Tanaka", "Epley", "AWGS", "Gallagher"]:
    check(token in evidence, f"evidence.md 含来源: {token}")
for level in ["强", "中", "弱", "共识"]:
    check(level in evidence, f"evidence.md 含证据强度: {level}")
check("非 ACSM 官方" in evidence, "活动系数标注非 ACSM 官方")
check("不存在 ACSM 官方" in evidence and "对照表" in evidence, "声明 %1RM 对照表不存在")
check("不构成医疗诊断或处方" in evidence, "evidence 含免责话术")

# ---------- T10 安全边界 ----------
section("T10 安全边界")
for token in ["≥180/110", "孕期", "未成年人", "BMI <18.5", "进食障碍", "心肌炎",
              "增殖性视网膜病变", "65+"]:
    check(token in skill, f"SKILL 红线含: {token}")
pop = read("references/populations.md")
for token in ["ACOG", "ESPEN", "SCOFF", "160~179", "≥3 天", "1.0~1.2"]:
    check(token in pop, f"populations 含: {token}")
tech = read("references/technique.md")
for token in ["热身", "Valsalva", "护具", "DOMS", "ramp-up"]:
    check(token in tech, f"technique 含: {token}")

# ---------- T11 跨文件数值一致性 ----------
section("T11 跨文件数值一致性")
allowed_protein = {(1.4, 2.0), (1.6, 2.2), (1.8, 2.4), (2.0, 2.4), (2.3, 3.1), (1.0, 1.2), (1.2, 1.5)}
bad_protein = []
for f in ["SKILL.md", "references/goals.md", "references/nutrition.md", "references/evidence.md"]:
    for m in re.finditer(r"(\d+(?:\.\d+)?)~(?<!\d)(\d+(?:\.\d+)?)\s*g/kg", read(f)):
        pair = (float(m.group(1)), float(m.group(2)))
        if pair not in allowed_protein:
            bad_protein.append((f, pair))
check(not bad_protein, f"蛋白质区间均在允许集合（越界: {bad_protein or '无'}）")
check("1.5 g/kg" not in skill and "1.5 g/kg" not in read("references/goals.md"), "无旧版 1.5 g/kg 蛋白口径")
check("减脂 2~3 次/周" in skill and "减脂 2~3 次/周" in templates, "有氧频次：减脂 2~3 次/周")
check("增肌/重组 1~2 次/周" in skill and "增肌/重组 1~2 次/周" in templates, "有氧频次：增肌/重组 1~2 次/周")
check("上胸与胸外延" in read("references/goals.md") and "上胸与胸外延" in templates,
      "瘦胸方向统一为上胸与胸外延")
check("强化下胸" not in skill and "强化下胸" not in templates, "无「强化下胸」矛盾表述")
check("重组 2.0~2.4" in skill, "重组蛋白口径唯一")
check("2~3min" in skill, "SKILL 含复合休息 2~3min")

# ---------- T12 模板与 evals ----------
section("T12 模板与 evals")
evals_path = SKILL_ROOT / "evals" / "evals.json"
evals = json.loads(evals_path.read_text(encoding="utf-8"))
check(evals.get("skill_name") == "fitness-coach", "evals skill_name 正确")
check(evals.get("version") == (ver_m.group(1) if ver_m else ""), "evals version 与 SKILL 一致")
check(len(evals.get("evals", [])) == 7, "evals 含 7 个行为用例")
check(len(evals.get("trigger_evals", [])) == 10, "evals 含 10 个触发用例")
ids = [e.get("id") for e in evals.get("evals", [])] + [e.get("id") for e in evals.get("trigger_evals", [])]
check(len(ids) == len(set(ids)), "evals id 唯一")
check(all(e.get("expectations") for e in evals.get("evals", [])), "每个行为用例含 expectations")
neg = [e for e in evals.get("trigger_evals", []) if not e.get("should_trigger")]
check(len(neg) == 3, "触发用例含 3 个负例")
check("with-skill" in read("evals/README.md") and "baseline" in read("evals/README.md"),
      "evals/README 说明 with-skill vs baseline")

# ---------- T13 卫生与规模 ----------
section("T13 卫生与规模")
check(skill.count("\n") <= 230, f"SKILL 行数 ≤230（实际 {skill.count(chr(10))}）")
check(len(skill) <= 10000, f"SKILL 字符数 ≤10000（实际 {len(skill)}）")
for p in sorted((SKILL_ROOT / "references").glob("*.md")):
    check(len(p.read_text(encoding="utf-8")) <= 9000, f"{p.name} 单文件 ≤9000 字符")
backups = [d for d in (SKILL_ROOT / "_backups").glob("*") if d.is_dir()] if (SKILL_ROOT / "_backups").exists() else []
check(len(backups) <= 1, f"_backups 仅保留最新 1 份（实际 {len(backups)}）")
repo_gitignore = (SKILL_ROOT / ".gitignore").read_text(encoding="utf-8")
check("_backups/" in repo_gitignore, ".gitignore 忽略 _backups/")
check(not list(SKILL_ROOT.rglob("__pycache__")), "无 __pycache__ 残留")

# ---------- T14 内容一致性（v3.1.0 校准） ----------
section("T14 内容一致性")
check("0.3~0.45" in skill and "500~1000" in skill, "SKILL 含缺口 ↔ 速度映射")
check("140~159/90~99" in skill and "160~179/100~109" in skill, "SKILL 血压分级明确（1 级 / 2 级）")
check("140~179" not in skill, "SKILL 无「140~179」模糊合并区间")
check("快车道" in skill and "本次假设" in skill, "SKILL 含快车道规则")
check("交付前自检" in skill, "SKILL 含交付前自检")
check("1RM 测试" in skill, "未成年人红线含 1RM 测试")
check("BMI <17.5" not in skill, "SKILL 不再用 BMI<17.5 作为唯一触发线")
bd = read("references/body-data.md")
check("1~12 或 1~30" in bd, "body-data 七项模板允许两种内脏脂肪刻度并注明")
check("≥15 属明显高值" not in bd, "body-data 无「≥15 属明显高值」孤立阈值")
check("纵向上升 ≥2 级" in bd, "body-data 内脏脂肪用同设备纵向趋势判读")
check(">1 kg/周" in read("references/adjustments.md") and ">1 kg/周" in read("references/nutrition.md"),
      "减重过快阈值统一为 >1 kg/周")
check(">体重 1%/周" not in read("references/adjustments.md"), "adjustments 无旧 >1%/周 口径")
check("3×30~60s" not in read("references/goals.md") and "3×30~60s" not in templates,
      "平板支撑时长统一（无 30~60s）")
check("48~72 h 不缓解" in read("references/technique.md"), "损伤判定统一为 48~72h")
check(">1 周不缓解" not in read("references/technique.md"), "technique 无 >1 周口径")
check("慢性高血压已控制" in read("references/populations.md"), "妊娠期高血压在相对禁忌中限定为已控制")
check("不推荐五分化" not in templates, "templates 无「不推荐五分化」矛盾表述")
check("与性别无关" in templates, "分化按可训练天数而非性别")
check("每周 3~5 次" not in venues, "venues 有氧频次与 SKILL 对齐（无 3~5 次）")
check("Borg 11~13" in venues, "venues 标注 RPE 量表换算口径")
check("RPE 11~13" not in venues and "RPE 11~13" not in read("references/populations.md"),
      "有氧/孕期 RPE 统一为 10 分制（无 11~13 混用）")
for f in ["references/body-data.md", "references/populations.md", "references/technique.md"]:
    check("完整出处与 URL" not in read(f), f"{f} 不再声称提供 URL")

# ---------- Summary ----------
section("SUMMARY")
total = passed + failed
print(f"  Score: {passed}/{total} ({passed / total * 100:.0f}%)")
if failures:
    print("  Failures:")
    for f in failures:
        print(f"   - {f}")
sys.exit(0 if failed == 0 else 1)
