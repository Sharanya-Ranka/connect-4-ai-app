import time
from concurrent.futures import ProcessPoolExecutor, as_completed
import os


import numpy as np


def perform_matrix_multiplication_parallel(size, worker_id):
    """
    Generates two random matrices and multiplies them.
    This function will be run in a separate process.
    """
    pid = os.getpid()
    print(f"Worker {worker_id} (PID: {pid}) starting matrix multiplication...")

    A = np.random.rand(size, size)
    B = np.random.rand(size, size)

    start_time = time.time()
    _ = A @ B  # Matrix multiplication
    end_time = time.time()

    elapsed_time = end_time - start_time
    print(f"Worker {worker_id} (PID: {pid}) finished in {elapsed_time:.4f} seconds.")
    return elapsed_time


if __name__ == "__main__":
    # Define matrix size
    matrix_size = 5000

    # Number of matrix multiplications to perform
    num_multiplications = 8

    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["OMP_NUM_THREADS"] = "1"

    # Get the number of available logical cores
    num_cores = os.cpu_count()
    if num_cores is None:
        num_cores = 1

    print(
        f"Starting {num_multiplications} matrix multiplications (size: {matrix_size}x{matrix_size}) using a pool of {num_cores} processes."
    )

    # List of worker IDs
    worker_ids = list(range(num_multiplications))

    total_time = 0
    start_all = time.time()

    with ProcessPoolExecutor(max_workers=num_cores) as executor:
        # Submit all tasks to the executor
        futures = {
            executor.submit(
                perform_matrix_multiplication_parallel, matrix_size, worker_id
            )
            for worker_id in worker_ids
        }

        # Wait for all futures to complete
        for future in as_completed(futures):
            elapsed_time = future.result()
            total_time += elapsed_time

    end_all = time.time()

    print(
        f"\nTotal time elapsed for all {num_multiplications} multiplications to complete: {(end_all - start_all):.4f} seconds."
    )
    print(f"Note: This total elapsed time is what matters for your throughput.")
