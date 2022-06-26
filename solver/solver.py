import enum
import itertools
import time
from typing import Tuple
import random


class AdvanceResult(enum.Enum):
  SUCCESS = 1
  POPPED_EMPTY_STACK = 2
  END_OF_INSTRUCTION_BIN_REACHED = 3


class EndOfInstructionBinReached(Exception):
  """This is a special type of 'pop empty bin' error because we want to allow
  it while running a recursive solve."""
  pass


def get_new_bins():
  bins = [[], [], [], [], [], [], [], [], [], []]
  bins[0] = [0] * 20
  return bins


def advance(bins):
  if len(bins[1]) < 2:
    raise EndOfInstructionBinReached()

  # Load
  instruction = bins[1].pop()
  param = bins[1].pop()

  # Execute
  if instruction == 0:    # STOP
    raise StopIteration()
  elif instruction == 1:  # LOAD
    bins[3].append(bins[param].pop())
  elif instruction == 2:  # STORE
    bins[param].append(bins[3].pop())
  elif instruction == 3:  # ADD
    bins[3][-1] = (bins[3][-1] + param) % 10
  elif instruction == 4:  # MUL
    bins[3][-1] = (bins[3][-1] * param) % 10
  elif 5 <= instruction <= 7:  # NOP
    pass
  elif instruction == 8:
    bins[bins[3][-1]] = bins[bins[3][-1]][::-1]
  elif instruction == 9:
    target_bin = bins[3][-1]
    temp_bin = bins[param]
    bins[param] = bins[target_bin]
    bins[target_bin] = temp_bin
  else:
    raise RuntimeError(f'Invalid instruction: {instruction}')

  # Recycle
  bins[2].append(instruction)
  bins[2].append(param)


def run(bins):
  while True:
    try:
      advance(bins)
    except StopIteration:
      return


def print_bins(bins):
  for i, cur_bin in enumerate(bins):
    print(f'{i}: {cur_bin[::-1]}')


def load_program(program: int):
  bins = get_new_bins()
  while program:
    bins[1].append(program % 10)
    program = program // 10
  return bins


def solver():
  num_valid_progs = 0
  num_solutions = 0
  for i in range(1000000):
    if i % 1000000 == 0:
      print(f'Checking program {i}')
    bins = load_program(i)
    try:
      run(bins)
    except IndexError:
      # Invalid program.
      continue
    num_valid_progs += 1
    if bins[9] == [3, 3, 3]:
      num_solutions += 1
      print(f'Found solution: {i}')

  print(f'Finished scan up to {i}, found {num_valid_progs} valid programs '
        f'and {num_solutions} solutions.')


# SUFFIXES = list(itertools.product(range(10), range(10), range(10)))
SUFFIXES = list(itertools.product(range(10), range(10)))
DISALLOWED_PREFIXES = [(1, 0, 0), (1, 0, 9, 1)]

num_progs = 0
num_valid_progs = 0
num_solutions = 0
checked = set()


def recursive_solver(prefix: Tuple[int, ...], max_len: int) -> None:
  global num_progs, num_valid_progs, num_solutions, checked
  end_of_instruction_bin_reached = False
  for suffix in SUFFIXES:
    bins = get_new_bins()
    program = prefix + suffix
    if program in checked:
      continue
    checked.add(program)
    num_progs += 1
    if len(program) > max_len:
      continue
    if any(program[:len(disallowed_prefix)] == disallowed_prefix
           for disallowed_prefix in DISALLOWED_PREFIXES):
      continue
    bins[1] = list(program[::-1])
    try:
      run(bins)
    except EndOfInstructionBinReached:
      # Allow recursion into programs which are valid except for terminating
      # without a Stop statement.
      end_of_instruction_bin_reached = True
    except IndexError:
      continue  # Invalid program.
    if random.random() < 1e-4:
      if end_of_instruction_bin_reached:
        print(f'Semi-valid program: {program}')
      else:
        print(f'Valid program: {program}')
    num_valid_progs += 1
    if bins[9] == [3, 3, 3]:
      num_solutions += 1
      if end_of_instruction_bin_reached:
        print(f'Found semi-solution: {program}')
      else:
        print(f'Found solution: {program}')
    recursive_solver(program, max_len)


def test_run1():
  bins = load_program(1033103310339900)
  run(bins)
  print_bins(bins)


def test_run2():
  bins = load_program(1131131139900)
  run(bins)
  print_bins(bins)


def test_run3():
  bins = load_program(10993199333)
  run(bins)
  print_bins(bins)


def test_invalid_run():
  bins = load_program(10)
  run(bins)


def main():
  global num_progs, num_valid_progs, num_solutions
  start_time = time.time()
  recursive_solver((1, 0), max_len=10)
  end_time = time.time()
  print(f'Found {num_progs} programs, '
        f'of which {num_valid_progs} were valid programs '
        f'and {num_solutions} were solutions.')
  print(f'Calculation took {end_time - start_time:.1f} seconds.')
  # solver()
  # test_run3()
  # test_invalid_run()


if __name__ == '__main__':
  main()
