import base64
from typing import Optional

from pydantic import BaseModel, Field
from tonsdk.boc import Cell

from domain.ton import InitialAccountState


class Domain(BaseModel):
    length_bytes: int = Field(alias="LengthBytes")
    value: str


class Proof(BaseModel):
    timestamp: int
    domain: Domain
    signature: str
    payload: str
    state_init: Optional[str] = Field(default=None, alias="state_init")


class CheckProofRequest(BaseModel):
    address: str
    network: str
    public_key: str
    proof: Proof


class CheckProofRequestRaw(CheckProofRequest):
    address_bytes: Optional[bytes] = None
    workchain: Optional[int] = None
    init_state: Optional[InitialAccountState] = None
    data: Optional[Cell] = None

    def __init__(self, request: CheckProofRequest):
        # Initialize base class with existing properties
        super().__init__(**request.dict())

        # Process the address to extract workchain and address bytes
        address = self.address
        if len(address) > 2 and address[1] == ':':
            try:
                self.workchain = int(address[:1])
                self.address_bytes = bytes.fromhex(address[2:])
            except ValueError:
                self.workchain = None
                self.address_bytes = None
                print("Error parsing the address.")
        else:
            print("Invalid address format.")

        # Process the StateInit to extract code and data cells
        if self.proof.state_init:
            try:
                # Decode the Base64-encoded StateInit
                boc_bytes = base64.b64decode(self.proof.state_init)

                # Deserialize the BOC to get the root cell
                root_cell = Cell.one_from_boc(boc_bytes)

                # Check if the root cell has at least two references
                if len(root_cell.refs) >= 2:
                    code_cell = root_cell.refs[0]
                    data_cell = root_cell.refs[1]

                    # Serialize the code and data cells back to BOC bytes
                    code_boc = code_cell.to_boc()
                    data_boc = data_cell.to_boc()

                    # Encode the BOC bytes back to Base64 strings
                    code_base64 = base64.b64encode(code_boc).decode('utf-8')
                    data_base64 = base64.b64encode(data_boc).decode('utf-8')

                    # Assign the init_state and data properties
                    self.init_state = InitialAccountState(
                        code=code_base64,
                        data=data_base64
                    )
                    self.data = data_cell
                else:
                    print("Root cell does not have enough references.")
            except Exception as e:
                print(f"Error processing state_init: {e}")
        else:
            print("No state_init provided in proof.")
