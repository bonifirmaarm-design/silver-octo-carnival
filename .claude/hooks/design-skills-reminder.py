#!/usr/bin/env python3
"""UserPromptSubmit hook: enforces the design-skills rule from CLAUDE.md.

Fires only when the prompt looks UI/design/UX related, then injects a short
reminder naming the mandatory core skills and the review step.
"""
import json
import re
import sys

KEYWORDS = [
    # en
    "ui", "ux", "design", "redesign", "frontend", "front-end", "interface", "layout",
    "landing", "page", "website", "web site", "dashboard", "component", "button",
    "form", "modal", "navbar", "sidebar", "hero", "css", "tailwind", "styling",
    "style", "theme", "dark mode", "typography", "font", "color", "palette",
    "spacing", "grid", "responsive", "animation", "motion", "transition", "scroll",
    "icon", "logo", "brand", "design system", "token", "figma", "mockup", "wireframe",
    "prototype", "accessibility", "a11y", "wcag", "contrast", "slides", "banner",
    "react", "vue", "svelte", "next.js", "nextjs", "html", "jsx", "tsx", "polish",
    "audit", "critique", "visual", "aesthetic", "three.js", "threejs", "3d",
    # ru
    "дизайн", "редизайн", "интерфейс", "вёрстк", "верстк", "фронт", "лендинг",
    "страниц", "сайт", "дашборд", "компонент", "кнопк", "форм", "модал", "навигац",
    "сайдбар", "стил", "тем", "типографик", "шрифт", "цвет", "палитр", "отступ",
    "сетк", "адаптив", "анимац", "переход", "скролл", "иконк", "логотип", "бренд",
    "токен", "макет", "прототип", "доступност", "контраст", "слайд", "баннер",
    "визуал", "эстетик", "красив", "оформ", "экран", "юзабилити", "ux-",
]

CORE = "frontend-design · impeccable · hallmark · ui-ux-pro-max · web-design-guidelines"

REMINDER = f"""[design-skills rule — CLAUDE.md]
Задача выглядит как UI/дизайн-работа. Правило репозитория обязывает:
1. Загрузить ядро до написания кода: {CORE}
2. Явно сформулировать визуальное направление (или взять DESIGN.md из
   .claude/design-resources/awesome-claude-design/design-md/) до первой строки разметки.
3. Подключить профильные скилы из таблицы в CLAUDE.md.
4. Обязательное ревью результата: hallmark + design-audit + critique-* (+ accessibility-audit).
Каталог всех 166 скилов: docs/DESIGN-SKILLS.md. Красные линии — в CLAUDE.md."""


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    prompt = str(payload.get("prompt", "")).lower()
    if not prompt:
        return 0

    for kw in KEYWORDS:
        # word-boundary match for short latin keywords, substring for the rest
        if len(kw) <= 3 and kw.isascii():
            if re.search(rf"\b{re.escape(kw)}\b", prompt):
                break
        elif kw in prompt:
            break
    else:
        return 0

    print(REMINDER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
