# ⚡ elec-agent — IEC 60364 Rules (European Standard)
# IEC 60364: Low-voltage electrical installations

# Key differences from NF C 15-100:
# - Voltage drop: 3% lighting / 5% power (same)
# - Differential protection: 30mA for sockets, 10mA for bathrooms
# - Cable sizing based on IEC 60287 tables

IEC_60364_RULES = {
    "_comment": "IEC 60364 rules database — elec-agent v0.2",
    "breaker_cable_coordination": {
        "description": "Cable section minimum per breaker rating (IEC 60364-5-52)",
        "table": [
            {"max_breaker_A": 6,   "min_section_mm2": 1.0},
            {"max_breaker_A": 10,  "min_section_mm2": 1.5},
            {"max_breaker_A": 16,  "min_section_mm2": 1.5},
            {"max_breaker_A": 20,  "min_section_mm2": 2.5},
            {"max_breaker_A": 25,  "min_section_mm2": 2.5},
            {"max_breaker_A": 32,  "min_section_mm2": 4.0},
            {"max_breaker_A": 40,  "min_section_mm2": 6.0},
            {"max_breaker_A": 50,  "min_section_mm2": 10.0},
            {"max_breaker_A": 63,  "min_section_mm2": 16.0},
            {"max_breaker_A": 80,  "min_section_mm2": 25.0},
            {"max_breaker_A": 100, "min_section_mm2": 35.0}
        ],
        "note": "IEC uses slightly different tables than NF C 15-100"
    },
    "differential_protection": {
        "description": "Differential protection requirements (IEC 60364-4-41)",
        "mandatory_for": ["socket", "lighting", "motor"],
        "sensitivity_mA": {
            "bathroom_zone1_2": 10,   # IEC requires 10mA for bathrooms
            "outdoor": 30,
            "indoor_general": 30,
            "socket_circuits": 30
        }
    },
    "voltage_drop": {
        "description": "Maximum voltage drop (IEC 60364-5-523)",
        "max_percent_lighting": 3.0,
        "max_percent_power": 5.0,
        "copper_resistivity_ohm_mm2_per_m": 0.01786,
        "note": "Same as NF C 15-100"
    },
    "socket_circuits": {
        "description": "Maximum outlets per circuit (IEC 60364-5-52)",
        "max_sockets_per_16A_circuit": 10,  # IEC allows 10 instead of 8
        "max_sockets_per_20A_circuit": 14
    },
    "lighting_circuits": {
        "description": "Maximum power per lighting circuit (IEC 60364-5-52)",
        "max_power_W_per_10A_circuit": 2300,
        "max_power_W_per_16A_circuit": 3680
    },
    "earthing_systems": {
        "description": "Earthing system types (IEC 60364-1)",
        "types": ["TN-S", "TN-C", "TN-C-S", "TT", "IT"],
        "note": "IEC defines 5 earthing systems vs NF C 15-100 which focuses on TT/TN"
    }
}
