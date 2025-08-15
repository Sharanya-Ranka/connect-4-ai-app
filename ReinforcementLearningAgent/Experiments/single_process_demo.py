import time
import os

os.environ["OPENBLAS_NUM_THREADS"] = "64"
# os.environ["MKL_NUM_THREADS"] = "2"
# os.environ["OMP_NUM_THREADS"] = "8"
# from threadpoolctl import threadpool_info



import numpy as np
# print(threadpool_info())
# print(np.show_config())

def perform_matrix_multiplication(size):
    """Generates two random matrices and multiplies them."""
    A = np.random.rand(size, size)
    B = np.random.rand(size, size)
    start_time = time.time()
    _ = A @ B  # Use the "@" operator for matrix multiplication
    end_time = time.time()
    return end_time - start_time


if __name__ == "__main__":
    # Define matrix size
    matrix_size = 5000  # A good size to show significant computation

    

    # Number of matrix multiplications to perform
    num_multiplications = 8

    print(
        f"Starting {num_multiplications} matrix multiplications (size: {matrix_size}x{matrix_size}) in a single process."
    )

    total_time = 0
    for i in range(num_multiplications):
        print(f"  Performing multiplication {i+1}...")
        elapsed_time = perform_matrix_multiplication(matrix_size)
        total_time += elapsed_time
        print(f"  Multiplication {i+1} took {elapsed_time:.4f} seconds.")

    print(
        f"\nTotal time for {num_multiplications} single-process multiplications: {total_time:.4f} seconds."
    )
