// Copyright NeoNexusOne. All Rights Reserved.

#include "UI/EchoHUDWidget.h"
#include "Components/ProgressBar.h"
#include "Components/TextBlock.h"

void UEchoHUDWidget::UpdateSignal(float NormalizedSignal)
{
	if (SignalBar)
	{
		SignalBar->SetPercent(NormalizedSignal);
	}
}

void UEchoHUDWidget::UpdateMapping(float Percent)
{
	if (MappingText)
	{
		if (Percent < 0.0f)
		{
			MappingText->SetText(FText::FromString(TEXT("MAPPING: --.--%")));
		}
		else
		{
			MappingText->SetText(FText::FromString(
				FString::Printf(TEXT("MAPPING: %.1f%%"), Percent)));
		}
	}
}

void UEchoHUDWidget::TriggerPulse()
{
	OnPulseTriggered();
}
