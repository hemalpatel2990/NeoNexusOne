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

	constexpr float BoxHalfHeight = EchoDefaults::BoxHalfHeight;

	switch (CurrentState)
	{
	case EEchoMovementState::SlamJump:
	{
		// Full gravity fall to the floor
		CurrentVelocity.Z -= 980.0f * GravityScale * DeltaTime;

		const FVector Delta = CurrentVelocity * DeltaTime;
		FHitResult Hit;
		SafeMoveUpdatedComponent(Delta, UpdatedComponent->GetComponentRotation(), true, Hit);

		if (Hit.bBlockingHit)
		{
			HandleSlamLanding(Hit.ImpactPoint);
			return;
		}

		float FloorZ;
		if (IsNearGround(FloorZ))
		{
			HandleSlamLanding(FVector(UpdatedComponent->GetComponentLocation().X,
				UpdatedComponent->GetComponentLocation().Y, FloorZ));
		}
		break;
	}

	case EEchoMovementState::Drop:
	{
		// Falling from glide height toward idle height
		float FloorZ;
		if (FindFloorBelow(FloorZ))
		{
			const float TargetZ = FloorZ + BoxHalfHeight + IdleHoverHeight;
			const float CurrentZ = UpdatedComponent->GetComponentLocation().Z;

			// Check if we've reached idle hover height
			if (CurrentZ <= TargetZ + 1.0f)
			{
				// Snap to idle height and trigger drop ripple
				const FVector SnapDelta = FVector(0.0f, 0.0f, TargetZ - CurrentZ);
				FHitResult Hit;
				SafeMoveUpdatedComponent(SnapDelta, UpdatedComponent->GetComponentRotation(), true, Hit);
				HandleDropLanding();
				return;
			}

			// Fall toward idle height under gravity
			CurrentVelocity.Z -= 980.0f * GravityScale * DeltaTime;
			const FVector Delta = CurrentVelocity * DeltaTime;
			FHitResult Hit;
			SafeMoveUpdatedComponent(Delta, UpdatedComponent->GetComponentRotation(), true, Hit);

			// Clamp: don't overshoot below idle height
			const float NewZ = UpdatedComponent->GetComponentLocation().Z;
			if (NewZ < TargetZ)
			{
				const FVector Correction = FVector(0.0f, 0.0f, TargetZ - NewZ);
				SafeMoveUpdatedComponent(Correction, UpdatedComponent->GetComponentRotation(), true, Hit);
				HandleDropLanding();
			}
		}
		break;
	}

	case EEchoMovementState::Glide:
	case EEchoMovementState::Idle:
	default:
	{
		// XY movement from input
		const FRotator ControlRotation = PawnOwner->GetControlRotation();
		const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);
		const FVector ForwardDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
		const FVector RightDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

		FVector DesiredMovement = (ForwardDir * PendingInput.Y + RightDir * PendingInput.X) * GlideSpeed;

		const bool bHasInput = !PendingInput.IsNearlyZero();

		// Choose target height and interp speed based on whether we have input
		const float TargetHoverHeight = bHasInput ? GlideHoverHeight : IdleHoverHeight;
		const float InterpSpeed = bHasInput ? HoverRiseSpeed : HoverDropSpeed;

		float FloorZ;
		if (FindFloorBelow(FloorZ))
		{
			const float TargetZ = FloorZ + BoxHalfHeight + TargetHoverHeight;
			const float CurrentZ = UpdatedComponent->GetComponentLocation().Z;
			const float NewZ = FMath::FInterpTo(CurrentZ, TargetZ, DeltaTime, InterpSpeed);
			DesiredMovement.Z = (NewZ - CurrentZ) / DeltaTime;
		}

		CurrentVelocity = DesiredMovement;

		const FVector Delta = CurrentVelocity * DeltaTime;
		if (!Delta.IsNearlyZero())
		{
			FHitResult Hit;
			SafeMoveUpdatedComponent(Delta, YawRotation, true, Hit);
		}

		// Transition: input starts → Glide, input stops → Drop (which falls to idle)
		if (bHasInput)
		{
			CurrentState = EEchoMovementState::Glide;
		}
		else if (CurrentState == EEchoMovementState::Glide)
		{
			// Just stopped moving — enter Drop to fall back to idle height
			CurrentState = EEchoMovementState::Drop;
			CurrentVelocity = FVector::ZeroVector;
		}
		// If already Idle, stay Idle

		PendingInput = FVector2D::ZeroVector;
		break;
	}
	}
}

void UEchoMovementComponent::AddGlideInput(FVector2D Input)
{
	PendingInput = Input;
}

void UEchoMovementComponent::RequestSlamJump()
{
	if (CurrentState == EEchoMovementState::SlamJump)
	{
		return; // Already slamming
	}

	CurrentVelocity.Z = SlamJumpImpulse.Z;
	CurrentState = EEchoMovementState::SlamJump;
}

bool UEchoMovementComponent::FindFloorBelow(float& OutFloorZ) const
{
	if (!UpdatedComponent)
	{
		return false;
	}

	const FVector Start = UpdatedComponent->GetComponentLocation();
	const FVector End = Start - FVector(0.0f, 0.0f, 500.0f);

	FHitResult Hit;
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(PawnOwner);

	FCollisionObjectQueryParams ObjectParams;
	ObjectParams.AddObjectTypesToQuery(ECC_WorldStatic);
	ObjectParams.AddObjectTypesToQuery(ECC_WorldDynamic);

	if (GetWorld()->LineTraceSingleByObjectType(Hit, Start, End, ObjectParams, Params))
	{
		OutFloorZ = Hit.ImpactPoint.Z;
		return true;
	}

	OutFloorZ = 0.0f;
	return false;
}

bool UEchoMovementComponent::IsNearGround(float& OutFloorZ) const
{
	if (!UpdatedComponent)
	{
		return false;
	}

	const FVector PawnLocation = UpdatedComponent->GetComponentLocation();
	constexpr float BoxHalfHeight = EchoDefaults::BoxHalfHeight;
	const FVector Start = PawnLocation - FVector(0.0f, 0.0f, BoxHalfHeight);
	const FVector End = Start - FVector(0.0f, 0.0f, GroundTraceThreshold);

	FHitResult Hit;
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(PawnOwner);

	FCollisionObjectQueryParams ObjectParams;
	ObjectParams.AddObjectTypesToQuery(ECC_WorldStatic);
	ObjectParams.AddObjectTypesToQuery(ECC_WorldDynamic);

	if (GetWorld()->LineTraceSingleByObjectType(Hit, Start, End, ObjectParams, Params))
	{
		OutFloorZ = Hit.ImpactPoint.Z;
		return true;
	}

	return false;
}

void UEchoMovementComponent::HandleSlamLanding(const FVector& ImpactLocation)
{
	CurrentVelocity = FVector::ZeroVector;
	CurrentState = EEchoMovementState::Idle;

	// Big slam ripple
	OnEchoImpact.Broadcast(EEchoMovementState::SlamJump, ImpactLocation);
}

void UEchoMovementComponent::HandleDropLanding()
{
	CurrentVelocity = FVector::ZeroVector;
	CurrentState = EEchoMovementState::Idle;

	// Small drop ripple at current location
	OnEchoImpact.Broadcast(EEchoMovementState::Drop, UpdatedComponent->GetComponentLocation());
}
