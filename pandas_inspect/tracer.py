import csv
import sys
from typing import List, Optional
import os
from collections import defaultdict

import pandas as pd


class LocalTracer:
    def __init__(self, frame):
        self.local_reprs = self._get_local_reprs(frame.f_locals)
        self.code_line = self._get_code_line(frame)

    def _dict_diff(self, d1, d2):
        diff = {}
        for k, v in d1.items():
            if k not in d2 or not self._values_equal(v, d2[k]):
                diff[k] = v
        return diff

    def _values_equal(self, val1, val2):
        return val1 == val2

    def get_difference(self, frame):
        new_local_reprs = self._get_local_reprs(frame.f_locals)

        difference = self._dict_diff(new_local_reprs, self.local_reprs)
        old_code_line = self.code_line

        self.local_reprs = new_local_reprs
        self.code_line = self._get_code_line(frame)

        return old_code_line, difference

    def _get_var_repr(self, var):
        if isinstance(var, pd.DataFrame):
            return f'DataFrame[{tuple(var.columns)}]'
        elif isinstance(var, pd.Series):
            return f'Series[{var.dtype}]'
        elif isinstance(var, (int, str)):
            return f'{repr(var)}'
        else:
            return None

    @staticmethod
    def _get_code_line(frame):
        return (
            frame.f_code.co_filename,
            frame.f_lineno
        )

    def _get_local_reprs(self, locals):
        local_reprs = {}
        for name, val in locals.items():
            var_repr = self._get_var_repr(val)
            if var_repr is not None:
                local_reprs[name] = var_repr
        return local_reprs


class HeadTracer(LocalTracer):
    def _get_var_repr(self, var):
        if isinstance(var, pd.DataFrame):
            return var.head()

    def _values_equal(self, val1, val2):
        return val1.equals(val2)


class LocalHeadWriter:
    def __init__(self, dir: str, code_name: str, function_name: str):
        self._dir = dir
        self._code_name = code_name
        self._function_name = function_name
        self._excel_path = self.make_excel_path(dir, code_name, function_name)
        self._row_counts = defaultdict(int)
        self._writer: Optional[pd.ExcelWriter] = None

    def open(self):
        self._writer = pd.ExcelWriter(self._excel_path)

    def close(self):
        if self._row_counts:
            self._writer.close()
        self._writer = None

    @staticmethod
    def make_excel_path(dir, code_name, function_name):
        # TODO do sth better than replacing with __
        filename = f'{code_name.replace("/", "__")}:{function_name}.xlsx'
        return os.path.join(dir, filename)

    def write(self, var_name, df_head: pd.DataFrame, code_line):
        assert self._writer is not None, 'Excel file not opened'

        rows_written = self._row_counts[var_name]
        pd.DataFrame({
            'code': [code_line[0]],
            'line_no': [code_line[1]],
            'df_name': [var_name]
        }).to_excel(self._writer, sheet_name=var_name, startrow=(rows_written + 1))
        df_head.to_excel(self._writer, sheet_name=var_name, startrow=(rows_written + 3))

        self._row_counts[var_name] += len(df_head) + df_head.index.nlevels + 3


class Tracer:
    def __init__(self, include_paths: List[str], exclude_paths: List[str],
                 output_path: str, heads_dir=None, excel_output_path=None) -> None:
        self._include_paths = include_paths
        self._exclude_paths = exclude_paths
        self._last_code_line = None
        self._local_tracers: List[LocalTracer] = []
        self._output_path = output_path
        self._output_stream = None
        self._csv_writer = None
        self._state = 'pending'
        self._heads = False
        if heads_dir:
            self._heads = True
            self._heads_dir = heads_dir
            self._head_tracers: List[HeadTracer] = []
            self._head_writers: List[LocalHeadWriter] = []

        self._excel_output_path = excel_output_path

    def _write_head(self, df: pd.DataFrame, sheet_name: str):
        df.head().to_excel(self._head_writers[-1], sheet_name=sheet_name)

    def _find_domain(self, filepath):
        for exclude_path in self._exclude_paths:
            if filepath.startswith(exclude_path):
                return None
        for include_path in self._include_paths:
            if filepath.startswith(include_path):
                return include_path
        return None

    def _handle_call(self, frame):
        filepath = frame.f_code.co_filename
        domain = self._find_domain(filepath)
        if domain is not None:
            if not os.path.isdir(domain):
                domain = os.path.dirname(domain)
            relative_filepath = os.path.relpath(filepath, domain)

            frame.f_trace = self
            self._local_tracers.append(LocalTracer(frame))
            if self._heads:
                self._head_tracers.append(HeadTracer(frame))
                head_writer = LocalHeadWriter(dir=self._heads_dir,
                                              code_name=relative_filepath,
                                              function_name=frame.f_code.co_name)
                head_writer.open()
                self._head_writers.append(head_writer)

            self._last_code_line = frame.f_lineno

    def _handle_return(self, frame, arg):
        # to consider the effect of the last line in a function
        self._handle_line(frame)

        self._local_tracers.pop()
        if self._heads:
            self._head_tracers.pop()
            head_writer = self._head_writers.pop()
            head_writer.close()

    def _handle_heads(self, frame):
        tracer = self._head_tracers[-1]
        code_line, difference = tracer.get_difference(frame)

        for var_name, df_head in difference.items():
            self._head_writers[-1].write(var_name, df_head, code_line)

    def _handle_line(self, frame):
        code_line, difference = self._local_tracers[-1].get_difference(frame)

        for var_name, var_repr in difference.items():
            self._csv_writer.writerow([
                '{}:{}'.format(*code_line),
                var_name,
                var_repr
            ])

        self._output_stream.flush()

        if self._heads:
            self._handle_heads(frame)

    def __call__(self, frame, event, arg):
        if event == 'call':
            return self._handle_call(frame)
        elif event == 'return':
            return self._handle_return(frame, arg)
        elif event == 'line':
            return self._handle_line(frame)

    def start(self):
        if self._state != 'pending':
            return
        self._state = 'running'

        sys.settrace(self)

        # open output file
        self._output_stream = open(self._output_path, 'w', encoding='utf-8')
        self._csv_writer = csv.writer(self._output_stream)

        # write header
        self._csv_writer.writerow(['code_line', 'variable', 'value_repr'])

    def stop(self):
        if self._state != 'running':
            return
        self._state = 'stopped'

        sys.settrace(None)
        self._output_stream.close()

        if self._excel_output_path:
            pd.read_csv(self._output_path).to_excel(self._excel_output_path)
