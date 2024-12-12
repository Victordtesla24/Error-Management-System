"""Performance tests for error management system."""

import asyncio
import time
from pathlib import Path

import pytest
import pytest_asyncio

from src.error_management.models import ErrorModel
from src.error_management.service import ErrorManagementService


def get_process_memory() -> float:
    """Get current process memory usage."""
    import psutil

    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)  # Convert to MB


@pytest_asyncio.fixture
async def service(test_project_path: Path) -> ErrorManagementService:
    """Create error management service instance."""
    service = ErrorManagementService(project_path=test_project_path)
    await service.start()
    yield service
    await service.stop()


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_usage_benchmarks(
    service: ErrorManagementService, tmp_path: Path
) -> None:
    """Test memory usage under various conditions."""
    # Record baseline memory
    baseline_memory = get_process_memory()

    # Create test files and errors
    test_files = []
    errors = []
    for i in range(10):
        test_file = tmp_path / f"test_{i}.py"
        test_file.write_text(f"def test_{i}(): pass")
        test_files.append(test_file)

        error = ErrorModel(
            id=f"{test_file}:1",
            file_path=test_file,
            line_number=1,
            error_type="Style",
            message=f"Test error {i}",
        )
        errors.append(error)

    # Add errors and measure memory
    for error in errors:
        await service.add_error(error)
        await asyncio.sleep(0.1)  # Allow time for processing

    # Verify memory usage
    current_memory = get_process_memory()
    memory_increase = current_memory - baseline_memory

    # Memory increase should be reasonable (less than 100MB)
    assert memory_increase < 100, f"Memory increase too high: {memory_increase}MB"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_error_processing_performance(
    service: ErrorManagementService, tmp_path: Path
) -> None:
    """Test error processing response times."""
    # Create test file
    test_file = tmp_path / "test.py"
    test_file.write_text("def test(): pass")

    # Measure error creation and processing times
    processing_times = []

    for i in range(10):
        error = ErrorModel(
            id=f"{test_file}:{i}",
            file_path=test_file,
            line_number=i,
            error_type="Style",
            message=f"Test error {i}",
        )

        start_time = time.time()
        await service.add_error(error)
        processing_time = time.time() - start_time
        processing_times.append(processing_time)

        await asyncio.sleep(0.1)  # Allow time for processing

    # Calculate average processing time
    avg_time = sum(processing_times) / len(processing_times)

    # Processing should be fast (less than 1 second per error)
    assert avg_time < 1.0, f"Average processing time too high: {avg_time}s"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_performance(
    service: ErrorManagementService, tmp_path: Path
) -> None:
    """Test system performance under concurrent operations."""
    # Record baseline memory
    baseline_memory = get_process_memory()

    # Create multiple test files
    files = []
    for i in range(5):
        test_file = tmp_path / f"test_{i}.py"
        test_file.write_text(f"def test_{i}(): pass")
        files.append(test_file)

    # Create multiple errors concurrently
    start_time = time.time()

    tasks = []
    for i, file in enumerate(files):
        error = ErrorModel(
            id=f"{file}:{i}",
            file_path=file,
            line_number=1,
            error_type="Style",
            message=f"Test error {i}",
        )
        tasks.append(service.add_error(error))

    # Wait for all tasks to complete
    await asyncio.gather(*tasks)

    total_time = time.time() - start_time
    current_memory = get_process_memory()
    memory_increase = current_memory - baseline_memory

    # Verify performance metrics
    assert total_time < 5.0, f"Concurrent processing too slow: {total_time}s"
    assert memory_increase < 100, f"Memory increase too high: {memory_increase}MB"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_system_scalability(
    service: ErrorManagementService, tmp_path: Path
) -> None:
    """Test system scalability with increasing load."""
    baseline_memory = get_process_memory()

    # Test with increasing numbers of errors
    error_counts = [10, 50, 100]
    processing_times = []
    memory_usage = []

    for count in error_counts:
        start_time = time.time()
        start_memory = get_process_memory()

        # Create and process multiple errors
        tasks = []
        for i in range(count):
            test_file = tmp_path / f"test_{i}.py"
            test_file.write_text(f"def test_{i}(): pass")

            error = ErrorModel(
                id=f"{test_file}:1",
                file_path=test_file,
                line_number=1,
                error_type="Style",
                message=f"Test error {i}",
            )
            tasks.append(service.add_error(error))

        # Wait for all tasks to complete
        await asyncio.gather(*tasks)

        # Record metrics
        processing_time = time.time() - start_time
        memory_used = get_process_memory() - start_memory

        processing_times.append(processing_time)
        memory_usage.append(memory_used)

        await asyncio.sleep(0.1)  # Allow time for cleanup

    # Verify scalability metrics
    for i in range(1, len(error_counts)):
        # Processing time should scale sub-linearly
        time_ratio = processing_times[i] / processing_times[i - 1]
        count_ratio = error_counts[i] / error_counts[i - 1]
        assert time_ratio < count_ratio, "Processing time scaling poorly"

        # Memory usage should scale sub-linearly
        memory_ratio = memory_usage[i] / memory_usage[i - 1]
        assert memory_ratio < count_ratio, "Memory usage scaling poorly"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_token_usage_optimization(
    service: ErrorManagementService, tmp_path: Path
) -> None:
    """Test token usage optimization."""
    # Create test file with varying content sizes
    sizes = [100, 500, 1000]  # Lines of code
    token_usage = []

    for size in sizes:
        test_file = tmp_path / f"test_{size}.py"
        content = "\n".join([f"def test_{i}(): pass" for i in range(size)])
        test_file.write_text(content)

        error = ErrorModel(
            id=f"{test_file}:1",
            file_path=test_file,
            line_number=1,
            error_type="Style",
            message="Test error",
        )

        # Measure token usage
        start_tokens = service.get_token_usage()
        await service.add_error(error)
        end_tokens = service.get_token_usage()

        token_usage.append(end_tokens - start_tokens)

        await asyncio.sleep(0.1)  # Allow time for processing

    # Verify token usage optimization
    for i in range(1, len(sizes)):
        # Token usage should scale sub-linearly with file size
        token_ratio = token_usage[i] / token_usage[i - 1]
        size_ratio = sizes[i] / sizes[i - 1]
        assert token_ratio < size_ratio, "Token usage not optimized for larger files"
