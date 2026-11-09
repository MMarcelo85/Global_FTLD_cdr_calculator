import sys
import os
sys.path.append(os.path.dirname(__file__))

import pandas as pd
import streamlit as st

import ftld_core

st.title("FTLD-CDR Global calculator")
st.subheader("A simple app to calculate the FTLD-CDR Global from the eight FTLD-CDR boxes.")
st.markdown(" ##### Please, test it, use it and write to mmaito@udesa.edu.ar if you find any scoring errors.")

instructions_md = ftld_core.INSTRUCTIONS.replace("\n", "\n\n", 1)
rules_md = "\n".join(f"    {c.upper()}. {ftld_core.rule_body('3' + c)}\n" for c in "abcd")
st.markdown(f"""### FTLD-CDR Scoring Instructions

{instructions_md}

#### {ftld_core.RULES_TITLE}
1. {ftld_core.rule_body('1')}
2. {ftld_core.rule_body('2')}
3. {ftld_core.RULE_3_INTRO}

{rules_md}
---
""")

st.markdown("##### Please, select the score for each of the eight domains.")

values = []
for key, label in ftld_core.DOMAINS:
    options = ftld_core.CARE_SCORES if key == "care" else ftld_core.SCORES
    help_text = "Personal care cannot be scored 0.5" if key == "care" else None
    values.append(st.radio(f"**{label}**", options=options, index=0, horizontal=True, help=help_text))

cdr_global, rule = ftld_core.calculate_ftld_cdr(values)

st.metric(label="**:blue[FTLD-CDR Global Score]**", value=ftld_core.fmt(cdr_global))
st.markdown("##### Applied rule:")
st.write(rule)

st.markdown("---")
st.markdown(f""" ##### Please, upload your csv file to have your FTLD-CDR Global calculated.
{ftld_core.CSV_HELP}
Comma, semicolon or tab separated files are accepted. The program returns the same csv with the columns
`{ftld_core.OUT_SCORE}`, `{ftld_core.OUT_RULE}` and `{ftld_core.OUT_NOTE}` (reason when a row could not be scored).""")

uploaded_file = st.file_uploader(label="File to calculate FTLD-CDR Global", type=["csv", "txt"],
                                 accept_multiple_files=False)
if uploaded_file:
    try:
        header, rows, out_csv, summary = ftld_core.process_csv(ftld_core.decode(uploaded_file.getvalue()))
    except ValueError as e:
        st.error(str(e))
    else:
        st.success(summary)
        st.write("Preview FTLD-CDR Global")
        st.dataframe(pd.DataFrame(rows, columns=header), hide_index=True)
        name = os.path.splitext(uploaded_file.name)[0]
        st.download_button(
            label="Download data as CSV",
            data=out_csv.encode("utf-8-sig"),
            file_name=f"{name}_FTLD_CDR_global.csv",
            mime="text/csv")

st.markdown("---")
st.caption(f"{ftld_core.AUTHORSHIP} Source code and desktop version: "
           "https://github.com/MMarcelo85/Global_FTLD_cdr_calculator")
