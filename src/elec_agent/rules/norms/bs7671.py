# ⚡ elec-agent — BS 7671 Rules (UK Standard)
# BS 7671: IET Wiring Regulations (UK)

# Key differences from NF C 15-100:
# - Voltage: 230V (same as France)
# - RCD protection mandatory for most circuits
# - Cable sizing per BS 7671 Appendix 4
# - Zs (earth loop impedance) checks required

BS_7671_RULES = {
    "_comment": "BS 7671 rules database — elec-agent v0.2",
    "breaker_cable_coordination": {
        "description": "Cable size per breaker (BS 7671 Appendix 4)",
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
            {"max_breaker_A": 80,  "min_section_mm2": 25.0}
        ],
        "note": "Similar to NF C 15-100 but with different correction factors"
    },
    "rcd_protection": {
        "description": "RCD protection requirements (BS 7671 531)",
        "mandatory_for": ["socket", "lighting", "motor", "outdoor"],
        "sensitivity_mA": {
            "bathroom": 30,
            "outdoor": 30,
            "general": 30,
            "all_new_installations": 30
        },
        "note": "RCD mandatory for almost all circuits in UK"
    },
    "voltage_drop": {
        "description": "Maximum voltage drop (BS 7671 525)",
        "max_percent_lighting": 3.0,
        "max_percent_power": 5.0,
        "copper_resistivity_ohm_mm2_per_m": 0.01786
    },
    "zs_earth_loop_impedance": {
        "description": "Maximum earth loop impedance Zs (BS 7671 411)",
        "max_zs_ohm": {
            "type_B_3A": 1600,
            "type_B_6A": 800,
            "type_B_10A": 480,
            "type_B_16A": 287,
            "type_B_20A": 230,
            "type_B_32A": 144,
            "type_C_10A": 320,
            "type_C_16A": 200,
            "type_C_32A": 100
        },
        "note": "Zs check required for every circuit in UK"
    },
    "socket_circuits": {
        "description": "Socket circuit rules (BS 7671)",
        "max_sockets_per_32A_circuit": "unlimited_with_load_calc",
        "note": "UK allows unlimited sockets if load calculation valid"
    },
    "voltage_systems": {
        "description": "UK voltage systems",
        "nominal_voltage_V": 230,
        "common_systems": ["230V single-phase", "400V 3-phase"]
    }
}
