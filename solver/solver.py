import collections
import enum
import itertools
import time
from typing import List, Tuple
import random

import tqdm


class AdvanceResult(enum.Enum):
  ADVANCE_SUCCESS = 0
  TERMINATED = 1
  POPPED_EMPTY_BIN = 2
  END_OF_INSTRUCTION_BIN_REACHED = 3


def get_new_bins():
  bins = [[], [], [], [], [], [], [], [], [], []]
  bins[0] = [0] * 20
  return bins


def advance(bins: List[List[int]]) -> AdvanceResult:
  if len(bins[1]) < 2:
    return AdvanceResult.END_OF_INSTRUCTION_BIN_REACHED

  # Load
  instruction = bins[1].pop()
  param = bins[1].pop()

  # Execute
  if instruction == 0:    # STOP
    return AdvanceResult.TERMINATED
  elif instruction == 1:  # LOAD
    if not bins[param]:
      return AdvanceResult.POPPED_EMPTY_BIN
    bins[3].append(bins[param].pop())
  elif instruction == 2:  # STORE
    if not bins[3]:
      return AdvanceResult.POPPED_EMPTY_BIN
    bins[param].append(bins[3].pop())
  elif instruction == 3:  # ADD
    if not bins[3]:
      return AdvanceResult.POPPED_EMPTY_BIN
    bins[3][-1] = (bins[3][-1] + param) % 10
  elif instruction == 4:  # MUL
    if not bins[3]:
      return AdvanceResult.POPPED_EMPTY_BIN
    bins[3][-1] = (bins[3][-1] * param) % 10
  elif 5 <= instruction <= 7:  # NOP
    pass
  elif instruction == 8:
    if not bins[3]:
      return AdvanceResult.POPPED_EMPTY_BIN
    bins[bins[3][-1]] = bins[bins[3][-1]][::-1]
  elif instruction == 9:
    if not bins[3]:
      return AdvanceResult.POPPED_EMPTY_BIN
    target_bin = bins[3][-1]
    temp_bin = bins[param]
    bins[param] = bins[target_bin]
    bins[target_bin] = temp_bin
  else:
    raise RuntimeError(f'Invalid instruction')

  # Recycle
  bins[2].append(instruction)
  bins[2].append(param)

  return AdvanceResult.ADVANCE_SUCCESS


def run(bins: List[List[int]]) -> AdvanceResult:
  while True:
    result = advance(bins)
    if result != AdvanceResult.ADVANCE_SUCCESS:
      return result


def print_bins(bins):
  for i, cur_bin in enumerate(bins):
    print(f'{i}: {cur_bin[::-1]}')


def load_program(program: int) -> List[List[int]]:
  bins = get_new_bins()
  while program:
    bins[1].append(program % 10)
    program = program // 10
  return bins


def solver():
  num_valid_progs = 0
  num_solutions = 0
  for i in tqdm.tqdm(range(1000000000)):
    bins = load_program(i)
    if run(bins) != AdvanceResult.TERMINATED:
      continue
    num_valid_progs += 1
    if bins[9] == [3, 3, 3]:
      num_solutions += 1
      print(f'Found solution: {i}')

  print(f'Finished scan up to {i}, found {num_valid_progs} valid programs '
        f'and {num_solutions} solutions.')


def smart_solver(num_shirts):
  max_num = int('1' + ('0' * num_shirts))
  num_valid_progs = 0
  num_solutions = 0
  bad_prefixes_by_len = collections.defaultdict(set)
  for prefix in tqdm.tqdm(range(max_num // 1000)):
    is_bad_prefix = False
    prefix_str = str(prefix)
    for i in range(1, len(prefix_str) + 1):
      if prefix_str[:i] in bad_prefixes_by_len[i]:
        is_bad_prefix = True
        break
    if is_bad_prefix:
      continue
    all_suffixes_failed = True
    for suffix in range(1000):
      program = prefix * 1000 + suffix
      bins = load_program(program)
      result = run(bins)
      if result == AdvanceResult.POPPED_EMPTY_BIN:
        continue
      all_suffixes_failed = False
      if result == AdvanceResult.END_OF_INSTRUCTION_BIN_REACHED:
        # Semi-valid program
        continue
      # Valid program
      num_valid_progs += 1
      if bins[9] == [3, 3, 3]:
        num_solutions += 1
        print(f'Found solution: {program}')
    if all_suffixes_failed:
      bad_prefix = str(prefix)
      bad_prefixes_by_len[len(bad_prefix)].add(bad_prefix)

  num_bad_prefixes = sum(
      len(bad_prefix) for bad_prefix in bad_prefixes_by_len.values())
  print(f'To solve for {num_shirts} shirts:')
  print(f'Scanned {num_valid_progs} valid progs, found {num_solutions} '
        f'solutions and {num_bad_prefixes} bad prefixes.')


def main():
  start_time = time.time()
  smart_solver(10)
  end_time = time.time()
  print(f'Calculation took {end_time - start_time:.1f} seconds.')

  # start_time = time.time()
  # solver()
  # end_time = time.time()
  # print(f'Calculation took {end_time - start_time:.1f} seconds.')


if __name__ == '__main__':
  main()
