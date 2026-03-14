import streamlit as st
import pandas as pd

st.set_page_config(page_title="Doctor Report Generator", layout="wide")
st.title("🏥 Specialist Doctor Share Report")

# এখানে type=['csv', 'xlsx'] করা হয়েছে যাতে এক্সেল ফাইল সাপোর্ট করে
uploaded_file = st.file_uploader("Upload Doc Payment File (CSV or Excel)", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        # ফাইলটি এক্সেল নাকি সিএসভি তা চেক করে পড়া
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=1)
        else:
            df = pd.read_excel(uploaded_file, skiprows=1)
            
        df.columns = df.columns.str.strip() 

        def calculate_share(row):
            doc_name = str(row['Doctor Name']).strip()
            alias = str(row['Doctor Name (Alias)']).strip()
            pt_name = str(row.get('Pt. Name', '')).upper()
            gross = float(row['Gross Amount'])
            net = float(row['Net Amount'])
            current_share = float(row['Doc Share'])

            # ১. Cardio Logic
            if doc_name in ['Dr. Nandini Biswas', 'Dr. Nirbhay Kulshrestha']:
                if 'PTF' in pt_name: return 0.0
                return gross * 0.25

            # ২. March ENT Logic
            if alias == 'March ENT':
                if 'USG' in pt_name or current_share == 0: return 0.0
                if any(x in pt_name for x in ['FIBRO', 'MICRO', 'NASAL']):
                    return gross * 0.80
                return gross * 0.20

            # ৩. Dialysis Logic
            if 'DIALYSIS' in pt_name:
                if 'SRKCPI' in doc_name.upper(): return net * 0.90
                return 1100 * 0.80

            return current_share

        df['New_Calculated_Share'] = df.apply(calculate_share, axis=1)
        df['Company_Profit'] = df['Net Amount'] - df['New_Calculated_Share']

        st.success("Report Ready!")
        cols_to_show = ['Date', 'Doctor Name', 'Pt. Name', 'Gross Amount', 'Net Amount', 'Doc Share', 'New_Calculated_Share']
        st.dataframe(df[cols_to_show])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Final Report", csv, "Doctor_Report.csv", "text/csv")

    except Exception as e:
        st.error(f"Error: {e}")
