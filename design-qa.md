# FOX TRADING Design QA

## Comparison target

- Source visual truth: `/workspace/scratch/2d4b9132b12f/generated_images/exec-9c3d4dd4-acfe-480d-a383-8c22f6ba0884.png`
- Browser-rendered implementation: `artifacts/design/fox-trading-implementation.jpg`
- Full-view comparison: `artifacts/design/fox-trading-comparison.png`
- Focused brand comparison: `artifacts/design/fox-trading-logo-comparison.png`
- Local implementation: `http://terminal.local:4173/`

## Normalization and state

- Source pixels: 1487 × 1058.
- Implementation screenshot pixels: 1353 × 929.
- Browser CSS viewport: approximately 1363 × 936 at device pixel ratio 1; the captured content image is 1353 × 929 after browser chrome and scrollbar exclusion.
- Density normalization: the source was proportionally resized to 929 pixels high before horizontal composition with the implementation. No device frame or browser chrome was included.
- State: desktop dark theme, `Market Pulse`, `EUR/USD`, `1D`, guided mode enabled, evidence drawer closed.

## Full-view comparison evidence

The normalized side-by-side image shows the same institutional console composition: fixed intelligence rail, centered global search, high-contrast Market Pulse hierarchy, safety and newcomer guidance, four-market selector, large candlestick workspace, and adjacent decision card. Major-region proportions, information density, dark navy surfaces, cyan interaction signals, amber wait state, green verification state, borders, and card rhythm all remain faithful to the selected target. The working chart is rendered rather than represented by a placeholder.

## Focused region comparison evidence

The focused upper-left comparison confirms a real geometric fox image asset—not CSS, an emoji, or a handcrafted SVG—with the selected cyan, white, deep-blue, and amber direction. The `FOX TRADING` lockup, cyan `FOX` word, white `TRADING` word, subtitle, vertical separator, learning-safe panel, and rail alignment remain clear at production size. The production mark has slightly more dimensional shading than the concept mark; this is an acceptable asset refinement and does not change recognition or hierarchy.

## Required fidelity surfaces

- Fonts and typography: compact sans-serif UI typography, optical weight contrast, tabular market numerals, uppercase eyebrows, and title hierarchy match the source. No important wrapping or truncation is visible.
- Spacing and layout rhythm: rail width, top-bar height, page insets, card spacing, border radii, table density, and above-the-fold composition align with the target. No persistent control is clipped.
- Colors and visual tokens: dark navy surfaces, cool cyan focus/brand color, green verification, amber caution, red downside, and muted secondary copy are consistently tokenized and visibly match the reference.
- Image quality and asset fidelity: the fox mark is a 512 × 512 transparent production PNG with a crisp 48-pixel rendering and dedicated app/apple icons. No placeholder or code-drawn substitute is used.
- Copy and content: the product name, safety boundary, newcomer reading order, plain-English decision, probability, reward/risk, point-in-time status, and evidence terminology are immediately understandable and consistent with the intended platform.

## Findings

- No actionable P0, P1, or P2 visual mismatches remain.
- No blocking accessibility or core-flow defect was observed in the inspected desktop state.

## Interaction and runtime verification

- Market switching updates the quote, asset class, explanation, and candlestick chart.
- `1H`/`4H`/`1D`/`1W` chart controls update pressed state.
- Evidence drawer opens, explains the decision, and closes.
- Guided mode toggles the novice explanation layer.
- Global search finds both markets and product features; selecting `Time Machine` navigates correctly.
- `Command/Ctrl + K` focuses global search and `Escape` clears it.
- Time Machine slider supports keyboard `Home`/`End`, changes the historical cutoff, and correctly shows singular/plural event labels.
- Every primary workspace navigation item renders its intended view.
- Application-origin browser warnings/errors checked: none. An unrelated browser-extension metadata error was excluded from application findings.

## Comparison history

- Initial normalized full-view and focused-brand comparison: no actionable P0/P1/P2 mismatch found; no visual correction loop was required.
- Functional QA correction completed before the final capture: global search originally matched markets only despite promising feature search. Feature navigation, keyboard focus, empty-state feedback, and regression coverage were added, then verified in the browser.

## Implementation checklist

- [x] Match selected FOX TRADING desktop composition and palette.
- [x] Use a production fox image asset and app icons.
- [x] Preserve real chart rendering and primary interactions.
- [x] Verify novice guidance and paper/fixture safety language.
- [x] Verify browser runtime and application console health.
- [x] Save normalized full-view and focused-region evidence.

final result: passed
