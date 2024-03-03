import pytest


@pytest.fixture
def owner(accounts):
    return accounts[0]


@pytest.fixture
def sender(accounts):
    return accounts[1]
