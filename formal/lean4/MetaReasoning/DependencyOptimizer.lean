/-
  Dependency Tree Optimizer
  Auto-suggests lemmas that reduce proof dependency chains

  Example: If proving A → B → C → D → E,
  suggests intermediate lemma A → D (cuts out B, C)
-/

import Lean
import Lean.Meta
import DualTract.Basic
import DualTract.Compression

open Lean Meta Elab

namespace MetaReasoning.DependencyOptimizer

/-- Represents a dependency edge in the proof graph -/
structure DependencyEdge where
  source : Name
  target : Name
  depth : Nat  -- How many steps between them
  deriving Repr, BEq

/-- Represents a proof dependency graph -/
structure DependencyGraph where
  nodes : List Name
  edges : List DependencyEdge
  deriving Repr

/-- Suggested intermediate lemma to cut dependency chains -/
structure LemmaSuggestion where
  name : Name
  sourceTheorem : Name
  targetTheorem : Name
  estimatedReduction : Nat  -- How many steps saved
  priority : Nat  -- Higher = more important
  deriving Repr

/-- Extract all theorem dependencies from a constant -/
def extractDependencies (constName : Name) : MetaM (List Name) := do
  try
    let info ← getConstInfo constName
    let deps := info.type.getUsedConstants
    return deps.toList
  catch _ =>
    return []

/-- Build dependency graph for a module -/
def buildDependencyGraph (moduleName : Name) : MetaM DependencyGraph := do
  let env ← getEnv
  let constants := env.constants.map₁.toList

  -- Filter to theorems in this module
  let theorems := constants.filter (fun (name, _) =>
    name.getPrefix == moduleName &&
    name.toString.contains "theorem")

  let mut edges : List DependencyEdge := []

  for (thmName, _) in theorems do
    let deps ← extractDependencies thmName
    for dep in deps do
      if dep.getPrefix == moduleName then
        edges := edges.concat {
          source := dep,
          target := thmName,
          depth := 1
        }

  let nodes := theorems.map (fun (n, _) => n)
  return { nodes := nodes, edges := edges }

/-- Find transitive dependencies (A → B → C means A → C) -/
def findTransitivePaths (graph : DependencyGraph) : List DependencyEdge := do
  let mut transitive : List DependencyEdge := []

  for edge1 in graph.edges do
    for edge2 in graph.edges do
      if edge1.target == edge2.source then
        -- Found path: edge1.source → edge1.target → edge2.target
        let totalDepth := edge1.depth + edge2.depth

        -- Check if direct edge exists
        let directExists := graph.edges.any (fun e =>
          e.source == edge1.source && e.target == edge2.target)

        if !directExists && totalDepth >= 2 then
          transitive := transitive.concat {
            source := edge1.source,
            target := edge2.target,
            depth := totalDepth
          }

  return transitive

/-- Suggest intermediate lemmas to short-circuit long chains -/
def suggestIntermediateLemmas (graph : DependencyGraph) :
    MetaM (List LemmaSuggestion) := do

  let transitivePaths := findTransitivePaths graph

  -- Sort by depth (longest chains first)
  let sortedPaths := transitivePaths.toArray.qsort
    (fun a b => a.depth > b.depth)

  let mut suggestions : List LemmaSuggestion := []

  for path in sortedPaths.toList do
    if path.depth >= 3 then  -- Only suggest for chains of 3+ steps
      let suggestion : LemmaSuggestion := {
        name := Name.mkStr path.source s!"_to_{path.target}",
        sourceTheorem := path.source,
        targetTheorem := path.target,
        estimatedReduction := path.depth - 1,  -- Direct lemma = 1 step
        priority := path.depth * 10  -- Higher depth = higher priority
      }
      suggestions := suggestions.concat suggestion

  return suggestions.take 10  -- Top 10 suggestions

/-- Analyze and report dependency optimization opportunities -/
def analyzeDependencies (moduleName : Name) : MetaM Unit := do
  IO.println s!"=== Analyzing Dependencies for {moduleName} ==="
  IO.println ""

  let graph ← buildDependencyGraph moduleName
  IO.println s!"Found {graph.nodes.length} theorems"
  IO.println s!"Found {graph.edges.length} direct dependencies"
  IO.println ""

  let suggestions ← suggestIntermediateLemmas graph

  if suggestions.isEmpty then
    IO.println "No optimization opportunities found (dependency tree is minimal)"
  else
    IO.println s!"Found {suggestions.length} optimization opportunities:"
    IO.println ""

    for (i, suggestion) in suggestions.enum do
      IO.println s!"{i + 1}. Suggested Lemma: {suggestion.name}"
      IO.println s!"   Connects: {suggestion.sourceTheorem} → {suggestion.targetTheorem}"
      IO.println s!"   Saves: {suggestion.estimatedReduction} proof steps"
      IO.println s!"   Priority: {suggestion.priority}"
      IO.println ""

/-- Generate Lean code for suggested lemmas -/
def generateLemmaCode (suggestion : LemmaSuggestion) : MetaM String := do
  let sourceInfo ← getConstInfo suggestion.sourceTheorem
  let targetInfo ← getConstInfo suggestion.targetTheorem

  let lemmaName := suggestion.name.toString.replace "DualTract." ""
  let sourceType := sourceInfo.type
  let targetType := targetInfo.type

  return s!"
/-
  AUTO-GENERATED SUGGESTION
  Priority: {suggestion.priority}
  Estimated reduction: {suggestion.estimatedReduction} steps
-/
theorem {lemmaName} : {sourceType} → {targetType} := by
  sorry  -- TODO: Complete proof
  -- This lemma short-circuits a {suggestion.estimatedReduction}-step chain
  -- Original path: {suggestion.sourceTheorem} → ... → {suggestion.targetTheorem}
"

/-- Export suggestions to a file -/
def exportSuggestions (moduleName : Name) (outputPath : String) : MetaM Unit := do
  let suggestions ← suggestIntermediateLemmas (← buildDependencyGraph moduleName)

  let mut output := s!"-- AUTO-GENERATED LEMMA SUGGESTIONS\n"
  output := output ++ s!"-- Module: {moduleName}\n"
  output := output ++ s!"-- Generated: {← IO.monoNanosNow}\n\n"

  for suggestion in suggestions do
    let code ← generateLemmaCode suggestion
    output := output ++ code ++ "\n"

  IO.FS.writeFile outputPath output
  IO.println s!"Exported {suggestions.length} suggestions to {outputPath}"

end MetaReasoning.DependencyOptimizer
