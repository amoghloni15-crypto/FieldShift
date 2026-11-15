"""
FieldShift Agronomic Scoring Engine.
Implements deterministic FAO-grounded rotation rules:
1. Botanical pest break rule (no back-to-back same family)
2. Legume nitrogen-fixation requirement
3. Root depth and canopy residue synergy
4. Climate and soil pH adaptability
5. Multi-criteria weighted scoring
"""

import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_crop_database():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    crops_path = os.path.join(base_dir, "crops.csv")
    if os.path.exists(crops_path):
        return pd.read_csv(crops_path)
    data = [
        {"crop_id": "maize", "crop_name": "Maize (Corn)", "plant_family": "Poaceae", "season": "Summer", "water_need_mm": 650, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 1.2, "nitrogen_fixing": "No", "soil_cover_residue": "Moderate", "ph_min": 5.8, "ph_max": 7.5, "economic_risk": "Moderate"},
        {"crop_id": "soybean", "crop_name": "Soybean", "plant_family": "Fabaceae", "season": "Summer", "water_need_mm": 500, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 1.0, "nitrogen_fixing": "Yes", "soil_cover_residue": "Moderate", "ph_min": 6.0, "ph_max": 7.0, "economic_risk": "Moderate"},
        {"crop_id": "winter_wheat", "crop_name": "Winter Wheat", "plant_family": "Poaceae", "season": "Winter/Spring", "water_need_mm": 450, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 1.5, "nitrogen_fixing": "No", "soil_cover_residue": "Moderate", "ph_min": 6.0, "ph_max": 7.5, "economic_risk": "Low"},
        {"crop_id": "sorghum", "crop_name": "Grain Sorghum", "plant_family": "Poaceae", "season": "Summer", "water_need_mm": 400, "heat_tolerance": "High", "drought_tolerance": "High", "rooting_depth_m": 1.5, "nitrogen_fixing": "No", "soil_cover_residue": "High", "ph_min": 5.5, "ph_max": 8.0, "economic_risk": "Low"},
        {"crop_id": "chickpea", "crop_name": "Chickpea (Garbanzo)", "plant_family": "Fabaceae", "season": "Spring/Winter", "water_need_mm": 320, "heat_tolerance": "Moderate", "drought_tolerance": "High", "rooting_depth_m": 0.8, "nitrogen_fixing": "Yes", "soil_cover_residue": "Moderate", "ph_min": 6.0, "ph_max": 8.0, "economic_risk": "Moderate"},
        {"crop_id": "alfalfa", "crop_name": "Alfalfa (Lucerne)", "plant_family": "Fabaceae", "season": "Perennial", "water_need_mm": 750, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 2.5, "nitrogen_fixing": "Yes", "soil_cover_residue": "High", "ph_min": 6.5, "ph_max": 7.8, "economic_risk": "Low"},
        {"crop_id": "sunflower", "crop_name": "Sunflower", "plant_family": "Asteraceae", "season": "Summer", "water_need_mm": 480, "heat_tolerance": "High", "drought_tolerance": "Moderate", "rooting_depth_m": 1.8, "nitrogen_fixing": "No", "soil_cover_residue": "High", "ph_min": 6.0, "ph_max": 7.5, "economic_risk": "Moderate"},
        {"crop_id": "clover_rye", "crop_name": "Cover Crop (Clover-Rye)", "plant_family": "Fabaceae/Poaceae", "season": "Fall/Winter", "water_need_mm": 220, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 0.6, "nitrogen_fixing": "Yes", "soil_cover_residue": "High", "ph_min": 5.5, "ph_max": 7.5, "economic_risk": "Low"},
        {"crop_id": "finger_millet", "crop_name": "Finger Millet (Ragi)", "plant_family": "Poaceae", "season": "Summer/Kharif", "water_need_mm": 350, "heat_tolerance": "High", "drought_tolerance": "High", "rooting_depth_m": 0.9, "nitrogen_fixing": "No", "soil_cover_residue": "High", "ph_min": 5.5, "ph_max": 7.5, "economic_risk": "Low"},
        {"crop_id": "pigeon_pea", "crop_name": "Pigeon Pea (Tur / Arhar)", "plant_family": "Fabaceae", "season": "Summer/Kharif", "water_need_mm": 420, "heat_tolerance": "High", "drought_tolerance": "High", "rooting_depth_m": 1.8, "nitrogen_fixing": "Yes", "soil_cover_residue": "High", "ph_min": 6.0, "ph_max": 7.8, "economic_risk": "Moderate"},
        {"crop_id": "groundnut", "crop_name": "Groundnut (Peanut)", "plant_family": "Fabaceae", "season": "Summer/Kharif", "water_need_mm": 450, "heat_tolerance": "Moderate", "drought_tolerance": "Moderate", "rooting_depth_m": 0.8, "nitrogen_fixing": "Yes", "soil_cover_residue": "Moderate", "ph_min": 5.8, "ph_max": 7.2, "economic_risk": "Moderate"}
    ]
    return pd.DataFrame(data)

def generate_and_score_rotations(
    crop_df: pd.DataFrame,
    past_crops: list,
    weights: dict,
    climate_data: dict,
    soil_data: dict
):
    """
    Evaluates permutation candidates across 3 forward seasons and ranks top sequences.
    """
    crops_list = crop_df.to_dict(orient="records")
    crop_by_name = {c["crop_name"]: c for c in crops_list}

    c_past1 = crop_by_name.get(past_crops[1], crops_list[0])

    candidates = []
    
    for c1 in crops_list:
        if c1["plant_family"] == c_past1["plant_family"] and "Cover" not in c1["crop_name"]:
            continue
        
        for c2 in crops_list:
            if c2["plant_family"] == c1["plant_family"] and "Cover" not in c2["crop_name"]:
                continue
            
            for c3 in crops_list:
                if c3["plant_family"] == c2["plant_family"] and "Cover" not in c3["crop_name"]:
                    continue
                
                seq = [c1, c2, c3]
                legume_count = sum(1 for c in seq if c["nitrogen_fixing"] == "Yes")
                if legume_count < 1:
                    continue
                
                if c1["crop_id"] == c2["crop_id"] == c3["crop_id"]:
                    continue
                
                total_water_need = sum(c["water_need_mm"] for c in seq)
                annual_water_need = total_water_need / 3.0
                mean_rainfall = climate_data["mean_annual_rainfall_mm"]
                water_ratio = annual_water_need / max(mean_rainfall, 250)
                
                if water_ratio <= 0.8:
                    s_water = 95.0
                elif water_ratio <= 1.0:
                    s_water = 82.0
                elif water_ratio <= 1.25:
                    s_water = 65.0
                elif water_ratio <= 1.5:
                    s_water = 45.0
                else:
                    s_water = 25.0
                
                if climate_data["mean_annual_rainfall_mm"] < 550:
                    drought_tol_count = sum(1 for c in seq if c["drought_tolerance"] == "High")
                    s_water = min(100.0, s_water + drought_tol_count * 5.0)

                n_fix_bonus = legume_count * 15.0
                residue_bonus = sum(12.0 for c in seq if c["soil_cover_residue"] == "High") + sum(6.0 for c in seq if c["soil_cover_residue"] == "Moderate")
                deep_root_bonus = sum(10.0 for c in seq if c["rooting_depth_m"] >= 1.5)
                family_count = len(set(c["plant_family"] for c in seq))
                diversity_bonus = family_count * 8.0
                s_soil = min(100.0, 20.0 + n_fix_bonus + residue_bonus + deep_root_bonus + diversity_bonus)

                risk_penalty = sum(15.0 for c in seq if c["economic_risk"] == "High") + sum(5.0 for c in seq if c["economic_risk"] == "Moderate")
                s_econ = max(30.0, 100.0 - risk_penalty)

                hot_days = climate_data["hot_days_per_year"]
                dry_spells = climate_data["dry_spells_per_year"]
                heat_fit = sum(12.0 for c in seq if c["heat_tolerance"] == "High") + sum(6.0 for c in seq if c["heat_tolerance"] == "Moderate")
                drought_fit = sum(12.0 for c in seq if c["drought_tolerance"] == "High") + sum(6.0 for c in seq if c["drought_tolerance"] == "Moderate")
                
                base_climate_stress = (hot_days * 0.4) + (dry_spells * 5.0)
                s_resilience = min(100.0, max(30.0, 50.0 + (heat_fit + drought_fit) - (base_climate_stress * 0.25)))

                soil_ph = soil_data.get("ph", 6.8)
                ph_mismatch = 0
                for c in seq:
                    if soil_ph < c["ph_min"] or soil_ph > c["ph_max"]:
                        ph_mismatch += 1
                ph_penalty = ph_mismatch * 8.0

                w_tot = sum(weights.values())
                composite_score = (
                    weights["water"] * s_water +
                    weights["soil"] * s_soil +
                    weights["econ"] * s_econ +
                    weights["resilience"] * s_resilience
                ) / max(w_tot, 1)
                composite_score = max(10.0, composite_score - ph_penalty)

                rationale_points = []
                if legume_count > 0:
                    rationale_points.append(f"Includes {legume_count} biological N-fixing season(s) cutting synthetic fertilizer dependency")
                if any(c["rooting_depth_m"] >= 1.5 for c in seq):
                    rationale_points.append("Deep taproots break hardpan compaction and tap deep moisture reserves")
                if annual_water_need <= mean_rainfall:
                    rationale_points.append(f"Annual water budget ({int(annual_water_need)}mm) is sustainable under NASA historical rainfall ({int(mean_rainfall)}mm)")
                else:
                    rationale_points.append(f"Water demand ({int(annual_water_need)}mm) slightly exceeds mean rain; requires soil water retention practices")
                if climate_data["hot_days_per_year"] > 30 and any(c["heat_tolerance"] == "High" for c in seq):
                    rationale_points.append("Utilizes C4 / heat-tolerant crops resilient to extreme summer temperature spikes")

                candidates.append({
                    "crops": [c["crop_name"] for c in seq],
                    "crop_objects": seq,
                    "composite_score": round(composite_score, 1),
                    "s_water": round(s_water, 1),
                    "s_soil": round(s_soil, 1),
                    "s_econ": round(s_econ, 1),
                    "s_resilience": round(s_resilience, 1),
                    "annual_water_need_mm": int(annual_water_need),
                    "total_water_need_mm": int(total_water_need),
                    "legume_seasons": legume_count,
                    "families": list(set(c["plant_family"] for c in seq)),
                    "rationale": " • ".join(rationale_points)
                })

    candidates.sort(key=lambda x: x["composite_score"], reverse=True)
    
    unique_candidates = []
    seen_seqs = set()
    for cand in candidates:
        key = tuple(cand["crops"])
        if key not in seen_seqs:
            seen_seqs.add(key)
            unique_candidates.append(cand)
            if len(unique_candidates) >= 5:
                break
                
    return unique_candidates

def evaluate_baseline_monoculture(past_crop_name: str, crop_df: pd.DataFrame, climate_data: dict, soil_data: dict, weights: dict):
    """
    Evaluates continuous monoculture of the farmer's current primary crop for comparative baseline.
    """
    crop_by_name = {c["crop_name"]: c for c in crop_df.to_dict(orient="records")}
    crop = crop_by_name.get(past_crop_name, list(crop_by_name.values())[0])
    
    s_water = 60.0 if crop["water_need_mm"] <= climate_data["mean_annual_rainfall_mm"] else 35.0
    s_soil = 30.0 if crop["nitrogen_fixing"] == "No" else 55.0
    s_econ = 65.0
    s_resilience = 40.0 if crop["drought_tolerance"] != "High" else 65.0
    
    w_tot = sum(weights.values())
    composite = (
        weights["water"] * s_water +
        weights["soil"] * s_soil +
        weights["econ"] * s_econ +
        weights["resilience"] * s_resilience
    ) / max(w_tot, 1)

    return {
        "crop_name": crop["crop_name"],
        "composite_score": round(composite, 1),
        "s_water": round(s_water, 1),
        "s_soil": round(s_soil, 1),
        "s_econ": round(s_econ, 1),
        "s_resilience": round(s_resilience, 1),
        "annual_water_need_mm": crop["water_need_mm"],
        "vulnerability_notes": "Continuous monoculture increases pest persistence, risks soil compaction, and compounds climate vulnerability."
    }
