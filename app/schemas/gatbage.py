from enum import Enum
from pydantic import BaseModel


class GarbageType(str, Enum):
    Cardboard = "Cardboard"
    Glass = "Glass"
    Metal = "Metal"
    Paper = "Paper"
    Plastic = "Plastic"
    Trash = "Trash"


class GarbageSubtype(str, Enum):
    PET_Bottle = "pet_bottle"
    PET_Bottle_white = "pet_bottle_white"
    PET_Container = "pet_container"

    HDPE_Container = "hdpe_container"
    HDPE_Film = "hdpe_film"
    HDPE_Bag = "hdpe_bag"

    PP_Container = "pp_container"
    PP_Large = "pp_large"
    PP_Bag = "pp_bag"

    FOAM_Packaging = "foam_packaging"
    FOAM_Egg = "foam_egg"
    FOAM_Building = "foam_building"
    FOAM_Food = "foam_food"

    Blister_pack = "blister_pack"
    Toothbrush = "toothbrush"
    Plastic_card = "plastic_card"
    Tube = "tube"
    Receipt = "receipt"

    Unknown = "unknown"


class GarbageState(str, Enum):
    Clean = "clean"
    Dirty = "dirty"
    Heavily_dirty = "heavily_dirty"
    Food_contaminated = "food_contaminated"
    With_labels = "with_labels"
    No_labels = "no_labels"
    Compressed = "compressed"
    Damaged = "damaged"
    Unknown = "unknown"


class GarbageData(BaseModel):
    type: GarbageType
    subtype: GarbageSubtype
    state: GarbageState


class GarbageDataList(BaseModel):
    items: list[GarbageData]
