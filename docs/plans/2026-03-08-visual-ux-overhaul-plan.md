# Visual UX Overhaul Implementation Plan

> **For Gemini:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implement the Player Silhouette rim-light, the Lingering Static navigation memory, and the Heartbeat proximity haptics to overhaul the game's atmosphere and UX.

**Architecture:** We will modify the core master material (`M_EchoMaster`) to support an independent player rim-light and a secondary "Memory Sphere". We will update `UEchoRippleManager` (C++) to drive the memory fading logic via a new timeline, and `AEchoPlayerController` (C++) to calculate enemy proximity for force feedback.

**Tech Stack:** Unreal Engine 5.6 (C++, Enhanced Input, Materials, Editor PIE).

---

### Task 1: Implement Player Silhouette Material

**Files:**
- Modify: `Content/EchoLocation/Materials/M_EchoMaster.uasset`
- Create: `Content/EchoLocation/Materials/MI_EchoPlayer.uasset`
- Modify: `Content/EchoLocation/Player/BP_EchoPawn.uasset`

**Step 1: Update Master Material Logic**
- Open `M_EchoMaster`.
- Add a `Fresnel` node.
- Multiply by a new Scalar Parameter `RimLightIntensity` (Default: 0).
- Multiply by a new Vector Parameter `RimLightColor` (Default: White).
- Add the result to the final Emissive Color output.
- Save and apply.

**Step 2: Create Player Material Instance**
- Right-click `M_EchoMaster` -> Create Material Instance (`MI_EchoPlayer`).
- Open `MI_EchoPlayer` and check the `RimLightIntensity` parameter, setting it to `0.5`.
- Check `RimLightColor` and set it to a pale blue `(R:0.1, G:0.5, B:1.0)`.

**Step 3: Apply to Player Pawn**
- Open `BP_EchoPawn`.
- Select the `CubeMesh` component.
- Change its material from `MI_EchoMaster` to `MI_EchoPlayer`.

**Step 4: Verify in PIE**
- Run PIE (Play In Editor). 
- Verify: The player cube should have glowing blue edges in total darkness, while the floor and walls remain black until a ripple triggers.

**Step 5: Commit**
```bash
git add Content/EchoLocation/Materials/ Content/EchoLocation/Player/
git commit -m "feat: implement player silhouette emissive material"
```

---

### Task 2: Implement Navigation Memory (C++ & Material)

**Files:**
- Modify: `Content/EchoLocation/Materials/MPC_GlobalSound.uasset`
- Modify: `Source/NeoNexusOne/Sound/EchoRippleManager.h`
- Modify: `Source/NeoNexusOne/Sound/EchoRippleManager.cpp`

**Step 1: Add MPC Parameters**
- Open `MPC_GlobalSound`.
- Add two new Scalar Parameters: `MemoryRadius` (Default: 0) and `MemoryOpacity` (Default: 0).

**Step 2: Define Memory Logic in C++ Header**
- Open `EchoRippleManager.h`.
```cpp
// Add below existing timeline properties
UPROPERTY()
FTimeline MemoryTimeline;

UPROPERTY(EditDefaultsOnly, Category = "Echo|Memory")
UCurveFloat* MemoryFadeCurve;

UFUNCTION()
void UpdateMemory(float Value);
```

**Step 3: Implement Memory Logic in C++**
- Open `EchoRippleManager.cpp`.
```cpp
// In TriggerRipple(FEchoRippleEvent Event):
// Instantly set MemoryRadius to the max radius of the event
UKismetMaterialLibrary::SetScalarParameterValue(this, MPC_GlobalSound, FName("MemoryRadius"), Event.MaxRadius);
// Start the memory fade timeline from 1.0 (full opacity)
MemoryTimeline.PlayFromStart();

// In UpdateMemory(float Value):
UKismetMaterialLibrary::SetScalarParameterValue(this, MPC_GlobalSound, FName("MemoryOpacity"), Value);

// In TickComponent:
MemoryTimeline.TickTimeline(DeltaTime);
```

**Step 4: Verify C++ Compilation**
Run: `UnrealBuildTool NeoNexusOneEditor Win64 Development -Project="D:\Users\hemal\Documents\Unreal Projects\NeoNexusOne\NeoNexusOne.uproject"`
Expected: Clean build.

**Step 5: Commit**
```bash
git add Source/NeoNexusOne/Sound/ Content/EchoLocation/Materials/MPC_GlobalSound.uasset
git commit -m "feat: implement lingering static memory logic in RippleManager"
```

---

### Task 3: Implement Heartbeat Tension Haptics

**Files:**
- Create: `Content/EchoLocation/Feedback/FFE_Heartbeat.uasset` (Force Feedback Effect)
- Modify: `Source/NeoNexusOne/Core/EchoPlayerController.h`
- Modify: `Source/NeoNexusOne/Core/EchoPlayerController.cpp`

**Step 1: Define Proximity Logic in Controller Header**
- Open `EchoPlayerController.h`.
```cpp
UPROPERTY(EditDefaultsOnly, Category = "Feedback")
UForceFeedbackEffect* HeartbeatFeedback;

UPROPERTY(EditDefaultsOnly, Category = "Feedback")
float TensionThreshold = 1500.0f;

void CheckEnemyProximity();
FTimerHandle ProximityTimerHandle;
```

**Step 2: Implement Logic in C++**
- Open `EchoPlayerController.cpp`.
```cpp
#include "Kismet/GameplayStatics.h"
#include "AI/EchoEnemyPawn.h"

// In BeginPlay:
GetWorldTimerManager().SetTimer(ProximityTimerHandle, this, &AEchoPlayerController::CheckEnemyProximity, 1.0f, true);

// In CheckEnemyProximity:
void AEchoPlayerController::CheckEnemyProximity() {
    APawn* PlayerPawn = GetPawn();
    if (!PlayerPawn || !HeartbeatFeedback) return;

    TArray<AActor*> Enemies;
    UGameplayStatics::GetAllActorsOfClass(this, AEchoEnemyPawn::StaticClass(), Enemies);
    
    for (AActor* Enemy : Enemies) {
        float Distance = FVector::Dist(PlayerPawn->GetActorLocation(), Enemy->GetActorLocation());
        if (Distance < TensionThreshold) {
            // Trigger feedback, scale intensity inversely by distance
            FForceFeedbackParameters Params;
            Params.bLooping = false;
            ClientPlayForceFeedback(HeartbeatFeedback, Params);
            break; // Just react to closest
        }
    }
}
```

**Step 3: Verify C++ Compilation**
Run: `UnrealBuildTool NeoNexusOneEditor Win64 Development -Project="D:\Users\hemal\Documents\Unreal Projects\NeoNexusOne\NeoNexusOne.uproject"`
Expected: Clean build.

**Step 4: Commit**
```bash
git add Source/NeoNexusOne/Core/
git commit -m "feat: add proximity heartbeat haptics to PlayerController"
```
