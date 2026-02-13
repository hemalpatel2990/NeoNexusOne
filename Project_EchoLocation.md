# Project: Echo-Location (Horror-Puzzle)

## 1. Project Vision
A minimalist, high-tension horror-puzzle game where **sound is your only sight**, but also your **greatest danger**. You control a cube in a pitch-black environment, using physics-based "impacts" to map out the world and avoid "Corrupted Cubes."

---

## 2. Core Mechanics

### A. Movement States
| State | Trigger | Sound Level | Visual Feedback |
| :--- | :--- | :--- | :--- |
| **Idle** | No Input | Silent | Total Darkness |
| **Glide** | Movement Input | Silent | Cube hovers/tilts; 0% visibility |
| **Drop** | Release Input | **Clunk** (Medium) | Emits a mid-range "Vision Ripple" |
| **Slam Jump** | Active Input | **Boom** (High) | Emits a room-wide "Sonar Pulse" |

### B. The "Sound-Vision" Loop
1. **Pulse:** An impact occurs (Drop or Slam).
2. **Propagate:** A mathematical "wave" expands from the impact point.
3. **Reveal:** As the wave passes over other cubes, their edges glow briefly.
4. **Decay:** The world returns to pitch black, forcing the player to move from memory.

---

## 3. Technical Roadmap (Unreal Engine 5)

### Phase 1: The Global Brain (Material Parameter Collection)
Create an `MPC_GlobalSound` to store data accessible by all objects:
* `Vector: LastImpactLocation` (XYZ coordinates of the sound source).
* `Scalar: CurrentRippleRadius` (The expanding edge of the light).
* `Scalar: RippleIntensity` (Brightness of the glow).

### Phase 2: The "Echo" Shader (Master Material)
Assign this material to every cube in the world.
* **Logic:** Use the `Distance` node between `Absolute World Position` and `LastImpactLocation`.
* **The Mask:** Use a `SphereMask` or a `SmoothStep` to create a ring effect based on `CurrentRippleRadius`.
* **Emissive:** Connect the mask to the `Emissive Color` output.

### Phase 3: Character Blueprint (The Player)
* **Floating Logic:** On `Tick`, if moving, use `VInterpTo` to raise the cube `+20 units` on the Z-axis.
* **Impact Logic:** On `OnLanded` or when movement stops, trigger a **Timeline**.
    * The Timeline will animate the `CurrentRippleRadius` from $0$ to $2000$.
    * Use `Report Noise Event` at the impact location to notify AI.

### Phase 4: Enemy AI (Corrupted Cubes)
* **Detection:** Use the `PawnSensing` or `AIPerception` component.
* **Behavior:** * If `Active Slam` is heard: Move to `LastImpactLocation`.
    * If `Passive Drop` is heard within a short radius: Move to Player Location (Chase).

---

## 4. Addictive Elements ("The Juice")
* **Camera Shake:** Subtle shake on `Drop`, violent shake on `Slam`.
* **Audio Synesthesia:** Match the "Vision Ripple" speed to the speed of the sound effect’s reverb tail.
* **Haptic Feedback:** Rumble the controller based on the intensity of the ripple passing through the player.

---

## 5. Development Milestones
1. **Milestone 1:** "The Greybox" — Cube movement + basic "Drop" vision.
2. **Milestone 2:** "The Threat" — Add AI cubes that react to the "Slam."
3. **Milestone 3:** "The Puzzle" — Create a level requiring "Blind Gliding" through obstacles.
4. **Milestone 4:** "Atmosphere" — Add 3D spatial audio and post-processing.