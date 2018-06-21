"""Module for epsilon functions."""
import math

# Please dont remove this defalt function
def default(cycle, max_cycle, environment):
    """Return epsilon value for a cycle."""

    _min = max(math.floor(max_cycle * 0.5), 1)
    return 0.01 - (0.00985 * min(cycle, _min) / _min)

# Add your epsilon functions here!

def linear(cycle, max_cycle, environment):
    """Return epsilon value for a cycle using a linear approach"""

    _min = max(math.floor(max_cycle * 0.5), 1)
    return 0.1 - (0.1 * min(cycle, _min) / _min)
    