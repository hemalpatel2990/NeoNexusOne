// Copyright NeoNexusOne. All Rights Reserved.

#include "Player/EchoMovementComponent.h"
#include "GameFramework/Actor.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoMovement, Log, All);

UEchoMovementComponent::UEchoMovementComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UEchoMovementComponent::TickComponent(float DeltaTime, ELevelTick TickType,
	FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	if (!PawnOwner || !UpdatedComponent)
	{
		return;
	}

	const bool bIsAirborne = (CurrentState == EEchoMovementState::Drop ||
		CurrentState == EEchoMovementState::SlamJump);

	if (bIsAirborne)
	{
		// Apply gravity
		CurrentVelocity.Z -= 980.0f * GravityScale * DeltaTime;

		// Move the pawn
		const FVector Delta = CurrentVelocity * DeltaTime;
		FHitResult Hit;
		SafeMoveUpdatedComponent(Delta, UpdatedComponent->GetComponentRotation(), true, Hit);

		if (Hit.bBlockingHit)
		{
			HandleLanding(Hit.ImpactPoint);
			return;
		}

		// Check ground contact via line trace
		float FloorZ;
		if (CheckGroundContact(FloorZ))
		{
			HandleLanding(UpdatedComponent->GetComponentLocation());
		}
	}
	else
	{
		// Glide mode: apply XY movement from input
		const FRotator ControlRotation = PawnOwner->GetControlRotation();
		const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);
		const FVector ForwardDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
		const FVector RightDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

		FVector DesiredMovement = (ForwardDir * PendingInput.Y + RightDir * PendingInput.X) * GlideSpeed;

		// Hover: always interpolate Z toward HoverHeight above ground
		// TargetZ = FloorZ + BoxHalfHeight + HoverHeight (so the bottom of the box clears the floor by HoverHeight)
		float FloorZ;
		if (CheckGroundContact(FloorZ))
		{
			const float BoxHalfHeight = 50.0f;
			const float TargetZ = FloorZ + BoxHalfHeight + HoverHeight;
			const float CurrentZ = UpdatedComponent->GetComponentLocation().Z;
			const float NewZ = FMath::FInterpTo(CurrentZ, TargetZ, DeltaTime, HoverInterpSpeed);
			DesiredMovement.Z = (NewZ - CurrentZ) / DeltaTime;
		}
		else
		{
			UE_LOG(LogEchoMovement, Warning, TEXT("CheckGroundContact failed — no floor detected below pawn at %s"),
				*UpdatedComponent->GetComponentLocation().ToString());
		}

		CurrentVelocity = FVector(DesiredMovement.X, DesiredMovement.Y, DesiredMovement.Z);

		const FVector Delta = CurrentVelocity * DeltaTime;
		if (!Delta.IsNearlyZero())
		{
			FHitResult Hit;
			SafeMoveUpdatedComponent(Delta, UpdatedComponent->GetComponentRotation(), true, Hit);
		}

		if (PendingInput.IsNearlyZero())
		{
			CurrentState = EEchoMovementState::Idle;
		}
		else
		{
			CurrentState = EEchoMovementState::Glide;
		}

		// Consume input
		PendingInput = FVector2D::ZeroVector;
	}
}

void UEchoMovementComponent::AddGlideInput(FVector2D Input)
{
	PendingInput = Input;
}

void UEchoMovementComponent::RequestSlamJump()
{
	if (CurrentState == EEchoMovementState::Drop || CurrentState == EEchoMovementState::SlamJump)
	{
		return; // Already airborne
	}

	CurrentVelocity = SlamJumpImpulse;
	CurrentState = EEchoMovementState::SlamJump;
}

bool UEchoMovementComponent::CheckGroundContact(float& OutFloorZ) const
{
	if (!UpdatedComponent)
	{
		return false;
	}

	const FVector Start = UpdatedComponent->GetComponentLocation();
	// Trace far enough to find the floor from any height (spawn, post-slam, etc.)
	const FVector End = Start - FVector(0.0f, 0.0f, 500.0f);

	FHitResult Hit;
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(PawnOwner);

	// Trace against WorldStatic and WorldDynamic object types — covers all level geometry
	FCollisionObjectQueryParams ObjectParams;
	ObjectParams.AddObjectTypesToQuery(ECC_WorldStatic);
	ObjectParams.AddObjectTypesToQuery(ECC_WorldDynamic);

	if (GetWorld()->LineTraceSingleByObjectType(Hit, Start, End, ObjectParams, Params))
	{
		OutFloorZ = Hit.ImpactPoint.Z;
		return true;
	}

	UE_LOG(LogEchoMovement, Warning, TEXT("CheckGroundContact: No hit — Start=%s End=%s"), *Start.ToString(), *End.ToString());
	OutFloorZ = 0.0f;
	return false;
}

void UEchoMovementComponent::HandleLanding(const FVector& ImpactLocation)
{
	// Determine impact type based on Z velocity before landing
	const float ImpactSpeed = FMath::Abs(CurrentVelocity.Z);
	const EEchoMovementState ImpactState =
		(ImpactSpeed >= SlamVelocityThreshold) ? EEchoMovementState::SlamJump : EEchoMovementState::Drop;

	// Reset velocity and state
	CurrentVelocity = FVector::ZeroVector;
	CurrentState = EEchoMovementState::Idle;

	// Broadcast impact event
	OnEchoImpact.Broadcast(ImpactState, ImpactLocation);
}
