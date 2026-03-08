// Copyright NeoNexusOne. All Rights Reserved.

#include "Sound/EchoRippleManager.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "Materials/MaterialParameterCollection.h"
#include "Curves/CurveFloat.h"

UEchoRippleManager::UEchoRippleManager()
{
	PrimaryComponentTick.bCanEverTick = true;
	PrimaryComponentTick.bStartWithTickEnabled = false;
}

void UEchoRippleManager::BeginPlay()
{
	Super::BeginPlay();

	if (!EchoMPC)
	{
		UE_LOG(LogTemp, Error, TEXT("EchoRippleManager: EchoMPC is null! Ripples will not be visible."));
	}

	if (RippleRadiusCurve)
	{
		// Bind the radius curve to its own callback — sampled by normalized time
		FOnTimelineFloat RadiusCallback;
		RadiusCallback.BindUFunction(this, FName("OnRadiusTimelineUpdate"));
		RippleTimeline.AddInterpFloat(RippleRadiusCurve, RadiusCallback);
	}
	else
	{
		UE_LOG(LogTemp, Warning, TEXT("EchoRippleManager: RippleRadiusCurve is not set! Ripples will not animate."));
	}

	if (RippleIntensityCurve)
	{
		// Bind the intensity curve to its own callback — sampled by normalized time independently
		FOnTimelineFloat IntensityCallback;
		IntensityCallback.BindUFunction(this, FName("OnIntensityTimelineUpdate"));
		RippleTimeline.AddInterpFloat(RippleIntensityCurve, IntensityCallback);
	}

	{
		// Bind the finished callback
		FOnTimelineEvent FinishCallback;
		FinishCallback.BindUFunction(this, FName("OnRippleTimelineFinished"));
		RippleTimeline.SetTimelineFinishedFunc(FinishCallback);

		RippleTimeline.SetLooping(false);
	}

	// Ensure MPC starts clean
	ResetMPC();
}

void UEchoRippleManager::TickComponent(float DeltaTime, ELevelTick TickType,
	FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// FTimeline requires manual ticking — this is the C++ equivalent of Blueprint Timeline auto-tick
	RippleTimeline.TickTimeline(DeltaTime);
}

void UEchoRippleManager::TriggerRipple(const FEchoRippleEvent& Event)
{
	ActiveEvent = Event;
	bRippleActive = true;
	CachedRadius = 0.0f;
	CachedIntensity = Event.Intensity;
	SetComponentTickEnabled(true);

	// Set the impact location immediately so the material knows where to center the ring
	UpdateMPC(Event.ImpactLocation, 0.0f, Event.Intensity);

	// Use play rate to map normalized 0→1 timeline to the desired duration
	RippleTimeline.SetPlayRate(1.0f / FMath::Max(RippleDuration, KINDA_SMALL_NUMBER));
	RippleTimeline.PlayFromStart();
}

void UEchoRippleManager::OnRadiusTimelineUpdate(float Value)
{
	// Value is the curve output (0→1) sampled at the current normalized time
	CachedRadius = Value * ActiveEvent.MaxRadius;
	UpdateMPC(ActiveEvent.ImpactLocation, CachedRadius, CachedIntensity);
}

void UEchoRippleManager::OnIntensityTimelineUpdate(float Value)
{
	// Value is the curve output (1→0) sampled at the current normalized time — independent of radius
	CachedIntensity = Value * ActiveEvent.Intensity;
	UpdateMPC(ActiveEvent.ImpactLocation, CachedRadius, CachedIntensity);
}

void UEchoRippleManager::OnRippleTimelineFinished()
{
	bRippleActive = false;
	CachedRadius = 0.0f;
	CachedIntensity = 0.0f;
	SetComponentTickEnabled(false);
	ResetMPC();
}

void UEchoRippleManager::UpdateMPC(const FVector& Location, float Radius, float Intensity)
{
	if (!EchoMPC)
	{
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	// MPC vectors are passed as FLinearColor (XYZW) — pack our FVector into RGB, W unused
	UKismetMaterialLibrary::SetVectorParameterValue(
		World, EchoMPC, EchoMPCParams::LastImpactLocation,
		FLinearColor(Location.X, Location.Y, Location.Z, 0.0f));

	UKismetMaterialLibrary::SetScalarParameterValue(
		World, EchoMPC, EchoMPCParams::CurrentRippleRadius, Radius);

	UKismetMaterialLibrary::SetScalarParameterValue(
		World, EchoMPC, EchoMPCParams::RippleIntensity, Intensity);
}

void UEchoRippleManager::ResetMPC()
{
	UpdateMPC(FVector::ZeroVector, 0.0f, 0.0f);
}
