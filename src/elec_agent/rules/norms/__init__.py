# ⚡ elec-agent — International Electrical Norms
# Support for multiple electrical standards (NF C 15-100, NEC, IEC 60364, etc.)

from .nfc15100 import NF_C_15_100_RULES
from .iec60364 import IEC_60364_RULES
from .nec_nfpa70 import NEC2023_RULES
from .bs7671 import BS_7671_RULES

NORMS = {
    "NFC15100": NF_C_15_100_RULES,
    "IEC60364": IEC_60364_RULES,
    "NEC2023":  NEC2023_RULES,
    "BS7671":   BS_7671_RULES,
}

def get_norm(norm_name: str):
    """Get rules database for a specific electrical norm."""
    return NORMS.get(norm_name)
