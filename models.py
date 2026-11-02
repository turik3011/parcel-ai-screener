
from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

NonEmpty = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]


class ParcelInput(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    cadastral_area: NonEmpty
    parcel_number: NonEmpty
    area_m2: int = Field(gt=0)
    land_type: NonEmpty

    land_use: str | None = None
    protection_regimes: list[NonEmpty] | None = None
    registered_encumbrances: list[NonEmpty] | None = None
    additional_context: str | None = None

    @field_validator("protection_regimes", "registered_encumbrances")
    @classmethod
    def no_duplicates(cls, values):
        if values is not None and len(values) != len(set(values)):
            raise ValueError("Duplicate entries are not allowed.")
        return values
