# Market Intelligence OS — Operator Console Design System

**Document ID:** `UI-DS-001`
**Status:** Authoritative. This document governs `web/styles/mios.css`.
**Scope:** Every operator-facing surface — dashboard, audit surface, time-machine
scrubber, execution ledger, phase ladder.

> If a rule in this document and a line of CSS disagree, **the CSS is wrong.**

---

## 0. Why this system exists

This is not a marketing site. It is an instrument panel for a system that reasons about
money under uncertainty. Every visual decision is therefore held to one test:

> **Does this make a true thing easier to see, or a false thing harder to believe?**

Beauty here is not decoration layered on top of data. It is the *legibility of truth* —
the reason a Bloomberg terminal, a flight deck, and a hospital monitor all look
serious. The console must feel calm at rest, and unmissable when something is wrong.

Three non-negotiable consequences:

1. **The interface may never look more certain than the data.** A number without
   provenance is not a number; it is a rumour. The stylesheet renders it as a defect.
2. **Run mode may never be ambiguous.** Fixture, shadow, paper and real are
   distinguished on four independent channels so no single failure (colour blindness,
   greyscale printing, a broken font) can collapse two of them into one.
3. **Nothing decorative may imply activity.** Motion is reserved for state that is
   genuinely changing. A pulsing dot means live data. It never means "we thought this
   looked nice."

---

## 1. Architecture: cascade layers

All CSS lives in exactly six ordered layers. **Never** write an unlayered rule, and
**never** use `!important` outside the reduced-motion block.

```css
@layer reset, tokens, base, layout, components, states, utilities;
```

| Layer | Owns | Never contains |
|---|---|---|
| `reset` | Normalisation, box model, media defaults | Any colour or brand decision |
| `tokens` | Every custom property; light-scheme re-anchoring | Any selector that paints an element |
| `base` | Element defaults: body, links, focus, scrollbars, numerals | Component classes |
| `layout` | App shell, rails, grids, section headers | Colour beyond surface/line tokens |
| `components` | `.card`, `.metric`, `.mode`, `.phase`, `.pill`, `.track` … | Page-specific one-offs |
| `states` | `:has()` reactions, motion, forced-colors, print | New component structure |
| `utilities` | Single-purpose helpers (`.muted`, `.mono`, `.sr-only`) | Anything multi-property |

**Why layers, not specificity:** specificity wars are how design systems die. With
layers, a single-class utility can always override a multi-class component without
`!important`, and overrides are *declared* rather than accidental.

---

## 2. Colour: OKLCH, hue as meaning

Every colour is `oklch()`. No hex. No `rgb()`. No exceptions.

**Rationale.** OKLCH is perceptually uniform: `oklch(70% …)` looks equally bright at
every hue, so a green "pass" and a red "halt" carry *identical* visual weight and
neither wins attention by accident. Adjusting one lightness value re-anchors the whole
theme, which is exactly how the light scheme is implemented — same tokens, new
lightness, zero component changes.

### 2.1 Hue is semantic, and hues are reserved

| Token | Hue | Means | May be used for |
|---|---|---|---|
| `--hue-void` | 255 | Structure | Surfaces, chrome, ink |
| `--hue-signal` | 232 | Interactive | Primary actions, focus, selection |
| `--hue-verified` | 158 | Verified / reconciled | Passed gates, clean reconciliation |
| `--hue-caution` | 78 | Pending / degraded | Paper mode, entitlement pending |
| `--hue-halt` | 22 | Failure / stop | Failed gates, kill switch, stale data |
| `--hue-shadow` | 286 | Observation-only | Shadow mode, zero order authority |
| `--hue-live` | 352 | **Real capital** | **Reserved. Unreachable in this build.** |

`--hue-live` is quarantined. Nothing decorative may borrow it, so the first time an
operator ever sees that hue, it means exactly one thing.

### 2.2 The elevation ramp

Six surfaces (`--surface-0` … `--surface-4`, plus `--surface-inset`) and four ink
steps (`--ink-0` … `--ink-3`). **Ink below `--ink-3` does not exist** — if text needs
to be quieter than `--ink-3`, it should not be on screen.

Tinting is always `oklch(from var(--token) l c h / <alpha>)` with the alpha drawn from
`--tint-weak | --tint-medium | --tint-strong`. This is why a "green card" and a "red
card" feel like siblings instead of two different products.

---

## 3. Type

| Role | Token | Notes |
|---|---|---|
| UI text | `--font-sans` (Inter var.) | Body, labels, navigation |
| **All numbers** | `--font-mono` + `tabular-nums slashed-zero` | Non-negotiable |

**Numbers are always tabular and always monospaced.** In a financial console,
proportional digits make a column of figures shift horizontally as values update —
the eye reads motion where there is only re-rendering. Slashed zero removes
zero/O ambiguity in hashes and IDs.

Sizes are a fluid `clamp()` ramp (`--text-2xs` → `--text-2xl`, plus `--text-num` for
hero figures). Only two line-heights exist: `--leading-tight` for display,
`--leading-body` for prose. Uppercase micro-labels always carry
`--tracking-caps` (0.09em) — uppercase without added tracking is a legibility bug.

---

## 4. Space and form

Space is one geometric scale, `--s-1` (4px) → `--s-8` (64px). **A component may not
invent a spacing value.** If a gap needs 13px, the design is wrong, not the scale.

Radii: `--radius-sm` (6px) for chips and inputs, `--radius` (10px) for controls,
`--radius-lg` (16px) for cards, `--radius-pill` for badges. Nesting rule: a child's
radius is always ≤ its parent's, or the corners visibly "float".

**The light-catch.** Every `.card` carries a 1px top-edge highlight via a masked
`::after`. This single detail — a gradient border that is brighter where light would
fall — is what separates a surface that reads as *physical* from a flat grey box. It
is the most quietly expensive-looking line in the system.

---

## 5. The mode badge (constitutional component)

Phase 10 requires that `FIXTURE`, `SHADOW`, `PAPER` and `REAL` be **unconfusable**.
The badge encodes mode on **four independent channels**:

| Channel | Fixture | Shadow | Paper | Real |
|---|---|---|---|---|
| Hue | void (neutral) | violet 286 | amber 78 | crimson 352 |
| Label | `FIXTURE` | `SHADOW` | `PAPER` | `REAL` |
| Glyph shape | ■ square | ● circle | ▲ triangle | ◆ diamond |
| Surface | diagonal hatch | diagonal hatch | diagonal hatch | **flat + double outline** |

Real capital is the *only* flat fill and the *only* double outline. A greyscale
printout, a colour-blind operator, and a monochrome terminal all still distinguish all
four. In this build the real badge renders with `[data-disabled]` — struck through at
42% opacity — because live authority does not exist in the codebase.

---

## 6. Lineage enforcement (the system's conscience)

```css
.metric:not(:has(.lineage)) {
  outline: 2px dashed var(--halt);
  background: oklch(from var(--halt) l c h / 0.08);
}
.metric:not(:has(.lineage))::before {
  content: "⚠ LINEAGE MISSING — METRIC NOT DISPLAYABLE";
}
```

A metric that cannot show where it came from does not fall back to looking normal —
**it renders as a visible defect.** The constitutional rule "no metric without
lineage" is enforced by the cascade itself, so a template author cannot ship an
unsourced number even by accident. This is the single most important rule in the
stylesheet.

The same pattern governs role gating: `.gated[data-role-ok="false"]` desaturates its
control *and* prints `requires <role>` beneath it. A disabled control that does not
explain itself is a dead end; this one teaches.

---

## 7. Motion

| Duration | Token | Used for |
|---|---|---|
| 90ms | `--t-instant` | Press feedback, row hover |
| 160ms | `--t-quick` | Hover, nav, card lift |
| 280ms | `--t-calm` | Panel and overlay transitions |

Easing is `--ease-out` (`cubic-bezier(.16,1,.3,1)`) for anything entering — fast start,
soft landing, the curve that feels responsive rather than floaty.

Two rules:

1. **Motion never carries information alone.** The staleness pulse is accompanied by
   colour *and* the `data-stale` attribute *and* text.
2. **Scroll-reveal is progressive enhancement only** — wrapped in
   `@supports (animation-timeline: view())` *and* `prefers-reduced-motion:
   no-preference`. Reduced motion collapses every duration to 0.01ms.

---

## 8. Accessibility floor (not a checklist — a gate)

- Body text meets **WCAG AA**; `--ink-3` is reserved for non-essential micro-copy.
- `:focus-visible` is a 2px `--signal` ring with 2px offset, **never removed**.
- `forced-colors: active` re-borders every chip and badge with `CanvasText` so
  Windows High Contrast keeps every boundary.
- Every state expressed by colour is *also* expressed as text or shape.
- Print styles drop the rail and flatten cards — an audit artifact must survive paper.

---

## 9. Authoring rules (the short version)

**Do**
- Add new colours as tokens with a documented semantic meaning.
- Compose from `.card`, `.metric`, `.pill`, `.mode`.
- Use `:has()` for state that flows parent-ward.
- Keep numbers in `--font-mono` with tabular figures.

**Don't**
- Write a raw hex or a one-off `px` spacing value.
- Use `!important` (outside reduced-motion).
- Style by element or ID in `components`.
- Add a hover-only affordance with no keyboard equivalent.
- Ever use `--hue-live` for decoration.

---

## 10. Review checklist

Before any console change merges:

- [ ] Every colour resolves to a token; no raw hex introduced.
- [ ] Every metric block contains a `.lineage` child.
- [ ] Mode badges present all four channels; `REAL` remains disabled.
- [ ] Keyboard traversal reaches every control; focus ring visible throughout.
- [ ] `prefers-reduced-motion` and `forced-colors` verified.
- [ ] Light and dark schemes both checked.
- [ ] No animation implies data movement that is not occurring.
