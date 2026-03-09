# Visual Aesthetics & Polish Design

## Section 1: The "Dual-Tone" Sonar Contrast
*   **The Environment:** We adopt the **Vector Sonar** look for the world. We update the Master Material so the Vision Ripple reveals sharp, glowing contour lines and a scanning grid (e.g., in cool Cyan or Mint Green). The architecture looks like a precise digital topographic map being actively scanned.
*   **The Threat:** We use the **Deep Sea / Organic** approach exclusively for the Corrupted Cubes. Their material uses panning 3D noise so that when the ripple hits them, they render as swirling, glitching, deep-red/magenta fluid. This creates an immediate, terrifying visual distinction between "safe floor" and "deadly enemy."

## Section 2: Post-Processing (The "Panicking Camera")
To completely eliminate the "default Unreal Engine" feel, we will configure a Global Post-Process Volume to act like a physical, flawed camera lens.
*   **Claustrophobia:** We apply a heavy, hard-edged Vignette and thick Film Grain. The darkness shouldn't just be the absence of light; it should look like thick static.
*   **Proximity Distortion:** We tie the Post-Process settings to the "Heartbeat" proximity system we designed earlier. As a Corrupted Cube gets closer, the screen's **Chromatic Aberration** and **Lens Distortion** (fisheye) ramp up. The visual field literally begins to fracture and tear apart the closer you are to death.
