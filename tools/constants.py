import difflib
from typing import Any, Dict, List, Optional, Union


class UniversalConstantsTool:    
    def __init__(self) -> None:
        self.constants: Dict[str, Union[int, Any]] = {
            "speed_of_light": {
                "value": 299792458,
                "unit": "m/s",
                "symbol": "c",
                "description": "Speed of light in vacuum"
            },
            "gravitational_constant": {
                "value": 6.67430e-11,
                "unit": "N⋅m²/kg²",
                "symbol": "G",
                "description": "Universal gravitational constant"
            },
            "planck_constant": {
                "value": 6.62607015e-34,
                "unit": "J⋅s",
                "symbol": "h",
                "description": "Planck constant"
            },
            "electron_charge": {
                "value": 1.602176634e-19,
                "unit": "C",
                "symbol": "e",
                "description": "Elementary charge"
            },
            "electron_mass": {
                "value": 9.1093837015e-31,
                "unit": "kg",
                "symbol": "mₑ",
                "description": "Electron rest mass"
            },
            "proton_mass": {
                "value": 1.67262192369e-27,
                "unit": "kg",
                "symbol": "mₚ",
                "description": "Proton rest mass"
            },
            "avogadro_number": {
                "value": 6.02214076e23,
                "unit": "mol⁻¹",
                "symbol": "Nₐ",
                "description": "Avogadro constant"
            },
            "boltzmann_constant": {
                "value": 1.380649e-23,
                "unit": "J/K",
                "symbol": "k",
                "description": "Boltzmann constant"
            }
        }
        self.formulas = {
            "kinetic_energy": "KE = (1/2) * m * v²",
            "potential_energy": "PE = m * g * h",
            "force": "F = m * a",
            "momentum": "p = m * v",
            "work": "W = F * d * cos(θ)",
            "power": "P = W / t",
            "wave_speed": "v = f * λ",
            "ohms_law": "V = I * R",
            "ideal_gas_law": "P * V = n * R * T",
            "work_energy_theorem": "W = ΔKE"
        }
        
    def normalize_key(self, name: str) -> str: return name.lower().replace(" ", "_").replace("-", "_")

    def lookup_constant(self, const_name: str) -> Optional[Dict[str, Any]]:
        normalized = self.normalize_key(const_name)
        if normalized in self.constants:
            return {
                "status": "success",
                "constant": normalized,
                "data": self.constants[normalized],
                "search_term": const_name
            }
        possible_matches = difflib.get_close_matches(normalized, \
            self.constants.keys(), n = 3, cutoff = 0.6)
        if possible_matches:
            suggestions = {match: self.constants[match]['description'] \
                for match in possible_matches}
            return {
                "status": "info",
                "message": f"Constant '{const_name}' not found. Did you mean one of: {', '.join(possible_matches)}?",
                "suggestions": suggestions,
                "search_term": const_name
            }
        return {
            "status": "error",
            "error": f"No constant found for '{const_name}'",
            "available": list(self.constants.keys())
        }

    def lookup_formula(self, formula_name: str):
        normalized = self.normalize_key(formula_name)
        if normalized in self.formulas:
            return {
                "status": "success",
                "formula": self.formulas[normalized],
                "search_term": formula_name
            }
        possible_matches = difflib.get_close_matches(normalized, \
            self.formulas.keys(), n = 3, cutoff = 0.6)
        if possible_matches:
            return {
                "status": "success",
                "message": f"Formula '{formula_name}' not found. Did you mean one of: {', '.join(possible_matches)}?",
                "suggestions": {match: self.formulas[match] for match in possible_matches},
                "search_term": formula_name
            }
        return {
            "status": "error",
            "error": f"No formula found for '{formula_name}'",
            "available": list(self.formulas.keys())
        }

    def list_constants(self) -> List[str]: return list(self.constants.keys())
    def list_formulas(self) -> List[str]: return list(self.formulas.keys())