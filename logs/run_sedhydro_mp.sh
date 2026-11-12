#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=30
#SBATCH --mem=220G
#SBATCH --time=2-00:00:00
#SBATCH --partition=cpu2021,cpu2022,cpu2023,cpu2025
#SBATCH --job-name=SedHydro_mp
#SBATCH --output=/work/comphyd_lab/users/arman.haddadchi/SedHydro/logs/SedHydro_mp_%j.out
#SBATCH --error=/work/comphyd_lab/users/arman.haddadchi/SedHydro/logs/SedHydro_mp_%j.err
#SBATCH --mail-user=arman.haddadchi@ucalgary.ca
#SBATCH --mail-type=END,FAIL

set -euo pipefail

# =========================================================
# Directories and configuration
# =========================================================

SEDHYDRO_DIR="/work/comphyd_lab/users/arman.haddadchi/SedHydro"

# Configuration passed to sbatch
TOML_FILE="${1:-directory_settings_Hay.toml}"

echo "========================================================"
echo "SedHydro multiprocessing calibration"
echo "========================================================"
echo "Job ID        : ${SLURM_JOB_ID}"
echo "Start time    : $(date)"
echo "Node          : $(hostname)"
echo "CPUs          : ${SLURM_CPUS_PER_TASK}"
echo "Memory        : ${SLURM_MEM_PER_NODE:-unknown} MB"
echo "Configuration : ${TOML_FILE}"
echo "========================================================"

# =========================================================
# Load ARC environment
# =========================================================

module --force purge
module load conda/base

conda activate erosionmodel

# =========================================================
# Set working directory
# =========================================================

cd "${SEDHYDRO_DIR}"

# Verify configuration exists
if [[ ! -f "${TOML_FILE}" ]]; then
    echo "ERROR: Configuration file not found: ${TOML_FILE}"
    exit 1
fi

# =========================================================
# Prevent thread oversubscription
# =========================================================

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

# =========================================================
# Verify Python environment
# =========================================================

echo "Python executable: $(which python)"
python --version

# =========================================================
# Run SedHydro
# =========================================================

echo "Starting SedHydro at $(date)"

python -u SedHydro_mp.py "${TOML_FILE}"

echo "========================================================"
echo "SedHydro completed successfully"
echo "End time: $(date)"
echo "========================================================"
