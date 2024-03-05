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


@pytest.fixture
def gamers(accounts):
    return accounts[5:]
