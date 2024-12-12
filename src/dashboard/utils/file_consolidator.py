import concurrent.futures
import hashlib
import logging
import os
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Set, Tuple

from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Excluded directories and file patterns
EXCLUDED_DIRS = {
    "node_modules",
    "venv",
    "__pycache__",
    ".git",
    ".pytest_cache",
    "build",
    "dist",
    "coverage",
    ".vscode",
    ".idea",
}

EXCLUDED_FILES = {
    "*.pyc",
    "*.pyo",
    "*.pyd",
    "*.so",
    "*.dll",
    "*.dylib",
    "*.egg-info",
    "*.egg",
    "*.whl",
    ".DS_Store",
    "Thumbs.db",
    "*.log",
    "*.bak",
    "*.swp",
    "*.tmp",
}

# File patterns to consolidate
CONSOLIDATION_PATTERNS = [
    ("utils", r".*_utils\.py$", "src/dashboard/utils/consolidated_utils.py"),
    ("styles", r".*\.(css|scss)$", "src/dashboard/static/style/main.css"),
    ("types", r".*_types\.(ts|tsx)$", "src/dashboard/static/src/types.ts"),
    (
        "components",
        r".*_component\.(ts|tsx)$",
        "src/dashboard/components/components.tsx",
    ),
    ("tests", r".*_test\.py$", "tests/consolidated_tests.py"),
    ("api", r".*_api\.(ts|tsx)$", "src/dashboard/static/src/api/api.ts"),
]


@dataclass
class FileGroup:
    """Represents a group of similar files."""

    pattern: str
    files: List[Path]
    target_path: Path


class TimeoutError(Exception):
    """Raised when an operation times out."""


class FileConsolidator:
    """Handles efficient file consolidation and organization."""

    def __init__(self, root_dir: Path, batch_size: int = 10, timeout: int = 30):
        self.root_dir = Path(root_dir)
        self.batch_size = batch_size
        self.timeout = timeout
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.processed_files: Set[Path] = set()
        self.start_time = time.time()
        self.pbar = None

    def should_process_file(self, file_path: Path) -> bool:
        """Quick check if a file should be processed."""
        try:
            path_str = str(file_path)
            return (
                file_path.is_file()
                and not any(
                    f"/{d}/" in path_str or path_str.endswith(f"/{d}")
                    for d in EXCLUDED_DIRS
                )
                and not any(file_path.match(p) for p in EXCLUDED_FILES)
                and os.path.getsize(file_path)
                < 10 * 1024 * 1024  # Skip files larger than 10MB
            )
        except Exception:
            return False

    def compute_file_hash(self, file_path: Path, chunk_size: int = 8192) -> str:
        """Compute hash of file content in chunks with timeout."""
        try:
            hasher = hashlib.md5()
            with open(file_path, "rb") as f:
                while chunk := f.read(chunk_size):
                    if time.time() - self.start_time > self.timeout:
                        raise TimeoutError("Global timeout reached")
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.warning(f"Error hashing {file_path}: {e}")
            return ""

    def find_files_to_process(self) -> List[Path]:
        """Find all files that need to be processed."""
        files = []
        try:
            with tqdm(desc="Scanning files", unit=" dirs") as scan_pbar:
                for root, _, filenames in os.walk(self.root_dir):
                    if any(excluded in root for excluded in EXCLUDED_DIRS):
                        continue
                    root_path = Path(root)
                    current_files = [
                        root_path / f
                        for f in filenames
                        if self.should_process_file(root_path / f)
                    ]
                    files.extend(current_files)
                    scan_pbar.update(1)
        except Exception as e:
            logger.error(f"Error scanning files: {e}")
        return files

    def process_file_batch(self, files: List[Path]) -> List[Tuple[str, Path]]:
        """Process a batch of files with timeout protection."""
        results = []
        for f in files:
            try:
                if time.time() - self.start_time > self.timeout:
                    logger.warning("Global timeout reached")
                    break

                file_hash = self.compute_file_hash(f)
                if file_hash:
                    results.append((file_hash, f))
                if self.pbar:
                    self.pbar.update(1)
            except Exception as e:
                logger.error(f"Error processing {f}: {e}")
        return results

    def consolidate_group(self, group: FileGroup) -> None:
        """Consolidate a group of files with progress tracking."""
        if not group.files:
            return

        logger.info(f"Consolidating {len(group.files)} files into {group.target_path}")

        try:
            # Create target directory
            group.target_path.parent.mkdir(parents=True, exist_ok=True)

            # Read and consolidate content
            contents = []
            with tqdm(
                total=len(group.files),
                desc=f"Consolidating {group.target_path.name}",
                leave=False,
            ) as pbar:
                for file_path in sorted(group.files):
                    try:
                        with open(file_path) as f:
                            content = f.read().strip()
                            if content:
                                contents.append(
                                    f"\n# Source: {file_path.name}\n{content}"
                                )
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")
                    finally:
                        pbar.update(1)

            if contents:
                # Write consolidated file
                with open(group.target_path, "w") as f:
                    f.write("\n\n".join(contents))

                # Remove original files
                for file_path in group.files:
                    try:
                        if file_path.exists() and file_path != group.target_path:
                            file_path.unlink()
                    except Exception as e:
                        logger.error(f"Error removing {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error consolidating group {group.target_path}: {e}")

    def run(self) -> None:
        """Run the optimized file consolidation process."""
        logger.info("Starting file consolidation process...")
        self.start_time = time.time()

        try:
            # Find all files to process
            all_files = self.find_files_to_process()
            if not all_files:
                logger.info("No files to process")
                return

            logger.info(f"Found {len(all_files)} files to process")

            # Process files in smaller batches with progress bar
            file_batches = [
                all_files[i : i + self.batch_size]
                for i in range(0, len(all_files), self.batch_size)
            ]

            self.pbar = tqdm(total=len(all_files), desc="Processing files")

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                futures = []
                for batch in file_batches:
                    if time.time() - self.start_time > self.timeout:
                        logger.warning("Timeout reached")
                        break
                    future = executor.submit(self.process_file_batch, batch)
                    futures.append(future)

                # Process results as they complete
                for future in concurrent.futures.as_completed(futures):
                    try:
                        results = future.result(timeout=5)
                        for file_hash, file_path in results:
                            self.file_hashes[file_hash].append(file_path)
                    except concurrent.futures.TimeoutError:
                        logger.warning("Batch processing timeout")
                    except Exception as e:
                        logger.error(f"Error processing batch: {e}")

            self.pbar.close()

            # Handle duplicates
            duplicates = {
                h: files for h, files in self.file_hashes.items() if len(files) > 1
            }
            if duplicates:
                logger.info(f"Found {len(duplicates)} sets of duplicate files")
                with tqdm(duplicates.values(), desc="Removing duplicates") as dup_pbar:
                    for files in dup_pbar:
                        for file_path in files[1:]:
                            try:
                                if file_path.exists():
                                    file_path.unlink()
                            except Exception as e:
                                logger.error(
                                    f"Error removing duplicate {file_path}: {e}"
                                )

            # Consolidate similar files
            for name, pattern, target in CONSOLIDATION_PATTERNS:
                matching_files = []
                for file_path in all_files:
                    if re.match(pattern, str(file_path)):
                        matching_files.append(file_path)

                if matching_files:
                    group = FileGroup(pattern, matching_files, self.root_dir / target)
                    self.consolidate_group(group)

            # Final cleanup
            logger.info("Cleaning up empty directories...")
            with tqdm(desc="Cleaning directories", leave=True) as clean_pbar:
                for root, dirs, files in os.walk(self.root_dir, topdown=False):
                    try:
                        if (
                            not dirs
                            and not files
                            and not any(excluded in root for excluded in EXCLUDED_DIRS)
                        ):
                            try:
                                os.rmdir(root)
                                clean_pbar.update(1)
                            except OSError:
                                pass
                    except Exception as e:
                        logger.error(f"Error cleaning up {root}: {e}")

            duration = time.time() - self.start_time
            logger.info(f"File consolidation completed in {duration:.2f} seconds")
        except Exception as e:
            logger.error(f"Error during consolidation process: {e}")
            raise
        finally:
            if self.pbar:
                self.pbar.close()
