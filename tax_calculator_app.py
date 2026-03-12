
import streamlit as st

def calculate_tax(taxable_income, slabs):
    tax = 0
    remaining_income = taxable_income
    sorted_slabs = sorted(slabs, key=lambda x: x[0], reverse=True)
    for threshold, rate in sorted_slabs:
        if remaining_income > threshold:
            taxable_at_this_rate = remaining_income - threshold
            tax += taxable_at_this_rate * rate
            remaining_income = threshold
    return tax

st.set_page_config(page_title="Income Tax AY 2026-27", layout="wide")

st.title("📊 Tax Computation Dashboard")
st.markdown("### Assessment Year 2026-27 (Financial Year 2025-26)")

# --- INPUT SECTION ---
with st.sidebar:
    st.header("💡 Input Values (Yellow Cells)")
    age = st.number_input("Enter Age", value=30)
    basic_da = st.number_input("Annual Basic + DA", value=500000)
    hra_rec = st.number_input("Annual HRA Received", value=200000)
    special_allowance = st.number_input("Special Allowance", value=100000)
    other_income = st.number_input("Other Income", value=0)
    
    st.divider()
    rent_paid = st.number_input("Annual Rent Paid", value=0)
    is_metro = st.checkbox("Living in Metro City?")
    
    st.divider()
    deduct_80c = st.number_input("Section 80C (Max 1.5L)", value=150000, max_value=150000)
    deduct_80d = st.number_input("Section 80D (Health Insurance)", value=25000)

# --- FORMULA ENGINE ---
gross_total = basic_da + hra_rec + special_allowance + other_income
std_deduction = 75000

# HRA Logic
hra_perc = 0.5 if is_metro else 0.4
hra_exempt = min(hra_rec, hra_perc * basic_da, max(0, rent_paid - (0.1 * basic_da)))

# Taxable Income
taxable_new = max(0, gross_total - std_deduction)
taxable_old = max(0, gross_total - std_deduction - hra_exempt - deduct_80c - deduct_80d)

# Slabs (AY 2026-27)
new_slabs = [(2400000, 0.30), (2000000, 0.25), (1600000, 0.20), (1200000, 0.15), (800000, 0.10), (400000, 0.05), (0, 0)]
old_slabs = [(1000000, 0.30), (500000, 0.20), (250000, 0.05), (0, 0)]

tax_new = calculate_tax(taxable_new, new_slabs)
tax_old = calculate_tax(taxable_old, old_slabs)

# Rebate 87A (Simplified)
if taxable_new <= 700000: tax_new = 0
if taxable_old <= 500000: tax_old = 0

# Final with Cess
final_new = tax_new * 1.04
final_old = tax_old * 1.04

# --- OUTPUT DASHBOARD ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("New Tax Regime")
    st.metric("Total Tax", f"₹{final_new:,.0f}")
    st.caption(f"Taxable Income: ₹{taxable_new:,.0f}")

with c2:
    st.subheader("Old Tax Regime")
    st.metric("Total Tax", f"₹{final_old:,.0f}")
    st.caption(f"Taxable Income: ₹{taxable_old:,.0f}")

st.divider()
if final_new < final_old:
    st.success(f"🏆 **Recommended:** NEW REGIME (Saves you ₹{final_old - final_new:,.0f})")
else:
    st.success(f"🏆 **Recommended:** OLD REGIME (Saves you ₹{final_new - final_old:,.0f})")
