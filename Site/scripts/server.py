import streamlit as st
import sys

import processing


# maybe some preparations #######
sys.tracebacklimit = 0
#################################

# some constants ###################################################################################################
colors = {"sms":"blue", "email":"orange", "calls":"green", "mortgage":"red", "pension":"violet", "savings":"grey"}
font_sizes = {"plus":20}
####################################################################################################################

# some functions ###################################################################################################
def MyMarkdown(body, fontsize):
    st.markdown(
        f"""
        <style>
        .big-font-{fontsize} {{ font-size:{fontsize}px !important; }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(f'<p class="big-font-{fontsize}">{body}</p>', unsafe_allow_html=True)
###################################################################################################################


# data input #######################################################################################################
with st.columns([145, 100, 100])[1]: st.title(f"**Input**", anchor=False)  # 0_o

input_cols = st.columns([2, 1])
with input_cols[0].container(border=True):
    with st.columns([155, 100, 100])[1]: st.markdown(f"**Contacts**")

    columns_ratio = [3, 10, 10]

    with st.container(border=True):
        sms_cols = st.columns(columns_ratio)
        with sms_cols[0]: st.title("💬", anchor=False)
        with sms_cols[1]: max_sms_input = st.text_input(f"**:{colors['sms']}[max SMS]**", value="500")
        with sms_cols[2]: sms_cost_input = st.text_input(f"**:{colors['sms']}[SMS ₽ cost]**", value="0.1")

    with st.container(border=True):
        email_cols = st.columns(columns_ratio)
        with email_cols[0]: st.title("📧", anchor=False)
        with email_cols[1]: max_emails_input = st.text_input(f"**:{colors['email']}[max Emails]**", value="5000")
        with email_cols[2]: email_cost_input = st.text_input(f"**:{colors['email']}[Email ₽ cost]**", value="0.01")

    with st.container(border=True):
        calls_cols = st.columns(columns_ratio)
        with calls_cols[0]: st.title("📞", anchor=False)
        with calls_cols[1]: max_calls_input = st.text_input(f"**:{colors['calls']}[max Calls]**", value="40")
        with calls_cols[2]: call_cost_input = st.text_input(f"**:{colors['calls']}[Calls ₽ cost]**", value="1")
        

with input_cols[1].container(border=True):
    with st.columns([150, 100, 100])[1]: st.markdown(f"**LTV**")

    columns_ratio = [4, 10]

    with st.container(border=True):
        mortgage_cols = st.columns(columns_ratio)
        with mortgage_cols[0]: st.title("🏠", anchor=False)
        with mortgage_cols[1]: ltv_mortgage_input = st.text_input(f"**:{colors['mortgage']}[Mortgage]**", value="10")
    with st.container(border=True):
        pension_cols = st.columns(columns_ratio)
        with pension_cols[0]: st.title("👨‍🦳", anchor=False)
        with pension_cols[1]: ltv_pension_input = st.text_input(f"**:{colors['pension']}[Pension]**", value="42")
    with st.container(border=True):
        savings_cols = st.columns(columns_ratio)
        with savings_cols[0]: st.title("💰", anchor=False)
        with savings_cols[1]: ltv_savings_input = st.text_input(f"**:{colors['savings']}[Savings]**", value="12")

model_input = st.selectbox("**Which model?**", processing.models)

####################################################################################################################


# parsing input into data ##########################################################################################
def ParseData():
    data = {}

    data["max_sms"] = int(max_sms_input)
    data["sms_cost"] = float(sms_cost_input)
    data["max_emails"] = int(max_emails_input)
    data["email_cost"] = float(email_cost_input)
    data["max_calls"] = int(max_calls_input)
    data["call_cost"] = float(call_cost_input)
    data["ltv_mortgage"] = float(ltv_mortgage_input)
    data["ltv_pension"] = float(ltv_pension_input)
    data["ltv_savings"] = float(ltv_savings_input)

    for key, val in data.items():
        if val < 0:
            st.info(f'**{val} not expected to be negative**')
            data = {}
            return data

    data["model"] = model_input

    return data
####################################################################################################################

# ouput ############################################################################################################

def FormatLarge(float_number):
    ans = int(float_number / 1000)
    return f'{ans:,}'.replace(',', ' ')

with st.columns([145, 100, 100])[1]: get_button = st.button(f"Get :rainbow[Results]")

def GetResults():
    data = ParseData()
    if (len(data.keys()) == 0) : return
    ProcessedData = processing.VeronicaAsAFunction(data)

    with st.columns([130, 100, 100])[1]: st.title("**:rainbow[Results]**", anchor=False)

    with st.container(border=True):
        with st.columns([145, 100, 100])[1]: st.markdown(f"**Contacts cost**")

        output_cols_ratio = [10, 3, 10, 3, 10, 3, 10]
        optut_cols = st.columns(output_cols_ratio)
        with optut_cols[0]:
            with st.container(border=True): st.markdown(f"**:{colors['sms']}[{FormatLarge(data['max_sms'] * data['sms_cost'])}k ₽]**")
        with optut_cols[1]:
            with st.container(border=False): MyMarkdown("  +", font_sizes["plus"])
        with optut_cols[2]:
            with st.container(border=True): st.markdown(f"**:{colors['email']}[{FormatLarge(data['max_emails'] * data['email_cost'])}k ₽]**")
        with optut_cols[3]:
            with st.container(border=False): MyMarkdown("  +", font_sizes["plus"])
        with optut_cols[4]:
            with st.container(border=True): st.markdown(f"**:{colors['calls']}[{FormatLarge(data['max_calls'] * data['call_cost'])}k ₽]**")
        with optut_cols[5]:
            with st.container(border=False): MyMarkdown("  =", font_sizes["plus"])
        with optut_cols[6]:
            with st.container(border=True): st.markdown(f"**{FormatLarge(data['max_sms'] * data['sms_cost'] + data['max_emails'] * data['email_cost'] + data['max_calls'] * data['call_cost'])}k ₽**")
    
    with st.container(border=True):
        with st.columns([131, 100, 100])[1]: st.markdown(f"**Model calculations**")

        idk_cols = st.columns(2)
        with idk_cols[0]:
            with st.container(border=True): st.markdown(f"**📈 Max profit   {FormatLarge(ProcessedData['max_profit'])}k ₽**")
        with idk_cols[1]:
            with st.container(border=True): st.markdown(f"**👥 Num Clients   {ProcessedData['num_clients']}**")


        with st.container(border=True):
            with st.columns([153, 100, 100])[1]: st.markdown(f"**Propensity**")

            propensity_cols = st.columns(3)
            with propensity_cols[0]:
                with st.container(border=True): st.markdown(f"**🏠 :{colors['mortgage']}[Mortgage   {round(ProcessedData['mortgage_propensity'], 5)}]**")
            with propensity_cols[1]:
                with st.container(border=True): st.markdown(f"**👨‍🦳 :{colors['pension']}[Pension   {round(ProcessedData['pension_propensity'], 5)}]**")
            with propensity_cols[2]:
                with st.container(border=True): st.markdown(f"**💰 :{colors['savings']}[Savings   {round(ProcessedData['savings_propensity'], 5)}]**")

        with st.container(border=True):
            with st.columns([147, 200, 100])[1]: st.markdown(f"**Score Distribution by Channels**")
            st.pyplot(ProcessedData["scores_distribution"])  # bad?

if get_button: GetResults()

####################################################################################################################



    








