// Copyright NeoNexusOne. All Rights Reserved.

#include "AI/EchoAIController.h"
#include "Perception/AIPerceptionComponent.h"
#include "Perception/AISenseConfig_Hearing.h"
#include "Navigation/PathFollowingComponent.h"

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
}

void AEchoAIController::OnPerceptionUpdated(AActor* Actor, FAIStimulus Stimulus)
{
	if (!Stimulus.WasSuccessfullySensed())
	{
		return;
	}

	const float Strength = Stimulus.Strength;

	// Slam (strength ~1.0): always investigate
	// Drop (strength ~0.5): only if Idle and within Drop radius
	if (Strength >= EchoDefaults::SlamNoiseVolume)
	{
		InvestigateLocation(Stimulus.StimulusLocation);
	}
	else if (CurrentState == EEchoAIState::Idle)
	{
		const float Distance = FVector::Dist(GetPawn()->GetActorLocation(), Stimulus.StimulusLocation);
		if (Distance <= EchoDefaults::DropRippleRadius)
		{
			InvestigateLocation(Stimulus.StimulusLocation);
		}
	}
}

void AEchoAIController::InvestigateLocation(const FVector& Location)
{
	CurrentState = EEchoAIState::Investigating;
	LingerTimer = 0.0f;
	MoveToLocation(Location, EchoDefaults::AIAcceptanceRadius);
}

void AEchoAIController::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (CurrentState == EEchoAIState::Investigating)
	{
		// If move is done (reached target), start linger countdown
		if (GetPathFollowingComponent() && GetPathFollowingComponent()->GetStatus() == EPathFollowingStatus::Idle)
		{
			LingerTimer += DeltaTime;
			if (LingerTimer >= EchoDefaults::AIInvestigateTimeout)
			{
				ReturnToSpawn();
			}
		}
	}
	else if (CurrentState == EEchoAIState::Returning)
	{
		if (GetPathFollowingComponent() && GetPathFollowingComponent()->GetStatus() == EPathFollowingStatus::Idle)
		{
			CurrentState = EEchoAIState::Idle;
		}
	}
}

void AEchoAIController::OnMoveCompleted(FAIRequestID RequestID, const FPathFollowingResult& Result)
{
	Super::OnMoveCompleted(RequestID, Result);

	if (CurrentState == EEchoAIState::Investigating)
	{
		// Arrived at investigation target — linger timer starts in Tick
		LingerTimer = 0.0f;
	}
	else if (CurrentState == EEchoAIState::Returning)
	{
		CurrentState = EEchoAIState::Idle;
	}
}

void AEchoAIController::ReturnToSpawn()
{
	CurrentState = EEchoAIState::Returning;
	MoveToLocation(SpawnLocation, EchoDefaults::AIAcceptanceRadius);
}
