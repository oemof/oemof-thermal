import os
import re
from difflib import unified_diff


def chop_trailing_whitespace(lines):
    return [re.sub(r'\s*$', '', l) for l in lines]


def remove(pattern, lines):
    if not pattern:
        return lines
    return re.subn(pattern, "", "\n".join(lines))[0].split("\n")


def normalize_to_positive_results(lines):
    negative_result_indices = [
        n for n, line in enumerate(lines)
        if re.match("^= -", line)]
    equation_start_indices = [
        [n for n in reversed(range(0, nri))
         if re.match('.*:$', lines[n])][0] + 1
        for nri in negative_result_indices]
    for (start, end) in zip(
            equation_start_indices,
            negative_result_indices):
        for n in range(start, end):
            lines[n] = (
                '-'
                if lines[n] and lines[n][0] == '+'
                else '+'
                if lines[n]
                else lines[n]) + lines[n][1:]
        lines[end] = '= ' + lines[end][3:]
    return lines


def compare_lp_files(lp_file_1, lp_file_2, ignored=None):
    lines_1 = remove(ignored, chop_trailing_whitespace(lp_file_1.readlines()))
    lines_2 = remove(ignored, chop_trailing_whitespace(lp_file_2.readlines()))

    lines_1 = normalize_to_positive_results(lines_1)
    lines_2 = normalize_to_positive_results(lines_2)

    if not lines_1 == lines_2:
        raise AssertionError(
            "Failed matching lp_file_1 with lp_file_2:\n"
            + "\n".join(
                unified_diff(
                    lines_1,
                    lines_2,
                    fromfile=os.path.relpath(
                        lp_file_1.name),
                    tofile=os.path.basename(
                        lp_file_2.name),
                    lineterm=""
                )
            ))
