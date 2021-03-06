# (c) Didier  LECLERC 2020 CMSIG MTE-MCTRCT/SG/SNUM/UNI/DRC Site de Rouen
# créé sept 2021
import os.path
import subprocess
import sys

#==================================================
def manageLibrary(mBibli) :
    if mBibli == "RDFLIB" :
       try:
           subprocess.check_call(['python3', '-m', 'pip', 'install', '--upgrade', 'pip'])
       except :
           pass
           
       # WHEEL
       mPathPerso = os.path.dirname(__file__) + '\\wheel-0.37.1-py2.py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # SIX
       mPathPerso = os.path.dirname(__file__) + '\\six-1.16.0-py2.py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # ISODATE
       mPathPerso = os.path.dirname(__file__) + '\\isodate-0.6.1-py2.py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # PYPARSING
       mPathPerso = os.path.dirname(__file__) + '\\pyparsing-3.0.7-py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # SETUPTOOLS
       mPathPerso = os.path.dirname(__file__) + '\\setuptools-61.2.0-py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       if sys.version_info < (3, 8) :
          # ZIPP
          mPathPerso = os.path.dirname(__file__) + '\\zipp-3.7.0-py3-none-any.whl'
          mPathPerso = mPathPerso.replace("\\","/")
          subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
          # TYPING-EXTENSIONS
          mPathPerso = os.path.dirname(__file__) + '\\typing_extensions-4.1.1-py3-none-any.whl'
          mPathPerso = mPathPerso.replace("\\","/")
          subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
          # IMPORTLIB-METADATA
          mPathPerso = os.path.dirname(__file__) + '\\importlib_metadata-4.11.3-py3-none-any.whl'
          mPathPerso = mPathPerso.replace("\\","/")
          subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
       # RDFLIB
       mPathPerso = os.path.dirname(__file__) + '\\rdflib-6.1.1-py3-none-any.whl'
       mPathPerso = mPathPerso.replace("\\","/")
       subprocess.check_call(['python3', '-m', 'pip', 'install', mPathPerso])
    return
    
#==================================================
#==================================================
# FIN
#==================================================
