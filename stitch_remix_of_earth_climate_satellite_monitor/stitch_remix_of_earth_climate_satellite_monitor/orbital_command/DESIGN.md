---
name: Orbital Command
colors:
  surface: '#16111b'
  surface-dim: '#16111b'
  surface-bright: '#3d3741'
  surface-container-lowest: '#110c15'
  surface-container-low: '#1f1a23'
  surface-container: '#231e27'
  surface-container-high: '#2e2832'
  surface-container-highest: '#39323d'
  on-surface: '#eadfed'
  on-surface-variant: '#cfc2d6'
  inverse-surface: '#eadfed'
  inverse-on-surface: '#342e38'
  outline: '#988da0'
  outline-variant: '#4c4354'
  surface-tint: '#dbb8ff'
  primary: '#dbb8ff'
  on-primary: '#470083'
  primary-container: '#b36fff'
  on-primary-container: '#3e0073'
  inverse-primary: '#802dd4'
  secondary: '#dbb8ff'
  on-secondary: '#411e65'
  secondary-container: '#58367e'
  on-secondary-container: '#cca5f5'
  tertiary: '#ffb77c'
  on-tertiary: '#4d2700'
  tertiary-container: '#ca7f3b'
  on-tertiary-container: '#432100'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#efdbff'
  primary-fixed-dim: '#dbb8ff'
  on-primary-fixed: '#2b0052'
  on-primary-fixed-variant: '#6600b7'
  secondary-fixed: '#efdbff'
  secondary-fixed-dim: '#dbb8ff'
  on-secondary-fixed: '#2a034f'
  on-secondary-fixed-variant: '#58367e'
  tertiary-fixed: '#ffdcc2'
  tertiary-fixed-dim: '#ffb77c'
  on-tertiary-fixed: '#2e1500'
  on-tertiary-fixed-variant: '#6d3900'
  background: '#16111b'
  on-background: '#eadfed'
  surface-variant: '#39323d'
typography:
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '700'
    lineHeight: 44px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: 0.05em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.5rem
  margin: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system delivers a high-contrast, immersive dark space aesthetic rooted in command-and-control operations. It evokes precision, high-stakes capability, and futuristic authority. 

- **Brand Personality:** Authoritative, advanced, focused, and impenetrable.
- **Target Audience:** Enterprise operators, technical directors, and aerospace or high-tech professionals who demand absolute clarity and zero visual friction in high-density environments.
- **Emotional Response:** Reassurance through rigorous control, technological dominance, and sleek efficiency.
- **Design Style:** A fusion of **Minimalism** and **High-Contrast / Bold** utilizing deep space-black backgrounds, razor-sharp geometry, and vibrant ultraviolet accents to guide the operator's eye strictly to actionable telemetry.

## Colors

The palette is engineered specifically for low-light command environments, reducing eye fatigue while maximizing the visual weight of critical status indicators. 

- **Primary & Secondary:** Deep ultraviolet (`#9b4def`) and muted purple (`#8b67b2`) replace conventional green to establish a distinct, high-tech identity. They highlight active states, primary actions, and telemetry focus points.
- **Neutrals:** Built upon an obsidian foundation (`#7c7480` toned accents) with layered surface tokens (`#121217`, `#18181b`) to create architectural depth without relying on heavy drop shadows.
- **Functional Accents:** Restrained use of amber (`#834600`) and emerald strictly for system warnings and nominal operational statuses.

## Typography

The typographic hierarchy marries futuristic geometry with utilitarian readability. 

- **Headlines:** Set in *Space Grotesk* for a technical, forward-looking architectural tone.
- **Body:** Set in *Inter* to ensure pristine legibility across dense data displays and long-form operational logs.
- **Labels & Data:** Set in *JetBrains Mono* for tabular alignment, metrics, timestamps, and system codes where character-to-character precision is paramount.

## Layout & Spacing

This design system uses a strict **fluid grid** combined with dense modular panels. The layout model is engineered for high-density command dashboards that scale gracefully from localized monitoring stations to ultra-wide control center displays.

- **Grid Structure:** 12-column flexible grid with fixed 24px gutters and dynamic outer margins.
- **Responsive Adaptation:** On mobile devices, multi-column telemetry feeds collapse into single-column vertical stacks, prioritizing top-level status alerts while preserving touch targets.

## Elevation & Depth

Depth is communicated primarily through **low-contrast outlines** and structured tonal layering rather than heavy drop shadows, reinforcing a flat, high-performance interface paradigm.

- **Surface Tiers:** Backgrounds are kept at the obsidian base layer, while functional containers step up to `#121217` and interactive cards sit at `#18181b`.
- **Borders & Glows:** Boundaries are defined by subtle 1px outlines (`#27272a`). Active or focused components emit a controlled, low-opacity ultraviolet ambient glow (`#9b4def` at 15% opacity) to establish immediate spatial hierarchy without visual clutter.

## Shapes

The shape language reflects engineered precision with controlled geometry. 

- **Soft Corner Radius:** Elements maintain a tight 0.25rem (`4px`) base radius, avoiding overly soft or consumer-grade pill shapes. Larger containers scale up to `0.5rem` or `0.75rem`.
- **Justification:** Sharp-enough corners convey technical rigor, equipment racks, and digital HUD displays, perfectly aligning with the aerospace command narrative.

## Components

All components must adhere to the high-contrast, data-dense nature of the system.

- **Buttons:** Primary buttons feature a solid ultraviolet (`#9b4def`) background with crisp typography, shifting to `#8b67b2` on hover with a subtle exterior glow. Secondary actions use ghost styles with a 1px border and transparent fill.
- **Chips & Tags:** Built using the monospace label font with uppercase text, tight padding, and subtle tinted backgrounds to designate subsystem categories (e.g., `PROPULSION`, `COMMS`).
- **Lists & Tables:** High-density rows separated by fine 1px dividing lines. Hover states subtly shift the row background to the elevated surface tier.
- **Checkboxes & Radio Buttons:** Geometric, square-cornered inputs with stark contrast states. Checked states fill immediately with the primary ultraviolet hue.
- **Input Fields:** Dark surface background (`#121217`) with a subtle border that hardens to purple upon focus. Monospace text variants are preferred for telemetry input.
- **Cards:** Structural data containers featuring the elevated surface color, a 1px subtle border, and optional top-accent status lines in primary purple.
- **Telemetry Readouts:** Specialized metric blocks pairing a large *Space Grotesk* value with an uppercase *JetBrains Mono* label, designed for instant scannability.