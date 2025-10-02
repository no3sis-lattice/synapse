/-
  Axiom Leverage Analyzer
  Discovers underleveraged axioms that could be applied across domains

  Example: Finds axioms used in Compression.lean that could also
  simplify proofs in Consciousness.lean
-/

import Lean
import Lean.Meta
import DualTract.Basic
import DualTract.Compression
import DualTract.Consciousness

open Lean Meta Elab

namespace MetaReasoning.AxiomAnalyzer

/-- Statistics about axiom usage -/
structure AxiomUsageStats where
  axiomName : Name
  directUses : Nat  -- Theorems that use it directly
  transitiveUses : Nat  -- Theorems that use it transitively
  domains : List Name  -- Which modules use it
  potentialUses : List Name  -- Theorems that could use it but don't
  leverageRatio : Float  -- potential / actual (higher = more underleveraged)
  deriving Repr

/-- Cross-domain application opportunity -/
structure CrossDomainOpportunity where
  axiom : Name
  sourceModule : Name
  targetTheorem : Name
  targetModule : Name
  estimatedSimplification : Nat  -- How much simpler the proof becomes
  confidence : Float  -- How confident we are it applies (0-1)
  deriving Repr

/-- Check if a theorem uses an axiom directly -/
def usesDirectly (theorem axiom : Name) : MetaM Bool := do
  try
    let info ← getConstInfo theorem
    let constants := info.value!.getUsedConstants
    return constants.contains axiom
  catch _ =>
    return false

/-- Check if a theorem uses an axiom transitively -/
def usesTransitively (theorem axiom : Name) : MetaM Bool := do
  try
    let info ← getConstInfo theorem
    let constants := info.value!.getUsedConstants

    -- Check direct use
    if constants.contains axiom then
      return true

    -- Check transitive use through dependencies
    for const in constants.toList do
      let transitiveUse ← usesDirectly const axiom
      if transitiveUse then
        return true

    return false
  catch _ =>
    return false

/-- Get all axioms in the environment -/
def getAllAxioms : MetaM (List Name) := do
  let env ← getEnv
  let constants := env.constants.map₁.toList

  let axioms := constants.filter (fun (_, info) =>
    match info with
    | .axiomInfo _ => true
    | _ => false
  ) |>.map (fun (n, _) => n)

  return axioms

/-- Get all theorems in the environment -/
def getAllTheorems : MetaM (List Name) := do
  let env ← getEnv
  let constants := env.constants.map₁.toList

  let theorems := constants.filter (fun (name, info) =>
    match info with
    | .thmInfo _ => true
    | _ => false
  ) |>.map (fun (n, _) => n)

  return theorems

/-- Infer which domain/module a theorem belongs to -/
def inferDomain (name : Name) : Name :=
  name.getPrefix

/-- Check if two theorems have similar structure -/
def structurallySimilar (thm1 thm2 : Name) : MetaM Bool := do
  try
    let info1 ← getConstInfo thm1
    let info2 ← getConstInfo thm2

    -- Simple heuristic: same return type and similar arity
    let rec getReturnType (e : Expr) : Name :=
      match e with
      | .forallE _ _ body _ => getReturnType body
      | .const n _ => n
      | _ => Name.anonymous

    let ret1 := getReturnType info1.type
    let ret2 := getReturnType info2.type

    return ret1 == ret2
  catch _ =>
    return false

/-- Compute axiom usage statistics -/
def computeAxiomStats : MetaM (List AxiomUsageStats) := do
  let axioms ← getAllAxioms
  let theorems ← getAllTheorems

  let mut stats : List AxiomUsageStats := []

  for axiom in axioms do
    -- Find direct uses
    let mut directUses : List Name := []
    for theorem in theorems do
      let uses ← usesDirectly theorem axiom
      if uses then
        directUses := directUses.concat theorem

    -- Find transitive uses
    let mut transitiveUses : List Name := []
    for theorem in theorems do
      let uses ← usesTransitively theorem axiom
      if uses then
        transitiveUses := transitiveUses.concat theorem

    -- Infer domains
    let domains := directUses.map inferDomain |>.eraseDups

    -- Find potential uses (similar structure but not using axiom)
    let mut potentialUses : List Name := []
    if !directUses.isEmpty then
      let exemplar := directUses.head!
      for theorem in theorems do
        let similar ← structurallySimilar theorem exemplar
        let alreadyUses ← usesTransitively theorem axiom
        if similar && !alreadyUses then
          potentialUses := potentialUses.concat theorem

    -- Calculate leverage ratio
    let leverageRatio :=
      if directUses.length > 0 then
        (potentialUses.length.toFloat / directUses.length.toFloat)
      else
        0.0

    stats := stats.concat {
      axiomName := axiom,
      directUses := directUses.length,
      transitiveUses := transitiveUses.length,
      domains := domains,
      potentialUses := potentialUses,
      leverageRatio := leverageRatio
    }

  -- Sort by leverage ratio (most underleveraged first)
  return stats.toArray.qsort (fun a b => a.leverageRatio > b.leverageRatio) |>.toList

/-- Find cross-domain application opportunities -/
def findCrossDomainOpportunities : MetaM (List CrossDomainOpportunity) := do
  let stats ← computeAxiomStats

  let mut opportunities : List CrossDomainOpportunity := []

  for axiomStat in stats do
    if axiomStat.leverageRatio >= 2.0 then  -- At least 2x potential
      for potentialUse in axiomStat.potentialUses do
        let targetModule := inferDomain potentialUse
        let sourceModule := axiomStat.domains.head!

        -- Estimate simplification (heuristic based on leverage ratio)
        let simplification := (axiomStat.leverageRatio * 2).toUInt64.toNat

        -- Confidence based on how many domains already use it
        let confidence :=
          (axiomStat.domains.length.toFloat / 5.0).min 1.0

        opportunities := opportunities.concat {
          axiom := axiomStat.axiomName,
          sourceModule := sourceModule,
          targetTheorem := potentialUse,
          targetModule := targetModule,
          estimatedSimplification := simplification,
          confidence := confidence
        }

  return opportunities.take 20  -- Top 20 opportunities

/-- Analyze and report axiom leverage -/
def analyzeAxiomLeverage : MetaM Unit := do
  IO.println "=== Analyzing Axiom Leverage ==="
  IO.println ""

  let stats ← computeAxiomStats

  -- Filter to underleveraged axioms (leverage ratio >= 2.0)
  let underleveraged := stats.filter (fun s => s.leverageRatio >= 2.0)

  if underleveraged.isEmpty then
    IO.println "No underleveraged axioms found (all axioms well-utilized)"
  else
    IO.println s!"Found {underleveraged.length} underleveraged axioms:"
    IO.println ""

    for (i, axiomStat) in underleveraged.enum do
      IO.println s!"{i + 1}. Axiom: {axiomStat.axiomName}"
      IO.println s!"   Current uses: {axiomStat.directUses} direct, {axiomStat.transitiveUses} transitive"
      IO.println s!"   Domains: {axiomStat.domains}"
      IO.println s!"   Potential uses: {axiomStat.potentialUses.length}"
      IO.println s!"   Leverage ratio: {axiomStat.leverageRatio}x"
      IO.println "   Sample applications:"
      for theorem in axiomStat.potentialUses.take 3 do
        IO.println s!"     - {theorem}"
      IO.println ""

/-- Report cross-domain opportunities -/
def reportCrossDomainOpportunities : MetaM Unit := do
  IO.println "=== Cross-Domain Application Opportunities ==="
  IO.println ""

  let opportunities ← findCrossDomainOpportunities

  if opportunities.isEmpty then
    IO.println "No cross-domain opportunities found"
  else
    IO.println s!"Found {opportunities.length} cross-domain opportunities:"
    IO.println ""

    for (i, opp) in opportunities.enum do
      IO.println s!"{i + 1}. Apply axiom: {opp.axiom}"
      IO.println s!"   From module: {opp.sourceModule}"
      IO.println s!"   To theorem: {opp.targetTheorem} (in {opp.targetModule})"
      IO.println s!"   Est. simplification: {opp.estimatedSimplification} steps"
      IO.println s!"   Confidence: {opp.confidence * 100}%"
      IO.println ""

/-- Export axiom analysis to a file -/
def exportAxiomAnalysis (outputPath : String) : MetaM Unit := do
  let stats ← computeAxiomStats
  let opportunities ← findCrossDomainOpportunities

  let mut output := "-- AUTO-GENERATED AXIOM ANALYSIS\n"
  output := output ++ s!"-- Generated: {← IO.monoNanosNow}\n\n"

  output := output ++ "-- UNDERLEVERAGED AXIOMS\n\n"
  for axiomStat in stats.filter (fun s => s.leverageRatio >= 2.0) do
    output := output ++ s!"/-\n"
    output := output ++ s!"  Axiom: {axiomStat.axiomName}\n"
    output := output ++ s!"  Leverage: {axiomStat.leverageRatio}x\n"
    output := output ++ s!"  Potential applications: {axiomStat.potentialUses.length}\n"
    output := output ++ s!"-/\n\n"

  output := output ++ "\n-- CROSS-DOMAIN OPPORTUNITIES\n\n"
  for opp in opportunities.take 10 do
    output := output ++ s!"/-\n"
    output := output ++ s!"  Apply: {opp.axiom}\n"
    output := output ++ s!"  To: {opp.targetTheorem}\n"
    output := output ++ s!"  Simplification: {opp.estimatedSimplification} steps\n"
    output := output ++ s!"  Confidence: {opp.confidence * 100}%\n"
    output := output ++ s!"-/\n\n"

  IO.FS.writeFile outputPath output
  IO.println s!"Exported axiom analysis to {outputPath}"

end MetaReasoning.AxiomAnalyzer
