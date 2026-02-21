import streamlit as st

st.set_page_config(page_title="ECMO Metabolic Calculator", layout="wide")

# --- APP HEADER ---
st.title("Metabolic Energy Expenditure Calculator")
st.subheader("Specialized Indirect Calorimetry & ECMO Tool")

# --- 1. METHOD SELECTION ---
method = st.selectbox(
    "Select Calculation Method:",
    ["capnography/dual-calorimeter", "EPER", "MEEP"]
)

st.divider()

# --- 2. DYNAMIC INPUT FIELDS ---
# We use columns to organize the 14 data points cleanly
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Standard Calorimetry")
    vo2 = st.number_input("VO2 (mL/min)", value=0.0, step=0.1, help="Oxygen consumption from ventilator/dual-calorimeter")
    vco2 = st.number_input("VCO2 (mL/min)", value=0.0, step=0.1, help="Carbon dioxide production from ventilator/dual-calorimeter")

with col2:
    st.markdown(f"### {method} Parameters")
    
    # Initializing all potential variables
    ecmo_vo2 = ecmo_vco2 = sweep_flow = fi_o2 = fe_co2 = blood_flow = hb = pre_s_o2 = pre_p_o2 = post_s_o2 = post_p_o2 = 0.0

    if method == "capnography/dual-calorimeter":
        ecmo_vo2 = st.number_input("ECMO-VO2 (mL/min)", value=0.0, step=0.1)
        ecmo_vco2 = st.number_input("ECMO-VCO2 (mL/min)", value=0.0, step=0.1)

    elif method == "EPER":
        sweep_flow = st.number_input("ECMO sweep gas flow (L/min)", value=0.0, step=0.1)
        fi_o2 = st.number_input("ECMO FiO2 (%)", value=0.0, step=0.1)
        fe_co2 = st.number_input("ECMO FeCO2 (%)", value=0.0, step=0.01)

    elif method == "MEEP":
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            blood_flow = st.number_input("ECMO blood flow (L/min)", value=0.0, step=0.1)
            sweep_flow = st.number_input("ECMO sweep gas flow (L/min)", value=0.0, step=0.1)
            fe_co2 = st.number_input("ECMO FeCO2 (%)", value=0.0, step=0.01)
            hb = st.number_input("Hemoglobin (g/dL)", value=0.0, step=0.1)
        with sub_col2:
            pre_s_o2 = st.number_input("Pre-circuit SvO2 (%)", value=0.0, step=0.1)
            pre_p_o2 = st.number_input("Pre-circuit PvO2 (%)", value=0.0, step=0.1)
            post_s_o2 = st.number_input("Post-circuit SaO2 (%)", value=0.0, step=0.1)
            post_p_o2 = st.number_input("Post-circuit PaO2 (%)", value=0.0, step=0.1)

st.divider()

# --- 3. CALCULATION LOGIC ---
final_ee = 0.0
final_rq = 0.0

try:
    if method == "capnography/dual-calorimeter":
        total_vo2 = vo2 + ecmo_vo2
        total_vco2 = vco2 + ecmo_vco2
        final_ee = ((3.94 * total_vo2) + (1.11 * total_vco2)) * 1.44
        final_rq = total_vco2 / total_vo2 if total_vo2 != 0 else 0

    elif method == "EPER":
        eper_vo2 = (sweep_flow * 1000) * ((fi_o2 / 100) - ((fi_o2 / 100) - (fe_co2 / 100)))
        eper_vco2 = (sweep_flow * 1000) * (fe_co2 / 100)
        total_vo2 = vo2 + eper_vo2
        total_vco2 = vco2 + eper_vco2
        final_ee = ((3.94 * total_vo2) + (1.11 * total_vco2)) * 1.44
        final_rq = total_vco2 / total_vo2 if total_vo2 != 0 else 0

    elif method == "MEEP":
        meep_vo2 = ((1.34 * hb * (post_s_o2 / 100) * (0.003 * post_p_o2)) - 
                    (1.34 * hb * (pre_s_o2 / 100) * (0.003 * pre_p_o2))) * blood_flow * 10
        meep_vco2 = sweep_flow * (fe_co2 / 100) * 1000 * 0.88
        total_vo2 = vo2 + meep_vo2
        total_vco2 = vco2 + meep_vco2
        final_ee = ((3.94 * total_vo2) + (1.11 * total_vco2)) * 1.44
        final_rq = total_vco2 / total_vo2 if total_vo2 != 0 else 0

    # --- 4. RESULTS DISPLAY ---
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("Energy Expenditure (kcal/day)", f"{final_ee:,.0f}")
    with res_col2:
        st.metric("Respiratory Quotient (RQ)", f"{final_rq:.2f}")

except Exception:
    st.warning("Please ensure all relevant data points are entered for calculation.")

# --- 5. CREDITS & CITATIONS ---
st.divider()
st.markdown("### Created by S Pelekhaty MS, RDN, LDN, CNSC, FAND, FASPEN 2.2026")

st.markdown("""
**Citations:**
1. Wollersheim T, Frank S, Müller MC, et al. Measuring Energy Expenditure in extracorporeal lung support Patients (MEEP) - Protocol, feasibility and pilot trial. *Clin Nutr.* 2018;37(1):301-307. doi:10.1016/j.clnu.2017.01.001
2. De Waele E, Jonckheer J, Pen JJ, et al. Energy expenditure of patients on ECMO: A prospective pilot study. *Acta Anaesthesiol Scand.* 2019;63(3):360-364. doi:10.1111/aas.13287
3. Pelekhaty SL, Rector RP, Wu ZJ, et al. ECMO patient energy requirements: A descriptive, retrospective cohort study. *Nutr Clin Pract.* 2026;41(1):110-119. doi:10.1002/ncp.11330
""")
