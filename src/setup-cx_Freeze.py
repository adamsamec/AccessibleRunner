import cx_Freeze

options = {
  'build_exe': '..\\build\\AccessibleRunner-cx_Freeze'
}
executables = [cx_Freeze.Executable('AccessibleRunner.py',
  base = 'Win32GUI',
  targetName = 'AccessibleRunner.exe'
  )]

cx_Freeze.setup(name = 'AccessibleRunner' ,
  version = '1.0' ,
  description = 'Utility for running console commands with screen reader accessible output.',
  options = {'build_exe': options},
  executables = executables
  )
