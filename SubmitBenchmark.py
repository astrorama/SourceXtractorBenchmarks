#
# Copyright (C) 2012-2020 Euclid Science Ground Segment
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3.0 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#
import argparse
import logging
import os.path
import sys
from glob import iglob

import chevron

SelfDir = os.path.split(__file__)[0]
TemplateDir = os.path.join(SelfDir, 'Templates')
JobDir = os.path.join(SelfDir, 'Jobs')
OutputDir = os.path.join(SelfDir, 'Output')

logger = logging.getLogger(__name__)


def generateRunId(args):
    if args.run_id:
        return args.run_id
    return f'{args.branch if args.branch else "default"}_{args.thread_count}'


def generateJob(args):
    """
    Generate the slurm job
    """
    logger.info(f'Generating slurm job for {args.binary_tag}, {args.thread_count} cores')
    if args.branch:
        logger.info(f'Using branch {args.branch}')
    else:
        logger.info('Using default version lookup')

    run_id = generateRunId(args)
    bench_dir = os.path.join(SelfDir, 'Benchmarks', args.benchmark)
    job_dir = os.path.join(JobDir, args.benchmark)

    template_params = {
        'queue': args.queue,
        'threads': args.thread_count,
        'email': args.email,
        'run_id': run_id,
        'cmake_project_path': args.project_path,
        'binary_tag': args.binary_tag,
        'output_dir': os.path.join(args.output_dir, args.benchmark),
        'benchmark': {
            'path': bench_dir,
            'configuration': next(iter(iglob(os.path.join(bench_dir, '*.conf')))),
            'branch': args.branch,
        },
    }

    with open(args.template, 'r') as fd:
        rendered = chevron.render(fd, template_params)

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(job_dir, exist_ok=True)

    output = os.path.join(job_dir, f'slurm_{run_id}.sh')
    with open(output, 'w') as fd:
        fd.write(rendered)
    print('Written', output)


def defineSpecificProgramOptions():
    """
    @brief Allows to define the (command line and configuration file) options
    specific to this program
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('--queue', type=str, default='p4', help='Slurm squeue')
    parser.add_argument('--thread-count', type=int, default=16, help='Passed to Slurm via --cpus-per-task')
    parser.add_argument('--template', type=str, default=os.path.join(TemplateDir, 'Slurm.sh'), help='Template file')
    parser.add_argument('--run-id', type=str, default=None, help='Run ID, used for the log and output files')
    parser.add_argument('--job-dir', type=str, default=JobDir, help='Write the slurm batch jobs here')
    parser.add_argument('--output-dir', type=str, default=OutputDir, help='Output dir')
    parser.add_argument('--branch', type=str, default=None)
    parser.add_argument('--binary-tag', type=str, metavar='BINARY_TAG', default=os.getenv('BINARY_TAG'))
    parser.add_argument('--project-path', type=str, metavar='CMAKE_PROJECT_PATH',
                        default=os.getenv('CMAKE_PROJECT_PATH'))
    parser.add_argument('--email', type=str, metavar='EMAIL', help='Tell Slurm to report to this email')
    parser.add_argument('benchmark', type=str, metavar='BENCHMARK')

    return parser


if __name__ == '__main__':
    parser = defineSpecificProgramOptions()
    args = parser.parse_args()
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler(sys.stderr))
    generateJob(args)
