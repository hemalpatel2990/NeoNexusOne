// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "EchoTypes.generated.h"

/**
 * Movement states for the player cube.
 * Determines sound output and visual feedback behavior.
 */
UENUM(BlueprintType)
enum class EEchoMovementState : uint8
{
	Idle      UMETA(DisplayName = "Idle"),
	Glide     UMETA(DisplayName = "Glide"),
	Drop      UMETA(DisplayName = "Drop"),
	SlamJump  UMETA(DisplayName = "Slam Jump")
};

/**
 * AI states for Corrupted Cube enemies.
 */
UENUM(BlueprintType)
enum class EEchoAIState : uint8
{
	Idle           UMETA(DisplayName = "Idle"),
	Investigating  UMETA(DisplayName = "Investigating"),
	Returning      UMETA(DisplayName = "Returning")
};

/**
 * Data payload for a ripple event triggered by an impact.
 * Passed from the player pawn to the EchoRippleManager.
 */
USTRUCT(BlueprintType)
struct FEchoRippleEvent
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Ripple")
	FVector ImpactLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Ripple")
	float MaxRadius = 2000.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Ripple")
	float Intensity = 1.0f;

	/** Loudness value passed to MakeNoise() for AI perception. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Ripple")
	float NoiseVolume = 1.0f;
};

/**
 * Gameplay constants. Tunable defaults — Blueprint subclasses can override via UPROPERTY.
 */
namespace EchoDefaults
{
	// Movement
	constexpr float IdleHoverHeight = 20.0f;
	constexpr float GlideHoverHeight = 75.0f;
	constexpr float HoverRiseSpeed = 15.0f;
	constexpr float HoverDropSpeed = 10.0f;

	// Ripple radii
	constexpr float DropRippleRadius = 800.0f;
	constexpr float SlamRippleRadius = 2000.0f;

	// Ripple intensities
	constexpr float DropIntensity = 0.6f;
	constexpr float SlamIntensity = 1.0f;

	// AI noise volumes
	constexpr float DropNoiseVolume = 0.5f;
	constexpr float SlamNoiseVolume = 1.0f;

	// Camera
	constexpr float CameraPitchMin = -70.0f;  // Look up limit (generous for spatial awareness)
	constexpr float CameraPitchMax = 20.0f;   // Look down limit (restricted to avoid under-floor view)

	// AI behavior
	constexpr float AIMovementSpeed = 400.0f;
	constexpr float AIHearingRange = 3000.0f;
	constexpr float AIInvestigateTimeout = 5.0f;
	constexpr float AIAcceptanceRadius = 100.0f;
	constexpr float AIKillOverlapRadius = 60.0f;
}

/**
 * MPC parameter names — single source of truth to avoid string typos at runtime.
 * Must match the parameter names in MPC_GlobalSound created in-Editor.
 */
namespace EchoMPCParams
{
	inline const FName LastImpactLocation = FName(TEXT("LastImpactLocation"));
	inline const FName CurrentRippleRadius = FName(TEXT("CurrentRippleRadius"));
	inline const FName RippleIntensity = FName(TEXT("RippleIntensity"));
}
