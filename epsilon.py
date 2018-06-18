"""Module for epsilon functions."""

# Please dont remove this defalt function
def default(cycle, max_cycle, environment):
    """Return epsilon value for a cycle."""
    return 0.01 - (0.00985 * min(cycle, 75) / 75)

# Add your epsilon functions here!