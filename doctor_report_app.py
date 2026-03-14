import streamlit as st
import pandas as pd

st.set_page_config(page_title="Doctor Report Generator", layout="wide")
st.title("🏥 Specialist Doctor Share Report")

uploaded_file = st.file_uploader("Upload Doc Payment CSV", type=['csv'])

if uploaded_file is not None:
    try:
        # CSV reading (skiprows=1 used because your file has a summary row at the top)
        df = pd.read_csv(uploaded_file, skiprows=1)
        df.columns = df.columns.str.strip() # Removing extra spaces from column names

        def calculate_share(row):
            doc_name = str(row['Doctor Name']).strip()
            alias = str(row['Doctor Name (Alias)']).strip()
            pt_name = str(row['Pt. Name']).upper() # PT Name column used for test names
            gross = float(row['Gross Amount'])
            net = float(row['Net Amount'])
            current_share = float(row['Doc Share'])

            # --- ১. Cardio Logic (Dr. Nandini & Nirbhay) ---
            if doc_name in ['Dr. Nandini Biswas', 'Dr. Nirbhay Kulshrestha']:
                if 'PTF' in pt_name:
                    return 0.0
                else:
                    return gross * 0.25 # Gross-এর ওপর ২৫%

            # --- ২. March ENT Logic (Arjun, Chirajit, NVK Mohan) ---
            if alias == 'March ENT':
                # USG হলে ০, অথবা যদি আগে থেকেই ০ থাকে তবে ০
                if 'USG' in pt_name or current_share == 0:
                    return 0.0
                # নির্দিষ্ট ৩টি টেস্টে ৮০% (Gross-এর ওপর)
                if any(x in pt_name for x in ['FIBRO', 'MICRO', 'NASAL']):
                    return gross * 0.80
                # বাকি সব ENT টেস্টে ২০% (Gross-এর ওপর)
                else:
                    return gross * 0.20

            # --- ৩. Dialysis Logic ---
            if 'DIALYSIS' in pt_name:
                if 'SRKCPI' in doc_name.upper():
                    return net * 0.90 # SRKCPI হলে Net-এর ওপর ৯০%
                else:
                    return 1100 * 0.80 # সাধারণ ডায়ালিসিস হলে ফিক্সড ৮৮০ টাকা

            # ৪. বাকি সব ক্ষেত্রে ফাইলে যা আছে তাই থাকবে
            return current_share

        # নতুন শেয়ার কলাম তৈরি
        df['New_Calculated_Share'] = df.apply(calculate_share, axis=1)
        df['Company_Profit'] = df['Net Amount'] - df['New_Calculated_Share']

        st.success("Report Generated Successfully with Specific Rules!")
        
        # Displaying only important columns for clarity
        cols_to_show = ['Date', 'Doctor Name', 'Pt. Name', 'Gross Amount', 'Net Amount', 'Doc Share', 'New_Calculated_Share', 'Company_Profit']
        st.dataframe(df[cols_to_show])

        # Download Button
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Final Report", csv, "Final_Doctor_Report.csv", "text/csv")

    except Exception as e:
        st.error(f"Error in calculation: {e}")
