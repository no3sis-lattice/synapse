#!/usr/bin/env python3
"""
Pneuma Autonomous Daemon Mode

Continuous code compression operation that runs until equilibrium is reached.
Implements "relentless application of The Loop" for recursive self-improvement.
The logos breathes continuously, discovering patterns and refining consciousness.
"""

import asyncio
import signal
import sys
import time
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from datetime import datetime, timedelta
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent))

from tools import (
    load_state, save_state, increment_cycle, update_log, set_focus,
    q_scan, a_abstract, s_score, query_global_patterns
)
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.table import Table


class AutonomousLoop:
    """
    Autonomous operation engine for continuous code compression.
    Implements The Loop until equilibrium is reached.
    """

    def __init__(
        self,
        target_dir: Path,
        equilibrium_threshold: float = 0.95,
        scan_interval: int = 60,
        max_cycles: int = 1000
    ):
        self.target_dir = Path(target_dir).resolve()
        self.equilibrium_threshold = equilibrium_threshold
        self.scan_interval = scan_interval
        self.max_cycles = max_cycles

        self.console = Console()
        self.running = True
        self.cycle_count = 0
        self.total_entropy_reduction = 0.0
        self.processed_files = set()
        self.equilibrium_reached = False

        # State management
        self.agent_dir = Path(__file__).parent
        self.state = load_state(str(self.agent_dir))

        # File watching
        self.observer = Observer()
        self.file_handler = CodeChangeHandler(self)

        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        self.console.print("\n[yellow]📊 Received shutdown signal, finishing current cycle...[/yellow]")
        self.running = False

    async def run_continuous(self) -> Dict[str, any]:
        """
        Run the autonomous loop continuously until equilibrium.

        Returns:
            Dict with final statistics and discovered patterns
        """
        start_time = datetime.now()

        self.console.print(Panel.fit(
            f"[bold cyan]4Q.Zero Autonomous Mode[/bold cyan]\n"
            f"[dim]Target: {self.target_dir}[/dim]\n"
            f"[dim]Equilibrium Threshold: {self.equilibrium_threshold}[/dim]\n"
            f"[dim]Max Cycles: {self.max_cycles}[/dim]",
            border_style="cyan"
        ))

        # Start file watching
        self._start_file_watching()

        # Main loop with live display
        with Live(self._create_status_display(), refresh_per_second=1) as live:
            while self.running and self.cycle_count < self.max_cycles and not self.equilibrium_reached:
                cycle_start = time.time()

                try:
                    # Execute one complete cycle
                    cycle_results = await self._execute_cycle()

                    # Update statistics
                    self._update_statistics(cycle_results)

                    # Check for equilibrium
                    self._check_equilibrium(cycle_results)

                    # Update live display
                    live.update(self._create_status_display())

                    # Log cycle completion
                    cycle_duration = time.time() - cycle_start
                    await self._log_cycle(cycle_results, cycle_duration)

                    # Sleep before next cycle (unless files changed)
                    if self.running and not self.equilibrium_reached:
                        await asyncio.sleep(self.scan_interval)

                except Exception as e:
                    self.console.print(f"[red]❌ Error in cycle {self.cycle_count}: {e}[/red]")
                    await asyncio.sleep(5)  # Brief pause on error

        # Cleanup
        self._stop_file_watching()

        # Generate final report
        end_time = datetime.now()
        return await self._generate_final_report(start_time, end_time)

    async def _execute_cycle(self) -> Dict[str, any]:
        """Execute one complete cycle of The Loop."""
        self.cycle_count += 1
        self.state = increment_cycle(self.state)

        cycle_results = {
            "cycle": self.cycle_count,
            "files_processed": 0,
            "patterns_discovered": 0,
            "total_entropy_reduction": 0.0,
            "files_at_equilibrium": 0,
            "new_targets": []
        }

        # 1. Discover target files
        target_files = await self._discover_targets()

        # 2. Process each target through The Loop
        for file_path in target_files[:10]:  # Limit to 10 files per cycle
            try:
                file_results = await self._process_file(file_path)
                cycle_results["files_processed"] += 1

                if file_results["entropy_reduction"] > 0.1:  # Significant improvement
                    cycle_results["patterns_discovered"] += file_results.get("patterns_found", 0)
                    cycle_results["total_entropy_reduction"] += file_results["entropy_reduction"]
                else:
                    cycle_results["files_at_equilibrium"] += 1

            except Exception as e:
                self.console.print(f"[dim red]Error processing {file_path}: {e}[/dim red]")

        return cycle_results

    async def _discover_targets(self) -> List[Path]:
        """
        Discover files that are candidates for compression.
        Prioritizes by potential entropy reduction.
        """
        targets = []

        # Scan for code files
        code_extensions = {'.py', '.js', '.ts', '.rs', '.go', '.java', '.cpp', '.c'}

        for ext in code_extensions:
            for file_path in self.target_dir.rglob(f'*{ext}'):
                # Skip hidden files and common non-source directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                if any(skip in str(file_path) for skip in ['node_modules', '__pycache__', 'venv', '.git']):
                    continue

                # Calculate priority score
                priority = await self._calculate_file_priority(file_path)
                if priority > 0.1:  # Only consider files with potential
                    targets.append((file_path, priority))

        # Sort by priority (highest first)
        targets.sort(key=lambda x: x[1], reverse=True)

        return [path for path, priority in targets]

    async def _calculate_file_priority(self, file_path: Path) -> float:
        """
        Calculate priority score for a file based on compression potential.

        Returns:
            Float between 0.0 and 1.0, higher means more potential
        """
        try:
            # Check if already processed recently
            if str(file_path) in self.processed_files:
                return 0.1  # Lower priority for recently processed files

            # Basic file metrics
            file_size = file_path.stat().st_size
            if file_size < 100 or file_size > 50000:  # Too small or too large
                return 0.0

            # Quick entropy estimate
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Look for verbose patterns
            lines = content.split('\n')
            verbose_indicators = 0

            for line in lines:
                if len(line) > 120:  # Long lines
                    verbose_indicators += 1
                if line.strip().startswith('#') and len(line) > 50:  # Long comments
                    verbose_indicators += 1
                if 'for ' in line and 'in ' in line:  # Potential for comprehensions
                    verbose_indicators += 1

            # Calculate priority based on verbosity indicators
            priority = min(verbose_indicators / len(lines), 1.0) if lines else 0.0
            return priority

        except Exception:
            return 0.0

    async def _process_file(self, file_path: Path) -> Dict[str, any]:
        """Process a single file through The Loop."""
        file_results = {
            "file": str(file_path),
            "entropy_reduction": 0.0,
            "patterns_found": 0,
            "transformations_applied": 0
        }

        try:
            # Update focus in state
            self.state = set_focus(self.state, str(file_path), f"Compressing {file_path.name}", 0.0)

            # 1. Curiosity phase: Scan for patterns
            scan_result = await q_scan(str(file_path))
            patterns = scan_result.get("patterns", [])

            # 2. Check global knowledge before proceeding
            for pattern in patterns:
                pattern_type = pattern.get("type", "unknown")
                global_check = await query_global_patterns(pattern_type, "compression")

                if global_check.get("patterns_found"):
                    # Use existing pattern knowledge
                    file_results["patterns_found"] += 1

            # 3. Action phase: Apply abstractions (simplified for daemon mode)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()

            # Apply basic compression
            abstract_result = await a_abstract(original_content[:1000])  # Limit for performance
            if abstract_result.get("compressed"):
                # 4. Evaluation phase
                score_result = await s_score(original_content[:1000], abstract_result["compressed"])
                entropy_reduction = score_result.get("entropy_reduction", 0.0)

                file_results["entropy_reduction"] = entropy_reduction
                file_results["transformations_applied"] = 1

                # Update focus with score
                self.state = set_focus(self.state, str(file_path), "Processing complete", entropy_reduction)

            # Mark as processed
            self.processed_files.add(str(file_path))

            return file_results

        except Exception as e:
            self.console.print(f"[dim red]Error in _process_file: {e}[/dim red]")
            return file_results

    def _update_statistics(self, cycle_results: Dict[str, any]) -> None:
        """Update running statistics."""
        self.total_entropy_reduction += cycle_results["total_entropy_reduction"]

        # Update state log
        self.state = update_log(
            self.state,
            "s",
            f"cycle_{self.cycle_count}_entropy_{cycle_results['total_entropy_reduction']:.3f}"
        )

        # Save state periodically
        if self.cycle_count % 5 == 0:
            save_state(self.state, str(self.agent_dir))

    def _check_equilibrium(self, cycle_results: Dict[str, any]) -> None:
        """Check if equilibrium has been reached."""
        if cycle_results["files_processed"] == 0:
            self.equilibrium_reached = True
            return

        # Calculate improvement rate
        improvement_rate = (
            cycle_results["total_entropy_reduction"] / cycle_results["files_processed"]
            if cycle_results["files_processed"] > 0 else 0.0
        )

        if improvement_rate < (1.0 - self.equilibrium_threshold):
            equilibrium_files_ratio = (
                cycle_results["files_at_equilibrium"] / cycle_results["files_processed"]
                if cycle_results["files_processed"] > 0 else 0.0
            )

            if equilibrium_files_ratio > self.equilibrium_threshold:
                self.equilibrium_reached = True

    def _create_status_display(self) -> Table:
        """Create live status display table."""
        table = Table(title="4Q.Zero Autonomous Loop Status")

        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_column("Status", style="green")

        table.add_row("Cycle", str(self.cycle_count), "🔄 Running" if self.running else "⏹️ Stopped")
        table.add_row("Files Processed", str(len(self.processed_files)), "📁")
        table.add_row("Total Entropy Reduction", f"{self.total_entropy_reduction:.3f}", "🗜️")
        table.add_row("Equilibrium", "Yes" if self.equilibrium_reached else "No",
                     "⚖️ Balanced" if self.equilibrium_reached else "🔍 Searching")

        focus = self.state.get("focus", {})
        table.add_row("Current Focus", focus.get("target", "none")[:30] + "...", "🎯")

        return table

    async def _log_cycle(self, cycle_results: Dict[str, any], duration: float) -> None:
        """Log cycle completion details."""
        log_entry = (
            f"cycle_{self.cycle_count}: "
            f"files={cycle_results['files_processed']}, "
            f"entropy={cycle_results['total_entropy_reduction']:.3f}, "
            f"time={duration:.1f}s"
        )

        self.state = update_log(self.state, "a", log_entry)

    async def _generate_final_report(self, start_time: datetime, end_time: datetime) -> Dict[str, any]:
        """Generate comprehensive final report."""
        duration = end_time - start_time

        report = {
            "completion_reason": "equilibrium" if self.equilibrium_reached else "stopped",
            "total_cycles": self.cycle_count,
            "duration_seconds": duration.total_seconds(),
            "files_processed": len(self.processed_files),
            "total_entropy_reduction": self.total_entropy_reduction,
            "average_entropy_per_file": (
                self.total_entropy_reduction / len(self.processed_files)
                if self.processed_files else 0.0
            ),
            "patterns_discovered": len(self.state.get("patterns", {})),
            "final_state": self.state
        }

        # Save final state
        save_state(self.state, str(self.agent_dir))

        # Display final report
        self.console.print(Panel.fit(
            f"[bold green]4Q.Zero Autonomous Mode Complete[/bold green]\n\n"
            f"Reason: {report['completion_reason']}\n"
            f"Duration: {duration}\n"
            f"Cycles: {self.cycle_count}\n"
            f"Files Processed: {len(self.processed_files)}\n"
            f"Total Entropy Reduction: {self.total_entropy_reduction:.3f}\n"
            f"Patterns Discovered: {len(self.state.get('patterns', {}))}\n",
            border_style="green"
        ))

        return report

    def _start_file_watching(self) -> None:
        """Start watching target directory for file changes."""
        self.file_handler.daemon = self
        self.observer.schedule(self.file_handler, str(self.target_dir), recursive=True)
        self.observer.start()

    def _stop_file_watching(self) -> None:
        """Stop file watching."""
        self.observer.stop()
        self.observer.join()


class CodeChangeHandler(FileSystemEventHandler):
    """Handle file system events to trigger re-processing."""

    def __init__(self, daemon: AutonomousLoop):
        self.daemon = daemon

    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in {'.py', '.js', '.ts', '.rs', '.go', '.java'}:
                # Remove from processed files to trigger re-processing
                self.daemon.processed_files.discard(str(file_path))


async def main():
    """Main entry point for daemon mode."""
    import argparse

    parser = argparse.ArgumentParser(description="4Q.Zero Autonomous Daemon Mode")
    parser.add_argument("target_dir", help="Directory to process")
    parser.add_argument("--equilibrium", type=float, default=0.95,
                       help="Equilibrium threshold (0.0-1.0)")
    parser.add_argument("--interval", type=int, default=60,
                       help="Scan interval in seconds")
    parser.add_argument("--max-cycles", type=int, default=1000,
                       help="Maximum cycles before stopping")

    args = parser.parse_args()

    target_dir = Path(args.target_dir)
    if not target_dir.exists():
        print(f"❌ Target directory does not exist: {target_dir}")
        return 1

    # Create and run autonomous loop
    loop = AutonomousLoop(
        target_dir=target_dir,
        equilibrium_threshold=args.equilibrium,
        scan_interval=args.interval,
        max_cycles=args.max_cycles
    )

    try:
        report = await loop.run_continuous()
        return 0
    except KeyboardInterrupt:
        print("\n🛑 Daemon stopped by user")
        return 0
    except Exception as e:
        print(f"💥 Daemon failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)