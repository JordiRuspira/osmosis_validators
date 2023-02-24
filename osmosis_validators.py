# -*- coding: utf-8 -*-
"""
Created on Tue Aug 16 00:42:24 2022
@author: Jordi Garcia Ruspira
"""
import streamlit as st
import pandas as pd
import requests
import json
import time
import plotly.graph_objects as go
import random
import plotly.io as pio 
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt 
import matplotlib.pyplot as plt
import numpy as np
from plotly.subplots import make_subplots
from PIL import Image 
import datetime 
import plotly.graph_objs as go

import plotly.graph_objects as go

import networkx as nx


import streamlit as st
import pandas as pd
import requests
import json
import time
import plotly.graph_objects as go
import random
import plotly.io as pio 
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt 
import matplotlib.pyplot as plt
import numpy as np
from shroomdk import ShroomDK
from plotly.subplots import make_subplots
from PIL import Image 
import datetime  

import plotly.graph_objs as go

import plotly.graph_objects as go

import streamlit as st
import pandas as pd
import requests
import json
import time
import plotly.graph_objects as go
import random
import plotly.io as pio 
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt 
import matplotlib.pyplot as plt
import numpy as np
from plotly.subplots import make_subplots
from PIL import Image 
import datetime 
import plotly.graph_objs as go
import base64

import plotly.graph_objects as go


st.set_page_config(
    page_title="Osmosis governance - a tool for validators",
    page_icon=":atom_symbol:",
    layout="wide",
    menu_items=dict(About="It's a work of Jordi"),
)


st.title(":atom_symbol: Osmosis Governance :atom_symbol:")
 
im_col1, im_col2 = st.columns(2) 
im_col1.image(
    "https://i.ibb.co/jJhVvNK/osmo.png" 
)


im_col2.image(
    "https://i.ibb.co/tqy8QcX/regen.jpg" 
)
 
st.text("")
st.subheader('Dashboard by [Jordi R](https://twitter.com/RuspiTorpi/). Powered by Flipsidecrypto')
st.text("")
st.markdown('The goal of this dashboard for validators to have a better understanding and insights of how their voting options impacts on their delegators.')
           
 
st.markdown(
    """
<style>
.reportview-container .markdown-text-container {
    font-family: monospace;
}
.sidebar .sidebar-content {
    background-image: linear-gradient(#2e7bcf,#2e7bcf);
    color: white;
}
.Widget>label {
    color: white;
    font-family: monospace;
}
[class^="st-b"]  {
    color: white;
    font-family: monospace;
}
.st-bb {
    background-color: transparent;
}
.st-at {
    background-color: transparent;
}
footer {
    font-family: monospace;
}
.reportview-container .main footer, .reportview-container .main footer a {
    color: #0c0080;
}
header .decoration {
    background-image: none;
}

</style>
""",
    unsafe_allow_html=True,
)
pio.renderers.default = 'browser'




API_KEY = "3b5afbf4-3004-433c-9b04-2e867026718b"
 
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)
 
set_background('C:/Users/User/Desktop/Osmosis/sincerely-media-cuEpo721ACY-unsplash.jpg')
def querying_pagination(query_string):
    sdk = ShroomDK('3b5afbf4-3004-433c-9b04-2e867026718b')
    
    # Query results page by page and saves the results in a list
    # If nothing is returned then just stop the loop and start adding the data to the dataframe
    result_list = []
    for i in range(1,11): # max is a million rows @ 100k per page
        data=sdk.query(query_string,page_size=100000,page_number=i)
        if data.run_stats.record_count == 0:  
            break
        else:
            result_list.append(data.records)
        
    # Loops through the returned results and adds into a pandas dataframe
    result_df=pd.DataFrame()
    for idx, each_list in enumerate(result_list):
        if idx == 0:
            result_df=pd.json_normalize(each_list)
        else:
            result_df=pd.concat([result_df, pd.json_normalize(each_list)])

    return result_df




st.header("") 

 
    

st.subheader("Introduction - Overview")

st.text("")
st.success("How to use this tool: you can select a proposal ID on Osmosis and a Validator, and it will give you insights on how delegators behaved after the proposal.")
st.success("When you select a proposal ID, the numbers displayed show movement between the go live of the proposal and 7 days after the ending of the vote.")
st.text("")
st.text("")
st.markdown("Start by selecting a proposal ID:")
    
df_query_0 ="""
select distinct proposal_id as proposal_id
from osmosis.core.fact_governance_votes
where tx_succeeded = 'TRUE' 
"""

df_proposals_selectbox = querying_pagination(df_query_0)

proposal_choice = '427'
proposal_choice = st.selectbox("Select a proposal", options = df_proposals_selectbox['proposal_id'].unique() ) 


df_query_aux1 ="""
with votes_times as 
(select proposal_id, max(date_trunc('day', block_timestamp)) as date 
 from osmosis.core.fact_governance_votes
 where tx_succeeded = 'TRUE'
 and proposal_id =  '"""

df_query_1 = df_query_aux1 + str(proposal_choice) + """' 

group by proposal_id ),  
validators_address as (
    select address, label, rank, raw_metadata:"account_address" as account_address
    from osmosis.core.fact_validators 
    ),

val_votes_aux as 

(
 select voter, 
 proposal_id, 
 b.description, 
 rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
 from osmosis.core.fact_governance_votes a 
 left join osmosis.core.dim_vote_options b 
 on a.vote_option = b.vote_id
 where voter in (select distinct account_address from validators_address)
 and proposal_id =  '""" + str(proposal_choice) + """'
 and tx_succeeded = 'TRUE'
 )

select voter, b.address, proposal_id, description, label, b.rank from val_votes_aux a
left join validators_address b 
on a.voter = b.account_address
where a.rank = 1 
and b.rank <= 150
"""


st.text("")
st.markdown("We can see how validators voted on the selected proposal, ordered by rank and voting option.")
st.text("")

df_valvote = querying_pagination(df_query_1)
df_valvote = df_valvote.sort_values(by ='rank', ascending = True)

fig = px.bar(df_valvote, x='label', y='rank', color='description', hover_data = ['description'])

st.plotly_chart(fig, use_container_width=True)  
    
df_query_val ="""
select address, account_address, label, rank from  osmosis.core.fact_validators
where rank <= 150
"""

st.text("")
st.markdown("Next, use the select box below to see insights for your favorite validator:")
st.text("")


df_proposals_selectbox = querying_pagination(df_query_val)
validator_choice = 'Stakecito'
validator_choice = st.selectbox("Select a validator", options = df_proposals_selectbox['label'].unique() ) 
validator_choice_address = df_proposals_selectbox['address'][df_proposals_selectbox['label'] == str(validator_choice)].to_string(index=False)


df_query_aux2 ="""
with votes_times as 
(select proposal_id, max(date_trunc('day', block_timestamp)) as date 
 from osmosis.core.fact_governance_votes
 where tx_succeeded = 'TRUE'
 and proposal_id =  '"""

df_query_2 = df_query_aux2 + str(proposal_choice) + """' 

group by proposal_id ),  
   
    
votes_proposal_aux as (
select voter, proposal_id, vote_option, rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
from osmosis.core.fact_governance_votes
where tx_succeeded = 'TRUE'
and proposal_id =  '""" + str(proposal_choice) + """'
),

votes_proposal as 
(select voter, 
proposal_id,
b.description
from votes_proposal_aux a 
left join osmosis.core.dim_vote_options b 
on a.vote_option = b.vote_id
where a.rank = 1
and proposal_id =  '""" + str(proposal_choice) + """'
),

delegations as (
select date_trunc('day', block_timestamp) as date,
delegator_address,
validator_address,
sum(amount/pow(10, decimal)) as amount 
from osmosis.core.fact_staking
where tx_succeeded = 'TRUE' 
and action = 'delegate'
and date_trunc('day', block_timestamp) <= (select date from votes_times)
group by date, delegator_address, validator_address
),

undelegations as (
select date_trunc('day', block_timestamp) as date,
delegator_address,
validator_address,
sum(amount/pow(10, decimal))*(-1) as amount 
from osmosis.core.fact_staking
where tx_succeeded = 'TRUE' 
and action = 'undelegate'
and date_trunc('day', block_timestamp) <= (select date from votes_times)
group by date, delegator_address, validator_address
),

redelegations_to as 
(
select date_trunc('day', block_timestamp) as date,
delegator_address,
validator_address,
sum(amount/pow(10, decimal)) as amount 
from osmosis.core.fact_staking
where tx_succeeded = 'TRUE' 
and action = 'redelegate'
and date_trunc('day', block_timestamp) <= (select date from votes_times)
group by date, delegator_address, validator_address

),

redelegations_from as 
(
select date_trunc('day', block_timestamp) as date,
delegator_address,
redelegate_source_validator_address as validator_address,
sum(amount/pow(10, decimal))*(-1) as amount 
from osmosis.core.fact_staking
where tx_succeeded = 'TRUE' 
and action = 'redelegate'
and date_trunc('day', block_timestamp) <= (select date from votes_times)
group by date, delegator_address, redelegate_source_validator_address

),

validators_address as (
select address, label, raw_metadata:"account_address" as account_address
from osmosis.core.fact_validators 
),

val_votes_aux as 

(
select voter, 
proposal_id, 
b.description, 
rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
from osmosis.core.fact_governance_votes a 
left join osmosis.core.dim_vote_options b 
on a.vote_option = b.vote_id
where voter in (select distinct account_address from validators_address)
and proposal_id =  '""" + str(proposal_choice) +"""' 
and tx_succeeded = 'TRUE'
),

val_votes as (
select voter, b.address, proposal_id, description from val_votes_aux a
left join validators_address b 
on a.voter = b.account_address
where rank = 1 
),

all_votes_per_proposal_and_validator as 
(

select 
delegator_address, 
case when b.voter is null then 'Did not vote'
else b.description end as vote, 
validator_address, 
c.label, 
c.rank,
case when d.description is null then 'Did not vote'
else d.description end as validator_vote,
sum(amount) as total_amount
from (
  select * from delegations
  union all 
  select * from undelegations 
  union all 
  select * from redelegations_to 
  union all 
  select * from redelegations_from
  ) a 
left join votes_proposal b 
on a.delegator_address = b.voter
left join osmosis.core.fact_validators c 
on a.validator_address = c.address 
left join val_votes d 
on a.validator_address = d.address 
where c.label =  '""" + str(validator_choice) + """'
group by 
delegator_address, 
vote,
validator_address,
c.label,
c.rank,
validator_vote
)

select validator_vote,
vote as delegator_vote,
count(distinct delegator_address) as num_voters,
sum(total_amount) as total_amount 
from all_votes_per_proposal_and_validator 
group by validator_vote,
vote
"""



df_delegator_vote_distribution = querying_pagination(df_query_2)

st.dataframe(df_delegator_vote_distribution) 




st.text("")
st.markdown("Next, use the select box below to see insights for your favorite validator:")
st.text("")

  

df_query_3 = df_query_aux2 + str(proposal_choice) +"""'
group by proposal_id
),

-- This part is done to drop later all duplicate votes

votes_proposal_aux as (
select voter, proposal_id, vote_option, rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
from osmosis.core.fact_governance_votes
where tx_succeeded = 'TRUE'
and proposal_id =  '"""+ str(proposal_choice)+"""'
),

votes_proposal as 
(select voter, 
proposal_id,
b.description
from votes_proposal_aux a 
left join osmosis.core.dim_vote_options b 
on a.vote_option = b.vote_id
where a.rank = 1
and proposal_id =  '"""+str(proposal_choice) +"""'
),

redelegations as 
(
select date_trunc('day', block_timestamp) as date,
delegator_address,
validator_address,
redelegate_source_validator_address,
sum(amount/pow(10, decimal)) as amount 
from osmosis.core.fact_staking
where tx_succeeded = 'TRUE' 
and action = 'redelegate'
and date_trunc('day', block_timestamp) between to_date((select date from votes_times)) - 5 and  to_date((select date from votes_times)) + 7
group by date, delegator_address, validator_address, REDELEGATE_SOURCE_VALIDATOR_ADDRESS

),


validators_address as (
select address, label, raw_metadata:"account_address" as account_address
from osmosis.core.fact_validators 
),

val_votes_aux as 

(
select voter, 
proposal_id, 
b.description, 
rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
from osmosis.core.fact_governance_votes a 
left join osmosis.core.dim_vote_options b 
on a.vote_option = b.vote_id
where voter in (select distinct account_address from validators_address)
and proposal_id =  '"""+str(proposal_choice) +"""'
and tx_succeeded = 'TRUE'
),

val_votes as (
select voter, b.address, proposal_id, description from val_votes_aux a
left join validators_address b 
on a.voter = b.account_address
where rank = 1 
),

all_votes_per_proposal_and_validator as 
(

select 
delegator_address, 
case when b.voter is null then 'Did not vote'
else b.description end as vote, 
redelegate_source_validator_address as redelegated_from,
validator_address as redelegated_to,
case when redelegated_from = 'osmovaloper14n8pf9uxhuyxqnqryvjdr8g68na98wn5amq3e5' then 'Prism validator'
else cc.label end as redelegated_from_label,
cc.rank as redelegated_from_rank, 
case when redelegated_to = 'osmovaloper14n8pf9uxhuyxqnqryvjdr8g68na98wn5amq3e5' then 'Prism validator'
else c.label end as redelegated_to_label,
c.rank as redelegated_to_rank,
case when d.description is null then 'Did not vote'
else d.description end as validator_redelegated_from_vote,
case when e.description is null then 'Did not vote'
else e.description end as validator_redelegated_to_vote,


sum(amount) as total_amount
from redelegations a 
left join votes_proposal b 
on a.delegator_address = b.voter
left join osmosis.core.fact_validators c 
on a.validator_address = c.address 
left join osmosis.core.fact_validators cc 
on a.redelegate_source_validator_address = cc.address 
left join val_votes d 
on a.validator_address = d.address 
left join val_votes e 
on a.redelegate_source_validator_address = d.address 
where c.label =  '"""+str(validator_choice) +"""'
group by 
delegator_address, 
vote,
redelegated_from,
redelegated_to,
redelegated_from_label,
redelegated_from_rank,
redelegated_to_label,
redelegated_to_rank, 
validator_redelegated_from_vote,
validator_redelegated_to_vote

)

select * from all_votes_per_proposal_and_validator"""



df_delegator_reledlegations_from = querying_pagination(df_query_3)
df_delegator_reledlegations_from_2 = df_delegator_reledlegations_from.groupby(by=['redelegated_from_label','validator_redelegated_from_vote']).sum().reset_index(drop=False)
df_delegator_reledlegations_from_3 = df_delegator_reledlegations_from.groupby(by=['redelegated_from_label','vote']).sum().reset_index(drop=False)


fig = px.bar(df_delegator_reledlegations_from_2, x='redelegated_from_label', y='total_amount', color='validator_redelegated_from_vote', hover_data = ['total_amount'])
st.plotly_chart(fig, use_container_width=True)  


fig = px.bar(df_delegator_reledlegations_from_3, x='redelegated_from_label', y='total_amount', color='vote', hover_data = ['total_amount'])
st.plotly_chart(fig, use_container_width=True)  

st.dataframe(df_delegator_reledlegations_from) 












df_query_4 = df_query_aux2 + str(proposal_choice) +"""'
group by proposal_id
),

-- This part is done to drop later all duplicate votes

votes_proposal_aux as (
select voter, proposal_id, vote_option, rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
from osmosis.core.fact_governance_votes
where tx_succeeded = 'TRUE'
and proposal_id =  '"""+ str(proposal_choice)+"""'
),

votes_proposal as 
(select voter, 
proposal_id,
b.description
from votes_proposal_aux a 
left join osmosis.core.dim_vote_options b 
on a.vote_option = b.vote_id
where a.rank = 1
and proposal_id =  '"""+str(proposal_choice) +"""'
),

redelegations as 
(
select date_trunc('day', block_timestamp) as date,
delegator_address,
validator_address,
redelegate_source_validator_address,
sum(amount/pow(10, decimal)) as amount 
from osmosis.core.fact_staking
where tx_succeeded = 'TRUE' 
and action = 'redelegate'
and date_trunc('day', block_timestamp) between to_date((select date from votes_times)) -5 and  to_date((select date from votes_times)) + 7
group by date, delegator_address, validator_address, REDELEGATE_SOURCE_VALIDATOR_ADDRESS

),


validators_address as (
select address, label, raw_metadata:"account_address" as account_address
from osmosis.core.fact_validators 
),

val_votes_aux as 

(
select voter, 
proposal_id, 
b.description, 
rank() over (partition by voter, proposal_id order by block_timestamp desc) as rank
from osmosis.core.fact_governance_votes a 
left join osmosis.core.dim_vote_options b 
on a.vote_option = b.vote_id
where voter in (select distinct account_address from validators_address)
and proposal_id =  '"""+str(proposal_choice) +"""'
and tx_succeeded = 'TRUE'
),

val_votes as (
select voter, b.address, proposal_id, description from val_votes_aux a
left join validators_address b 
on a.voter = b.account_address
where rank = 1 
),

all_votes_per_proposal_and_validator as 
(

select 
delegator_address, 
case when b.voter is null then 'Did not vote'
else b.description end as vote, 
redelegate_source_validator_address as redelegated_from,
validator_address as redelegated_to,
case when redelegated_from = 'osmovaloper14n8pf9uxhuyxqnqryvjdr8g68na98wn5amq3e5' then 'Prism validator'
else cc.label end as redelegated_from_label,
cc.rank as redelegated_from_rank, 
case when redelegated_to = 'osmovaloper14n8pf9uxhuyxqnqryvjdr8g68na98wn5amq3e5' then 'Prism validator'
else c.label end as redelegated_to_label,
c.rank as redelegated_to_rank,
case when d.description is null then 'Did not vote'
else d.description end as validator_redelegated_from_vote,
case when e.description is null then 'Did not vote'
else e.description end as validator_redelegated_to_vote,

sum(amount) as total_amount
from redelegations a 
left join votes_proposal b 
on a.delegator_address = b.voter
left join osmosis.core.fact_validators c 
on a.validator_address = c.address 
left join osmosis.core.fact_validators cc 
on a.redelegate_source_validator_address = cc.address 
left join val_votes d 
on a.validator_address = d.address 
left join val_votes e 
on a.redelegate_source_validator_address = d.address 
where cc.label =  '"""+str(validator_choice) +"""'
group by 
delegator_address, 
vote,
redelegated_from,
redelegated_to,
redelegated_from_label,
redelegated_from_rank,
redelegated_to_label,
redelegated_to_rank, 
validator_redelegated_from_vote,
validator_redelegated_to_vote

)

select * from all_votes_per_proposal_and_validator"""



df_delegator_reledlegations_to = querying_pagination(df_query_4)
df_delegator_reledlegations_to_2 = df_delegator_reledlegations_to.groupby(by=['redelegated_to_label','validator_redelegated_to_vote']).sum().reset_index(drop=False)
df_delegator_reledlegations_to_3 = df_delegator_reledlegations_to.groupby(by=['redelegated_to_label','vote']).sum().reset_index(drop=False)

fig = px.bar(df_delegator_reledlegations_to_2, x='redelegated_to_label', y='total_amount', color='validator_redelegated_to_vote', hover_data = ['total_amount'])
st.plotly_chart(fig, use_container_width=True)  
fig = px.bar(df_delegator_reledlegations_to_3, x='redelegated_to_label', y='total_amount', color='vote', hover_data = ['total_amount'])
st.plotly_chart(fig, use_container_width=True)  

st.dataframe(df_delegator_reledlegations_to) 


  

