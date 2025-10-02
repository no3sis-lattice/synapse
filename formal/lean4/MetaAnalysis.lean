/-
  Meta-Analysis Entry Point
  Run comprehensive meta-reasoning analysis on the Synapse verification system

  Usage: lake exe metaanalysis
-/

import MetaReasoning.SynapseMeta

open Lean Meta MetaReasoning.SynapseMeta

def main : IO Unit := do
  -- Initialize meta environment
  initSearchPath (← findSysroot)

  let env ← importModules
    (imports := #[
      { module := `DualTract.Basic },
      { module := `DualTract.Compression },
      { module := `DualTract.Consciousness },
      { module := `DualTract.CategoryTheory },
      { module := `DualTract.CorpusCallosum }
    ])
    (opts := {})

  let coreCtx : Core.Context := {
    fileName := "<metaanalysis>",
    fileMap := default
  }

  let metaCtx : Meta.Context := {}
  let metaState : Meta.State := {}

  -- Run meta-analysis
  let (report, _) ← (runCompleteAnalysis).run metaCtx metaState |>.run coreCtx { env := env }

  IO.println ""
  IO.println "═══════════════════════════════════════════════════════════"
  IO.println "Meta-analysis complete!"
  IO.println ""
  IO.println "To export results:"
  IO.println "  lake exe metaanalysis --export ./meta-output"
  IO.println ""
  IO.println "To view dual-tract integration:"
  IO.println "  lake exe metaanalysis --demonstrate"
  IO.println "═══════════════════════════════════════════════════════════"
