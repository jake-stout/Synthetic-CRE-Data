import importlib.util
import pandas as pd
from pathlib import Path
import pytest


def load_module():
    file_path = Path('scripts/create_synthetic_sample_data.py')
    spec = importlib.util.spec_from_file_location('synthetic', file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generate_user_rows_and_unique_ids():
    module = load_module()
    df = module.generate_user(count=5)
    assert len(df) == 5
    assert df['user_id'].is_unique


def test_generate_user_default_count_range():
    module = load_module()
    df = module.generate_user()
    assert 5 <= len(df) <= 10
    assert df['user_id'].is_unique


def test_generate_user_negative_count():
    module = load_module()
    with pytest.raises(ValueError):
        module.generate_user(count=-5)

