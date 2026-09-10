"""Analytical predicates for the selected assay; no official finding is created."""

from dataclasses import dataclass
from decimal import Decimal

from .core import MissingInput


@dataclass(frozen=True)
class AssayResult:
    valid: bool
    selected_assay: bool
    cq: Decimal | None
    explicit_no_cq: bool

    def __post_init__(self):
        if any(type(v) is not bool for v in (self.valid, self.selected_assay, self.explicit_no_cq)):
            raise TypeError("Assay statuses require explicit booleans")
        if self.cq is not None and (not isinstance(self.cq, Decimal) or not self.cq.is_finite() or self.cq < 0):
            raise ValueError("Cq requires a finite nonnegative Decimal")
        if self.cq is not None and self.explicit_no_cq:
            raise ValueError("Numeric Cq and explicit no-Cq are mutually exclusive")


def analytical_predicates(result: AssayResult, lower: Decimal,
                          upper: Decimal | None) -> dict[str, bool]:
    valid = result.valid and result.selected_assay
    if valid and result.cq is None and not result.explicit_no_cq:
        raise MissingInput("numeric Cq or explicit source-defined no-Cq result")
    cq = result.cq
    present = valid and cq is not None
    return {
        "valid Cq < 32": present and cq < lower,
        "valid Cq > 32": present and cq > lower,
        "valid assay with no Cq value": valid and result.explicit_no_cq,
        "valid analytical evidence": valid,
        "Cq = 32": present and cq == lower,
        "analytical evidence missing or invalid": not result.valid,
        "valid Cq > 32 and < 35": present and upper is not None and lower < cq < upper,
        "valid Cq > 35 or source-defined no-Cq result": valid and (result.explicit_no_cq or cq is not None and upper is not None and cq > upper),
        "Cq = 35": present and upper is not None and cq == upper,
        "analytical result uses the DDS45-selected Harper et al. 2010 real-time PCR assay with the 2013 erratum": result.selected_assay,
    }
