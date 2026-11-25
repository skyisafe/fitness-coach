# fitness-coach · All-Around Fitness Coach

**English** | [简体中文](README.zh-CN.md)

> MIT License ｜ No runtime dependencies ｜ Current version: see `SKILL.md`

An AI Agent skill for all-around fitness coaching: it analyzes body data (BMI, BMR, TDEE), then builds a scientific, actionable, periodized training plan with progression built in — gym strength training, home bodyweight training, running, cycling, swimming, and hiking are covered equally — backed by evidence-based nutrition and weight-management knowledge.

> Language note: the skill's instructions and reference files are written in Chinese, and the coach replies in Chinese. This English README (and the [Chinese edition](README.zh-CN.md)) exists so the project can be discovered and reviewed internationally.

## What it is

- One-liner: given body data, training setting, and goal, output a plan the user can follow as-is — gym strength, home bodyweight, and outdoor endurance all included; ask about nutrition and supplements to get restrained, evidence-based advice.
- Who is this for: people who want fat loss, muscle gain, recomposition, or general fitness; users with smart-scale / InBody data who need it interpreted; users who want a ready-to-follow weekly plan that adapts to feedback.
- Who it is not for: competitive sports preparation, injury rehabilitation prescriptions, or medical nutrition therapy — those need professionals.
- Type: knowledge + workflow skill (no scripts). The main file stays lean; domain knowledge loads on demand from `references/`, keeping context cost proportional to the request. Numbers live in a single source of truth (`references/evidence.md`), so the same threshold is never maintained in two places.

## When to use

- Goals: fat loss, muscle gain, slimming chest/waist/abdomen, body recomposition, general fitness.
- Training settings: gym (machines / free weights / treadmill); non-gym — indoor (bodyweight, home equipment, cardio machines) and outdoor (running, cycling, swimming, hiking). Multi-setting combinations are supported.
- Plan horizons, in weeks: one week (default, repeatable), two weeks, four weeks (4-week progression), eight weeks and beyond; longer plans roll forward in 4-week blocks; month wording is converted at 1 month = 4 weeks.
- Dynamic adjustment: after the user reports weights/reps, heart rate/pace, weight/waist changes, or injury/schedule changes, the plan is adjusted along "feedback classification → L1 parameters / L2 structure / L3 goal reassessment". Every adjustment ships a "changes table + full updated weekly schedule", so the user always has a complete plan to follow.
- Ready-made templates: four built-in schedules — Schedule 1 "lean-bulk / recomp, 4 sessions/week", Schedule 2 "skinny-fat variant: waist fat + chest appearance", Schedule 3 "3-day split: back / legs / chest", Schedule 4 "no-equipment bodyweight: home / travel, 3–4 sessions/week" — with shared rules and a bodyweight-based starting-weight table, personal data filled in on request.
- Concrete starting numbers: strength exercises get recommended starting weights by bodyweight ratio (with RPE self-calibration); treadmill and cardio-machine sessions get incline, pace, cadence, and heart-rate guidance.
- Pre-delivery self-check: deficit ↔ rate ↔ timeline, every lift's sets/reps and starting weight, all four cardio elements, protein grams, and the 8-section structure — plans whose numbers don't add up are not shipped.
- Technique & special populations: warm-up, technique cues for 8 core lifts, breathing/bracing, and belt use; dedicated guidance for women (cycle, perimenopause, pregnancy, postpartum), adults 65+, minors, controlled hypertension/type-2 diabetes, and eating-disorder risk.
- On demand: three-meal nutrition plans and supplement advice (protein powder, creatine, caffeine) — not offered unless asked.
- Intake: step-by-step guided questions through option pickers (training background → time budget → injuries & body data); supports extracting body-composition data from smart-scale screenshots / InBody reports and converting it into a standard format (with self-check formulas and device-caliber validation).

## Installation

The skill uses the common `SKILL.md + references/` layout and has no runtime dependencies. Put the repository into your Agent's skills directory (e.g. `~/.claude/skills/`, `~/.codex/skills/`, or a directory managed by SkillsManager):

```bash
# Option 1: clone straight into the skills directory
git clone https://github.com/<your-name>/fitness-coach.git ~/.claude/skills/fitness-coach

# Option 2: clone anywhere, then symlink it
git clone https://github.com/<your-name>/fitness-coach.git ~/code/fitness-coach
ln -s ~/code/fitness-coach ~/.claude/skills/fitness-coach
```

Repository layout:

```text
fitness-coach/
├── SKILL.md            Main workflow, core formulas, output format, safety red lines
├── README.md           English README (default)
├── README.zh-CN.md     Chinese README
├── DESIGN.md           Architecture, token budget, design decisions
├── CHANGELOG.md        Version history
├── LICENSE
├── evals/
│   ├── evals.json      Behavioral evaluation cases (7 real prompts + expectations)
│   └── README.md       How to run and grade the evals
├── tests/
│   └── test.py         Structural + numeric assertions (python3 tests/test.py)
├── .github/
│   └── workflows/
│       └── test.yml    CI: run tests on push / PR
└── references/
    ├── goals.md        Goal strategies + how to set a target when the user has none
    ├── venues.md       Training-setting movement library (gym / indoor / outdoor, incl. treadmill, cardio machines, cycling, swimming, hiking)
    ├── templates.md    Ready-made schedules (shared rules + 4 schedules + output example)
    ├── technique.md    Warm-up, 8 core lifts, breathing/bracing, belts, DOMS vs injury
    ├── populations.md  Women, 65+, minors, controlled hypertension/T2D, eating disorders
    ├── body-data.md    Body-composition extraction and interpretation (smart scales / InBody, image support)
    ├── nutrition.md    Nutrition, meal templates, supplements, fasted training
    ├── programs.md     Periodization skeletons, split library, progressive overload, recovery
    ├── adjustments.md  Dynamic adjustment protocol (follow-up visits)
    └── evidence.md     Authoritative sources, chosen thresholds, evidence strength
```

## Quick start

1. Describe your request with body data: "I'm 30, 175 cm, 78 kg, want to lose fat, gym 3×/week, make me a four-week plan."
2. Missing data is collected step by step (basic info → training background → time budget → injuries & body data); free-form values such as sex, height, and weight are asked in a single text message. If the six basics (sex, age, height, weight, goal, training setting) are already given, intake is skipped and the plan ships immediately, opening with a one-line "assumptions" note. Say "use defaults" to skip the rest. The plan horizon defaults to one week — ask for two/four/eight weeks explicitly if needed.
3. Ask for nutrition or supplement advice separately: "Plan my three meals for fat loss", "Should I buy protein powder and creatine?", "What about fasted cardio?".
4. Come back with training feedback ("week 2: squatting 40 kg for 12 easy reps") to enter the adjustment loop.

## Triggering

- Automatic: the skill loads when the message mentions 健身, 锻炼, 减脂, 减重, 减肥, 增肌, 塑形, 体能, 体脂, 体脂秤, 腹肌, 臀腿, 瘦肚瘦腰, 哑铃, 弹力带, 无器械, 出差, 宿舍, 三餐食谱, 蛋白粉, 肌酸, 跑步, 游泳, 徒步, 训练计划, etc. (Chinese keywords — the skill is Chinese-first).
- Manual: `/fitness-coach your question`.
- The authoritative trigger list is the `description` / `triggers` fields in `SKILL.md`; this README does not duplicate it.

## Boundaries & safety

- Plans and nutrition advice are not medical advice. The skill asks users to see a doctor first for: blood pressure ≥180/110, unexplained syncope/chest pain, recent myocarditis, pregnancy complications, uncontrolled proliferative retinopathy, eating-disorder risk or BMI <18.5 with rapid weight loss, unassessed osteoporosis in adults 65+, and weight-loss requests from minors.
- Body-fat figures are formula estimates when the user provides no measurement, and are less accurate than professional devices (DEXA, InBody). Smart-scale muscle rate, visceral-fat grade, and bone mass are manufacturer models — not medical standards.
- Out of scope: competitive sports preparation, injury rehabilitation prescriptions, and medical nutrition therapy.
- Numbers and sources are maintained in `references/evidence.md`; when two files disagree, that file wins. Do not duplicate thresholds elsewhere.
- Current version: see the `version` field in `SKILL.md`; history in `CHANGELOG.md`; design trade-offs in `DESIGN.md`.

## Development & testing

No dependencies; Python 3.9+.

```bash
python3 tests/test.py
```

The suite covers file completeness, bilingual README links, frontmatter rules, formula coefficients, numeric fact tables, schedule volume arithmetic, recovery spacing, routing anchors, README file-tree consistency, version consistency, description triggers/over-promises, output-format columns, design-time token budget, and cross-file content consistency (red-line tiers, single-source thresholds, fast-lane and pre-delivery self-check presence). CI runs the same suite on every push and pull request.

Behavioral evals are in `evals/evals.json`; see `evals/README.md` for how to run them against the skill and a baseline.

## Publishing to GitHub

The repository is initialized locally on `main`. Create and push tags for released versions as needed:

```bash
git remote add origin git@github.com:<your-name>/fitness-coach.git
git push -u origin main
git push origin --tags
```

## License

[MIT](LICENSE) © 2026 shiyu
