import uuid
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, constr, PositiveInt, conint, Field
from fastapi.middleware.cors import CORSMiddleware
from os import system as cmdrun
from os import popen as cmdread
import smartpy as sp

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenContractInput(BaseModel):
    token_name: constr(strip_whitespace=True, min_length=1)  # type: ignore
    symbol: constr(strip_whitespace=True, min_length=1, max_length=5)  # type: ignore
    initial_supply: PositiveInt
    decimals: conint(ge=1, le=18)  # type: ignore
    initial_owner: constr(regex=r"tz[1-3][1-9A-HJ-NP-Za-km-z]{33}")  # type: ignore
    can_mint: bool = Field(default=False)
    can_pause: bool = Field(default=False)
    blacklist: bool = Field(default=False)
    burn: bool = Field(default=False)
    icon: str = Field(default="https://smartpy.io/static/img/logo-only.svg")


def verify_header(request: Request):
    expected_header_value = "dK3KQQFw7Bnq"
    if request.headers.get("Authorization") != expected_header_value:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/create")
async def submit_form(form_data: TokenContractInput):
    contract_id = str(uuid.uuid4())[:6]
    mixins = []
    if form_data.can_mint:
        mixins.append("Mint")
    if form_data.can_pause:
        mixins.append("Pause")
    mixins.append("Admin")
    if form_data.burn:
        mixins.append("Burn")

    mixin_init = []
    if form_data.can_mint:
        mixin_init.append("Mint.__init__(self)\n            ")
    if form_data.can_pause:
        mixin_init.append("Pause.__init__(self)\n            ")
    mixin_init.append("Admin.__init__(self, administrator)\n            ")
    if form_data.burn:
        mixin_init.append("Burn.__init__(self)\n            ")

    blacklist_mixin_code = (
        """
        @sp.entrypoint
        def add_to_blacklist(self, address):
            sp.cast(address, sp.address)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.blacklist.add(address)

        @sp.entrypoint
        def remove_from_blacklist(self, address):
            sp.cast(address, sp.address)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.blacklist.remove(address)"""
        if form_data.blacklist
        else ""
    )

    pause_mixin_code = (
        """
    class Pause(AdminInterface):
        def __init__(self):
            AdminInterface.__init__(self)
            self.data.paused = False

        @sp.private(with_storage="read-only")
        def is_paused_(self):
            return self.data.paused

        @sp.entrypoint
        def setPause(self, param):
            sp.cast(param, sp.bool)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.paused = param
    """
        if form_data.can_pause
        else ""
    )

    mint_mixin_code = (
        """
    class Mint(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def mint(self, param):
            sp.cast(param, sp.record(address=sp.address, value=sp.nat))
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            receiver_balance = self.data.balances.get(
                param.address, default=sp.record(balance=0, approvals={})
            )
            receiver_balance.balance += param.value
            self.data.balances[param.address] = receiver_balance
            self.data.total_supply += param.value
    """
        if form_data.can_mint
        else ""
    )

    burn_mixin_code = (
        """
    class Burn(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def burn(self, param):
            sp.cast(param, sp.record(address=sp.address, value=sp.nat))
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            receiver_balance = self.data.balances.get(
                param.address, default=sp.record(balance=0, approvals={})
            )
            receiver_balance.balance = sp.as_nat(
                receiver_balance.balance - param.value,
                error="FA1.2_InsufficientBalance",
            )
            self.data.balances[param.address] = receiver_balance
            self.data.total_supply = sp.as_nat(self.data.total_supply - param.value)
    """
        if form_data.burn
        else ""
    )

    token_metadata = {
        "decimals": f'sp.scenario_utils.bytes_of_string("{form_data.decimals}")',
        "name": f'sp.scenario_utils.bytes_of_string("{form_data.token_name}")',
        "symbol": f'sp.scenario_utils.bytes_of_string("{form_data.symbol}")',
        "icon": f'sp.scenario_utils.bytes_of_string("{form_data.icon}")',
    }

    contract = f"""
import smartpy as sp

@sp.module
def m():
    class AdminInterface(sp.Contract):
        @sp.private(with_storage="read-only")
        def is_administrator_(self, sender):
            sp.cast(sp.sender, sp.address)
            return True

        @sp.private(with_storage="read-only")
        def is_blacklisted_(self, address):
            sp.cast(address, sp.address)
            return False

    class CommonInterface(AdminInterface):
        def __init__(self):
            AdminInterface.__init__(self)
            self.data.balances = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.address,
                    sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat),
                ],
            )
            self.data.total_supply = 0
            self.data.token_metadata = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.nat,
                    sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes]),
                ],
            )
            self.data.metadata = sp.cast(
                sp.big_map(),
                sp.big_map[sp.string, sp.bytes],
            )
            self.data.balances = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.address,
                    sp.record(approvals=sp.map[sp.address, sp.nat], balance=sp.nat),
                ],
            )
            self.data.total_supply = 0
            self.data.token_metadata = sp.cast(
                sp.big_map(),
                sp.big_map[
                    sp.nat,
                    sp.record(token_id=sp.nat, token_info=sp.map[sp.string, sp.bytes]),
                ],
            )
            self.data.metadata = sp.cast(
                sp.big_map(),
                sp.big_map[sp.string, sp.bytes],
            )
            self.data.blacklist = sp.set()
            sp.cast(self.data.blacklist, sp.set[sp.address])

        @sp.private(with_storage="read-only")
        def is_paused_(self):
            return False

    class Fa1_2(CommonInterface):
        def __init__(self, metadata, ledger, token_metadata):
            CommonInterface.__init__(self)
            self.data.metadata = metadata
            self.data.token_metadata = sp.big_map(
                {{0: sp.record(token_id=0, token_info=token_metadata)}}
            )

            for owner in ledger.items():
                self.data.balances[owner.key] = owner.value
                self.data.total_supply += owner.value.balance

        @sp.entrypoint
        def transfer(self, param):
            assert not self.is_blacklisted_(param.from_) and not self.is_blacklisted_(
                param.to_
            ), "FA1.2_Blacklisted"
            sp.cast(
                param,
                sp.record(from_=sp.address, to_=sp.address, value=sp.nat).layout(
                    ("from_ as from", ("to_ as to", "value"))
                ),
            )
            balance_from = self.data.balances.get(
                param.from_, default=sp.record(balance=0, approvals={{}})
            )
            balance_to = self.data.balances.get(
                param.to_, default=sp.record(balance=0, approvals={{}})
            )
            balance_from.balance = sp.as_nat(
                balance_from.balance - param.value, error="FA1.2_InsufficientBalance"
            )
            balance_to.balance += param.value
            if not self.is_administrator_(sp.sender):
                assert not self.is_paused_(), "FA1.2_Paused"
                if param.from_ != sp.sender:
                    balance_from.approvals[sp.sender] = sp.as_nat(
                        balance_from.approvals[sp.sender] - param.value,
                        error="FA1.2_NotAllowed",
                    )
            self.data.balances[param.from_] = balance_from
            self.data.balances[param.to_] = balance_to

        @sp.entrypoint
        def approve(self, param):
            sp.cast(
                param,
                sp.record(spender=sp.address, value=sp.nat).layout(
                    ("spender", "value")
                ),
            )
            assert not self.is_paused_(), "FA1.2_Paused"
            spender_balance = self.data.balances.get(
                sp.sender, default=sp.record(balance=0, approvals={{}})
            )
            alreadyApproved = spender_balance.approvals.get(param.spender, default=0)
            assert (
                alreadyApproved == 0 or param.value == 0
            ), "FA1.2_UnsafeAllowanceChange"
            spender_balance.approvals[param.spender] = param.value
            self.data.balances[sp.sender] = spender_balance

        @sp.entrypoint
        def getBalance(self, param):
            (address, callback) = param
            result = self.data.balances.get(
                address, default=sp.record(balance=0, approvals={{}})
            ).balance
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getAllowance(self, param):
            (args, callback) = param
            result = self.data.balances.get(
                args.owner, default=sp.record(balance=0, approvals={{}})
            ).approvals.get(args.spender, default=0)
            sp.transfer(result, sp.tez(0), callback)

        @sp.entrypoint
        def getTotalSupply(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.nat]])
            sp.transfer(self.data.total_supply, sp.tez(0), sp.snd(param))

        @sp.offchain_view()
        def token_metadata(self, token_id):
            sp.cast(token_id, sp.nat)
            return self.data.token_metadata[token_id]

    class Admin(sp.Contract):
        def __init__(self, administrator):
            self.data.administrator = administrator
            self.data.blacklist = sp.set()
            sp.cast(self.data.blacklist, sp.set[sp.address])

        {blacklist_mixin_code}

        @sp.private(with_storage="read-only")
        def is_administrator_(self, sender):
            return sender == self.data.administrator

        @sp.entrypoint
        def setAdministrator(self, params):
            sp.cast(params, sp.address)
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.administrator = params

        @sp.entrypoint()
        def getAdministrator(self, param):
            sp.cast(param, sp.pair[sp.unit, sp.contract[sp.address]])
            sp.transfer(self.data.administrator, sp.tez(0), sp.snd(param))

        @sp.onchain_view()
        def get_administrator(self):
            return self.data.administrator

    {pause_mixin_code}

    {mint_mixin_code}

    {burn_mixin_code}

    class ChangeMetadata(CommonInterface):
        def __init__(self):
            CommonInterface.__init__(self)

        @sp.entrypoint
        def update_metadata(self, key, value):
            assert self.is_administrator_(sp.sender), "Fa1.2_NotAdmin"
            self.data.metadata[key] = value

    class Fa1_2TestCustom({", ".join(mixins)}, Fa1_2, ChangeMetadata):
        def __init__(self, administrator, metadata, ledger, token_metadata):
            ChangeMetadata.__init__(self)
            Fa1_2.__init__(self, metadata, ledger, token_metadata)
            {"Mint.__init__(self)" if form_data.can_mint else ""}
            {"Pause.__init__(self)" if form_data.can_pause else ""}
            {"Burn.__init__(self)" if form_data.burn else ""}
            Admin.__init__(self, administrator)

if "main" in __name__:

    @sp.add_test()
    def test():
        sc = sp.test_scenario("{contract_id}", m)
        sc.h1("FA1.2 template - Fungible assets")

        sc.h1("Contract")
        token_metadata = {{{", ".join(f'"{k}": {v}' for k, v in token_metadata.items())}}}
        contract_metadata = sp.scenario_utils.metadata_of_url(
            "ipfs://QmaiAUj1FFNGYTu8rLBjc3eeN9cSKwaF8EGMBNDmhzPNFd"
        )
        c1 = m.Fa1_2TestCustom(
            administrator=sp.address("{form_data.initial_owner}"),
            metadata=contract_metadata,
            ledger=sp.map({{sp.address("{form_data.initial_owner}"): sp.record(balance=sp.nat(1000000), approvals=sp.map())}}),
            token_metadata=token_metadata,
        )
        sc += c1
    """
    contract_file = f"contract_{contract_id}.py"
    with open(contract_file, "w") as f:
        f.write(contract)
    print(contract)
    cmdrun("python3.9 " + contract_file)
    cmdrun(f"rm {contract_file}")
    res = cmdread(
        f'octez-client originate contract {contract_id} transferring .0001 from {form_data.initial_owner} running "$(cat {contract_id}/step_003_cont_0_contract.tz)" --init "$(cat {contract_id}/step_003_cont_0_storage.tz)" --burn-cap 1'
    ).read()
    cmdrun(f"rm -rf {contract_id}")
    return {
        "contractAddress/errorMessage": (
            res[
                res.find("New contract ")
                + len("New contract ") : res.find("New contract ")
                + len("New contract ")
                + 36
            ]
            if "New contract " in res
            else None
        )
    }
