# Status: NeoNexusOne — Echo-Location

## Current Milestone
**Milestone 2: "The Threat" — IN PROGRESS**
*Goal: Implement enemy AI (Corrupted Cubes) reacting to player-generated noise.*

---

## Roadmap

### Milestone 1: "The Greybox" — **COMPLETE**
*   [x] Basic cube movement state machine (Idle, Glide, Drop, SlamJump).
*   [x] Timeline-driven Vision Ripple system via MPC.
*   [x] Enhanced Input integration (Move, Look, Slam).
*   [x] Sound-Vision feedback (Camera shakes + haptics).
*   [x] Core C++ foundation (GameMode, PlayerController, Pawn).

### Milestone 2: "The Threat" — **IN PROGRESS**
*   [ ] `AEchoEnemyPawn`: AI cube with navigation and kill logic.
*   [ ] `AEchoAIController`: Perception-driven state machine (Idle/Investigating/Returning).
*   [ ] Navigation Mesh setup in `L_EchoPrototype`.
*   [ ] Noise prioritization (Slam > Drop).

### Milestone 3: "The Puzzle" — **PLANNED**
*   [ ] Glide-only navigation through dark obstacles.
*   [ ] Level hazards and puzzle triggers.
*   [ ] Movement-based vision persistence tuning.

### Milestone 4: "Atmosphere" — **PLANNED**
*   [ ] 3D spatial audio (reverb/echo matching ripple size).
*   [ ] Post-processing effects (vignette/distortion).
*   [ ] Visual polish (Corrupted Cube aesthetic).

---

## Technical Health
*   **Engine:** Unreal Engine 5.6
*   **Build Status:** Clean (Milestone 1 verified)
*   **Last Review:** `reviews/Code-Review.md` (Consulted and synced)
*   **Pending Tasks:** AI implementation starts next.
