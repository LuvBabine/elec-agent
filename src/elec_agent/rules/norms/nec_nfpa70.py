# ⚡ elec-agent — NEC (NFPA 70) Rules (US Standard)
# NEC: National Electrical Code — US standard for electrical safety

# Key differences from NF C 15-100:
# - Voltage: 120V/240V split-phase instead of 230V
# - GFCI/AFCI instead of differential 30mA
# - Cable sizing per NEC Table 310.16
# - No strict limit on outlets per circuit (load calculation required)

NEC_2023_RULES = {
    "_comment": "NEC 2023 rules database — elec-agent v0.2",
    "breaker_cable_coordination": {
        "description": "Cable ampacity per breaker rating (NEC Table 310.16)",
        "table": [
            {"max_breaker_A": 15,  "min_section_mm2": 2.0,  # 14 AWG
             "ampacity_A": 15, "wire_gauge": "14 AWG"},
            {"max_breaker_A": 20,  "min_section_mm2": 3.3,  # 12 AWG
             "ampacity_A": 20, "wire_gauge": "12 AWG"},
            {"max_breaker_A": 30,  "min_section_mm2": 5.2,  # 10 AWG
             "ampacity_A": 30, "wire_gauge": "10 AWG"},
            {"max_breaker_A": 40,  "min_section_mm2": 8.4,  # 8 AWG
             "ampacity_A": 40, "wire_gauge": "8 AWG"},
            {"max_breaker_A": 60,  "min_section_mm2": 16.0, # 6 AWG
             "ampacity_A": 60, "wire_gauge": "6 AWG"},
            {"max_breaker_A": 100, "min_section_mm2": 42.0, # 3 AWG
             "ampacity_A": 100, "wire_gauge": "3 AWG"}
        ],
        "note": "NEC uses AWG gauge instead of mm^2"
    },
    "gfci_protection": {
        "description": "GFCI required locations (NEC 210.8)",
        "mandatory_locations": [
            "bathrooms",
            "garages",
            "outdoors",
            "kitchens",
            "basements",
            "laundry_areas",
            "sinks_with_floor_contact"
        ],
        "sensitivity_mA": 5,  # GFCI trips at 5mA
        "note": "GFCI instead of differential 30mA"
    },
    "afc_protection": {
        "description": "AFCI required locations (NEC 210.12)",
        "mandatory_locations": [
            "living_rooms",
            "dining_rooms",
            "bedrooms",
            "hallways",
            "closets"
        ],
        "note": "AFCI protects against arc faults"
    },
    "voltage_drop": {
        "description": "Recommended voltage drop (NEC Chapter 9, Note 3)",
        "max_percent_branch_circuit": 3.0,
        "max_percent_feeder": 5.0,
        "note": "NEC voltage drop is a recommendation, not mandatory"
    },
    "outlet_spacing": {
        "description": "Maximum spacing between outlets (NEC 210.52)",
        "max_spacing_wall_feet": 6,  # 6 feet = 1.8m
        "max_room_width_without_outlet_feet": 12,
        "note": "NEC focuses on spacing, not count per circuit"
    },
    "voltage_systems": {
        "description": "US voltage systems",
        "common_systems": ["120V single-phase", "120/240V split-phase", "208V 3-phase", "480V 3-phase"],
        "nominal_voltage_V": 120
    }
}

# Alias for consistent naming
NEC2023_RULES = NEC_2023_RULES
