# Camera Controls Redesign Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace right-click-to-look with standard free mouse look (always-on camera, hidden cursor, pitch clamp, tunable sensitivity).

**Architecture:** Cursor lock and pitch clamping go in `AEchoPlayerController::BeginPlay()` (controller responsibility). Mouse sensitivity property and scaled look input go in `AEchoPawn` (pawn responsibility). Editor fix removes the right-click modifier from `IMC_EchoDefault`.

**Tech Stack:** Unreal Engine 5.6 (C++, Enhanced Input, PlayerCameraManager)

---

### Task 1: Add Cursor Lock and Pitch Clamp to PlayerController

**Files:**
- Modify: `Source/NeoNexusOne/Core/EchoPlayerController.cpp`

**Step 1: Add cursor lock and pitch clamp**

Open `Source/NeoNexusOne/Core/EchoPlayerController.cpp`. The current `BeginPlay()` adds the mapping context. After that block, add cursor lock and pitch clamp:

```cpp
// Copyright NeoNexusOne. All Rights Reserved.

#include "Core/EchoPlayerController.h"
#include "EnhancedInputSubsystems.h"

void AEchoPlayerController::BeginPlay()
{
	Super::BeginPlay();

	if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
		ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(GetLocalPlayer()))
	{
		if (DefaultMappingContext)
		{
			Subsystem->AddMappingContext(DefaultMappingContext, 0);
		}
	}

	// Lock cursor for free mouse look
	FInputModeGameOnly InputMode;
	SetInputMode(InputMode);
	bShowMouseCursor = false;

	// Clamp pitch to prevent camera flipping
	if (PlayerCameraManager)
	{
		PlayerCameraManager->ViewPitchMin = -70.0f;
		PlayerCameraManager->ViewPitchMax = 20.0f;
	}
}
```

**Step 2: Verify compilation**

Close the Editor. Rebuild the solution in VS/Rider (`NeoNexusOneEditor`, Development Editor, Win64). Expected: clean build, no errors.

**Step 3: Commit**

```bash
git add Source/NeoNexusOne/Core/EchoPlayerController.cpp
git commit -m "feat: add cursor lock and pitch clamp to PlayerController"
```

---

### Task 2: Add Mouse Sensitivity to EchoPawn

**Files:**
- Modify: `Source/NeoNexusOne/Player/EchoPawn.h`
- Modify: `Source/NeoNexusOne/Player/EchoPawn.cpp`

**Step 1: Add MouseSensitivity property to header**

Open `Source/NeoNexusOne/Player/EchoPawn.h`. Add the property after the existing `IA_Slam` input action declaration (around line 66):

```cpp
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
	TObjectPtr<UInputAction> IA_Slam;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Input")
	float MouseSensitivity = 1.0f;
```

**Step 2: Modify HandleLook to use sensitivity**

Open `Source/NeoNexusOne/Player/EchoPawn.cpp`. Change `HandleLook()` (around line 103) from:

```cpp
void AEchoPawn::HandleLook(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();
	AddControllerYawInput(Input.X);
	AddControllerPitchInput(Input.Y);
}
```

To:

```cpp
void AEchoPawn::HandleLook(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();
	AddControllerYawInput(Input.X * MouseSensitivity);
	AddControllerPitchInput(Input.Y * MouseSensitivity);
}
```

**Step 3: Verify compilation**

Close the Editor. Rebuild the solution in VS/Rider. Expected: clean build, no errors.

**Step 4: Commit**

```bash
git add Source/NeoNexusOne/Player/EchoPawn.h Source/NeoNexusOne/Player/EchoPawn.cpp
git commit -m "feat: add tunable mouse sensitivity to EchoPawn"
```

---

### Task 3: Fix Input Mapping Context in Editor (Manual)

**Files:**
- Modify: `Content/EchoLocation/Input/IMC_EchoDefault.uasset` (Editor only)

**Step 1: Open the Editor**

Launch the project via `NeoNexusOne.uproject`.

**Step 2: Edit IMC_EchoDefault**

1. In Content Browser, navigate to `Content/EchoLocation/Input/`
2. Double-click `IMC_EchoDefault` to open the Input Mapping Context editor
3. Find the `IA_Look` mapping row
4. Look at its **Modifiers** and **Triggers** columns
5. **Remove any right-click condition** — this may appear as:
   - A `Chorded Action` trigger referencing a right-mouse-button action
   - A custom trigger/modifier requiring mouse button hold
6. The `IA_Look` mapping should end up as: **Mouse XY → IA_Look** with no modifiers or triggers (or only a `Negate` modifier on the Y axis if pitch inversion was set up)
7. Save the asset

**Step 3: PIE Test**

1. Press Play (PIE)
2. Verify: mouse immediately controls camera rotation without any clicking
3. Verify: WASD moves the cube relative to camera facing direction
4. Verify: looking down stops at ~-70 degrees, looking up stops at ~+20 degrees
5. Verify: cursor is not visible during gameplay
6. Verify: Space still triggers Slam Jump
7. If sensitivity feels too fast or slow, adjust `MouseSensitivity` on `BP_EchoPawn` Details panel

**Step 4: Commit**

```bash
git add Content/EchoLocation/Input/IMC_EchoDefault.uasset
git commit -m "fix: remove right-click modifier from IA_Look for free mouse look"
```
