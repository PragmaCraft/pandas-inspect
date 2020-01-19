import sys
import os
import runpy
import argparse

from .tracer import Tracer


def main():
    parser = argparse.ArgumentParser(description='Dynamically analyze pandas code.')

    parser.add_argument('--include', '-i', nargs='+', help='include directories to analyze')
    parser.add_argument('--exclude', '-e', nargs='+', help='exclude directories from analyze')
    parser.add_argument('--output', '-o', nargs=1, help='path to output csv file')
    parser.add_argument('--output-excel', nargs=1, help='path to output excel file')
    parser.add_argument('--heads', nargs=1, help='directory to write df heads')
    parser.add_argument('module', help='path to python module to execute')
    parser.add_argument('arguments', nargs='*', help='arguments for the given module')

    args = parser.parse_args()

    if not args.include:
        sys.stderr.write('Please use --include to specify at least one directory to analyze\n')
        sys.exit(1)

    if not args.output:
        sys.stderr.write('Please use --output to specify output path\n')
        sys.exit(1)

    include_paths = args.include
    exclude_paths = args.exclude or []

    # convert included/excluded paths to absolute paths
    include_paths = list(map(os.path.abspath, include_paths))
    exclude_paths = list(map(os.path.abspath, exclude_paths))

    heads_dir = None
    if args.heads:
        heads_dir = args.heads[0]

    excel_output_path = None
    if args.output_excel:
        excel_output_path = args.output_excel[0]

    # Initialize tracer
    tracer = Tracer(include_paths=include_paths, exclude_paths=exclude_paths,
                    output_path=args.output[0], heads_dir=heads_dir, excel_output_path=excel_output_path)

    module_path = os.path.abspath(args.module)
    arguments = args.arguments

    # Modify sys.argv
    sys.argv = [module_path] + arguments

    # Modify sys.path[0] to module's directory
    sys.path[0] = os.path.abspath(os.path.dirname(module_path))

    tracer.start()

    # Run the module
    runpy.run_path(module_path, run_name='__main__')

    tracer.stop()
