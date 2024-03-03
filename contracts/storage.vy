#pragma version ^0.3.10

enum Roles:
  ADMIN
  USER

storedData: int128
roles: public(HashMap[address, Roles])

@external
def __init__(_x: int128):
  self.storedData = _x
  self.roles[msg.sender] = Roles.ADMIN

@external
def set(_x: int128):
  self.storedData = _x

@external
@view
def get() -> int128:
  return self.storedData


@external
def add_user(_address: address):
  if self.roles[msg.sender] == Roles.ADMIN:
    self.roles[_address] = Roles.USER
  else:
    raise("You are not an admin")
