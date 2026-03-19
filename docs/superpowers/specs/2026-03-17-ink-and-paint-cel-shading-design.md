# "Ink & Sonar" Cel-Shaded Visual Design

> **Supersedes:** `docs/plans/2026-03-16-living-contour-map-design.md`, `docs/plans/2026-03-17-comic-sonar-cel-shading-design.md`

## Overview

This design merges the **Ink & Paint** and **Comic Sonar** concepts into a single unified visual mode. The sonar-reveal gameplay loop is unchanged — the world is dark by default and revealed by sonar impacts. What changes is what revealed geometry *looks like*: three visual layers that replicate the feel of a hand-illustrated comic book.

The three layers, each serving a different visual scale:
1. **Ink Outlines** (macro) — dark near-black strokes on geometric edges, giving structure and "weight"
2. **Cel-Shading Bands** (mid) — discrete brightness steps based on distance from sonar impact, providing spatial lighting
3. **Halftone Dots** (micro) — triplanar-projected screentone pattern adding surface texture within each band

## Architecture

### Reveal Systems (Unchanged)

All three reveal systems remain intact:

1. **Sonar Ring Edge** — bright expanding wavefront driven by `CurrentRippleRadius` MPC
2. **Sonar Afterglow** — temporal noise dissolve behind the ring, driven by `RippleStartTime`
3. **Proximity Awareness** — faint persistent glow within `ProximityRadius` of the player

These control the `reveal_mask` (0 = dark, 1 = fully revealed). The visual layers below only affect what is shown *within* that mask.

### Layer 1: Ink Outlines

Dark near-black outlines on all geometric edges, derived from surface normal discontinuities.

- Same `fwidth(Normal)` edge detection with distance normalization (existing)
- Increased `EdgeSensitivity` default: 20 → 40 for thicker, bolder lines
- Outlines are **subtracted** from the color fill — `(1.0 - InkMask)` — producing dark ink strokes over vibrant color, like pen on paper
- HLSL (existing node, retuned):
  ```hlsl
  float3 N = normalize(Parameters.WorldNormal);
  float Edge = length(fwidth(N));
  float3 CameraPos = LWCToFloat(ResolvedView.WorldCameraOrigin);
  float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
  return saturate(Edge * (Sensitivity / (length(WorldPos - CameraPos) * 0.001 + 1.0)));
  ```
- Note: `fwidth(Normal)` is zero on flat surfaces (constant normal), so large flat walls/floors show no outlines. Outlines appear on geometric edges (corners, mesh intersections). Full silhouette outlines require the planned Milestone 2 screen-space post-process edge pass.

### Layer 2: Cel-Shading Bands

Distance from sonar impact quantized into discrete brightness steps. The sonar impact acts as the "light source".

- Distance normalized to `[0, 1]` using the static `MaxRippleRadius` parameter (default 2000)
- Quantized into 3 bands:
  - Band 1 (nearest third): 1.0 brightness
  - Band 2 (middle third): 0.667 brightness
  - Band 3 (far third): 0.333 brightness
- Custom node inputs: `ImpactLoc` (from MPC `LastImpactLocation`), `MaxRadius` (from `MaxRippleRadius` scalar param), `NumBands` (from `NumBands` scalar param), `StartTime` (from MPC `RippleStartTime`)
- HLSL:
  ```hlsl
  float3 WorldPos = LWCToFloat(GetWorldPosition(Parameters));
  float DistToImpact = length(WorldPos - ImpactLoc);
  if (StartTime <= 0.0) return 0.5;
  float DistRatio = saturate(DistToImpact / max(MaxRadius, 1.0));
  float BandIndex = min(floor(DistRatio * NumBands), NumBands - 1.0);
  return 1.0 - BandIndex / NumBands;
  ```
- Uses static `MaxRippleRadius` so band widths are fixed — geometry near the impact is always in Band 1 regardless of ring expansion progress
- When no sonar is active (`StartTime <= 0`), returns flat 0.5 tone

### Layer 3: Halftone Dots

Triplanar-projected dot pattern that simulates comic-book screentone printing. Adds surface texture within each cel-band.

- **Triplanar projection** ensures pattern stays consistent on complex geometry (no UV dependency, no swimming when objects move)
- Dot size scales dynamically with cel-band brightness:
  - Bright bands (Band 1): small/sparse dots → mostly solid color
  - Dark bands (Band 3): large/dense dots → heavy screentone shadow
- Custom node inputs: `Position` (from IsActor coordinate switch), `CelBandValue` (from cel-bands node output), `DotScale` (density param), `DotContrast` (strength param)
- HLSL:
  ```hlsl
  // Triplanar blend weights from normal
  float3 N = abs(normalize(Parameters.WorldNormal));
  N = N / (N.x + N.y + N.z + 0.001);

  // Dot pattern on each plane
  float2 uvXY = Position.xy * DotScale;
  float2 uvXZ = Position.xz * DotScale;
  float2 uvYZ = Position.yz * DotScale;

  // Circular dots via distance from cell center
  float dotXY = length(frac(uvXY) - 0.5);
  float dotXZ = length(frac(uvXZ) - 0.5);
  float dotYZ = length(frac(uvYZ) - 0.5);

  // Blend by normal direction
  float dot = dotXY * N.z + dotXZ * N.y + dotYZ * N.x;

  // Threshold scales with cel-band: darker band = larger dots (lower threshold)
  float threshold = lerp(DotMinSize, DotMaxSize, CelBandValue);
  float halftone = smoothstep(threshold - 0.02, threshold + 0.02, dot);
  return lerp(1.0, 1.0 - DotContrast, halftone);
  ```
- `DotMinSize` / `DotMaxSize` control the dynamic range of dot coverage
- `DotContrast` controls how much dots darken the surface (default 0.3 — subtle)
- The `smoothstep` provides a slight anti-aliased edge on each dot to prevent harsh pixel aliasing

### Layer Compositing

```
cel_visual = cel_bands * halftone_mask * (1.0 - ink_mask)
final = cel_visual * reveal_mask * EchoColor
```

Order of operations:
1. `cel_bands` provides the base brightness (1.0 / 0.667 / 0.333)
2. `halftone_mask` modulates within each band (0.7–1.0 range, subtle darkening from dots)
3. `(1.0 - ink_mask)` punches dark outlines on edges
4. `reveal_mask` controls what is visible at all (ring + afterglow + proximity)
5. `EchoColor` applies the per-instance vibrant color

### Color Differentiation

Per-instance `VectorParameter` **`EchoColor`** with vibrant comic book colors:

| Material Instance | Color | HDR Value | Purpose |
|---|---|---|---|
| `MI_EchoMaster` | Vibrant Blue | `(0, 200, 800)` | World geometry (walls, floors) |
| `MI_EchoObstacle` | Vivid Purple | `(400, 0, 800)` | Obstacles — distinct from walls |
| `MI_EchoEnemy` | Hot Red | `(800, 50, 0)` | Threats — immediately distinguishable |
| `MI_EchoPlayer` | Bright Green | `(0, 800, 100)` | Player cube (always visible) |
| Future objectives | Gold | `(800, 600, 0)` | Data Keys, Exit Ports |

### Proximity Rendering

Within the proximity radius, cel-bands use **player-distance** instead of impact-distance:

```hlsl
float DistToPlayer = length(WorldPos - PlayerPos);
float ProxRatio = saturate(DistToPlayer / max(ProximityRadius, 1.0));
float ProxBandIdx = min(floor(ProxRatio * NumBands), NumBands - 1.0);
float ProxBands = 1.0 - ProxBandIdx / NumBands;
```

Final cel-band value is `max(sonar_bands, proximity_bands)`. Halftone dots and ink outlines apply identically regardless of which band source is active.

### Player Rendering (IsPlayer=True)

In Comic Sonar mode (`UseFluxLook=True`), the player path renders:
- **Ink outlines** at full strength (dark edges on the cube)
- **Base fill** at 1.0 brightness — no cel-bands (no "distance to sonar" concept for the player)
- **Halftone** at minimum coverage (bright band = small dots, nearly solid)
- Combined: `1.0 * halftone_bright * (1.0 - ink_mask) * EchoColor`
- Result: a solid bright-green glowing cube with dark ink edges and minimal screentone. The player reads as the boldest, most "drawn" object in the scene.

## Temporal Behavior

1. **Ring expanding:** `ring_edge` reveals geometry at the wavefront. Behind the ring, `afterglow` is 1.0 (not yet decaying). Cel-bands shade by distance to impact. Halftone dots and ink outlines render on all revealed surfaces.
2. **Ring finished:** `ring_edge = 0`, `CurrentRippleRadius = 0`. Afterglow begins dissolving pixel-by-pixel via noise threshold. Cel-banded, halftoned, ink-outlined geometry progressively dissolves — pixels pop out crisply (no gradual dim), which suits the comic aesthetic.
3. **Full decay:** `afterglow = 0` everywhere. `reveal_mask = proximity` only. Nearby geometry shows with proximity-based cel-bands, halftone, and ink outlines.

### Rapid Successive Slams

When a new slam occurs while afterglow decays, `RippleStartTime` and `LastImpactLocation` are overwritten. Previous afterglow disappears, new expansion begins. Cel-band brightness may jump discontinuously. The noise dissolve partially masks this. Known limitation of single-active-ripple system.

## Data Flow

```
Slam Impact
  -> RippleManager expands ring via FTimeline + MPC (unchanged)
  -> Ring edge: bright band at CurrentRippleRadius (unchanged)
  -> Behind ring: afterglow noise dissolve (unchanged)
  -> reveal_mask = max(ring_edge, afterglow, proximity)  (unchanged)
  -> Layer 1: ink_mask from fwidth(Normal) (ENHANCED sensitivity)
  -> Layer 2: cel_bands from distance-to-impact quantization (NEW)
  -> Layer 3: halftone_mask from triplanar dots scaled by cel_bands (NEW)
  -> cel_visual = cel_bands * halftone_mask * (1.0 - ink_mask)
  -> Final = cel_visual * reveal_mask * EchoColor
  -> IsPlayer bypass: full brightness + ink outlines + minimal halftone
```

## MPC Parameters (Unchanged)

- `LastImpactLocation` (Vector)
- `CurrentRippleRadius` (Scalar)
- `RippleIntensity` (Scalar)
- `PlayerWorldPosition` (Vector)
- `RippleStartTime` (Scalar)

## C++ Changes

None. All changes are in the material build script and material instance setup.

## Material Changes (`M_EchoMaster`)

### Script: `13_build_blueprint_sonar_material.py`

1. **Remove** contour lines HLSL node and `ContourScale`/`ContourFlowSpeed` parameters
2. **Add** cel-shading bands HLSL node (inputs: `ImpactLoc`, `MaxRadius`, `NumBands`, `StartTime`)
3. **Add** proximity cel-bands HLSL node (inputs: `PlayerPos`, `ProximityRadius`, `NumBands`)
4. **Add** halftone dots HLSL node (inputs: `Position`, `CelBandValue`, `DotScale`, `DotContrast`, `DotMinSize`, `DotMaxSize`)
5. **Retune** edge detection — increase `EdgeSensitivity` default to 40
6. **Add** `NumBands`, `DotScale`, `DotContrast`, `DotMinSize`, `DotMaxSize` scalar parameters
7. **Change compositing** from `max(edges, contour) * reveal * color` to `cel * halftone * (1 - ink) * reveal * color`
8. `UseFluxLook` static switch branches:
   - **False (Blueprint):** Grid + edges + sonar fill mask (existing)
   - **True (Ink & Sonar):** Cel-bands + halftone + ink outlines + ring/afterglow/proximity reveal
9. **Player path** (`IsPlayer=True`, `UseFluxLook=True`): `1.0 * halftone_bright * (1.0 - ink_mask) * EchoColor`

### Script: `06_create_material.py`

- `MI_EchoMaster`: EchoColor → `(0, 200, 800)` Vibrant Blue
- `MI_EchoEnemy`: EchoColor → `(800, 50, 0)` Hot Red (unchanged)
- `MI_EchoPlayer`: EchoColor → `(0, 800, 100)` Bright Green
- New `MI_EchoObstacle`: EchoColor → `(400, 0, 800)` Vivid Purple, `IsActor=False`, `IsPlayer=False`, `UseFluxLook=True`

Note: `IsActor=False` on `MI_EchoObstacle` uses WorldPosition coordinates. Correct for static level obstacles. Movable actors should use `IsActor=True`.

## Tunable Parameters (Material Instance)

| Parameter | Type | Default | Purpose |
|---|---|---|---|
| `EchoColor` | Vector | `(0, 200, 800)` | Per-instance vibrant color |
| `EdgeSensitivity` | Scalar | `40.0` | Ink outline detection sensitivity |
| `NumBands` | Scalar | `3.0` | Number of cel-shading brightness bands |
| `DotScale` | Scalar | `0.15` | Halftone dot density (world-space) |
| `DotContrast` | Scalar | `0.3` | How much dots darken the surface (0=none, 1=full) |
| `DotMinSize` | Scalar | `0.15` | Dot threshold in bright bands (small dots) |
| `DotMaxSize` | Scalar | `0.4` | Dot threshold in dark bands (large dots) |
| `MaxRippleRadius` | Scalar | `2000.0` | Normalization range for cel-band distance |
| `SonarDecaySeconds` | Scalar | `5.0` | Afterglow duration (unchanged) |
| `ProximityRadius` | Scalar | `400.0` | Always-on glow range (unchanged) |

**Removed parameters:** `ContourScale`, `ContourFlowSpeed`

## Safety

- **`IsPlayer` bypass:** Player always fully visible with ink outlines and bright fill
- **Band count clamped:** `max(NumBands, 1.0)` prevents division by zero
- **Band index clamped:** `min(floor(...), NumBands - 1)` prevents black at exact max distance
- **Halftone anti-aliasing:** `smoothstep` on dot edges prevents harsh pixel aliasing
- **Triplanar stability:** Dots project from world/local space — no swimming on moving actors
- **No engine lighting dependency:** All shading from sonar distance, not engine lights
- **Static Switch optimization:** Blueprint mode objects incur zero cost from cel/halftone logic

## Success Criteria

- Geometry is instantly recognizable via bold dark outlines even at low sonar intensity
- The world feels "hand-drawn" and vibrant, not "digital" or "procedural"
- No visual "swimming" of halftone patterns when player or objects move
- Clearly distinguishable object types via per-instance color (blue walls, purple obstacles, red enemies, green player)
- Cel-bands provide immediate spatial readability — "near slam = bright, far = dim"
- Halftone dots add tactile printed-page quality without obscuring geometry
