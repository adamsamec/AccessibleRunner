import os
import sys

import cx_Freeze

sys.path.append(os.path.realpath(sys.path[0] + '\\..\\src'))

options = {
  'build_exe': '..\\build\\cx_Freeze\\AccessibleRunner'
}
executables = [cx_Freeze.Executable('..\\src\\AccessibleRunner.py',
  base = 'Win32GUI',
  targetName = 'AccessibleRunner.exe'
  )]

cx_Freeze.setup(
  name = 'AccessibleRunner' ,
  version = '1.0' ,
  description = 'Utility for running console commands with screen reader accessible output.',
  options = {'build_exe': options},
  executables = executables
  )
