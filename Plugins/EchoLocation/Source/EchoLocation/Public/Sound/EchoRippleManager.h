// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "Components/TimelineComponent.h"
#include "Core/EchoTypes.h"
#include "EchoRippleManager.generated.h"

class UMaterialParameterCollection;
class UCurveFloat;

/**
 * Manages the Sound-Vision ripple lifecycle.
 *
 * Owns an FTimeline that animates MPC_GlobalSound parameters (LastImpactLocation,
 * CurrentRippleRadius, RippleIntensity) when a ripple is triggered. Attach this
 * component to the GameMode actor — it acts as the global ripple authority.
 *
 * Usage:
 *   1. In Editor, create MPC_GlobalSound and set EchoMPC to point at it.
 *   2. Create float curves for radius (0→1 ease-out) and intensity (1→0 fade).
 *   3. Call TriggerRipple() from the player pawn on impact.
 */
UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class NEONEXUSONE_API UEchoRippleManager : public UActorComponent
{
	GENERATED_BODY()

public:
	UEchoRippleManager();

	virtual void BeginPlay() override;
	virtual void TickComponent(float DeltaTime, ELevelTick TickType,
		FActorComponentTickFunction* ThisTickFunction) override;

	// --- MPC Reference (set in Blueprint to MPC_GlobalSound asset) ---

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Ripple")
	TObjectPtr<UMaterialParameterCollection> EchoMPC;

	// --- Animation Curves (set in Blueprint) ---

	/** Normalized radius curve: 0→1 over the ripple duration. Multiplied by MaxRadius at runtime. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Ripple")
	TObjectPtr<UCurveFloat> RippleRadiusCurve;

	/** Intensity decay curve: 1→0 over the ripple duration. Multiplied by event Intensity. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Ripple")
	TObjectPtr<UCurveFloat> RippleIntensityCurve;

	// --- Tunable ---

	/** Total duration of the ripple expand + decay animation in seconds. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Ripple")
	float RippleDuration = 1.5f;

	// --- API ---

	/** Start a new ripple. Overwrites any currently active ripple. */
	UFUNCTION(BlueprintCallable, Category = "Echo|Ripple")
	void TriggerRipple(const FEchoRippleEvent& Event);

	UFUNCTION(BlueprintPure, Category = "Echo|Ripple")
	bool IsRippleActive() const { return bRippleActive; }

private:
	
	UPROPERTY()
	FTimeline RippleTimeline;
	FEchoRippleEvent ActiveEvent;
	bool bRippleActive = false;

	UFUNCTION()
	void OnRadiusTimelineUpdate(float Value);

	UFUNCTION()
	void OnIntensityTimelineUpdate(float Value);

	UFUNCTION()
	void OnRippleTimelineFinished();

	float CachedRadius = 0.0f;
	float CachedIntensity = 0.0f;
	bool bMPCDirty = false;

	void UpdateMPC(const FVector& Location, float Radius, float Intensity);
	void ResetMPC();
};
