// Copyright NeoNexusOne. All Rights Reserved.

#include "Player/EchoPawn.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/PawnNoiseEmitterComponent.h"
#include "EnhancedInputComponent.h"
#include "InputActionValue.h"
#include "Player/EchoMovementComponent.h"
#include "Feedback/EchoFeedbackComponent.h"
#include "Core/EchoGameMode.h"
#include "Sound/EchoRippleManager.h"
#include "Kismet/KismetMaterialLibrary.h"
#include "Materials/MaterialParameterCollection.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoPawn, Log, All);

AEchoPawn::AEchoPawn()
{
	PrimaryActorTick.bCanEverTick = true;

	// Box collision as root — 50cm half-extent cube
	BoxCollision = CreateDefaultSubobject<UBoxComponent>(TEXT("BoxCollision"));
	BoxCollision->InitBoxExtent(FVector(50.0f));
	BoxCollision->SetCollisionProfileName(TEXT("Pawn"));
	SetRootComponent(BoxCollision);

	// Static mesh for the cube visual (mesh asset set in Blueprint)
	CubeMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CubeMesh"));
	CubeMesh->SetupAttachment(BoxCollision);

	// Spring arm for third-person camera
	SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
	SpringArm->SetupAttachment(BoxCollision);
	SpringArm->TargetArmLength = 400.0f;
	SpringArm->bUsePawnControlRotation = true;

	// Camera attached to spring arm
	Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("Camera"));
	Camera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
	Camera->bUsePawnControlRotation = false;

	// Movement component (UpdatedComponent is auto-set to root by UPawnMovementComponent)
	MovementComponent = CreateDefaultSubobject<UEchoMovementComponent>(TEXT("MovementComponent"));

	// Feedback component (camera shake + haptics)
	FeedbackComponent = CreateDefaultSubobject<UEchoFeedbackComponent>(TEXT("FeedbackComponent"));

	// Noise emitter for AI perception
	NoiseEmitter = CreateDefaultSubobject<UPawnNoiseEmitterComponent>(TEXT("NoiseEmitter"));
}

void AEchoPawn::BeginPlay()
{
	Super::BeginPlay();

	// Bind to movement component impact delegate
	if (MovementComponent)
	{
		MovementComponent->OnEchoImpact.AddDynamic(this, &AEchoPawn::OnImpact);
	}
}

void AEchoPawn::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Write player world position to MPC every frame for proximity awareness shader
	if (EchoMPC)
	{
		if (UWorld* World = GetWorld())
		{
			const FVector Loc = GetActorLocation();
			UKismetMaterialLibrary::SetVectorParameterValue(
				World, EchoMPC, EchoMPCParams::PlayerWorldPosition,
				FLinearColor(Loc.X, Loc.Y, Loc.Z, 0.0f));
		}
	}
}

void AEchoPawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent);
	if (!EnhancedInput)
	{
		return;
	}

	if (IA_Move)
	{
		EnhancedInput->BindAction(IA_Move, ETriggerEvent::Triggered, this, &AEchoPawn::HandleMove);
		EnhancedInput->BindAction(IA_Move, ETriggerEvent::Completed, this, &AEchoPawn::HandleMove);
	}

	if (IA_Look)
	{
		EnhancedInput->BindAction(IA_Look, ETriggerEvent::Triggered, this, &AEchoPawn::HandleLook);
	}

	if (IA_Slam)
	{
		EnhancedInput->BindAction(IA_Slam, ETriggerEvent::Started, this, &AEchoPawn::HandleSlam);
	}
}

UPawnMovementComponent* AEchoPawn::GetMovementComponent() const
{
	return MovementComponent;
}

void AEchoPawn::HandleMove(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();
	if (MovementComponent)
	{
		MovementComponent->AddGlideInput(Input);
	}
}

void AEchoPawn::HandleLook(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();
	AddControllerYawInput(Input.X * MouseSensitivity);
	AddControllerPitchInput(Input.Y * MouseSensitivity);
}

void AEchoPawn::HandleSlam(const FInputActionValue& Value)
{
	if (MovementComponent)
	{
		MovementComponent->RequestSlamJump();
	}
}

void AEchoPawn::OnImpact(EEchoMovementState State, FVector Location)
{
	UE_LOG(LogEchoPawn, Warning, TEXT("OnImpact: State=%d Location=(%s)"), static_cast<int32>(State), *Location.ToString());

	// Build ripple event based on impact type
	FEchoRippleEvent RippleEvent;
	RippleEvent.ImpactLocation = Location;

	switch (State)
	{
	case EEchoMovementState::SlamJump:
		RippleEvent.MaxRadius = EchoDefaults::SlamRippleRadius;
		RippleEvent.Intensity = EchoDefaults::SlamIntensity;
		RippleEvent.NoiseVolume = EchoDefaults::SlamNoiseVolume;
		break;

	case EEchoMovementState::Drop:
	default:
		RippleEvent.MaxRadius = EchoDefaults::DropRippleRadius;
		RippleEvent.Intensity = EchoDefaults::DropIntensity;
		RippleEvent.NoiseVolume = EchoDefaults::DropNoiseVolume;
		break;
	}

	// Trigger the visual ripple via the GameMode's RippleManager
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	if (AEchoGameMode* GM = Cast<AEchoGameMode>(World->GetAuthGameMode()))
	{
		if (UEchoRippleManager* RippleMgr = GM->GetRippleManager())
		{
			RippleMgr->TriggerRipple(RippleEvent);
		}
	}

	// Report noise for AI perception
	MakeNoise(RippleEvent.NoiseVolume, this, Location);

	// Play camera shake + haptic feedback
	if (FeedbackComponent)
	{
		FeedbackComponent->PlayFeedback(State);
	}
}
