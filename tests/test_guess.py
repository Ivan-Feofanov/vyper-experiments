from dataclasses import dataclass

import pytest
from faker import Faker

fake = Faker()


@dataclass
class Fact:
    name: str
    description: str


@pytest.fixture
def fact() -> Fact:
    return Fact(name=fake.name(), description=fake.text())


@pytest.fixture
def guess_service(owner, project, fact):
    return owner.deploy(
        project.guess,
        fact.name,
        fact.description,
        [
            {"name": "initial name A", "description": "initial description A"},
            {"name": "initial name B", "description": "initial description B"},
        ],
    )


def test_initial_state(guess_service, sender, fact):
    deployed_fact = guess_service.get_fact(sender=sender)
    assert deployed_fact.name == fact.name
    assert deployed_fact.description == fact.description


def test_get_outcomes(guess_service, sender):
    outcomes = guess_service.get_outcomes(sender=sender)
    assert len(outcomes) == 2
    assert outcomes[0]["name"] == "initial name A"
    assert outcomes[0]["description"] == "initial description A"
    assert outcomes[1]["name"] == "initial name B"
    assert outcomes[1]["description"] == "initial description B"
