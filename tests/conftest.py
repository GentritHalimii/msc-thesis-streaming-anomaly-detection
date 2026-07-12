import pytest

from src.config import REPO_ROOT, load_config
from src.data.load import load_transactions
from src.data.split import chronological_split


@pytest.fixture(scope="session")
def cfg():
    return load_config()


@pytest.fixture(scope="session")
def df(cfg):
    path = REPO_ROOT / cfg.data.raw_csv
    if not path.exists():
        pytest.skip(f"dataset not found at {path}; see README for how to obtain it")
    return load_transactions(path)


@pytest.fixture(scope="session")
def split(cfg, df):
    return chronological_split(df, cfg.split.train_fraction)
