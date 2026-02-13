# GEMINI.md - NeoNexusOne: Echo-Location

## Project Overview
**NeoNexusOne** is the repository for **Project: Echo-Location**, a minimalist, high-tension horror-puzzle game developed in **Unreal Engine 5**. 

The core concept is "Sound-Vision": the player is in total darkness and must create physical impacts (sound) to generate "Vision Ripples" that briefly reveal the environment. However, sound also attracts "Corrupted Cubes" (enemies), creating a risk-reward loop between visibility and safety.

### Main Technologies
*   **Engine:** Unreal Engine 5
*   **Visuals:** Custom "Echo" Shaders using Material Parameter Collections (MPC) and SphereMasks.
*   **AI:** AI Perception / Pawn Sensing reacting to `Report Noise Event`.
*   **Audio:** 3D Spatial Audio and Audio Synesthesia (visuals matched to audio decay).

---

## Project Structure
*   `NeoNexusOne.uproject`: The Unreal Engine 5 project descriptor file.
*   `Source/`: Contains the C++ source code for the game, including the `NeoNexusOne` module.
*   `Project_EchoLocation.md`: Detailed design document covering mechanics, technical roadmap, and milestones.
*   `.gitignore`: Configured for Unreal Engine 5 development (ignores `Intermediate/`, `Saved/`, `Binaries/`, `.vs/`, etc.).
*   `README.md`: Basic project introduction.

---

## Building and Running
As an Unreal Engine 5 project, the following workflows are standard:

*   **Editor:** Open the `.uproject` file (to be created/located in the root) in Unreal Engine 5.
*   **Build:** Use the Unreal Build Tool (UBT) or compile directly from within the Editor / Visual Studio.
*   **Test:** Use the "Play In Editor" (PIE) mode for functional testing of mechanics and AI.
*   **TODO:** Define specific CI/CD build commands if automated packaging is required.

---

## Development Conventions

### 1. Sound-Vision Loop
All interactive objects should adhere to the "Echo" Shader logic:
*   Use `MPC_GlobalSound` for `LastImpactLocation` and `CurrentRippleRadius`.
*   Materials should implement the `SphereMask` logic to respond to global sound pulses.

### 2. Movement & Physics
*   **Glide:** Silent movement (no vision).
*   **Drop/Slam:** Physics-based impacts that trigger vision ripples and notify AI.

### 3. AI Behavior
*   Enemies react to noise events.
*   **Active Slam:** High priority, moves AI to the source.
*   **Passive Drop:** Low priority, initiates a local chase if close.

### 4. Aesthetic Standards
*   Maintain a minimalist "Greybox" aesthetic initially.
*   Focus on "The Juice": Camera shakes, haptic feedback, and synced audio-visual decay.
