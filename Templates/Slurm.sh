#!/bin/bash
#SBATCH -p {{queue}}
#SBATCH -N 1 # number of nodes
#SBATCH -n 1 # number of tasks
#SBATCH --cpus-per-task {{threads}}
{{#email}}
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user={{email}}
{{/email}}

RUN_ID="{{run_id}}"

# Project location
export CMAKE_PROJECT_PATH="{{cmake_project_path}}"
BINARY_TAG="{{binary_tag}}"
OUTPUT_DIR="{{output_dir}}"

# Resources to use
NCORES=${SLURM_JOB_CPUS_PER_NODE:-1}

# Should not be needed since pull request #351
export MKL_NUM_THREADS=1
export MKL_DYNAMIC="FALSE"
export OMP_NUM_THREADS=1
export OMP_DYNAMIC="FALSE"

# Working area
pushd "{{benchmark.path}}"

# Run using the profiler
${CMAKE_PROJECT_PATH}/SourceXtractorTools/build.${BINARY_TAG}/run RunProfiled \
  -b "${BINARY_TAG}" \
  --log "${OUTPUT_DIR}/sx_${RUN_ID}.log" \
  --pidstat "${OUTPUT_DIR}/sx_${RUN_ID}.pidstat" \
  --use-version "{{benchmark.branch}}" \
  -- \
  --conf "{{benchmark.configuration}}" \
  --output-catalog-filename "{{benchmark.catalog}}" \
  --thread-count ${NCORES} \
  --progress-bar-disable

popd
