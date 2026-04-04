// Copyright NeoNexusOne. All Rights Reserved.

using UnrealBuildTool;
using System.IO;

public class EchoLocation : ModuleRules
{
    public EchoLocation(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicIncludePaths.AddRange(new string[] {
            ModuleDirectory,
            Path.Combine(ModuleDirectory, "Public")
        });

        PrivateIncludePaths.AddRange(new string[] {
            Path.Combine(ModuleDirectory, "Private")
        });

        PublicDependencyModuleNames.AddRange(new string[] {
            "Core",
            "CoreUObject",
            "Engine",
            "InputCore",
            "EnhancedInput"
        });

        PrivateDependencyModuleNames.AddRange(new string[] {
            "AIModule",
            "GameplayTasks",
            "NavigationSystem",
            "Slate",
            "SlateCore",
            "UMG"
        });
    }
}
