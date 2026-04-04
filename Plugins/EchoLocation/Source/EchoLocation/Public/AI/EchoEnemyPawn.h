// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "EchoEnemyPawn.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class USphereComponent;
class UFloatingPawnMovement;

UCLASS()
class ECHOLOCATION_API AEchoEnemyPawn : public APawn
{
	GENERATED_BODY()

public:
	AEchoEnemyPawn();

protected:
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UBoxComponent> BoxCollision;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UStaticMeshComponent> CubeMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<USphereComponent> KillSphere;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UFloatingPawnMovement> FloatingMovement;

private:
	UFUNCTION()
	void OnKillOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex,
		bool bFromSweep, const FHitResult& SweepResult);
};
