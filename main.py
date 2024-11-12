import numpy as np
import pandas as pd
import warnings
from io import StringIO
import streamlit as st

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = None

# Function that calculates FTLD-CDR global from CDR boxes
# Ultima versión 09/01/2024
def calculate_cdr_FTD_inline(memory, secondary_categories):
    """
    memory (int): 0, 0.5, 1, 2
    secondary_categories (list): list of box scores .i.e [1, 1, 1, 0.5, 2, 1,2]
    """
    ### Scoring rules ### 
   
    rules={
        "1": "Rule 1: If all domains are 0, CDR = 0",
        "2": "Rule 2:  If max(domains) == 0.5, CDR = 0.5",
        "3a": "Rule 3 (If any domain >0.5) and A: if one domain is 1 and all other are 0, CDR = 0.5",
        "3b": "Rule 3 (If any domain >0.5) and B: if one domain is 2 or 3 and all other are 0, CDR = 1",
        "3c": "Rule 3 (If any domain >0.5) and C: if max(domain) is not repeated and there is another domain > 0 , CDR = one level below max(domain)",
        "3d":  "Rule 3 (If any domain >0.5) and D: if max(domain) is repeated , CDR =  max(domain)",
        "Missing": "One ore more domains are missing"
    }
    domains = [memory] + secondary_categories
    max_score = np.max(domains)
    serie = pd.Series(domains).value_counts().sort_index()
    categories = list(serie.index)
    
    # Rule 0, if any domain is missing, don't calculate the CDR-FTLD score
    if np.isnan(domains).any():
        rule = rules['Missing']
        return np.nan, rule
    
    # Rule 1
    ## If all domains are 0, CDR = 0
    if max_score == 0:
        rule = rules["1"]
        return 0, rule
    
    # Rule 2
    ## If max(domains) == 0.5, CDR = 0.5
    if max_score == 0.5:
        rule = rules["2"]
        return 0.5, rule
    
    # Rule 3
    ## If any domain >0.5
    if max_score > 0.5:
        
        ## Rule 3.A
        ## if one domain is 1 and all other are 0, CDR = 0.5
        if (domains.count(0) == 7) and (max_score == 1):
            rule = rules['3a']
            return 0.5, rule
        ## Rule 3.B
        ## if one domain is 2 or 3 and all other are 0, CDR = 1
        elif (domains.count(0) == 7) and ((max_score == 2) | (max_score == 3)):
            rule = rules['3b']
            return 1, rule
        ## Rule 3.C
        ## if max(domain) is not repeated and there is another domain > 0 , CDR = one level below max(domain)
        elif (domains.count(max_score) == 1) and ( (domains.count(0.5)>= 1) |  ((domains.count(1)>= 1) and max_score != 1) | ((domains.count(2)>= 1) and max_score != 2) | ((domains.count(3)>= 1) and max_score != 3) ):
            # temp_serie = serie.drop(index=max_score, axis=0)
            # return temp_serie.index[-1]
            rule = rules['3c']
            if max_score !=1:
                return max_score - 1, rule
            else:
                return 0.5, rule
        
        ## Rule 3.D
        ## if max(domain) is repeated , CDR =  max(domain)
        elif (domains.count(max_score) > 1):
            rule = rules['3d']
            return max_score, rule
        

def calculate_cdr_FTD(memory, secondary_categories):
    """
    memory (int): 0, 0.5, 1, 2
    secondary_categories (list): list of box scores .i.e [1, 1, 1, 0.5, 2, 1,2]

    ### Scoring rules ### 
    # Rule 1
    ## If all domains are 0, CDR = 0
    #Rule 2
    ## If max(domains) == 0.5, CDR = 0.5
    # Rule 3
    ## If any domain >0.5
        ## Rule 3.A
        ## if one domain is 1 and all other are 0, CDR = 0.5
        ## Rule 3.B
        ## if one domain is 2 or 3 and all other are 0, CDR = 1
        ## Rule 3.C
        ## if max(domain) is not repeated and there is another domain > 0 , CDR = one level below max(domain)
        ## Rule 3.D
        ## if max(domain) is repeated , CDR =  max(domain)
      """
    import numpy as np
    import pandas as pd
    domains = [memory] + secondary_categories
    max_score = np.max(domains)
    serie = pd.Series(domains).value_counts().sort_index()
    categories = list(serie.index)
    
    # Rule 0, if any domain is missing, don't calculate the CDR-FTLD score
    if np.isnan(domains).any():
        print("One ore more domains are missing. Fill your NaNs and try again")
        return np.nan
    
    # Rule 1
    ## If all domains are 0, CDR = 0
    if max_score == 0:
        print('Rule 1')
        return 0
    
    # Rule 2
    ## If max(domains) == 0.5, CDR = 0.5
    if max_score == 0.5:
        print('Rule 2')
        return 0.5
    
    # Rule 3
    ## If any domain >0.5
    if max_score > 0.5:
        
        ## Rule 3.A
        ## if one domain is 1 and all other are 0, CDR = 0.5
        if (domains.count(0) == 7) and (max_score == 1):
            print('Rule 3a')
            return 0.5
        ## Rule 3.B
        ## if one domain is 2 or 3 and all other are 0, CDR = 1
        elif (domains.count(0) == 7) and ((max_score == 2) | (max_score == 3)):
            print("Rule 3b")
            return 1
        ## Rule 3.C
        ## if max(domain) is not repeated and there is another domain > 0 , CDR = one level below max(domain)
        elif (domains.count(max_score) == 1) and ( (domains.count(0.5)>= 1) |  ((domains.count(1)>= 1) and max_score != 1) | ((domains.count(2)>= 1) and max_score != 2) | ((domains.count(3)>= 1) and max_score != 3) ):
            # temp_serie = serie.drop(index=max_score, axis=0)
            # return temp_serie.index[-1]
            print("Rule 3c")
            if max_score !=1:
                return max_score - 1
            else:
                return 0.5
        
        ## Rule 3.D
        ## if max(domain) is repeated , CDR =  max(domain)
        elif (domains.count(max_score) > 1):
            print("Rule 3d")
            return max_score
        

st.title("FTLD-CDR Global calculator.")
st.subheader("A simple app to calculate the FTLD-CDR global from the CDR boxes.")
st.markdown(" ##### Please, test it, use it and write to mmaito@udesa.edu.ar if you find any scoring errors.")
st.markdown(""" ### FTLD-CDR Scoring Instructions.
            
Two scores must be obtained:

1. FTLD-CDR Box Sum (automatically calculated in REDCap): Calculate the sum of values for all responses (including the two additional domains) and enter the total score in the provided space.
2. Global FTLD-CDR: derived from the scores in each of the eight categories ("box scores").
            
#### The rules for determining the FTLD-CDR global score are as follows. (Remember, it involves the eight domains or boxes):
1. If all domains are 0, the FTLD-CDR global score is 0.
2. If the maximum domain score is 0.5, the FTLD-CDR global score is 0.5.
3. If the maximum domain score is greater than 0.5 in any domain, the following applies:

    A. If the maximum domain score is 1 and all other domains are 0, the FTLD-CDR global score is 0.5.
            
    B. If the maximum domain score is 2 or 3 and all other domains are 0, the FTLD-CDR global score is 1.
            
    C. If the maximum domain score occurs only once, and there is another score other than zero, the FTLD-CDR global score is one level lower than the level corresponding to the maximum impairment (for example, if the maximum = 2, and there is another score other than zero, the FTLD-CDR global score is 1; if the maximum = 1, and there is another score other than zero, the FTLD-CDR global score is 0.5).
            
    D. If the maximum domain score occurs more than once (for example, 1 in 2 domains, 2 in 2 domains), then the FTLD-CDR global score is that maximum domain score.          
---
          """)

st.markdown("##### Please, select the score for memory and secundary scores.")

### Selectbox
memory = st.radio(f"**Memory**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)
orientation = st.radio(f"**Orientation**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)
problem = st.radio(f"**Judgment and Problem Solving**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)
community = st.radio(f"**Community Affairs**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)
home = st.radio(f"**Home and Hobbies**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)
care = st.radio(f"**Personal Care**", options=(0, 1, 2, 3), index=0, horizontal=True, help="Personal care cannot be scored 0.5")
behav = st.radio(f"**Behavior, Comportment and Personality**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)
lang = st.radio(f"**Language**", options=(0, 0.5, 1, 2, 3), index=0, horizontal=True)

secondary_categories = [orientation, problem, community, home, care, behav, lang]

cdr_global, rule = calculate_cdr_FTD_inline(memory=memory, secondary_categories=secondary_categories)

st.metric(label="**:blue[FTLD-CDR Global Score]**", value=cdr_global, delta=None)
st.markdown(f"##### Applied rule:")
st.write(f"{rule}")

st.markdown("---")
st.markdown(""" ##### Please, upload your csv file yo have your cdr global calculated.
 First row must be columna names in this order: Memory, box1, box2, ..., box7.
 The programm returns the same csv with the FTLD_CDR_global column for each row""")

uploaded_file = st.file_uploader(label="File to calculate FTLD-CDR Global", accept_multiple_files=False)
if uploaded_file:

    pd_file = pd.read_csv(uploaded_file)
    rows = pd_file.shape[0]
    results =[]

    for row in range(len(pd_file)):
        m = pd_file.iloc[row,0]
        sc = list(pd_file.iloc[row, 1:].values)
        cdr = calculate_cdr_FTD(memory=m, secondary_categories=sc)
        results.append(cdr)


    pd_file['FTLD_CDR_global'] = results
    st.write("Preview FTLD-CDR Global")
    st.table(pd_file.head().style.format("{:.1f}"))

    data_as_csv= pd_file.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download data as CSV",
        data=data_as_csv,
        file_name="Calculated_FTLD_CDR_global.csv",
        mime="text/plain")
    
