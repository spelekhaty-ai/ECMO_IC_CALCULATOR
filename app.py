import streamlit as st
import requests

# --- 1. CONFIG & COUNTER LOGIC ---
st.set_page_config(page_title="ECMO Metabolic Calculator", layout="wide")

# This hits the API to increment the count
try:
    # We use a unique key based on your name to keep your count separate
    count_url = "https://api.countapi.xyz/hit/spelekhaty_ecmo_calc/visits"
    visit_count = requests.get(count_url, timeout=2).json()['value']
except:
    visit_count = None
    
st.set_page_config(page_title="ECMO Metabolic Calculator", layout="wide")

# --- APP HEADER ---
st.title("Metabolic Energy Expenditure Calculator")
st.subheader("Specialized Indirect Calorimetry & ECMO Tool")

# --- 1. METHOD SELECTION ---
method = st.selectbox(
    "Select Calculation Method:",
    ["capnography/dual-calorimeter", "EPER", "MEEP-modified*"]
)

st.divider()

# --- 2. DYNAMIC INPUT FIELDS ---
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Standard Calorimetry")
    vo2 = st.number_input("VO2 (mL/min)", value=0.0, step=0.1)
    vco2 = st.number_input("VCO2 (mL/min)", value=0.0, step=0.1)

with col2:
    st.markdown(f"### {method} Parameters")
    
    # Initialize all potential variables
    ecmo_vo2 = ecmo_vco2 = sweep_flow = fi_o2 = fe_co2 = 0.0
    blood_flow = hb = hco3 = pre_s_o2 = pre_p_o2 = post_s_o2 = post_p_o2 = pre_pco2 = post_pco2 = 0.0

    if method == "capnography/dual-calorimeter":
        ecmo_vo2 = st.number_input("ECMO-VO2 (mL/min)", value=0.0)
        ecmo_vco2 = st.number_input("ECMO-VCO2 (mL/min)", value=0.0)

    elif method == "EPER":
        sweep_flow = st.number_input("ECMO sweep gas flow (L/min)", value=0.0)
        fi_o2 = st.number_input("ECMO FiO2 (%)", value=0.0)
        fe_co2 = st.number_input("ECMO FeCO2 (%)", value=0.0)

    elif method == "MEEP-modified*":
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            blood_flow = st.number_input("ECMO blood flow (L/min)", value=0.0)
            sweep_flow = st.number_input("ECMO sweep gas flow (L/min)", value=0.0)
            hb = st.number_input("Hemoglobin (g/dL)", value=0.0)
            hco3 = st.number_input("HCO3-", value=0.0)
        with sub_col2:
            pre_s_o2 = st.number_input("Pre-circuit SvO2", value=0.0)
            pre_p_o2 = st.number_input("Pre-circuit PvO2", value=0.0)
            pre_pco2 = st.number_input("Pre-circuit PCO2", value=0.0)
            post_s_o2 = st.number_input("Post-circuit SaO2", value=0.0)
            post_p_o2 = st.number_input("Post-circuit PaO2", value=0.0)
            post_pco2 = st.number_input("Post-circuit PCO2", value=0.0)

st.divider()

# --- 3. CALCULATION LOGIC ---
final_ee = 0.0
final_rq = 0.0

try:
    if method == "capnography/dual-calorimeter":
        total_vo2 = vo2 + ecmo_vo2
        total_vco2 = vco2 + ecmo_vco2
        
    elif method == "EPER":
        calc_vo2 = (sweep_flow * 1000) * ((fi_o2 / 100) - ((fi_o2 / 100) - (fe_co2 / 100)))
        calc_vco2 = (sweep_flow * 1000) * (fe_co2 / 100)
        total_vo2 = vo2 + calc_vo2
        total_vco2 = vco2 + calc_vco2

    elif method == "MEEP-modified*":
        calc_vo2 = ((1.34 * hb * (post_s_o2 / 100) * (0.003 * post_p_o2)) - 
                    (1.34 * hb * (pre_s_o2 / 100) * (0.003 * pre_p_o2))) * blood_flow * 10
        calc_vco2 = (((pre_pco2 * 0.03) + hco3) - ((post_pco2 * 0.03) + hco3)) * blood_flow * 10
        total_vo2 = vo2 + calc_vo2
        total_vco2 = vco2 + calc_vco2

    # Global Weir and RQ formulas using method-specific totals
    final_ee = ((3.94 * total_vo2) + (1.11 * total_vco2)) * 1.44
    final_rq = total_vco2 / total_vo2 if total_vo2 != 0 else 0

    # --- 4. RESULTS DISPLAY ---
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Energy Expenditure (kcal/day)", f"{final_ee:,.0f}")
    with res_col2:
        st.metric("Respiratory Quotient (RQ)", f"{final_rq:.2f}")

except Exception:
    st.info("Awaiting complete data entry for calculation.")

# --- 5. DISCLAIMER & REFERENCES ---
st.divider()
st.warning("**Disclaimer:** This calculator is intended for educational purposes and to increase accessability to indirect calorimetry calculations in ECMO patients, it is not intended to diagnose or treat any condition or replace clinical judgement.")

if method == "MEEP-modified*":
    st.caption("*Note: The MEEP protocol is modified in this calculator to use the Fick and Douglas equations to allow for calculation of VO2 and VCO2 from blood gases without complex computational algorithms. However, this simplified approach does not incorporate Haldane effect. The full computational model used by the MEEP protocol is available at Physio-Biome model 0149, but cannot be incorporated into this calculator.")

st.markdown("**Created by S Pelekhaty MS, RDN (February 2026)**")
    
st.markdown("""
**References:**
* Wollersheim T, Frank S, Müller MC, et al. Measuring Energy Expenditure in extracorporeal lung support Patients (MEEP) - Protocol, feasibility and pilot trial. *Clin Nutr.* 2018;37(1):301-307. doi:10.1016/j.clnu.2017.01.001
* Basnet A, Rout P. Calculating FICK Cardiac Output and Input. [Updated 2024 May 29]. In: StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; 2025 Jan-.
* Mahutte CK, Jaffe MB, Sassoon CS, Wong DH. Cardiac output from carbon dioxide production and arterial and venous oximetry. *Crit Care Med.* 1991;19(10):1270-1277.
* De Waele E, Jonckheer J, Pen JJ, et al. Energy expenditure of patients on ECMO: A prospective pilot study. *Acta Anaesthesiol Scand.* 2019;63(3):360-364.
* Pelekhaty SL, Rector RP, Wu ZJ, et al. ECMO patient energy requirements: A descriptive, retrospective cohort study. *Nutr Clin Pract.* 2026;41(1):110-119. doi:10.1002/ncp.11330
""")

# Place the counter at the absolute bottom
if visit_count:
    st.caption(f"Total tool accesses: {visit_count}")
