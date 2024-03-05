from dataclasses import dataclass
from enum import IntEnum

import pytest
from ape import exceptions
from faker import Faker

fake = Faker()


class Status(IntEnum):
    DRAFT = 1
    OPEN = 2
    FINISHED = 3
    CANCELLED = 4


@dataclass
class Outcome:
    name: str
    description: str


@dataclass
class Fact:
    name: str
    description: str
    oracles: list = None
    outcomes: list[Outcome] = None
    status: Status = Status.OPEN


@pytest.fixture
def fact(oracles) -> Fact:
    fact = Fact(
        name=fake.name(),
        description=fake.text(),
        oracles=oracles,
        outcomes=[
            Outcome(fake.sentence(), fake.text()),
            Outcome(fake.sentence(), fake.text()),
        ],
    )
    return fact


@pytest.fixture
def guess_service(owner, project):
    return owner.deploy(project.guess)


def test_initial_state(guess_service, owner):
    assert guess_service.owner() == owner


def test_create_fact(guess_service, fact, sender):
    guess_service.create_fact(fact.name, fact.description, sender=sender)
    created_fact = guess_service.get_fact(0)

    assert created_fact.owner == sender
    assert created_fact.name == fact.name
    assert created_fact.description == fact.description
    assert created_fact.status == Status.DRAFT
    assert created_fact.outcomes == []
    assert created_fact.oracles == []


def test_add_oracle(guess_service, fact, oracles, sender):
    guess_service.create_fact(fact.name, fact.description, sender=sender)
    guess_service.add_oracle(0, oracles[0], sender=sender)
    guess_service.add_oracle(0, oracles[1], sender=sender)

    created_fact = guess_service.get_fact(0)
    assert created_fact.oracles == oracles[:2]


def test_add_outcome(guess_service, fact, sender):
    guess_service.create_fact(fact.name, fact.description, sender=sender)

    guess_service.add_outcome(
        0, fact.outcomes[0].name, fact.outcomes[0].description, sender=sender
    )
    guess_service.add_outcome(
        0, fact.outcomes[1].name, fact.outcomes[1].description, sender=sender
    )
    created_fact = guess_service.get_fact(0)

    assert len(created_fact.outcomes) == 2
    assert created_fact.outcomes[0].name == fact.outcomes[0].name
    assert created_fact.outcomes[0].description == fact.outcomes[0].description
    assert created_fact.outcomes[1].name == fact.outcomes[1].name
    assert created_fact.outcomes[1].description == fact.outcomes[1].description


def test_run_guess(guess_service, fact, oracles, sender):
    guess_service.create_fact(fact.name, fact.description, sender=sender)
    guess_service.add_oracle(0, oracles[0], sender=sender)
    guess_service.add_oracle(0, oracles[1], sender=sender)
    guess_service.add_outcome(
        0, fact.outcomes[0].name, fact.outcomes[0].description, sender=sender
    )
    guess_service.add_outcome(
        0, fact.outcomes[1].name, fact.outcomes[1].description, sender=sender
    )

    guess_service.start_guess(0, sender=sender)
    created_fact = guess_service.get_fact(0)

    assert created_fact.status == Status.OPEN


def test_run_guess__no_outcomes(guess_service, fact, oracles, sender):
    guess_service.create_fact(fact.name, fact.description, sender=sender)
    guess_service.add_oracle(0, oracles[0], sender=sender)
    guess_service.add_oracle(0, oracles[1], sender=sender)

    with pytest.raises(exceptions.ContractLogicError) as exc:
        guess_service.start_guess(0, sender=sender)
    created_fact = guess_service.get_fact(0)

    assert exc.value.message == "Minimum outcomes not reached"
    assert created_fact.status == Status.DRAFT


def test_run_guess__no_oracles(guess_service, fact, sender):
    guess_service.create_fact(fact.name, fact.description, sender=sender)
    guess_service.add_outcome(
        0, fact.outcomes[0].name, fact.outcomes[0].description, sender=sender
    )
    guess_service.add_outcome(
        0, fact.outcomes[1].name, fact.outcomes[1].description, sender=sender
    )

    with pytest.raises(exceptions.ContractLogicError) as exc:
        guess_service.start_guess(0, sender=sender)
    created_fact = guess_service.get_fact(0)

    assert exc.value.message == "Minimum oracles not reached"
    assert created_fact.status == Status.DRAFT
