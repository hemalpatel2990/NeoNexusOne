// Copyright NeoNexusOne. All Rights Reserved.

#include "AI/EchoAIController.h"
#include "Perception/AIPerceptionComponent.h"
#include "Perception/AISenseConfig_Hearing.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoAI, Log, All);

AEchoAIController::AEchoAIController()
{
	PrimaryActorTick.bCanEverTick = true;

	AIPerceptionComp = CreateDefaultSubobject<UAIPerceptionComponent>(TEXT("AIPerception"));
	SetPerceptionComponent(*AIPerceptionComp);

	HearingConfig = CreateDefaultSubobject<UAISenseConfig_Hearing>(TEXT("HearingConfig"));
	HearingConfig->HearingRange = EchoDefaults::AIHearingRange;
	HearingConfig->DetectionByAffiliation.bDetectEnemies = true;
	HearingConfig->DetectionByAffiliation.bDetectFriendlies = true;
	HearingConfig->DetectionByAffiliation.bDetectNeutrals = true;

	AIPerceptionComp->ConfigureSense(*HearingConfig);
	AIPerceptionComp->SetDominantSense(UAISense_Hearing::StaticClass());
}

void AEchoAIController::BeginPlay()
{
	Super::BeginPlay();

	if (GetPawn())
	{
		SpawnLocation = GetPawn()->GetActorLocation();
	}

	AIPerceptionComp->OnTargetPerceptionUpdated.AddDynamic(this, &AEchoAIController::OnPerceptionUpdated);

	UE_LOG(LogEchoAI, Verbose, TEXT("AIController BeginPlay: Pawn=%s Perception=%s HearingRange=%.0f"),
		GetPawn() ? *GetPawn()->GetName() : TEXT("NONE"),
		AIPerceptionComp ? TEXT("VALID") : TEXT("NULL"),
		HearingConfig ? HearingConfig->HearingRange : -1.0f);
}

void AEchoAIController::OnPerceptionUpdated(AActor* Actor, FAIStimulus Stimulus)
{
	UE_LOG(LogEchoAI, Verbose, TEXT("OnPerceptionUpdated: Actor=%s Sensed=%d Strength=%.2f Location=(%s)"),
		Actor ? *Actor->GetName() : TEXT("NULL"),
		Stimulus.WasSuccessfullySensed() ? 1 : 0,
		Stimulus.Strength,
		*Stimulus.StimulusLocation.ToString());

	if (!Stimulus.WasSuccessfullySensed())
	{
		return;
	}

	const float Strength = Stimulus.Strength;

	UE_LOG(LogEchoAI, Verbose, TEXT("  Strength=%.4f SlamThreshold=%.4f State=%d"),
		Strength, EchoDefaults::SlamNoiseVolume, static_cast<int32>(CurrentState));

	// Slam (strength ~1.0): always investigate
	// Drop (strength ~0.5): only if Idle and within Drop radius
	if (Strength >= EchoDefaults::SlamNoiseVolume)
	{
		UE_LOG(LogEchoAI, Verbose, TEXT("  -> SLAM detected, investigating"));
		InvestigateLocation(Stimulus.StimulusLocation);
	}
	else if (CurrentState == EEchoAIState::Idle)
	{
		const float Distance = FVector::Dist(GetPawn()->GetActorLocation(), Stimulus.StimulusLocation);
		UE_LOG(LogEchoAI, Verbose, TEXT("  -> DROP: Distance=%.1f DropRadius=%.1f"), Distance, EchoDefaults::DropRippleRadius);
		if (Distance <= EchoDefaults::DropRippleRadius)
		{
			InvestigateLocation(Stimulus.StimulusLocation);
		}
	}
	else
	{
		UE_LOG(LogEchoAI, Verbose, TEXT("  -> Ignored (State=%d, not Idle)"), static_cast<int32>(CurrentState));
	}
}

void AEchoAIController::InvestigateLocation(const FVector& Location)
{
	CurrentState = EEchoAIState::Investigating;
	LingerTimer = 0.0f;
	TargetLocation = Location;

	UE_LOG(LogEchoAI, Verbose, TEXT("InvestigateLocation: Target=(%s)"),
		*Location.ToString());
}

void AEchoAIController::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (!GetPawn()) { return; }
	const float DistToTarget = FVector::Dist(GetPawn()->GetActorLocation(), TargetLocation);

	if (CurrentState == EEchoAIState::Investigating || CurrentState == EEchoAIState::Returning)
	{
		if (DistToTarget <= EchoDefaults::AIAcceptanceRadius)
		{
			// Arrived at target
			if (CurrentState == EEchoAIState::Investigating)
			{
				LingerTimer += DeltaTime;
				if (LingerTimer >= EchoDefaults::AIInvestigateTimeout)
				{
					ReturnToSpawn();
				}
			}
			else
			{
				CurrentState = EEchoAIState::Idle;
			}
		}
		else
		{
			// Move toward target directly (bypasses NavMesh)
			const FVector Direction = (TargetLocation - GetPawn()->GetActorLocation()).GetSafeNormal();
			GetPawn()->AddMovementInput(Direction, 1.0f);
		}
	}
}

void AEchoAIController::ReturnToSpawn()
{
	CurrentState = EEchoAIState::Returning;
	TargetLocation = SpawnLocation;
}
