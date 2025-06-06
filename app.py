import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import base64
from io import BytesIO
from fpdf import FPDF

# Set page config
st.set_page_config(page_title="CO₂ Reduction Calculator", layout="wide")

# Custom CSS for clean layout
st.markdown("""
    <style>
    .stApp {
        max-width: 1300px;
        margin: 0 auto;
    }
    .metric-box {
        background-color: #ffffff;
        padding: 30px;
        border-radius: 14px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        font-size: 28px;
        font-weight: bold;
        border: 1px solid #e5e7eb;
    }
    .metric-label {
        font-size: 15px;
        color: #444;
        margin-top: 6px;
    }
    h1, h2, h3, h4 {
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 CO₂ Reduction & ROI Dashboard")

# Carbon emission factors by country (kg CO₂/kWh)
country_factors = {
    "Indonesia": 0.87,
    "Singapore": 0.408,
    "Malaysia": 0.585,
    "Thailand": 0.513,
    "Vietnam": 0.618,
    "Philippines": 0.65,
    "China": 0.555,
    "Japan": 0.474,
    "South Korea": 0.405,
    "India": 0.82,
    "Australia": 0.79,
    "United States": 0.42,
    "United Kingdom": 0.233,
    "Germany": 0.338,
    "Custom": None
}

# Input Section
st.header("🔧 Input Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    energy_savings = st.number_input("Estimated Energy Savings (kWh/year)", value=1040249.0)

with col2:
    selected_country = st.selectbox("Select Country", list(country_factors.keys()))
    if selected_country == "Custom":
        carbon_emission_factor = st.number_input("Custom Carbon Emission Factor (kg CO₂/kWh)", value=0.82)
    else:
        carbon_emission_factor = country_factors[selected_country]
        st.info(f"Using carbon factor for {selected_country}: {carbon_emission_factor} kg CO₂/kWh")

with col3:
    electricity_rate = st.number_input("Electricity Rate ($/kWh)", value=0.14)
    savings_percentage = st.number_input("Savings Percentage", value=8.8, format="%.2f") / 100

# Derived Calculations
total_energy_before = energy_savings / savings_percentage if savings_percentage > 0 else 0
energy_after = total_energy_before - energy_savings
electricity_cost_before = total_energy_before * electricity_rate
electricity_cost_after = energy_after * electricity_rate
annual_co2_reduction = energy_savings * carbon_emission_factor

# ROI Calculations
initial_investment = st.number_input("Initial Investment ($)", value=16000.0)
software_fee = st.number_input("Annual Software Fee ($)", value=72817.0)
years = 10
annual_savings = energy_savings * electricity_rate
cumulative_savings = []
net_cash_flow = []
total_costs = [initial_investment + software_fee] + [software_fee] * (years - 1)

for i in range(years):
    net = annual_savings - total_costs[i]
    net_cash_flow.append(net if i == 0 else net_cash_flow[-1] + net)
    cumulative_savings.append(net_cash_flow[-1])

three_year_net_income = round(cumulative_savings[2] / 1000)
payback_months = 0
for i in range(years):
    if cumulative_savings[i] >= 0:
        payback_months = round((i + 1) * 12 * ((total_costs[i] - annual_savings) / annual_savings), 0)
        break

# Metrics Display
st.markdown("### 📈 Overview")
metrics_col, chart_col = st.columns([1, 3])

with metrics_col:
    st.markdown(f"""
    <div class=\"metric-box\">{annual_co2_reduction / 1000:.1f}<div class=\"metric-label\">tCO₂e/year<br>Carbon Reduction</div></div>
    <br>
    <div class=\"metric-box\">{energy_savings / 1000:,.0f}k<div class=\"metric-label\">kWh/year<br>Energy Reduction</div></div>
    <br>
    <div class=\"metric-box\">{savings_percentage * 100:.1f}%<div class=\"metric-label\">Saving Percentage</div></div>
    <br>
    <div class=\"metric-box\">{int(payback_months):02d}<div class=\"metric-label\">Months<br>Payback Period</div></div>
    <br>
    <div class=\"metric-box\">{three_year_net_income}k<div class=\"metric-label\">US Dollars<br>Net Income (3yrs)</div></div>
    """, unsafe_allow_html=True)

with chart_col:
    st.subheader("📉 Annual Saving (2025)")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["2025"], y=[energy_savings], name='Annual Energy Reduction (kWh)',
                         marker_color='#3B82F6', text=[f"{int(energy_savings / 1000)}k"], textposition="outside"))
    fig.update_layout(height=420, xaxis=dict(showgrid=False), yaxis=dict(showgrid=True),
                      margin=dict(l=20, r=20, t=30, b=30), showlegend=False, plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("💰 10-Year ROI Forecast")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=list(range(years)), y=[annual_savings]*years, name="Annual Savings", marker_color="#10B981"))
    fig2.add_trace(go.Bar(x=list(range(years)), y=total_costs, name="Annual Costs", marker_color="#F87171"))
    fig2.add_trace(go.Scatter(x=list(range(years)), y=cumulative_savings, mode='lines+markers', name="Cumulative Net Savings", line=dict(color="#3B82F6")))
    fig2.update_layout(barmode='group', height=400, xaxis_title='Year', yaxis_title='Cash Flow ($)',
                       plot_bgcolor='white', legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig2, use_container_width=True)

# PDF Export Section
st.markdown("---")
st.subheader("🧒 Export Proposal Summary")

report_content = f'''
CO₂ Reduction Proposal Summary

Energy Savings: {energy_savings:,.0f} kWh/year
Carbon Reduction: {annual_co2_reduction / 1000:.1f} tCO₂e/year
Electricity Rate: ${electricity_rate:.3f} /kWh
Savings Percentage: {savings_percentage * 100:.1f}%
Initial Investment: ${initial_investment:,.0f}
Software Fee: ${software_fee:,.0f}/year
Net Income (3yrs): ${three_year_net_income:,}k
Payback Period: {int(payback_months)} months
'''

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 14)
        self.image("univers_logo.png", 10, 8, 33)  # Add logo image
        self.cell(0, 10, "Univers CO₂ Reduction Summary", ln=True, align='C')
        self.ln(10)

    def chapter_body(self, text):
        self.set_font("Arial", '', 12)
        self.multi_cell(0, 10, text)
        self.ln()

    def create_pdf(self, content):
        self.add_page()
        self.chapter_body(content)

pdf = PDF()
pdf.create_pdf(report_content)
pdf_buffer = BytesIO()
pdf.output(pdf_buffer)

st.download_button(
    label="🗓️ Download Summary Report (PDF)",
    data=pdf_buffer.getvalue(),
    file_name="CO2_Proposal_Summary.pdf",
    mime="application/pdf"
)

# Browser Print Option
st.markdown("""
    <br>
    <button onclick="window.print()" style="padding:10px 20px; font-size:16px; background:#1f77b4; color:white; border:none; border-radius:6px; cursor:pointer;">
        ☑️ Print / Save Full Page as PDF
    </button>
    <p style='font-size:13px; margin-top:10px;'>Use this button to export the entire dashboard view including charts and inputs.</p>
""", unsafe_allow_html=True)

st.markdown("""
Notes:
- Chart shows only total for 2025 without monthly breakdown.
- ROI forecast reflects adjustable investment + fee vs. energy cost savings.
- PDF download includes summary metrics.
- Blue print button lets you download full dashboard manually.
""")

st.caption("Crafted by Univers AI • Powered by Streamlit • Engineered for client impact.")
