# Hover Movement Redesign

## Problem
The original movement model had a single hover height for all non-airborne states. The intended behavior is a two-height system: low idle rest + higher glide, with the transition between them producing a small ripple.

## Movement Model

### States & Heights
| State | Height (above floor) | Entry | Exit |
|-------|---------------------|-------|------|
| **Idle** | 20u (resting) | Drop settles at idle height | WASD → Glide |
| **Glide** | 75u | WASD pressed | WASD released → Drop |
| **Drop** | 75u → 20u (falling) | Glide input stops | Reaches idle height → small ripple → Idle |
| **SlamJump** | Launch up → floor | Slam key | Hits floor → big ripple → Idle |

### Flow
1. Idle at 20u — cube rests above floor, no sound
2. WASD pressed → Glide, cube smoothly rises to 75u (~0.3s)
3. WASD released → Drop, cube falls under gravity to 20u
4. Cube reaches 20u → small Drop ripple, transition to Idle
5. Slam from any state → launch up, gravity fall to floor, big Slam ripple → rise to Idle at 20u

### Two Trace Functions
- `FindFloorBelow()` — long 500u trace, for hover height targeting
- `IsNearGround()` — short trace from box bottom, for slam landing detection

## Constants
- `IdleHoverHeight = 20`
- `GlideHoverHeight = 75`
- `HoverRiseSpeed = 15` (smooth ~0.3s rise)
- `HoverDropSpeed = 10` (slightly slower settle)

## Files Modified
- `Source/NeoNexusOne/Core/EchoTypes.h` — update hover constants
- `Source/NeoNexusOne/Player/EchoMovementComponent.h` — add new properties and state logic
- `Source/NeoNexusOne/Player/EchoMovementComponent.cpp` — implement two-height hover system
