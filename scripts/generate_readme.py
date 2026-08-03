#!/usr/bin/env python3
"""排版机器人：读 data/prompts.yaml，生成 README.md（英文）+ README_zh.md（中文）。
本地跑：python3 scripts/generate_readme.py
线上：GitHub Actions 在数据变化或每天定时自动跑。"""
import os
import datetime
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "prompts.yaml")

REPO = "velokey-ai/awesome-seedream-5.0-pro-prompts"
SITE = "https://velokey.ai?sourceChannel=github-awesome-seedream"
BANNER = "images/banner.png"  # 顶部横幅，images/ 下存在才会显示

# ---------------- 分类注册表 ----------------
# 素材表里 category 填左边的 key；新增分类在这里加一行即可
CATEGORIES = {
    "portrait":    {"zh": "人像与头像",   "en": "Portrait & Avatar",    "emoji": "🧑"},
    "product":     {"zh": "产品与质感",   "en": "Product & Materials",  "emoji": "🧊"},
    "card":        {"zh": "卡片与海报",   "en": "Cards & Posters",      "emoji": "🎴"},
    "style":       {"zh": "风格转绘",     "en": "Style Transfer",       "emoji": "🎨"},
    "infographic": {"zh": "信息图与教育", "en": "Infographics & Edu",   "emoji": "📊"},
    "creative":    {"zh": "创意脑洞",     "en": "Creative Ideas",       "emoji": "🌀"},
    "other":       {"zh": "其他",         "en": "Others",               "emoji": "📦"},
}

TEXT = {
    "en": {
        "title": "🎨 Awesome Seedream 5.0 Pro Prompts",
        "intro": (
            "> A curated collection of creative prompts for ByteDance's **Seedream 5.0 Pro** "
            "image model, collected from the community with attribution.\n>\n"
            "> ⚡ Try every prompt through one OpenAI-compatible API — "
            f"**[Velokey]({SITE})** gives you Seedream, Nano Banana, GPT Image and more "
            "with a single key, pay-as-you-go."
        ),
        "copyright": (
            "> ⚠️ **Copyright**: All prompts and images are collected from public community "
            "posts for educational purposes, with author attribution and source links. "
            "If any content infringes your rights, please open an issue and we will remove it promptly."
        ),
        "stats": "📊 Statistics", "total": "📝 Total Prompts", "featured_c": "⭐ Featured",
        "cats": "🏷️ Categories", "updated": "🔄 Last Updated",
        "toc": "🗂️ Browse by Category",
        "all_sec": "📋 All Prompts",
        "prompt": "📝 Prompt", "note": "💡 Note",
        "needs_input": "**Input:** upload a reference image",
        "credit": "👤 Credit", "via": "collected via",
        "contribute": "🤝 How to Contribute",
        "contribute_body": (
            "Found a great prompt on X / Reddit / RedNote? "
            f"[**Submit it via Issue form**](https://github.com/{REPO}/issues/new?template=submit-prompt.yml) "
            "— once approved, it appears in the README automatically."
        ),
        "try_line": f"▶️ **Run this prompt via API** → [Velokey]({SITE}) (model id: `{{model}}`)",
        "license": "📄 License",
        "license_body": "Licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Prompt credits belong to their original authors.",
        "lang_switch": "**English** · [简体中文](README_zh.md)",
        "footer": f"One API for leading text, image & video models · [velokey.ai]({SITE})",
    },
    "zh": {
        "title": "🎨 Seedream 5.0 Pro 神级提示词合集",
        "intro": (
            "> 精选社区疯传的 **Seedream 5.0 Pro** 创意提示词，全部标注原作者与出处。\n>\n"
            f"> ⚡ 想直接跑这些提示词？**[Velokey]({SITE})** 一个 API 调用 Seedream、"
            "Nano Banana、GPT Image 等主流模型，一个 Key，按量付费。"
        ),
        "copyright": (
            "> ⚠️ **版权说明**：所有提示词与图片均收集自公开社区帖子，仅作学习交流，"
            "均已标注作者与来源。如有侵权请提 Issue，我们会第一时间删除。"
        ),
        "stats": "📊 数据统计", "total": "📝 提示词总数", "featured_c": "⭐ 精选",
        "cats": "🏷️ 分类数", "updated": "🔄 最近更新",
        "toc": "🗂️ 按分类浏览",
        "all_sec": "📋 全部提示词",
        "prompt": "📝 提示词", "note": "💡 使用说明",
        "needs_input": "**输入：** 需上传一张参考图",
        "credit": "👤 出处", "via": "转自",
        "contribute": "🤝 投稿",
        "contribute_body": (
            "在 X / Reddit / 小红书看到好提示词？"
            f"[**点这里用表单投稿**](https://github.com/{REPO}/issues/new?template=submit-prompt.yml)"
            "，审核通过后自动收录进 README。"
        ),
        "try_line": f"▶️ **用 API 跑这条提示词** → [Velokey]({SITE})（模型 id：`{{model}}`）",
        "license": "📄 协议",
        "license_body": "本仓库采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) 协议，提示词版权归原作者所有。",
        "lang_switch": "[English](README.md) · **简体中文**",
        "footer": f"一个 API 接入主流文本 / 图片 / 视频模型 · [velokey.ai]({SITE})",
    },
}


def anchor(text):
    keep = []
    for ch in text.lower():
        if ch.isalnum() or ch == " " or ch == "-" or "一" <= ch <= "鿿":
            keep.append(ch)
    return "".join(keep).strip().replace(" ", "-")


def cat_of(p):
    key = p.get("category", "other")
    return key if key in CATEGORIES else "other"


def cat_label(key, lang):
    c = CATEGORIES[key]
    return f"{c['emoji']} {c[lang]}"


def entry_md(p, t, lang):
    title = p["title"] if lang == "zh" else p.get("title_en", p["title"])
    ckey = cat_of(p)
    cname = CATEGORIES[ckey][lang]
    lines = [f"### No.{p['id']} {title}", ""]
    badges = [
        f"![Category](https://img.shields.io/badge/{'分类' if lang=='zh' else 'category'}-{cname.replace(' ', '_').replace('-', '--')}-8A2BE2)",
        f"![Model](https://img.shields.io/badge/model-{p.get('model','seedream-5.0-pro').replace('-','--')}-blue)",
    ]
    if p.get("featured"):
        badges.append("![Featured](https://img.shields.io/badge/%E2%AD%90-Featured-gold)")
    if p.get("needs_input"):
        badges.append("![Needs input](https://img.shields.io/badge/needs-reference_image-orange)")
    lines += [" ".join(badges), ""]
    imgs = [f for f in p.get("images", []) if not f.lower().endswith((".mp4", ".mov", ".webm"))]
    detail = f"prompts/{p['id']}.md"
    open_p = "📖 查看提示词" if lang == "zh" else "📖 View prompt"
    if imgs:
        lines += ["<div align=\"center\">", "",
                  f'<a href="{detail}"><img src="images/{imgs[0]}" width="360" loading="lazy" alt="{title}"></a>', "",
                  f'<b><a href="{detail}">{open_p}</a></b>', "", "</div>", ""]
    lines += ["---", ""]
    return "\n".join(lines)


def write_details(prompts):
    """为每条生成 prompts/<id>.md 详情页（含完整 prompt），让 README 保持轻量。"""
    dirp = os.path.join(ROOT, "prompts")
    os.makedirs(dirp, exist_ok=True)
    for p in prompts:
        title_zh = p["title"]; title_en = p.get("title_en", p["title"])
        cat = CATEGORIES[cat_of(p)]
        imgs = [f for f in p.get("images", []) if not f.lower().endswith((".mp4", ".mov", ".webm"))]
        L = ["[← 返回全部 / Back]( ../README_zh.md )　|　[English](../README.md)", "",
             f"# No.{p['id']} · {title_zh} / {title_en}", "",
             f"`{cat['zh']} / {cat['en']}`　`model: {p.get('model','seedream-5.0-pro')}`", ""]
        if imgs:
            cells = " ".join(f'<img src="../images/{f}" width="460" alt="{title_en}">' for f in imgs)
            L += ["<div align=\"center\">", "", cells, "", "</div>", ""]
        if p.get("needs_input"):
            L += ["> 📎 需上传一张参考图 / needs a reference image", ""]
        if p.get("note"):
            L += [f"> 💡 {p['note']}", ""]
        L += ["## 📝 Prompt", "", "```", p["prompt"].strip(), "```", ""]
        credit = f"**👤 出处 / Credit:** [{p['author']}]({p['author_link']}) · [source]({p['source']})"
        if p.get("via"): credit += f" · {p['via']}"
        L += [credit, "",
              f"▶️ **用 API 跑这条 / Run via API** → [Velokey]({SITE}) (`{p.get('model','seedream-5.0-pro')}`)", ""]
        with open(os.path.join(dirp, f"{p['id']}.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(L))


def build(lang):
    t = TEXT[lang]
    with open(DATA, encoding="utf-8") as f:
        prompts = yaml.safe_load(f) or []
    prompts.sort(key=lambda p: (not p.get("featured", False), p["id"]))
    featured = [p for p in prompts if p.get("featured")]
    used_cats = [k for k in CATEGORIES if any(cat_of(p) == k for p in prompts)]
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    md = []
    if os.path.exists(os.path.join(ROOT, BANNER)):
        md.append(f'<a href="{SITE}"><img src="{BANNER}" width="100%" alt="Awesome Seedream 5.0 Pro Prompts"></a>\n')
    md.append(f"# {t['title']}\n")
    md.append(t["lang_switch"] + "\n")
    md.append("[![Awesome](https://awesome.re/badge.svg)](https://github.com/sindresorhus/awesome) "
              f"[![PRs Welcome](https://img.shields.io/badge/submissions-welcome-brightgreen.svg)](https://github.com/{REPO}/issues/new?template=submit-prompt.yml) "
              "[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)\n")
    md.append(t["intro"] + "\n")
    md.append(t["copyright"] + "\n")

    md.append(f"## {t['stats']}\n")
    md.append(f"| {t['total']} | {t['featured_c']} | {t['cats']} | {t['updated']} |")
    md.append("|---|---|---|---|")
    md.append(f"| **{len(prompts)}** | **{len(featured)}** | **{len(used_cats)}** | {now} |\n")

    md.append(f"## {t['toc']}\n")
    for ckey in used_cats:
        group = [p for p in prompts if cat_of(p) == ckey]
        md.append(f"<details open><summary><b>{cat_label(ckey, lang)}</b> ({len(group)})</summary>\n")
        for p in group:
            title = p["title"] if lang == "zh" else p.get("title_en", p["title"])
            star = "⭐ " if p.get("featured") else ""
            md.append(f"- [{star}No.{p['id']} {title}](#no{p['id']}-{anchor(title)})")
        md.append("\n</details>\n")

    md.append(f"## {t['all_sec']}\n")
    for p in prompts:
        md.append(entry_md(p, t, lang))

    md.append(f"## {t['contribute']}\n")
    md.append(t["contribute_body"] + "\n")
    md.append(f"## {t['license']}\n")
    md.append(t["license_body"] + "\n")
    md.append(f"[![Star History Chart](https://api.star-history.com/svg?repos={REPO}&type=Date)](https://star-history.com/#{REPO}&Date)\n")
    md.append("<div align=\"center\">\n")
    md.append(f"<sub>🤖 Auto-generated from <code>data/prompts.yaml</code> · {now}</sub>\n")
    md.append(f"<br><sub>{t['footer']}</sub>\n")
    md.append("</div>")
    return "\n".join(md)


if __name__ == "__main__":
    _prompts = yaml.safe_load(open(DATA, encoding="utf-8")) or []
    write_details(_prompts)
    for lang, fname in (("en", "README.md"), ("zh", "README_zh.md")):
        out = build(lang)
        path = os.path.join(ROOT, fname)
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"✅ {fname} generated")
