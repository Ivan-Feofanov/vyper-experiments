from dataclasses import dataclass
from enum import IntEnum

import pytest
from ape import exceptions
from faker import Faker

fake = Faker()


class Status(IntEnum):
    DRAFT = 1
    OPEN = 2
    FINISHED = 4
    CANCELLED = 8


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
        description=fake.sentence(),
        oracles=oracles,
        outcomes=[
            Outcome(fake.word(), fake.sentence()),
            Outcome(fake.word(), fake.sentence()),
        ],
    )
    return fact


@pytest.fixture
def guess_service(owner, project):
    return owner.deploy(project.guess)


@pytest.fixture
def prepared_service(guess_service, fact, oracles, sender):
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
    return guess_service


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


def test_place_bet(guess_service, fact, oracles, sender, accounts):
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
    first_better = accounts[4]
    second_better = accounts[5]

    guess_service.place_bet(0, 0, sender=first_better, value=100)
    guess_service.place_bet(0, 1, sender=second_better, value=200)

    created_fact = guess_service.get_fact(0)
    assert created_fact.outcomes[0].total == 100
    assert created_fact.outcomes[1].total == 200
    assert created_fact.total == 300


def test_finish_fact(prepared_service, oracles, owner, sender, gamers):
    first_better = gamers[0]
    second_better = gamers[1]
    prepared_service.place_bet(0, 0, sender=first_better, value=1000)
    prepared_service.place_bet(0, 1, sender=second_better, value=1000)
    first_better_balance = first_better.balance
    fact_owner_balance = sender.balance
    owner_balance = owner.balance

    prepared_service.finish_fact(0, 0, sender=oracles[0])
    created_fact = prepared_service.get_fact(0)

    assert created_fact.status == Status.FINISHED
    assert first_better.balance == first_better_balance + 1800
    assert sender.balance == fact_owner_balance + 100
    assert owner.balance == owner_balance + 100


def test_finish_fact__two_winners(prepared_service, oracles, owner, sender, gamers):
    first_better = gamers[0]
    second_better = gamers[1]
    third_better = gamers[2]
    prepared_service.place_bet(0, 0, sender=first_better, value=1000)
    prepared_service.place_bet(0, 0, sender=second_better, value=1000)
    prepared_service.place_bet(0, 1, sender=third_better, value=1000)
    first_better_balance = first_better.balance
    second_better_balance = second_better.balance
    fact_owner_balance = sender.balance
    owner_balance = owner.balance

    prepared_service.finish_fact(0, 0, sender=oracles[0])
    created_fact = prepared_service.get_fact(0)

    assert created_fact.status == Status.FINISHED
    assert first_better.balance == first_better_balance + 1350
    assert second_better.balance == second_better_balance + 1350
    assert sender.balance == fact_owner_balance + 150
    assert owner.balance == owner_balance + 150


def test_finish_fact__not_oracle(prepared_service, gamers):
    with pytest.raises(exceptions.ContractLogicError) as exc:
        prepared_service.finish_fact(0, 0, sender=gamers[0])

    assert exc.value.message == "Only oracles can finish the fact"


def test_finish_fact__not_open(prepared_service, gamers, oracles):
    prepared_service.finish_fact(0, 0, sender=oracles[0])

    with pytest.raises(exceptions.ContractLogicError) as exc:
        prepared_service.finish_fact(0, 0, sender=gamers[0])

    assert exc.value.message == "The fact is not open"
