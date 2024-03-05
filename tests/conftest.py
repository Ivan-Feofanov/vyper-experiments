import pytest


@pytest.fixture
def owner(accounts):
    return accounts[0]


@pytest.fixture
def sender(accounts):
    return accounts[1]


@pytest.fixture
def oracles(accounts):
    return accounts[2:5]
