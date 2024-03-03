#pragma version ^0.3.10

enum Status:
    OPEN
    FINISHED
    CANCELED

enum OutcomeTypes:
    A
    B

struct Fact:
    name: String[50]
    description: String[500]

struct Outcome:
    name: String[20]
    description: String[100]

fact: Fact
status: Status
outcomes: HashMap[OutcomeTypes, Outcome]


@external
def __init__(_name: String[50], _description: String[500], _outcomes: Outcome[2]):
    self.fact = Fact({
        name: _name,
        description: _description,
    })
    self.outcomes[OutcomeTypes.A] = _outcomes[0]
    self.outcomes[OutcomeTypes.B] = _outcomes[1]
    self.status = Status.OPEN


@external
@view
def get_fact() -> Fact:
    return self.fact


@external
@view
def get_outcomes() -> Outcome[2]:
    return [self.outcomes[OutcomeTypes.A], self.outcomes[OutcomeTypes.B]]