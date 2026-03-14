import streamlit as st
import pandas as pd

st.set_page_config(page_title="Doctor Report Generator", layout="wide")
st.title("🏥 Doctor Share & Payment Report")

uploaded_file = st.file_uploader("আপনার এক্সেল বা সিএসভি ফাইলটি এখানে আপলোড করুন", type=['csv', 'xlsx'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, skiprows=1)
        else:
            df = pd.read_excel(uploaded_file, skiprows=1)

        def calculate_share(row):
            doc_name = str(row['Doctor Name']).strip()
            alias = str(row['Doctor Name (Alias)']).strip()
            test_name = str(row['Pt. Name']).upper()
            gross = float(row['Gross Amount'])
            net = float(row['Net Amount'])

            if doc_name in ['Dr. Nandini Biswas', 'Dr. Nirbhay Kulshrestha']:
                if 'PTF' in test_name: return 0
                return gross * 0.25

            if alias == 'March ENT':
                if any(x in test_name for x in ['FIBRO', 'MICRO', 'NASAL']):
                    return gross * 0.80
                elif 'USG' in test_name or gross == 0:
                    return 0
                return gross * 0.20

            if 'DIALYSIS' in test_name:
                if 'SRKCPI' in doc_name.upper(): return net * 0.90
                return 1100 * 0.80

            return float(row['Doc Share'])

        df['Final_Doc_Share'] = df.apply(calculate_share, axis=1)
        df['Company_Share'] = df['Net Amount'] - df['Final_Doc_Share']

        st.success("রিপোর্ট তৈরি হয়ে গেছে!")
        st.dataframe(df[['Date', 'Doctor Name', 'Pt. Name', 'Gross Amount', 'Net Amount', 'Final_Doc_Share', 'Company_Share']])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 ডাউনলোড রিপোর্ট (CSV)", csv, "Doctor_Report.csv", "text/csv")

    except Exception as e:
        st.error(f"ফাইলটি চেক করুন। এরর: {e}")
