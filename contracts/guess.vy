#pragma version ^0.3.10

enum Status:
    DRAFT
    OPEN
    FINISHED
    CANCELED

struct Outcome:
    name: String[50]
    description: String[500]
    total: uint256

struct Fact:
    owner: address
    name: String[50]
    description: String[500]
    oracles: DynArray[address, 3]
    outcomes: DynArray[Outcome, 5]
    status: Status
    total: uint256

struct Bet:
    owner: address
    fact_idx: int128
    outcome_idx: int128
    amount: uint256

MAX_BETS: constant(uint256) = 100
MAX_PARTICIPANTS: constant(uint256) = 100

owner: public(address)
facts: DynArray[Fact, 10]
fact_bets: HashMap[int128, DynArray[Bet, MAX_BETS]]


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
        status: Status.DRAFT,
        total: 0
    }))


@external
def add_oracle(_idx: int128, _oracle: address):
    assert self.facts[_idx].owner == msg.sender, "Only the owner can add oracles"
    assert len(self.facts[_idx].oracles) < 3, "Maximum oracles reached"
    
    self.facts[_idx].oracles.append(_oracle)


@external
def add_outcome(_idx: uint256, _name: String[50], _description: String[500]):
    assert self.facts[_idx].owner == msg.sender, "Only the owner can add outcomes"
    assert len(self.facts[_idx].outcomes) < 5, "Maximum outcomes reached"
    
    self.facts[_idx].outcomes.append(Outcome({name: _name, description: _description, total: 0}))


@external
def start_guess(_idx: int128):
    assert self.facts[_idx].status == Status.DRAFT, "The fact is not draft"
    assert len(self.facts[_idx].outcomes) > 1, "Minimum outcomes not reached"
    assert len(self.facts[_idx].oracles) > 0, "Minimum oracles not reached"
    
    self.facts[_idx].status = Status.OPEN


@external
@payable
def place_bet(_fact_idx: int128, _outcome_idx: int128):
    assert self.facts[_fact_idx].status == Status.OPEN, "The fact is not open"
    assert msg.value > 0, "Invalid amount"

    self.facts[_fact_idx].total += msg.value
    self.facts[_fact_idx].outcomes[_outcome_idx].total += msg.value
    self.fact_bets[_fact_idx].append(Bet({owner: msg.sender, fact_idx: _fact_idx, outcome_idx: _outcome_idx, amount: msg.value}))


@external
def finish_fact(_idx: int128, _outcome_idx: int128):
    assert self.facts[_idx].status == Status.OPEN, "The fact is not open"
    assert msg.sender in self.facts[_idx].oracles, "Only oracles can finish the fact"

    self.facts[_idx].status = Status.FINISHED

    comission: uint256 = self.facts[_idx].total * 5 / 100 # 5% comission to system and fact owner
    self.facts[_idx].total = self.facts[_idx].total - comission * 2 # total 10% comission
    
    winners: DynArray[address, MAX_PARTICIPANTS] = []

    for i in range(MAX_BETS):
        if i >= len(self.fact_bets[_idx]):
            break
        if self.fact_bets[_idx][i].outcome_idx == _outcome_idx:
            winners.append(self.fact_bets[_idx][i].owner)
    
    for i in range(MAX_PARTICIPANTS):
        if i >= len(winners):
            break
        send(winners[i], self.facts[_idx].total / len(winners))

    send(self.facts[_idx].owner, comission)
    send(self.owner, self.balance)