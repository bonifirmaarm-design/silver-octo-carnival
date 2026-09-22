# Design skills — обязательное правило

В этом репозитории установлена библиотека из **166 design/UX-скилов** (`.claude/skills/`)
и библиотека готовых визуальных направлений (`.claude/design-resources/`).

**Правило: любая работа, которая затрагивает интерфейс, визуал или UX, обязана идти
через эти скилы.** Не «по желанию», не «если вспомню» — всегда. Полный каталог с
источниками: `docs/DESIGN-SKILLS.md`.

## Когда правило срабатывает

Всегда, если задача включает хотя бы одно: вёрстка и UI-код (HTML/CSS/React/Vue/Svelte/
Tailwind/RN), лендинг, дашборд, форма, компонент, дизайн-система, токены, типографика,
палитра, иконки, анимация и скролл, адаптив, тёмная тема, доступность, редизайн, аудит
и критика интерфейса, UX-исследование, прототип, слайды, баннер, 3D-сцена.

Не срабатывает только для задач, где интерфейса нет совсем: чистый бэкенд, CI, скрипты,
инфраструктура, работа с данными без визуализации.

## Обязательное ядро (загружать до написания кода)

Для **любой** UI-задачи сначала читаются эти скилы — они задают планку и режут «AI-slop»:

| Скил | Зачем |
|---|---|
| `frontend-design` | база Anthropic: намеренное визуальное направление вместо шаблонных дефолтов |
| `impeccable` | полный рабочий цикл: shape · audit · polish · harden, есть live-итерация в браузере |
| `hallmark` | жёсткий анти-slop чек-лист, применяется как финальный фильтр |
| `ui-ux-pro-max` | большая база паттернов UI/UX, шрифты, иконки, токены |
| `web-design-guidelines` | инженерные правила качества вёрстки (Vercel) |

Дальше по типу задачи подключается профильный скил (таблица ниже) — ядро при этом
не отменяется.

## Пайплайн

1. **Направление.** До кода — выбрать визуальный язык: `frontend-design`, `design-taste-frontend`,
   `brand`, `brandkit`, либо готовый `DESIGN.md` из `.claude/design-resources/awesome-claude-design/design-md/`
   (brutalist, editorial, cinematic, glass, terminal, warm, playful, indie, data-dense, remix).
   Направление формулируется явно, одним абзацем, до первой строки разметки.
2. **Сборка.** Профильные скилы под задачу.
3. **Ревью — обязательный шаг, не опциональный.** Прогнать результат через
   `hallmark` + `design-audit` + профильные `critique-*`, для доступности —
   `accessibility-audit`. Найденное чинится в этой же итерации, а не «потом».

## Профильные наборы

| Задача | Скилы |
|---|---|
| Лендинг, портфолио, редизайн | `design-taste-frontend`, `redesign-existing-projects`, `interface-design`, `frontend-design-pro` |
| Продуктовый UI, дашборды, формы | `impeccable`, `ui-ux-pro-max`, `form-design`, `data-visualization`, `information-architecture` |
| Дизайн-система и токены | `design-system`, `design-token`, `component-spec`, `theming-system`, `naming-convention`, `pattern-library`, `icon-system` |
| Типографика | `ui-typography`, `typography-scale`, `readable-measure`, `critique-typography` |
| Цвет и тема | `color-system`, `dark-mode-design`, `critique-color` |
| Раскладка и иерархия | `layout-grid`, `spacing-system`, `visual-hierarchy`, `responsive-design`, законы гештальта `law-of-*` |
| Анимация, скролл, микровзаимодействия | `scroll-craft`, `motion-system`, `animation-principles`, `micro-interaction-spec`, `loading-states`, `vercel-react-view-transitions` |
| Психология поведения | `fitts-law`, `hicks-law`, `jakobs-law`, `millers-law`, `teslers-law`, `doherty-threshold`, `peak-end-rule`, `von-restorff-effect`, `zeigarnik-effect`, `aesthetic-usability` |
| Аудит и критика | `design-audit`, `heuristic-evaluation`, `ux-heuristics`, `design-debt-audit`, `design-qa-checklist`, `critique-*` |
| Доступность | `accessibility-audit`, `accessibility-test-plan`, `localization-design` |
| UX-исследование | `user-persona`, `journey-map`, `jobs-to-be-done`, `interview-script`, `usability-test-plan`, `empathy-map`, `affinity-diagram` |
| Стратегия и процесс | `design-sprint`, `design-brief`, `design-principles`, `north-star-vision`, `service-blueprint`, `experience-map` |
| React / фронтенд-инженерия | `vercel-react-best-practices`, `vercel-composition-patterns`, `vercel-optimize`, `vercel-react-native-skills` |
| Графика и 3D | `img2threejs`, `imagegen-frontend-web`, `imagegen-frontend-mobile`, `image-to-code`, `illustration-style` |
| Презентации и баннеры | `slides`, `banner-design`, `presentation-deck` |
| UX-тексты | `ux-writing`, `writing-guidelines`, `content-strategy` |

## Красные линии

Результат не принимается, если в нём есть:

- дефолтные «AI-шаблоны»: фиолетово-синий градиент, generic-карточки со скруглением 8px
  и одинаковой тенью, Inter по умолчанию без причины, центрированный hero с двумя кнопками;
- визуальное решение без сформулированного направления из шага 1;
- пропущенный шаг ревью;
- произвольные значения вместо шкалы: цвета, отступы и размеры шрифта берутся
  из токенов/шкалы, а не подбираются на глаз;
- интерфейс без состояний loading / empty / error;
- контраст ниже WCAG AA и недоступная клавиатурная навигация.

## Как пользоваться

Скилы — проектные, Claude Code подхватывает их из `.claude/skills/` автоматически.
Вызов вручную: `/impeccable`, `/hallmark`, `/frontend-design` и т.д.
Перед стартом UI-задачи скил читается целиком (`SKILL.md` + его `references/`),
а не пересказывается по памяти.
