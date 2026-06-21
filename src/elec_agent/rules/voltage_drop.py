# ⚡ elec-agent — Voltage Drop Calculator
# NF C 15-100 §525: Max 3% lighting / 5% power

RHO_COPPER = 0.01786   # Ω⋅mm^2/m (copper resistivity)
RHO_ALU    = 0.02941   # Ω⋅mm^2/m (aluminum resistivity)

VOLTAGE_NOMINAL_SINGLE = 230.0   # V (single-phase)
VOLTAGE_NOMINAL_THREE  = 400.0   # V (three-phase)


def calc_voltage_drop(
    current_A: float,
    length_m: float,
    section_mm2: float,
    phases: int = 1,
    conductor: str = "copper",
) -> dict:
    """
    Calculate voltage drop along a cable.

    Formulas:
        Single-phase: ΔU = (2 × ρ × L × I) / S
        Three-phase:  ΔU = (√3 × ρ × L × I) / S

    Args:
        current_A:    Load current in amperes
        length_m:     One-way cable length in meters
        section_mm2:  Cable cross-section in mm^2
        phases:       1 (single-phase) or 3 (three-phase)
        conductor:    "copper" or "aluminium"

    Returns:
        Dict with:
            - delta_U_V: voltage drop in volts
            - delta_U_percent: voltage drop as percentage
            - compliant_lighting: True if <= 3%
            - compliant_power: True if <= 5%
    """
    rho = RHO_COPPER if conductor == "copper" else RHO_ALU

    if phases == 1:
        delta_U = (2 * rho * length_m * current_A) / section_mm2
        v_ref   = VOLTAGE_NOMINAL_SINGLE
    elif phases == 3:
        delta_U = (1.732 * rho * length_m * current_A) / section_mm2
        v_ref   = VOLTAGE_NOMINAL_THREE
    else:
        raise ValueError("phases must be 1 or 3")

    delta_U_pct = (delta_U / v_ref) * 100

    return {
        "delta_U_V":       round(delta_U, 3),
        "delta_U_percent": round(delta_U_pct, 3),
        "compliant_lighting": delta_U_pct <= 3.0,
        "compliant_power":    delta_U_pct <= 5.0,
    }


def current_from_power(power_W: float, voltage_V: float = 230.0,
                        power_factor: float = 1.0) -> float:
    """
    Calculate current from power (I = P / (U × cosφ)).

    Args:
        power_W:     Power in watts
        voltage_V:   Voltage in volts (default 230V single-phase)
        power_factor: cosφ (default 1.0 for resistive loads)

    Returns:
        Current in amperes
    """
    return power_W / (voltage_V * power_factor)
