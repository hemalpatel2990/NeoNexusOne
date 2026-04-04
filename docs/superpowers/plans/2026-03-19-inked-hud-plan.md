# Inked HUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the "Inked HUD" — a minimalist, data-focused digital overlay with dynamic signal decay and proximity interference. Mapping progress is included as a placeholder (real zone logic deferred to Milestone 3).

**Architecture:**
- `AEchoPlayerController` manages state (`CurrentSignal`, `ProximityIntensity`, `MappingProgress`) and updates `MPC_GlobalSound` every Tick.
- `AEchoPawn::OnImpact()` calls `ResetSignal()` on the controller.
- `UEchoHUDWidget` (C++ base class with `BindWidget` slots) drives the widget; `WBP_InkedHUD` is a Blueprint child created manually in Editor.
- Static Interference is a post-process scanline material driven by `ProximityInterference` MPC parameter.

**Tech Stack:** Unreal Engine 5.6 C++, UMG, Material Parameter Collections.

**UI Spec Reference:** `docs/plans/2026-03-08-hacker-view-hud-design.md`
- **Signal Strength (Top Left):** Sharp, glowing cyan progress bar. 100% on impact, decays to 0% over 5 seconds (synced to Vision Ripple). Pulsing icon on impact.
- **Mapping Progress (Top Right):** Digital percentage counter (`MAPPING: --.--%`). Placeholder until Milestone 3.
- **Static Interference (Fullscreen):** Faint flickering scanlines. Intensity increases with Corrupted Cube proximity.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `Scripts/EditorUtility/helpers.py` | Modify | Add new MPC parameter constants. |
| `Scripts/EditorUtility/01_create_mpc.py` | Modify | Rebuild MPC with new HUD and Proximity parameters. |
| `Source/NeoNexusOne/Public/Core/EchoTypes.h` | Modify | Add MPC param names + HUD defaults. |
| `Source/NeoNexusOne/Public/Core/EchoPlayerController.h` | Modify | Define HUD state variables and update functions. |
| `Source/NeoNexusOne/Private/Core/EchoPlayerController.cpp` | Modify | Implement signal decay, proximity tracking, HUD creation, and MPC updates. |
| `Source/NeoNexusOne/Public/UI/EchoHUDWidget.h` | Create | C++ UUserWidget base with BindWidget slots. |
| `Source/NeoNexusOne/Private/UI/EchoHUDWidget.cpp` | Create | Widget update functions. |
| `Source/NeoNexusOne/Private/Player/EchoPawn.cpp` | Modify | Call `ResetSignal()` on sound impacts. |
| `Source/NeoNexusOne/NeoNexusOne.Build.cs` | Modify | Add UMG module dependency. |
| `WBP_InkedHUD` (Asset) | Create (Manual) | The UMG widget Blueprint child of UEchoHUDWidget. |
| `M_EchoInterference` (Asset) | Create (Manual) | Post-process scanline material. |

---

### Task 1: Update Global MPC Parameters

**Files:**
- Modify: `Scripts/EditorUtility/helpers.py`
- Modify: `Scripts/EditorUtility/01_create_mpc.py`
- Modify: `Source/NeoNexusOne/Public/Core/EchoTypes.h`

- [ ] **Step 1: Update helpers.py**
Add to `MPCParams` class:
```python
    PROXIMITY_INTERFERENCE   = "ProximityInterference"
    SIGNAL_INTENSITY         = "SignalIntensity"
```

- [ ] **Step 2: Update 01_create_mpc.py**
In the `run()` function, under `scalar_params = [`, add:
```python
        make_scalar(MPCParams.PROXIMITY_INTERFERENCE),
        make_scalar(MPCParams.SIGNAL_INTENSITY),
```

- [ ] **Step 3: Update EchoTypes.h**
Add to the `EchoMPCParams` namespace:
```cpp
    inline const FName ProximityInterference = FName(TEXT("ProximityInterference"));
    inline const FName SignalIntensity = FName(TEXT("SignalIntensity"));
```

Add to the `EchoDefaults` namespace:
```cpp
    // HUD
    constexpr float SignalDecayDuration = 5.0f;   // Seconds for signal to decay from 1→0
    constexpr float MaxProximityRange = 1500.0f;   // Distance at which interference starts
```

- [ ] **Step 4: Run the MPC script in Editor**
Run: `$env:UNREAL_PROJECT="NeoNexusOne.uproject"; python Scripts/EditorUtility/00_run_all.py`
Expected: Rebuilds `MPC_GlobalSound` with new `ProximityInterference` and `SignalIntensity` parameters.

- [ ] **Step 5: Commit**
```bash
git add Scripts/EditorUtility/helpers.py Scripts/EditorUtility/01_create_mpc.py Source/NeoNexusOne/Public/Core/EchoTypes.h
git commit -m "feat(materials): add proximity and signal intensity MPC parameters and defaults"
```

---

### Task 2: Add UMG Module Dependency

**Files:**
- Modify: `Source/NeoNexusOne/NeoNexusOne.Build.cs`

- [ ] **Step 1: Add UMG to PrivateDependencyModuleNames**
Uncomment the existing Slate line and add UMG:
```csharp
PrivateDependencyModuleNames.AddRange(new string[] {
    "AIModule",
    "GameplayTasks",
    "NavigationSystem",
    "Slate",
    "SlateCore",
    "UMG"
});
```

- [ ] **Step 2: Commit**
```bash
git add Source/NeoNexusOne/NeoNexusOne.Build.cs
git commit -m "build: add Slate and UMG module dependencies for HUD widget"
```

---

### Task 3: Create UEchoHUDWidget Base Class

**Files:**
- Create: `Source/NeoNexusOne/Public/UI/EchoHUDWidget.h`
- Create: `Source/NeoNexusOne/Private/UI/EchoHUDWidget.cpp`

- [ ] **Step 1: Header File**
Create `EchoHUDWidget.h`:
```cpp
// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "EchoHUDWidget.generated.h"

class UProgressBar;
class UTextBlock;

/**
 * C++ base for the Inked HUD widget.
 * Blueprint child (WBP_InkedHUD) provides layout; this class binds to named slots.
 *
 * UI Spec: Signal Strength (top-left cyan bar), Mapping Progress (top-right counter),
 * pulsing impact indicator.
 */
UCLASS(Abstract)
class NEONEXUSONE_API UEchoHUDWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    /** Update signal strength bar (0-1 normalized). */
    UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
    void UpdateSignal(float NormalizedSignal);

    /** Update mapping progress text. Pass negative to show placeholder. */
    UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
    void UpdateMapping(float Percent);

    /** Flash the pulse indicator on impact. */
    UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
    void TriggerPulse();

protected:
    /** Sharp, glowing cyan progress bar — top left. */
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UProgressBar> SignalBar;

    /** Digital percentage counter — top right. e.g. "MAPPING: 45.2%" */
    UPROPERTY(meta = (BindWidget))
    TObjectPtr<UTextBlock> MappingText;

    /** Small pulsing icon that flashes on sound impact. */
    UPROPERTY(meta = (BindWidgetOptional))
    TObjectPtr<UWidget> PulseIndicator;

    /** Blueprint-implementable event for pulse animation. */
    UFUNCTION(BlueprintImplementableEvent, Category = "Echo|HUD")
    void OnPulseTriggered();
};
```

- [ ] **Step 2: CPP File**
Create `EchoHUDWidget.cpp`:
```cpp
// Copyright NeoNexusOne. All Rights Reserved.

#include "UI/EchoHUDWidget.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoHUD, Log, All);

void UEchoHUDWidget::UpdateSignal(float NormalizedSignal)
{
    if (SignalBar)
    {
        SignalBar->SetPercent(NormalizedSignal);
    }
}

void UEchoHUDWidget::UpdateMapping(float Percent)
{
    if (MappingText)
    {
        if (Percent < 0.0f)
        {
            MappingText->SetText(FText::FromString(TEXT("MAPPING: --.--%")));
        }
        else
        {
            MappingText->SetText(FText::FromString(
                FString::Printf(TEXT("MAPPING: %.1f%%"), Percent)));
        }
    }
}

void UEchoHUDWidget::TriggerPulse()
{
    OnPulseTriggered();
}
```

- [ ] **Step 3: Compile**
Close Editor. Rebuild solution in VS/Rider. Verify DLL timestamp.

- [ ] **Step 4: Commit**
```bash
git add Source/NeoNexusOne/Public/UI/EchoHUDWidget.h Source/NeoNexusOne/Private/UI/EchoHUDWidget.cpp
git commit -m "feat(ui): add UEchoHUDWidget base class with BindWidget slots"
```

---

### Task 4: PlayerController — State & Tick Logic

**Files:**
- Modify: `Source/NeoNexusOne/Public/Core/EchoPlayerController.h`
- Modify: `Source/NeoNexusOne/Private/Core/EchoPlayerController.cpp`

- [ ] **Step 1: Update Header**
Add includes, forward declarations, and members:
```cpp
#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "EchoPlayerController.generated.h"

class UInputMappingContext;
class UEchoHUDWidget;
class UMaterialParameterCollection;

UCLASS()
class NEONEXUSONE_API AEchoPlayerController : public APlayerController
{
    GENERATED_BODY()

public:
    /** Called by EchoPawn on impact — resets signal to 1.0 and triggers HUD pulse. */
    UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
    void ResetSignal();

protected:
    virtual void BeginPlay() override;
    virtual void PlayerTick(float DeltaTime) override;

    /** Input Mapping Context to add on BeginPlay. Set in BP to IMC_EchoDefault. */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    // --- HUD ---

    /** Widget class to spawn. Set in BP to WBP_InkedHUD. */
    UPROPERTY(EditDefaultsOnly, Category = "Echo|HUD")
    TSubclassOf<UEchoHUDWidget> HUDWidgetClass;

    /** Current signal strength (0-1). 1.0 on impact, decays over SignalDecayDuration. */
    UPROPERTY(BlueprintReadOnly, Category = "Echo|HUD")
    float CurrentSignal = 0.0f;

    /** Mapping progress percentage. Placeholder until Milestone 3. */
    UPROPERTY(BlueprintReadOnly, Category = "Echo|HUD")
    float MappingProgress = -1.0f;

    /** Enemy proximity intensity (0-1). 0 = no enemies nearby, 1 = enemy at point-blank. */
    UPROPERTY(BlueprintReadOnly, Category = "Echo|HUD")
    float ProximityIntensity = 0.0f;

private:
    UPROPERTY()
    TObjectPtr<UEchoHUDWidget> HUDWidget;

    UPROPERTY()
    TObjectPtr<UMaterialParameterCollection> GlobalSoundMPC;
};
```

- [ ] **Step 2: Update CPP — Full Implementation**
```cpp
// Copyright NeoNexusOne. All Rights Reserved.

#include "Core/EchoPlayerController.h"
#include "Core/EchoTypes.h"
#include "UI/EchoHUDWidget.h"
#include "EnhancedInputSubsystems.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "AI/EchoEnemyPawn.h"
#include "EngineUtils.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoPC, Log, All);

void AEchoPlayerController::BeginPlay()
{
    Super::BeginPlay();

    // Enhanced Input setup
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
        PlayerCameraManager->ViewPitchMin = EchoDefaults::CameraPitchMin;
        PlayerCameraManager->ViewPitchMax = EchoDefaults::CameraPitchMax;
    }

    // Load MPC reference
    GlobalSoundMPC = LoadObject<UMaterialParameterCollection>(nullptr,
        TEXT("/Game/EchoLocation/Materials/MPC_GlobalSound.MPC_GlobalSound"));

    // Create and display HUD widget
    if (HUDWidgetClass && IsLocalController())
    {
        HUDWidget = CreateWidget<UEchoHUDWidget>(this, HUDWidgetClass);
        if (HUDWidget)
        {
            HUDWidget->AddToViewport();
            HUDWidget->UpdateMapping(MappingProgress); // Show placeholder
        }
    }
}

void AEchoPlayerController::PlayerTick(float DeltaTime)
{
    Super::PlayerTick(DeltaTime);

    // --- Signal Decay ---
    if (CurrentSignal > 0.0f)
    {
        CurrentSignal = FMath::Max(0.0f,
            CurrentSignal - (DeltaTime / EchoDefaults::SignalDecayDuration));
    }

    // --- Enemy Proximity ---
    float ClosestDistSq = FMath::Square(EchoDefaults::MaxProximityRange + 1.0f);
    if (APawn* MyPawn = GetPawn())
    {
        const FVector MyLoc = MyPawn->GetActorLocation();
        for (TActorIterator<AEchoEnemyPawn> It(GetWorld()); It; ++It)
        {
            const float DistSq = FVector::DistSquared(MyLoc, It->GetActorLocation());
            if (DistSq < ClosestDistSq)
            {
                ClosestDistSq = DistSq;
            }
        }
    }
    const float ActualDist = FMath::Sqrt(ClosestDistSq);
    ProximityIntensity = FMath::Clamp(
        1.0f - (ActualDist / EchoDefaults::MaxProximityRange), 0.0f, 1.0f);

    // --- Update MPC for post-process interference material ---
    if (GlobalSoundMPC)
    {
        UKismetMaterialLibrary::SetScalarParameterValue(
            GetWorld(), GlobalSoundMPC,
            EchoMPCParams::SignalIntensity, CurrentSignal);
        UKismetMaterialLibrary::SetScalarParameterValue(
            GetWorld(), GlobalSoundMPC,
            EchoMPCParams::ProximityInterference, ProximityIntensity);
    }

    // --- Update HUD Widget ---
    if (HUDWidget)
    {
        HUDWidget->UpdateSignal(CurrentSignal);
    }
}

void AEchoPlayerController::ResetSignal()
{
    CurrentSignal = 1.0f;
    if (HUDWidget)
    {
        HUDWidget->TriggerPulse();
    }
}
```

- [ ] **Step 3: Compile**
Close Editor. Rebuild solution. Verify DLL timestamp.

- [ ] **Step 4: Commit**
```bash
git add Source/NeoNexusOne/Public/Core/EchoPlayerController.h Source/NeoNexusOne/Private/Core/EchoPlayerController.cpp
git commit -m "feat(player): implement signal decay, proximity tracking, and HUD widget management"
```

---

### Task 5: Trigger Signal Reset from Pawn

**Files:**
- Modify: `Source/NeoNexusOne/Private/Player/EchoPawn.cpp`

- [ ] **Step 1: Add include**
At the top of `EchoPawn.cpp`:
```cpp
#include "Core/EchoPlayerController.h"
```

- [ ] **Step 2: Add ResetSignal call in OnImpact**
In `AEchoPawn::OnImpact()`, after the `MakeNoise()` call (line ~178), add:
```cpp
    // Reset HUD signal strength
    if (AEchoPlayerController* EchoPC = Cast<AEchoPlayerController>(GetController()))
    {
        EchoPC->ResetSignal();
    }
```

- [ ] **Step 3: Compile and verify**
Close Editor. Rebuild solution.

- [ ] **Step 4: Commit**
```bash
git add Source/NeoNexusOne/Private/Player/EchoPawn.cpp
git commit -m "feat(player): trigger HUD signal reset on pawn impact"
```

---

### Task 6: WBP_InkedHUD Widget Blueprint (Manual Editor Steps)

**Files:**
- Create: `WBP_InkedHUD` (Editor asset, child of UEchoHUDWidget)

- [ ] **Step 1: Create Widget Blueprint**
1. Content Browser → `Content/EchoLocation/UI/`
2. Right-click → User Interface → Widget Blueprint
3. Name it `WBP_InkedHUD`
4. In the Class Settings, set Parent Class to `EchoHUDWidget`

- [ ] **Step 2: Layout the Signal Strength bar (Top Left)**
1. Add a `CanvasPanel` as root
2. Add a `ProgressBar` named exactly **`SignalBar`** (must match BindWidget)
3. Anchor: Top-Left. Position: ~(20, 20). Size: ~(250, 12)
4. Style: Fill color = Cyan (0, 1, 1, 1), Background = near-black (0.02, 0.02, 0.05, 0.8)
5. Percent: leave at 0 (driven by C++)

- [ ] **Step 3: Add Pulse Indicator**
1. Add an `Image` widget named **`PulseIndicator`** next to the signal bar
2. Anchor: Top-Left. Position: ~(280, 16). Size: ~(16, 16)
3. Tint: Cyan. Set initial Render Opacity to 0
4. In Event Graph: implement `OnPulseTriggered` → play a Widget animation that sets opacity to 1.0 then fades to 0 over 0.3s

- [ ] **Step 4: Layout Mapping Progress (Top Right)**
1. Add a `TextBlock` named exactly **`MappingText`**
2. Anchor: Top-Right. Position: ~(-200, 20). Size: auto
3. Font: Roboto Mono or similar monospace, size 14
4. Color: Cyan (0, 1, 1, 0.8)
5. Default text: `MAPPING: --.--%`

- [ ] **Step 5: Set HUDWidgetClass on PlayerController BP**
1. Open `BP_EchoPlayerController`
2. In Details → Echo|HUD → set `HUD Widget Class` to `WBP_InkedHUD`

---

### Task 7: Post-Process Interference Material (Manual Editor Steps)

**Files:**
- Create: `M_EchoInterference` post-process material (Editor asset)

- [ ] **Step 1: Create Material**
1. Content Browser → `Content/EchoLocation/Materials/`
2. Create new Material → `M_EchoInterference`
3. Material Domain: **Post Process**
4. Blendable Location: After Tonemapping

- [ ] **Step 2: Build Scanline Graph**
The material creates horizontal flickering scanlines:
1. **ScreenPosition** node → break into components
2. Multiply Y by a high frequency (~200) → add **Time** node (for flicker)
3. Feed into **Sine** → **Abs** → this creates horizontal scanlines
4. **MPC_GlobalSound** → `ProximityInterference` scalar parameter
5. Multiply scanline pattern by `ProximityInterference` (0 = invisible, 1 = heavy)
6. Output: Lerp between Scene Color (alpha=0, no interference) and a slightly offset/noisy Scene Color, blended by the scanline × proximity value
7. Connect to **Emissive Color** output

- [ ] **Step 3: Add to PostProcessVolume**
1. In `L_EchoPrototype`, select the existing PostProcessVolume
2. Under Rendering Features → Post Process Materials → add `M_EchoInterference`

- [ ] **Step 4: Test**
In PIE, verify:
- With no enemies: screen is clean (no scanlines)
- Place a `BP_EchoEnemyPawn` nearby: scanlines should appear and intensify as it approaches
