cat > pages/4_Analytics_Dashboard.py << 'EOF'
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import psycopg2

st.set_page_config(page_title="Analytics Dashboard", page_icon="📊", layout="wide")

st.markdown("""
<style>
    .big-metric {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
    }
</style>
""", unsafe_allow_html=True)

# Database connection
@st.cache_resource
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="postgres-service.ecommerce-platform.svc.cluster.local",
            port=5432,
            database="ecommerce_analytics",
            user="admin",
            password="strongpassword123"
        )
        return conn
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return None

# Fetch data
@st.cache_data(ttl=30)
def fetch_data(query):
    conn = get_db_connection()
    if conn:
        try:
            df = pd.read_sql_query(query, conn)
            return df
        except Exception as e:
            st.error(f"Query failed: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# Header
st.title("📊 Business Analytics Dashboard")
st.markdown("Real-time insights from your e-commerce platform")
st.markdown("---")

# Refresh button
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()
with col2:
    st.caption(f"Updated: {datetime.now().strftime('%H:%M:%S')}")

# KPIs Section
st.subheader("📈 Key Performance Indicators")

# Fetch KPI data
total_views = fetch_data("SELECT COUNT(*) as count FROM product_views")
unique_sessions = fetch_data("SELECT COUNT(DISTINCT session_id) as count FROM product_views")
unique_users = fetch_data("SELECT COUNT(DISTINCT client_id) as count FROM product_views")
avg_views_per_session = fetch_data("""
    SELECT COALESCE(AVG(views), 0) as avg_views 
    FROM (
        SELECT session_id, COUNT(*) as views 
        FROM product_views 
        GROUP BY session_id
    ) as session_stats
""")

# Display KPIs
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    views = int(total_views['count'].iloc[0]) if not total_views.empty else 0
    st.metric(
        label="Total Product Views",
        value=f"{views:,}",
        delta="Live"
    )

with kpi2:
    sessions = int(unique_sessions['count'].iloc[0]) if not unique_sessions.empty else 0
    st.metric(
        label="Unique Sessions",
        value=f"{sessions:,}",
        delta="Active"
    )

with kpi3:
    users = int(unique_users['count'].iloc[0]) if not unique_users.empty else 0
    st.metric(
        label="Unique Visitors",
        value=f"{users:,}",
        delta="Total"
    )

with kpi4:
    avg_views = float(avg_views_per_session['avg_views'].iloc[0]) if not avg_views_per_session.empty else 0
    st.metric(
        label="Avg Views/Session",
        value=f"{avg_views:.1f}",
        delta="Engagement"
    )

st.markdown("---")

# Charts Section
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Top 10 Most Viewed Products")
    
    top_products_query = """
        SELECT 
            product_id,
            COUNT(*) as views,
            COUNT(DISTINCT session_id) as unique_sessions
        FROM product_views
        GROUP BY product_id
        ORDER BY views DESC
        LIMIT 10
    """
    top_products = fetch_data(top_products_query)
    
    if not top_products.empty:
        # Enrichir avec les noms
        if 'products' in st.session_state:
            products = st.session_state.products
            top_products = top_products.merge(
                products[['id', 'name']], 
                left_on='product_id', 
                right_on='id', 
                how='left'
            )
            top_products['product_name'] = top_products['name'].fillna('Product ' + top_products['product_id'].astype(str))
        else:
            top_products['product_name'] = 'Product ' + top_products['product_id'].astype(str)
        
        fig = px.bar(
            top_products,
            x='views',
            y='product_name',
            orientation='h',
            labels={'views': 'Views', 'product_name': ''},
            color='views',
            color_continuous_scale='Blues'
        )
        fig.update_layout(showlegend=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data yet. Browse products to see analytics!")

with col2:
    st.subheader("👥 User Engagement")
    
    engagement_query = """
        SELECT 
            CASE 
                WHEN views = 1 THEN '1 view'
                WHEN views BETWEEN 2 AND 3 THEN '2-3 views'
                WHEN views BETWEEN 4 AND 5 THEN '4-5 views'
                WHEN views > 5 THEN '6+ views'
            END as engagement_level,
            COUNT(*) as sessions
        FROM (
            SELECT session_id, COUNT(*) as views
            FROM product_views
            GROUP BY session_id
        ) as session_stats
        GROUP BY 
            CASE 
                WHEN views = 1 THEN '1 view'
                WHEN views BETWEEN 2 AND 3 THEN '2-3 views'
                WHEN views BETWEEN 4 AND 5 THEN '4-5 views'
                WHEN views > 5 THEN '6+ views'
            END
        ORDER BY 
            CASE 
                CASE 
                    WHEN views = 1 THEN '1 view'
                    WHEN views BETWEEN 2 AND 3 THEN '2-3 views'
                    WHEN views BETWEEN 4 AND 5 THEN '4-5 views'
                    WHEN views > 5 THEN '6+ views'
                END
                WHEN '1 view' THEN 1
                WHEN '2-3 views' THEN 2
                WHEN '4-5 views' THEN 3
                WHEN '6+ views' THEN 4
            END
    """
    engagement = fetch_data(engagement_query)
    
    if not engagement.empty:
        fig = px.pie(
            engagement,
            values='sessions',
            names='engagement_level',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No engagement data yet")

st.markdown("---")

# Time-based analysis
st.subheader("⏱️ Activity Timeline (Last Hour)")

timeline_query = """
    SELECT 
        DATE_TRUNC('minute', timestamp) as minute,
        COUNT(*) as views
    FROM product_views
    WHERE timestamp > NOW() - INTERVAL '1 hour'
    GROUP BY minute
    ORDER BY minute
"""
timeline = fetch_data(timeline_query)

if not timeline.empty:
    fig = px.line(
        timeline,
        x='minute',
        y='views',
        labels={'minute': 'Time', 'views': 'Views'}
    )
    fig.update_traces(line_color='#667eea', line_width=3)
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No activity in the last hour")

st.markdown("---")

# Detailed Tables
col1, col2 = st.columns(2)

with col1:
    st.subheader("📋 Recent Activity")
    
    recent_query = """
        SELECT 
            product_id as "Product ID",
            SUBSTRING(client_id, 1, 20) as "Client",
            SUBSTRING(session_id, 1, 15) as "Session",
            TO_CHAR(timestamp, 'HH24:MI:SS') as "Time"
        FROM product_views
        ORDER BY timestamp DESC
        LIMIT 10
    """
    recent = fetch_data(recent_query)
    
    if not recent.empty:
        st.dataframe(recent, use_container_width=True, hide_index=True)
    else:
        st.info("No recent activity")

with col2:
    st.subheader("🎯 Top Sessions")
    
    session_query = """
        SELECT 
            SUBSTRING(session_id, 1, 15) as "Session",
            COUNT(*) as "Views",
            COUNT(DISTINCT product_id) as "Unique Products"
        FROM product_views
        GROUP BY session_id
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """
    sessions = fetch_data(session_query)
    
    if not sessions.empty:
        st.dataframe(sessions, use_container_width=True, hide_index=True)
    else:
        st.info("No session data")

st.markdown("---")

# Category Analysis
if 'products' in st.session_state:
    st.subheader("📊 Performance by Category")
    
    category_query = """
        SELECT 
            product_id,
            COUNT(*) as views
        FROM product_views
        GROUP BY product_id
    """
    category_views = fetch_data(category_query)
    
    if not category_views.empty:
        products = st.session_state.products
        category_data = category_views.merge(
            products[['id', 'category']], 
            left_on='product_id', 
            right_on='id', 
            how='left'
        )
        
        category_summary = category_data.groupby('category')['views'].sum().reset_index()
        category_summary = category_summary.sort_values('views', ascending=False)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                category_summary,
                x='category',
                y='views',
                color='views',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Category Breakdown")
            total = category_summary['views'].sum()
            for idx, row in category_summary.iterrows():
                percentage = (row['views'] / total * 100) if total > 0 else 0
                st.metric(
                    label=row['category'],
                    value=f"{int(row['views'])}",
                    delta=f"{percentage:.1f}%"
                )

st.markdown("---")
st.caption("📊 Dashboard auto-refreshes every 30 seconds | Data from PostgreSQL")
EOF
