#pragma version ^0.3.10

enum Status:
    DRAFT
    OPEN
    FINISHED
    CANCELED

struct Outcome:
    name: String[50]
    description: String[500]

struct Fact:
    owner: address
    name: String[50]
    description: String[500]
    oracles: DynArray[address, 3]
    outcomes: DynArray[Outcome, 5]
    status: Status

owner: public(address)
facts: DynArray[Fact, 10]

event oracle_added:
    setter: indexed(address)
    total_oracles: uint256

@external
def __init__():
    self.owner = msg.sender


@external
@view
def get_fact(_idx: int128) -> Fact:
    return self.facts[_idx]


@external
def create_fact(_name: String[50], _description: String[500]):
    self.facts.append(Fact({
        owner: msg.sender,
        name: _name, 
        description: _description, 
        oracles: [], 
        outcomes: [], 
        status: Status.DRAFT
    }))


@external
def add_oracle(_idx: int128, _oracle: address):
    assert self.facts[_idx].owner == msg.sender, "Only the owner can add oracles"
    assert len(self.facts[_idx].oracles) < 3, "Maximum oracles reached"
    self.facts[_idx].oracles.append(_oracle)


@external
def add_outcome(_idx: int128, _name: String[50], _description: String[500]):
    assert self.facts[_idx].owner == msg.sender, "Only the owner can add outcomes"
    assert len(self.facts[_idx].outcomes) < 5, "Maximum outcomes reached"
    self.facts[_idx].outcomes.append(Outcome({name: _name, description: _description}))
    log oracle_added(msg.sender, len(self.facts[_idx].outcomes))


@external
def start_guess(_idx: int128):
    assert self.facts[_idx].status == Status.DRAFT, "The fact is not draft"
    assert len(self.facts[_idx].outcomes) > 1, "Minimum outcomes not reached"
    assert len(self.facts[_idx].oracles) > 0, "Minimum oracles not reached"
    self.facts[_idx].status = Status.OPEN
