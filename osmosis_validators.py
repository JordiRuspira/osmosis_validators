# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import requests
import json
import time 
import plotly.io as pio 
import plotly.express as px  
import base64


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
    "https://i.ibb.co/jJhVvNK/osmo.png" 
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




API_KEY = st.secrets["API_KEY"]



TTL_MINUTES = 15
# return up to 100,000 results per GET request on the query id
PAGE_SIZE = 100000
# return results of page 1
PAGE_NUMBER = 1
    
def create_query(SQL_QUERY):
    r = requests.post(
            'https://node-api.flipsidecrypto.com/queries', 
            data=json.dumps({
                "sql": SQL_QUERY,
                "ttlMinutes": TTL_MINUTES
            }),
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY},
    )
    if r.status_code != 200:
        raise Exception("Error creating query, got response: " + r.text + "with status code: " + str(r.status_code))
        
    return json.loads(r.text)    
       
    
def get_query_results(token):
    r = requests.get(
            'https://node-api.flipsidecrypto.com/queries/{token}?pageNumber={page_number}&pageSize={page_size}'.format(
              token=token,
              page_number=PAGE_NUMBER,
              page_size=PAGE_SIZE
            ),
            headers={"Accept": "application/json", "Content-Type": "application/json", "x-api-key": API_KEY}
    )
    if r.status_code != 200:
        raise Exception("Error getting query results, got response: " + r.text + "with status code: " + str(r.status_code))
        
    data = json.loads(r.text)
    if data['status'] == 'running':
        time.sleep(10)
        return get_query_results(token)
    
    return data
 
set_background('sincerely-media-cuEpo721ACY-unsplash.jpg')

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

query = create_query(df_query_0)
token = query.get('token')
data0 = get_query_results(token) 
df_proposals_selectbox = pd.DataFrame(data0['results'], columns = ['proposal_id']) 


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




query = create_query(df_query_1)
token = query.get('token')
data0 = get_query_results(token) 
df_valvote = pd.DataFrame(data0['results'], columns = ['voter','address','proposal_id','description','label','rank'])  
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


query = create_query(df_query_val)
token = query.get('token')
data0 = get_query_results(token) 
df_proposals_selectbox = pd.DataFrame(data0['results'], columns = ['address','account_address','label','rank'])   
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



query = create_query(df_query_2)
token = query.get('token')
data0 = get_query_results(token) 
df_delegator_vote_distribution = pd.DataFrame(data0['results'], columns = ['validator_cote', 'delegator_vote','num_voters','total_amount'])    

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




query = create_query(df_query_3)
token = query.get('token')
data0 = get_query_results(token) 
df_delegator_reledlegations_from = pd.DataFrame(data0['results'], columns = ['delegator_address','vote','redelegated_from','redelegaterd_to','redelegated_from_label','redelegated_from_rank','redelegated_to_label','redelegated_to_rank','validator_redelegated_from_vote','valdiator_redelegated_to_vote','total_amount'])    

 
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



query = create_query(df_query_4)
token = query.get('token')
data0 = get_query_results(token) 
df_delegator_reledlegations_to = pd.DataFrame(data0['results'], columns = ['delegator_address','vote','redelegated_from','redelegaterd_to','redelegated_from_label','redelegated_from_rank','redelegated_to_label','redelegated_to_rank','validator_redelegated_from_vote','validator_redelegated_to_vote','total_amount'])    
 
df_delegator_reledlegations_to_2 = df_delegator_reledlegations_to.groupby(by=['redelegated_to_label','validator_redelegated_to_vote']).sum().reset_index(drop=False)
df_delegator_reledlegations_to_3 = df_delegator_reledlegations_to.groupby(by=['redelegated_to_label','vote']).sum().reset_index(drop=False)

fig = px.bar(df_delegator_reledlegations_to_2, x='redelegated_to_label', y='total_amount', color='validator_redelegated_to_vote', hover_data = ['total_amount'])
st.plotly_chart(fig, use_container_width=True)  
fig = px.bar(df_delegator_reledlegations_to_3, x='redelegated_to_label', y='total_amount', color='vote', hover_data = ['total_amount'])
st.plotly_chart(fig, use_container_width=True)  

st.dataframe(df_delegator_reledlegations_to) 


  
