// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/PlayerController.h"
#include "EchoPlayerController.generated.h"

class UInputMappingContext;

UCLASS()
class NEONEXUSONE_API AEchoPlayerController : public APlayerController
{
	GENERATED_BODY()

protected:
	virtual void BeginPlay() override;

	/** Input Mapping Context to add on BeginPlay. Set in BP to IMC_EchoDefault. */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Echo|Input")
	TObjectPtr<UInputMappingContext> DefaultMappingContext;
};
