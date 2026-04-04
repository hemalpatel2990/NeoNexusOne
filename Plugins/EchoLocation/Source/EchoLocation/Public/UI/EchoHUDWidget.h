// Copyright NeoNexusOne. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "EchoHUDWidget.generated.h"

class UProgressBar;
class UTextBlock;

/**
 * C++ base for the Inked HUD widget.
 * Blueprint child (WBP_InkedHUD) provides layout; this class binds to named slots.
 *
 * UI Spec: Signal Strength (top-left cyan bar), Mapping Progress (top-right counter),
 * pulsing impact indicator.
 */
UCLASS(Abstract)
class ECHOLOCATION_API UEchoHUDWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	/** Update signal strength bar (0-1 normalized). */
	UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
	void UpdateSignal(float NormalizedSignal);

	/** Update mapping progress text. Pass negative to show placeholder. */
	UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
	void UpdateMapping(float Percent);

	/** Flash the pulse indicator on impact. */
	UFUNCTION(BlueprintCallable, Category = "Echo|HUD")
	void TriggerPulse();

protected:
	/** Sharp, glowing cyan progress bar — top left. */
	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UProgressBar> SignalBar;

	/** Digital percentage counter — top right. e.g. "MAPPING: 45.2%" */
	UPROPERTY(meta = (BindWidget))
	TObjectPtr<UTextBlock> MappingText;

	/** Small pulsing icon that flashes on sound impact. */
	UPROPERTY(meta = (BindWidgetOptional))
	TObjectPtr<UWidget> PulseIndicator;

	/** Blueprint-implementable event for pulse animation. */
	UFUNCTION(BlueprintImplementableEvent, Category = "Echo|HUD")
	void OnPulseTriggered();
};
