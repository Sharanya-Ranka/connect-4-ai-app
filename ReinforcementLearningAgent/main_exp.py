import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

from Experiments import model_checks
from config import TEST_CONFIG

if __name__ == "__main__":
    mt = model_checks.ModelTesting(TEST_CONFIG)
    mt.performTest()
