import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="E-Commerce Conversion Dashboard", layout="wide", page_icon="🛒")

@st.cache_data
def load_data():
    df = pd.read_csv('data/ecommerce_sessions.csv')
    df['page_views'] = df['page_views'].fillna(df['page_views'].median()).astype(int)
    df['session_duration'] = df['session_duration'].fillna(df['session_duration'].median())
    df['is_converted'] = (df['revenue'] > 0).astype(int)
    df['duration_minutes'] = round(df['session_duration'] / 60, 2)
    df['engagement_score'] = (
        df['page_views'] * 0.3 + df['product_pages_viewed'] * 0.4 + df['cart_additions'] * 0.3
    ).round(2)
    month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    df['month'] = pd.Categorical(df['month'], categories=month_order, ordered=True)
    df['day_of_week'] = pd.Categorical(df['day_of_week'], categories=day_order, ordered=True)
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

visitor_types = st.sidebar.multiselect("Visitor Type", df['visitor_type'].unique().tolist(), default=df['visitor_type'].unique().tolist())
traffic_sources = st.sidebar.multiselect("Traffic Source", df['traffic_source'].unique().tolist(), default=df['traffic_source'].unique().tolist())
devices = st.sidebar.multiselect("Device Type", df['device_type'].unique().tolist(), default=df['device_type'].unique().tolist())
regions = st.sidebar.multiselect("Region", sorted(df['region'].unique().tolist()), default=sorted(df['region'].unique().tolist()))
days = st.sidebar.multiselect("Day of Week", ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],
                               default=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])

filtered = df[
    (df['visitor_type'].isin(visitor_types)) &
    (df['traffic_source'].isin(traffic_sources)) &
    (df['device_type'].isin(devices)) &
    (df['region'].isin(regions)) &
    (df['day_of_week'].isin(days))
]

st.sidebar.markdown(f"**Showing {len(filtered):,} of {len(df):,} sessions**")

# --- Header ---
st.title("E-Commerce Session Conversion Dashboard")
st.markdown("Analyzing visitor sessions to understand conversion patterns and funnel behaviour.")

# --- KPI Row ---
col1, col2, col3, col4 = st.columns(4)
total_sessions = len(filtered)
conv_rate = filtered['is_converted'].mean() if total_sessions > 0 else 0
avg_revenue = filtered[filtered['revenue'] > 0]['revenue'].mean() if (filtered['revenue'] > 0).any() else 0
avg_duration = filtered['duration_minutes'].mean() if total_sessions > 0 else 0

col1.metric("Total Sessions", f"{total_sessions:,}")
col2.metric("Conversion Rate", f"{conv_rate:.2%}")
col3.metric("Avg Revenue (converters)", f"${avg_revenue:.2f}")
col4.metric("Avg Session Duration", f"{avg_duration:.1f} min")

st.divider()

# --- Funnel Chart ---
st.subheader("Conversion Funnel")

total = len(filtered)
viewed_product = (filtered['product_pages_viewed'] > 0).sum()
added_cart = (filtered['cart_additions'] > 0).sum()
purchased = (filtered['is_converted'] == 1).sum()

funnel_stages = ['All Sessions', 'Viewed Product Pages', 'Added to Cart', 'Purchased']
funnel_values = [total, viewed_product, added_cart, purchased]

col_funnel, col_table = st.columns([2, 1])

with col_funnel:
    fig_funnel = go.Figure(go.Funnel(
        y=funnel_stages, x=funnel_values,
        textinfo="value+percent initial",
        marker=dict(color=['#4C72B0', '#55A868', '#DD8452', '#C44E52']),
        connector=dict(line=dict(color='#aaa', width=1))
    ))
    fig_funnel.update_layout(height=350, margin=dict(t=20, b=20))
    st.plotly_chart(fig_funnel, use_container_width=True)

with col_table:
    dropoff = ['-'] + [f"{(1 - funnel_values[i]/funnel_values[i-1])*100:.1f}%" if funnel_values[i-1] > 0 else '-' for i in range(1, 4)]
    funnel_df = pd.DataFrame({
        'Stage': funnel_stages,
        'Count': funnel_values,
        '% of Total': [f"{v/total*100:.1f}%" if total > 0 else '0%' for v in funnel_values],
        'Drop-off': dropoff
    })
    st.dataframe(funnel_df, use_container_width=True, hide_index=True)

st.divider()

# --- Conversion Comparison ---
st.subheader("Conversion Breakdown")

tab1, tab2, tab3, tab4 = st.tabs(["By Traffic Source", "By Visitor Type", "By Device", "By Region"])

with tab1:
    grp = filtered.groupby('traffic_source')['is_converted'].agg(['mean','count']).reset_index()
    grp.columns = ['Traffic Source', 'Conversion Rate', 'Sessions']
    grp = grp.sort_values('Conversion Rate', ascending=True)
    fig = px.bar(grp, y='Traffic Source', x='Conversion Rate', orientation='h',
                 color='Conversion Rate', color_continuous_scale='Viridis',
                 text=grp['Conversion Rate'].apply(lambda x: f'{x:.1%}'))
    fig.update_layout(height=350, margin=dict(t=20))
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    grp = filtered.groupby('visitor_type')['is_converted'].agg(['mean','count']).reset_index()
    grp.columns = ['Visitor Type', 'Conversion Rate', 'Sessions']
    fig = px.bar(grp, x='Visitor Type', y='Conversion Rate',
                 color='Visitor Type', text=grp['Conversion Rate'].apply(lambda x: f'{x:.1%}'),
                 color_discrete_sequence=['#4C72B0', '#DD8452'])
    fig.update_layout(height=350, margin=dict(t=20), showlegend=False)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    grp = filtered.groupby('device_type')['is_converted'].agg(['mean','count']).reset_index()
    grp.columns = ['Device', 'Conversion Rate', 'Sessions']
    fig = px.bar(grp, x='Device', y='Conversion Rate',
                 color='Device', text=grp['Conversion Rate'].apply(lambda x: f'{x:.1%}'),
                 color_discrete_sequence=['#4C72B0', '#55A868', '#DD8452'])
    fig.update_layout(height=350, margin=dict(t=20), showlegend=False)
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    grp = filtered.groupby('region')['is_converted'].agg(['mean','count']).reset_index()
    grp.columns = ['Region', 'Conversion Rate', 'Sessions']
    grp = grp.sort_values('Conversion Rate', ascending=True)
    fig = px.bar(grp, y='Region', x='Conversion Rate', orientation='h',
                 color='Conversion Rate', color_continuous_scale='RdYlGn',
                 text=grp['Conversion Rate'].apply(lambda x: f'{x:.1%}'))
    fig.update_layout(height=400, margin=dict(t=20))
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Temporal Analysis ---
st.subheader("Temporal Analysis")

col_heat, col_monthly = st.columns(2)

with col_heat:
    st.markdown("**Conversion Rate: Hour x Day of Week**")
    heat_data = filtered.pivot_table(values='is_converted', index='day_of_week', columns='hour', aggfunc='mean', observed=True)
    fig = px.imshow(heat_data, color_continuous_scale='YlOrRd', aspect='auto',
                    labels=dict(x='Hour of Day', y='Day of Week', color='Conv Rate'))
    fig.update_layout(height=380, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with col_monthly:
    st.markdown("**Monthly Sessions & Conversion Rate**")
    monthly = filtered.groupby('month', observed=True).agg(
        sessions=('session_id', 'count'),
        conversion_rate=('is_converted', 'mean')
    ).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=monthly['month'], y=monthly['sessions'], name='Sessions',
                         marker_color='#4C72B0', opacity=0.6))
    fig.add_trace(go.Scatter(x=monthly['month'], y=monthly['conversion_rate'], name='Conv Rate',
                             yaxis='y2', mode='lines+markers', line=dict(color='#C44E52', width=2)))
    fig.update_layout(
        yaxis=dict(title='Sessions'), yaxis2=dict(title='Conv Rate', overlaying='y', side='right'),
        height=380, margin=dict(t=10, b=10), legend=dict(orientation='h', yanchor='bottom', y=1.02)
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Behavioural Patterns ---
st.subheader("Behavioural Patterns: Converted vs Not Converted")

col_pv, col_dur, col_eng = st.columns(3)

conv_labels = filtered['is_converted'].map({1: 'Converted', 0: 'Not Converted'})

with col_pv:
    fig = px.box(filtered, x=conv_labels, y='page_views', color=conv_labels,
                 color_discrete_map={'Converted': '#C44E52', 'Not Converted': '#4C72B0'})
    fig.update_layout(title='Page Views', showlegend=False, height=350, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_dur:
    fig = px.box(filtered, x=conv_labels, y='duration_minutes', color=conv_labels,
                 color_discrete_map={'Converted': '#C44E52', 'Not Converted': '#4C72B0'})
    fig.update_layout(title='Duration (min)', showlegend=False, height=350, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

with col_eng:
    fig = px.box(filtered, x=conv_labels, y='engagement_score', color=conv_labels,
                 color_discrete_map={'Converted': '#C44E52', 'Not Converted': '#4C72B0'})
    fig.update_layout(title='Engagement Score', showlegend=False, height=350, margin=dict(t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- Key Insights ---
st.subheader("Key Insights")

if total_sessions > 0:
    conv_by_vt = filtered.groupby('visitor_type')['is_converted'].mean()
    best_vt = conv_by_vt.idxmax()
    conv_by_ts = filtered.groupby('traffic_source')['is_converted'].mean()
    best_ts = conv_by_ts.idxmax()
    worst_ts = conv_by_ts.idxmin()
    bounce_rate = filtered['bounce'].mean()
    cart_conv = filtered[filtered['cart_additions'] > 0]['is_converted'].mean()

    insights = [
        f"**Overall conversion rate:** {conv_rate:.2%} across {total_sessions:,} filtered sessions",
        f"**Best visitor type:** {best_vt} ({conv_by_vt[best_vt]:.2%} conversion)",
        f"**Top traffic source:** {best_ts} ({conv_by_ts[best_ts]:.2%}) — worst: {worst_ts} ({conv_by_ts[worst_ts]:.2%})",
        f"**Bounce rate:** {bounce_rate:.1%} of sessions view only one page",
        f"**Cart-to-purchase rate:** {cart_conv:.1%} of sessions that added items to cart ended up purchasing",
        f"**Biggest funnel drop-off:** {(1 - added_cart/viewed_product)*100:.1f}% between product view and cart addition" if viewed_product > 0 else "",
    ]
    for i in insights:
        if i:
            st.markdown(f"- {i}")
else:
    st.warning("No sessions match the current filters.")
