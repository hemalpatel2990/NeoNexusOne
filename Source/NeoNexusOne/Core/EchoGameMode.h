// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "EchoGameMode.generated.h"

class UEchoRippleManager;

UCLASS()
class NEONEXUSONE_API AEchoGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AEchoGameMode();

	UFUNCTION(BlueprintPure, Category = "Echo|Core")
	UEchoRippleManager* GetRippleManager() const { return RippleManager; }

protected:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Echo|Core")
	TObjectPtr<UEchoRippleManager> RippleManager;
};
