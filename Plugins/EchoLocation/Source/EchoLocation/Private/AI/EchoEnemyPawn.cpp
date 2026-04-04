// Copyright NeoNexusOne. All Rights Reserved.

#include "AI/EchoEnemyPawn.h"
#include "AI/EchoAIController.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "GameFramework/FloatingPawnMovement.h"
#include "Player/EchoPawn.h"
#include "Core/EchoGameMode.h"
#include "Core/EchoTypes.h"
#include "Engine/Engine.h"

DEFINE_LOG_CATEGORY_STATIC(LogEchoEnemy, Log, All);

AEchoEnemyPawn::AEchoEnemyPawn()
{
	// Box collision as root
	BoxCollision = CreateDefaultSubobject<UBoxComponent>(TEXT("BoxCollision"));
	BoxCollision->SetBoxExtent(FVector(50.0f));
	BoxCollision->SetCollisionProfileName(TEXT("Pawn"));
	RootComponent = BoxCollision;

	// Cube mesh
	CubeMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CubeMesh"));
	CubeMesh->SetupAttachment(BoxCollision);
	CubeMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeFinder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeFinder.Succeeded())
	{
		CubeMesh->SetStaticMesh(CubeFinder.Object);
	}

	// Kill overlap sphere
	KillSphere = CreateDefaultSubobject<USphereComponent>(TEXT("KillSphere"));
	KillSphere->SetupAttachment(BoxCollision);
	KillSphere->SetSphereRadius(EchoDefaults::AIKillOverlapRadius);
	KillSphere->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	KillSphere->SetGenerateOverlapEvents(true);

	// Floating pawn movement
	FloatingMovement = CreateDefaultSubobject<UFloatingPawnMovement>(TEXT("FloatingMovement"));
	FloatingMovement->MaxSpeed = EchoDefaults::AIMovementSpeed;

	// AI controller setup
	AIControllerClass = AEchoAIController::StaticClass();
	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;
}

void AEchoEnemyPawn::BeginPlay()
{
	Super::BeginPlay();

	KillSphere->OnComponentBeginOverlap.AddDynamic(this, &AEchoEnemyPawn::OnKillOverlap);

	UE_LOG(LogEchoEnemy, Verbose, TEXT("EnemyPawn BeginPlay: Controller=%s AIControllerClass=%s AutoPossess=%d"),
		GetController() ? *GetController()->GetName() : TEXT("NONE"),
		AIControllerClass ? *AIControllerClass->GetName() : TEXT("NONE"),
		static_cast<int32>(AutoPossessAI));
}

void AEchoEnemyPawn::OnKillOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex,
	bool bFromSweep, const FHitResult& SweepResult)
{
	if (AEchoPawn* Player = Cast<AEchoPawn>(OtherActor))
	{
		if (AEchoGameMode* GM = Cast<AEchoGameMode>(GetWorld()->GetAuthGameMode()))
		{
			GM->TriggerGameOver();
		}
	}
}
