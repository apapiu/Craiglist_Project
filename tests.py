#tests:
import os
import pytest
#!export PYTHONPATH="$PYTHONPATH:/Users/alexpapiu/Documents/Craiglist_Project"

import cl_pipeline


def test_check_base():
    assert cl_pipeline.get_data(limit = 1) is not None
