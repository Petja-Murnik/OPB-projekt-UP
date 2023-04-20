from dataclasses import dataclass, field

@dataclass
class Zaposleni:
    ime_priimek: str = field(default="")
    naslov: str = field(default="")
    mesto: str = field(default="")
    TRR: str = field(default="")
    placa: float = field(default=0)
    stevilo_ur : float = field(default=0)

@dataclass
class Produkti:
    produkt : int = field(default=0)
    prodajna_cena : float = field(default=0)
    nabavna_cena : float = field(default=0)

@dataclass
class Oddelek:
    oddelek :   int = field(default=0) 
    TRR :   str = field(default="")
    stanje : float = field(default=0)

@dataclass 
class Kupci:
    ime_priimek : str = field(default="")
    naslov: str = field(default="")
    mesto: str = field(default="")
    drzava : str = field(default="")
    TRR: str = field(default="")









