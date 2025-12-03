import sys
import logging

# Set up logging to see DEBUG messages
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(name)s - %(message)s')

# Now import and run the test
sys.path.insert(0, '.')
from test_import import *

if __name__ == "__main__":
    import_and_verify('funny_test_data.json')

