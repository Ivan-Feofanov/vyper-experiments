from enum import IntEnum

import pytest
from ape import exceptions

INITIAL_VALUE = 4


class Roles(IntEnum):
    ADMIN = 1
    USER = 2


@pytest.fixture
def storage(owner, project):
    return owner.deploy(project.storage, INITIAL_VALUE)


def test_initial_state(storage, sender, owner):
    assert storage.get(sender=sender) == INITIAL_VALUE
    assert storage.roles(owner) == Roles.ADMIN


@pytest.mark.parametrize(("input", "expected"), [(5, 5), (0, 0), (-3, -3)])
def test_contract(storage, sender, input, expected):
    storage.set(input, sender=sender)
    assert storage.get(sender=sender) == expected


def test_add_user(storage, sender, owner):
    storage.add_user(sender, sender=owner)

    assert storage.roles(sender) == Roles.USER


def test_add_user_not_admin(storage, sender):
    with pytest.raises(exceptions.ContractLogicError):
        storage.add_user(sender, sender=sender)
