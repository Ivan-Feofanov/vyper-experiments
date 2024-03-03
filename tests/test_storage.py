from enum import IntEnum

import pytest
from ape import exceptions

INITIAL_VALUE = 4


class Roles(IntEnum):
    ADMIN = 1
    USER = 2


@pytest.fixture
def owner(accounts):
    return accounts[0]


@pytest.fixture
def sender(accounts):
    return accounts[1]


@pytest.fixture
def my_contract(owner, project):
    return owner.deploy(project.storage, INITIAL_VALUE)


def test_initial_state(my_contract, sender, owner):
    assert my_contract.get(sender=sender) == INITIAL_VALUE
    assert my_contract.roles(owner) == Roles.ADMIN


@pytest.mark.parametrize(("input", "expected"), [(5, 5), (0, 0), (-3, -3)])
def test_contract(my_contract, sender, input, expected):
    my_contract.set(input, sender=sender)
    assert my_contract.get(sender=sender) == expected


def test_add_user(my_contract, sender, owner):
    my_contract.add_user(sender, sender=owner)

    assert my_contract.roles(sender) == Roles.USER


def test_add_user_not_admin(my_contract, sender):
    with pytest.raises(exceptions.ContractLogicError):
        my_contract.add_user(sender, sender=sender)
