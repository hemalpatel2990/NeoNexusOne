// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "EchoPlayerController.generated.h"

class UInputMappingContext;
class UEchoHUDWidget;
class UMaterialParameterCollection;

UCLASS()
class NEONEXUSONE_API AEchoPlayerController : public APlayerController
{
	GENERATED_BODY()

public:
	/** Called by EchoPawn on impact — resets signal to 1.0 and triggers HUD pulse. */
	UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
	void ResetSignal();

protected:
	virtual void BeginPlay() override;
	virtual void PlayerTick(float DeltaTime) override;

	/** Input Mapping Context to add on BeginPlay. Set in BP to IMC_EchoDefault. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
	TObjectPtr<UInputMappingContext> DefaultMappingContext;

	// --- HUD ---

	/** Widget class to spawn. Set in BP to WBP_InkedHUD. */
	UPROPERTY(EditDefaultsOnly, Category = "Echo|HUD")
	TSubclassOf<UEchoHUDWidget> HUDWidgetClass;

	/** Current signal strength (0-1). 1.0 on impact, decays over SignalDecayDuration. */
	UPROPERTY(BlueprintReadOnly, Category = "Echo|HUD")
	float CurrentSignal = 0.0f;

	/** Mapping progress percentage. Placeholder until Milestone 3. */
	UPROPERTY(BlueprintReadOnly, Category = "Echo|HUD")
	float MappingProgress = -1.0f;

	/** Enemy proximity intensity (0-1). 0 = no enemies nearby, 1 = enemy at point-blank. */
	UPROPERTY(BlueprintReadOnly, Category = "Echo|HUD")
	float ProximityIntensity = 0.0f;

private:
	UPROPERTY()
	TObjectPtr<UEchoHUDWidget> HUDWidget;

	UPROPERTY()
	TObjectPtr<UMaterialParameterCollection> GlobalSoundMPC;
};
