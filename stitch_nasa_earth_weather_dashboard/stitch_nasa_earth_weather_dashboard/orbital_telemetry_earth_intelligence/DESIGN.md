---
name: Orbital Telemetry & Earth Intelligence
colors:
  surface: '#10131c'
  surface-dim: '#10131c'
  surface-bright: '#363942'
  surface-container-lowest: '#0b0e16'
  surface-container-low: '#181b24'
  surface-container: '#1c1f28'
  surface-container-high: '#272a33'
  surface-container-highest: '#31353e'
  on-surface: '#e0e2ee'
  on-surface-variant: '#cdc2d8'
  inverse-surface: '#e0e2ee'
  inverse-on-surface: '#2d3039'
  outline: '#968da1'
  outline-variant: '#4b4455'
  surface-tint: '#d4bbff'
  primary: '#d4bbff'
  on-primary: '#41008b'
  primary-container: '#8a3ffc'
  on-primary-container: '#faf1ff'
  inverse-primary: '#7825ea'
  secondary: '#4cd6fb'
  on-secondary: '#003642'
  secondary-container: '#00b2d6'
  on-secondary-container: '#003f4e'
  tertiary: '#ffafd1'
  on-tertiary: '#63003e'
  tertiary-container: '#d21489'
  on-tertiary-container: '#fff1f4'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ebdcff'
  primary-fixed-dim: '#d4bbff'
  on-primary-fixed: '#270058'
  on-primary-fixed-variant: '#5d00c2'
  secondary-fixed: '#b3ebff'
  secondary-fixed-dim: '#4cd6fb'
  on-secondary-fixed: '#001f27'
  on-secondary-fixed-variant: '#004e5f'
  tertiary-fixed: '#ffd8e6'
  tertiary-fixed-dim: '#ffafd1'
  on-tertiary-fixed: '#3d0024'
  on-tertiary-fixed-variant: '#8b0059'
  background: '#10131c'
  on-background: '#e0e2ee'
  surface-variant: '#31353e'
typography:
  display-xl:
    fontFamily: Space Grotesk
    fontSize: 3.5rem
    fontWeight: '700'
    lineHeight: 4rem
    letterSpacing: -0.03em
  headline-lg:
    fontFamily: Space Grotesk
    fontSize: 2.25rem
    fontWeight: '600'
    lineHeight: 2.75rem
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Space Grotesk
    fontSize: 1.75rem
    fontWeight: '600'
    lineHeight: 2.25rem
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 1.5rem
    fontWeight: '600'
    lineHeight: 2rem
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 1.25rem
    fontWeight: '500'
    lineHeight: 1.75rem
  body-lg:
    fontFamily: Geist
    fontSize: 1.125rem
    fontWeight: '400'
    lineHeight: 1.75rem
  body-md:
    fontFamily: Geist
    fontSize: 0.9375rem
    fontWeight: '400'
    lineHeight: 1.5rem
  body-sm:
    fontFamily: Geist
    fontSize: 0.8125rem
    fontWeight: '400'
    lineHeight: 1.25rem
  label-lg:
    fontFamily: JetBrains Mono
    fontSize: 0.875rem
    fontWeight: '500'
    lineHeight: 1.25rem
    letterSpacing: 0.05em
  label-md:
    fontFamily: JetBrains Mono
    fontSize: 0.75rem
    fontWeight: '500'
    lineHeight: 1rem
    letterSpacing: 0.06em
  label-sm:
    fontFamily: JetBrains Mono
    fontSize: 0.6875rem
    fontWeight: '400'
    lineHeight: 0.875rem
    letterSpacing: 0.08em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-mobile: 0.75rem
  margin: 2rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 1rem
  space-lg: 1.5rem
  space-xl: 2.5rem
---

## Brand & Style

This design system is tailored for high-precision scientific Earth observation, orbital sensor telemetry, and planetary data intelligence. Designed for atmospheric researchers, orbital payload specialists, climatologists, and mission controllers, the system projects rigorous analytical credibility balanced with the wonder of deep-space exploration.

The aesthetic fuses **Glassmorphism** with **Technical Sci-Fi Minimalism**:
- **Deep Space Obsidian Foundations:** Low-reflectance obsidian and deep midnight canvases replicate the void of space, ensuring maximum contrast and zero visual fatigue during prolonged monitoring cycles.
- **Bioluminescent Spectral Accents:** Neon violet, cosmic magenta, and electric cyan/blue gradients inspired by planetary auroras, orbital tracking paths, and deep nebula clouds delineate vital live telemetry.
- **Glass Optics & Frosted Sheens:** Translucent layered panels with microscopic frosted glass backdrops echo high-grade spacecraft instrumentation visors and precision sensor overlays.
- **Engineered Legibility:** Crisp, monospaced tabular numerals and geometric headings reinforce authoritative scientific precision.

## Colors

The palette derives directly from cosmic nebulae and planetary orbital telemetry, structured strictly for ultra-dark mission environments.

- **Primary (`#8A3FFC` - Neon Violet):** Primary interactive elements, mission milestones, active orbital paths, and primary system focal states.
- **Secondary (`#00B4D8` - Electric Blue / Cyan):** Real-time planetary telemetry, atmospheric and oceanographic readings, operational data streams, and active radar metrics.
- **Tertiary (`#E02694` - Cosmic Magenta / Solar Flare):** Critical threshold alerts, solar radiation indices, thermal anomalies, and highlight states.
- **Neutral (`#070A12` - Deep Space Obsidian):** The deep foundation layer, complemented by tinted glass tiers (`rgba(15, 20, 36, 0.65)` for card surfaces, `rgba(255, 255, 255, 0.08)` for structural boundaries, and `#E2E8F0` for primary readable data values).

### Semantic & Metric Glow Accents
- **Temperature & Solar Metrics:** Linear transition from `#FF5436` to `#E02694`.
- **Atmospheric & Wind Telemetry:** Sharp gradient from `#00B4D8` into `#8A3FFC`.
- **Precipitation & Hydrological Vectors:** Crisp, focused cyan `#38BDF8` with a diffused `0 0 12px rgba(56, 189, 248, 0.35)` field.

## Typography

The typographic hierarchy establishes clear technical delineation:

- **Display & Headlines (`Space Grotesk`):** Delivers clean, aerospace-grade geometric structure. Used for mission titles, sensor platform labels, and primary dashboard readouts.
- **Body Copy (`Geist`):** Provides pristine readability for analytical reports, telemetry descriptions, and payload state summaries without visual interference.
- **Labels & Tabular Numerals (`JetBrains Mono`):** Applied to telemetry data coordinates, ISO timestamps, live sensor fluctuations, and status tags. All tabular figures must render in monospaced widths to prevent visual jittering during live real-time updates. Labels are predominantly uppercase with relaxed letter-spacing.

## Layout & Spacing

Telemetry dashboards demand dense, well-organized information density with absolute geometric balance.

### Grid Architecture
- **Desktop (1440px+):** 12-column dynamic grid, `2rem` outer canvas margin, `1.25rem` column gutters. Designed for 3-to-4 card instrumentation tiers and multi-layer orbital viewports.
- **Tablet (768px - 1439px):** 8-column layout, `1.5rem` canvas margin, `1rem` gutters. Secondary telemetry strips collapse into accordion drawers.
- **Mobile (< 768px):** 4-column layout, `1rem` outer canvas margin, `0.75rem` gutters. Sensor cards stack sequentially into single-column telemetry monitors.

### Spacing Principles
- Compact micro-spacing (`space-xs`, `space-sm`) binds units with their direct numerical metrics (e.g., `24.8` alongside `km/h`).
- Standard panel padding relies on `space-md` (mobile) and `space-lg` (desktop) to ensure glass card edges do not crowd live graphs.

## Elevation & Depth

Visual hierarchy uses frosted glass refraction, selective luminous halos, and edge highlight lines rather than conventional drop shadows.

- **Level 0 (Canvas Base):** Deep obsidian void `#070A12` with an ambient radial backdrop gradient `radial-gradient(ellipse at 50% 0%, rgba(138, 63, 252, 0.08), transparent 70%)`.
- **Level 1 (Telemetry Panels & Cards):** Translucent background `rgba(13, 18, 30, 0.70)`, backdrop-filter `blur(16px)`, accompanied by a top-edge light refraction line: `1px solid rgba(255, 255, 255, 0.08)`.
- **Level 2 (Active Panels & Modal Overlays):** Semi-opaque dark slate `rgba(18, 24, 42, 0.85)`, backdrop-filter `blur(24px)`, outlined with `1px solid rgba(138, 63, 252, 0.35)` and a subtle ambient perimeter glow `0 0 24px rgba(138, 63, 252, 0.12)`.
- **Level 3 (Focused Instruments & Live Nodes):** Accentuated by interactive luminous halos:
  - Cyan highlights: `box-shadow: 0 0 16px rgba(0, 180, 216, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)`.
  - Violet/Magenta highlights: `box-shadow: 0 0 20px rgba(224, 38, 148, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2)`.

## Shapes

The interface balances aerodynamic curves with structural stability:
- **Base Components (Inputs, Chips, Small Buttons):** Rounded level `2` (`0.5rem` / `8px`) creates refined, technical contours reminiscent of avionics touch consoles.
- **Containers & Glass Panels (`rounded-lg`):** `1rem` (`16px`) corner radiuses soften panel bounds while retaining structural grid discipline.
- **Floating Controls & Indicators (`rounded-xl`):** `1.5rem` (`24px`) or full pill silhouettes (`9999px`) reserved for status badges, live tracking toggles, and orbital timeline cursors.

## Components

### Buttons & Interactive Controls
- **Primary Mission Actions:** High-intensity gradient fill (`linear-gradient(135deg, #8A3FFC 0%, #00B4D8 100%)`) with crisp white text (`Space Grotesk`, medium weight). On hover: scale factor `1.02` accompanied by an expanded outer neon bloom (`box-shadow: 0 0 20px rgba(0, 180, 216, 0.5)`).
- **Secondary Telemetry Controls:** Translucent slate fill `rgba(255, 255, 255, 0.05)`, perimeter border `1px solid rgba(255, 255, 255, 0.15)`, text color `#E2E8F0`. Hover triggers cyan edge illumination `rgba(0, 180, 216, 0.6)`.

### Telemetry Cards & Metric Glass Panels
- **Structure:** Encased in translucent midnight glass with `16px` border-radius and inner padding `1.5rem`.
- **Header:** Uppercase `label-md` tracking category accompanied by a live status dot (`6px` circular pulse: green `#10B981` nominal, magenta `#E02694` critical).
- **Value Grouping:** Large numerical metrics rendered in `Space Grotesk` or `JetBrains Mono` with unit indicators offset in muted slate.
- **Embedded Sparklines:** Glowing SVGs with `stroke-width: 2px` and gradient line strokes transitioning from Electric Cyan to Neon Violet.

### Chips & Sensor Badges
- Compact pill silhouettes with background `rgba(138, 63, 252, 0.12)`, dynamic perimeter `1px solid rgba(138, 63, 252, 0.35)`, and monospace text (`label-sm`).
- Used for orbital payload coordinates, active satellite identification numbers, and environmental status (e.g., `LEO-ALT 408KM`, `SPEC-IR ACTIVE`).

### Input Fields & Search Bars
- Recessed background `rgba(7, 10, 18, 0.6)` with inner line `1px solid rgba(255, 255, 255, 0.1)`.
- Active focus state introduces an electric cyan border `1px solid #00B4D8` and ambient glow `0 0 10px rgba(0, 180, 216, 0.25)`.
- Search triggers show monospaced shortcut badges (e.g., `⌘K`).

### Checkboxes, Switches & Radio Nodes
- **Switches:** Pill track in `rgba(255, 255, 255, 0.1)`. Active state triggers gradient illumination from Neon Violet into Electric Cyan, with a bright white thumb featuring a `0 0 8px rgba(0, 180, 216, 0.8)` corona glow.
- **Checkboxes:** Squared `0.25rem` radius boxes with cosmic magenta fill on selection, accompanied by a razor-sharp white checkmark.

### Environmental Wave & Telemetry Gauge Components
- Circular radar rings, radial dials, and velocity vectors utilizing conic gradients with neon violet and electric cyan progress sweeps.
- Center nodes display high-legibility tabular readouts of wind vector angle (`deg`), barometric pressure (`hPa`), and solar flux density.