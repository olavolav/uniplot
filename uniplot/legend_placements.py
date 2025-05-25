from enum import Enum


class LegendPlacement(Enum):
    AUTO = 1
    VERTICAL = 2

    @classmethod
    def from_string(cls, label: str) -> "LegendPlacement":
        clean_label = str(label).lower().strip()
        if clean_label == "auto":
            return cls.AUTO
        if clean_label == "vertical":
            return cls.VERTICAL
        raise ValueError(f"Unknown value for legend placement: '{label}'")
