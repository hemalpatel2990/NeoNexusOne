// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "Core/EchoTypes.h"
#include "EchoPawn.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class USpringArmComponent;
class UCameraComponent;
class UEchoMovementComponent;
class UEchoFeedbackComponent;
class UPawnNoiseEmitterComponent;
class UMaterialParameterCollection;
class UInputAction;
struct FInputActionValue;

UCLASS()
class ECHOLOCATION_API AEchoPawn : public APawn
{
	GENERATED_BODY()

public:
	AEchoPawn();

	virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
	virtual UPawnMovementComponent* GetMovementComponent() const override;

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	// --- Components ---

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UBoxComponent> BoxCollision;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UStaticMeshComponent> CubeMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<USpringArmComponent> SpringArm;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UCameraComponent> Camera;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UEchoMovementComponent> MovementComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UEchoFeedbackComponent> FeedbackComponent;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Components")
	TObjectPtr<UPawnNoiseEmitterComponent> NoiseEmitter;

	/** MPC reference for writing player position each tick. Set in Blueprint to MPC_GlobalSound. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Ripple")
	TObjectPtr<UMaterialParameterCollection> EchoMPC;

	// --- Input Actions (set in Blueprint to IA_ assets) ---

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
	TObjectPtr<UInputAction> IA_Move;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
	TObjectPtr<UInputAction> IA_Look;

	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
	TObjectPtr<UInputAction> IA_Slam;

	/** Multiplier for mouse look input. Tunable per-instance at runtime. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Echo|Input", meta = (ClampMin = "0.01", UIMax = "5.0"))
	float MouseSensitivity = EchoDefaults::DefaultMouseSensitivity;

private:
	// --- Input Handlers ---
	void HandleMove(const FInputActionValue& Value);
	void HandleLook(const FInputActionValue& Value);
	void HandleSlam(const FInputActionValue& Value);

	// --- Impact Callback ---
	UFUNCTION()
	void OnImpact(EEchoMovementState State, FVector Location);
};
