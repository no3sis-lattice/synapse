import Lake
open Lake DSL

package «dualtract» where
  -- add package configuration options here

lean_lib «DualTract» where
  -- add library configuration options here

lean_lib «MetaReasoning» where
  -- Meta-reasoning modules for self-improvement

@[default_target]
lean_exe «dualtract» where
  root := `Main

lean_exe «metaanalysis» where
  root := `MetaAnalysis
  supportInterpreter := true

require mathlib from git
  "https://github.com/leanprover-community/mathlib4.git" @ "master"
