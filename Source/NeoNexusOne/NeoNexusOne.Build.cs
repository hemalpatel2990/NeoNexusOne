// Copyright NeoNexusOne. All Rights Reserved.

using UnrealBuildTool;

public class NeoNexusOne : ModuleRules
{
    public NeoNexusOne(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine"
        });
    }
}
