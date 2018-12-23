import sys, os

sys.path.append(os.path.realpath(os.path.dirname(__file__)))

from analyzing.main import main_analyze
import userconfig

main_analyze()
