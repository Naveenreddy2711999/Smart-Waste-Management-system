import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import folium
from streamlit_folium import st_folium
import random

# Page configuration
st.set_page_config(
    page_title="Smart Waste Management System",
    page_icon="🗂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .alert-high {
        background-color: #ff4444;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .alert-medium {
        background-color: #ffaa00;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .status-good {
        color: #28a745;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .status-danger {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def generate_bin_data():
    """Generate mock smart bin data"""
    bin_locations = [
        {"id": "BIN001", "lat": 28.6139, "lon": 77.2090, "area": "Connaught Place"},
        {"id": "BIN002", "lat": 28.6562, "lon": 77.2410, "area": "Red Fort"},
        {"id": "BIN003", "lat": 28.5535, "lon": 77.2588, "area": "Lotus Temple"},
        {"id": "BIN004", "lat": 28.6129, "lon": 77.2295, "area": "India Gate"},
        {"id": "BIN005", "lat": 28.6448, "lon": 77.2167, "area": "Chandni Chowk"},
        {"id": "BIN006", "lat": 28.5244, "lon": 77.1855, "area": "Qutub Minar"},
        {"id": "BIN007", "lat": 28.6692, "lon": 77.4538, "area": "Akshardham"},
        {"id": "BIN008", "lat": 28.6304, "lon": 77.2177, "area": "Rajpath"},
    ]
    
    bins = []
    for location in bin_locations:
        fill_level = random.randint(10, 95)
        status = "Critical" if fill_level > 85 else "Warning" if fill_level > 70 else "Good"
        
        # Generate waste classification data
        waste_types = {
            "Plastic": random.randint(20, 40),
            "Paper": random.randint(15, 30),
            "Glass": random.randint(5, 20),
            "Metal": random.randint(5, 15),
            "Organic": random.randint(25, 45)
        }
        
        bins.append({
            **location,
            "fill_level": fill_level,
            "status": status,
            "last_collection": datetime.now() - timedelta(hours=random.randint(2, 48)),
            "daily_waste": random.randint(50, 200),
            "waste_classification": waste_types,
            "temperature": random.randint(20, 35),
            "humidity": random.randint(40, 80)
        })
    
    return bins

# Initialize session state for real-time data
if 'last_update' not in st.session_state:
    st.session_state.last_update = datetime.now()
    st.session_state.bin_data = generate_bin_data()

def create_city_map(bin_data):
    """Create interactive map with bin locations"""
    # Center map on Delhi
    m = folium.Map(location=[28.6139, 77.2090], zoom_start=11)
    
    for bin_info in bin_data:
        # Color based on fill level
        color = 'red' if bin_info['fill_level'] > 85 else 'orange' if bin_info['fill_level'] > 70 else 'green'
        
        popup_text = f"""
        <b>Bin ID:</b> {bin_info['id']}<br>
        <b>Area:</b> {bin_info['area']}<br>
        <b>Fill Level:</b> {bin_info['fill_level']}%<br>
        <b>Status:</b> {bin_info['status']}<br>
        <b>Daily Waste:</b> {bin_info['daily_waste']} kg<br>
        <b>Temperature:</b> {bin_info['temperature']}°C
        """
        
        folium.CircleMarker(
            location=[bin_info['lat'], bin_info['lon']],
            radius=10 + (bin_info['fill_level'] / 10),
            popup=popup_text,
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7
        ).add_to(m)
    
    return m

def create_waste_classification_chart(bin_data):
    """Create waste classification pie chart"""
    total_waste = {"Plastic": 0, "Paper": 0, "Glass": 0, "Metal": 0, "Organic": 0}
    
    for bin_info in bin_data:
        for waste_type, amount in bin_info['waste_classification'].items():
            total_waste[waste_type] += amount
    
    fig = px.pie(
        values=list(total_waste.values()),
        names=list(total_waste.keys()),
        title="City-wide Waste Classification",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    return fig

def create_fill_level_chart(bin_data):
    """Create fill level monitoring chart"""
    df = pd.DataFrame([
        {"Bin ID": bin_info['id'], "Fill Level": bin_info['fill_level'], 
         "Area": bin_info['area'], "Status": bin_info['status']}
        for bin_info in bin_data
    ])
    
    fig = px.bar(
        df, x="Bin ID", y="Fill Level", color="Status",
        title="Smart Bin Fill Levels",
        color_discrete_map={"Good": "green", "Warning": "orange", "Critical": "red"}
    )
    fig.add_hline(y=85, line_dash="dash", line_color="red", 
                  annotation_text="Critical Level (85%)")
    fig.add_hline(y=70, line_dash="dash", line_color="orange", 
                  annotation_text="Warning Level (70%)")
    return fig

def create_efficiency_metrics(bin_data):
    """Calculate and display efficiency metrics"""
    total_bins = len(bin_data)
    critical_bins = sum(1 for bin_info in bin_data if bin_info['status'] == 'Critical')
    warning_bins = sum(1 for bin_info in bin_data if bin_info['status'] == 'Warning')
    good_bins = total_bins - critical_bins - warning_bins
    
    avg_fill_level = np.mean([bin_info['fill_level'] for bin_info in bin_data])
    total_daily_waste = sum(bin_info['daily_waste'] for bin_info in bin_data)
    
    # Calculate collection efficiency
    collection_efficiency = ((good_bins + warning_bins * 0.7) / total_bins) * 100
    
    return {
        "total_bins": total_bins,
        "critical_bins": critical_bins,
        "warning_bins": warning_bins,
        "good_bins": good_bins,
        "avg_fill_level": avg_fill_level,
        "total_daily_waste": total_daily_waste,
        "collection_efficiency": collection_efficiency
    }

def create_route_optimization_chart():
    """Create route optimization visualization"""
    routes = [
        {"Route": "Route A", "Bins": 8, "Distance": 25.5, "Time": 3.2, "Efficiency": 85},
        {"Route": "Route B", "Bins": 6, "Distance": 18.3, "Time": 2.8, "Efficiency": 92},
        {"Route": "Route C", "Bins": 10, "Distance": 32.1, "Time": 4.1, "Efficiency": 78},
        {"Route": "Route D", "Bins": 7, "Distance": 21.7, "Time": 3.0, "Efficiency": 88}
    ]
    
    df = pd.DataFrame(routes)
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Distance (km)', 'Time (hours)', 'Bins per Route', 'Efficiency (%)'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    fig.add_trace(go.Bar(x=df['Route'], y=df['Distance'], name='Distance'), row=1, col=1)
    fig.add_trace(go.Bar(x=df['Route'], y=df['Time'], name='Time'), row=1, col=2)
    fig.add_trace(go.Bar(x=df['Route'], y=df['Bins'], name='Bins'), row=2, col=1)
    fig.add_trace(go.Bar(x=df['Route'], y=df['Efficiency'], name='Efficiency'), row=2, col=2)
    
    fig.update_layout(title_text="Garbage Collection Route Optimization", showlegend=False)
    return fig

# Main Dashboard
def main():
    st.markdown('<h1 class="main-header">🗂️ Smart Waste Management System</h1>', unsafe_allow_html=True)
    st.markdown("### Real-time City-wide Waste Monitoring & Analytics Dashboard")
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)
    
    if auto_refresh:
        # Auto refresh every 30 seconds
        time.sleep(1)
        if (datetime.now() - st.session_state.last_update).seconds > 30:
            st.session_state.bin_data = generate_bin_data()
            st.session_state.last_update = datetime.now()
            st.rerun()
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data"):
        st.session_state.bin_data = generate_bin_data()
        st.session_state.last_update = datetime.now()
        st.rerun()
    
    # Phase selection
    phase = st.sidebar.selectbox(
        "Deployment Phase",
        ["Phase 1 - Pilot Test", "Phase 2 - City-wide Rollout", "Phase 3 - Full Deployment"]
    )
    
    bin_data = st.session_state.bin_data
    metrics = create_efficiency_metrics(bin_data)
    
    # Key Metrics Row
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Smart Bins", metrics['total_bins'], delta=None)
    
    with col2:
        st.metric("Avg Fill Level", f"{metrics['avg_fill_level']:.1f}%", 
                 delta=f"{random.randint(-5, 5):.1f}%")
    
    with col3:
        st.metric("Daily Waste", f"{metrics['total_daily_waste']} kg", 
                 delta=f"{random.randint(-50, 100)} kg")
    
    with col4:
        st.metric("Collection Efficiency", f"{metrics['collection_efficiency']:.1f}%", 
                 delta=f"{random.randint(-3, 7):.1f}%")
    
    with col5:
        st.metric("Critical Bins", metrics['critical_bins'], 
                 delta=random.randint(-2, 3))
    
    # Alerts Section
    st.subheader("🚨 Real-time Alerts")
    alert_col1, alert_col2 = st.columns(2)
    
    with alert_col1:
        critical_bins = [bin_info for bin_info in bin_data if bin_info['status'] == 'Critical']
        if critical_bins:
            st.markdown("#### Critical Alerts")
            for bin_info in critical_bins:
                st.markdown(f"""
                <div class="alert-high">
                    <strong>🔴 {bin_info['id']} - {bin_info['area']}</strong><br>
                    Fill Level: {bin_info['fill_level']}% | Immediate collection required
                </div>
                """, unsafe_allow_html=True)
    
    with alert_col2:
        warning_bins = [bin_info for bin_info in bin_data if bin_info['status'] == 'Warning']
        if warning_bins:
            st.markdown("#### Warning Alerts")
            for bin_info in warning_bins[:3]:  # Show max 3
                st.markdown(f"""
                <div class="alert-medium">
                    <strong>🟡 {bin_info['id']} - {bin_info['area']}</strong><br>
                    Fill Level: {bin_info['fill_level']}% | Schedule collection soon
                </div>
                """, unsafe_allow_html=True)
    
    # Main Dashboard Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Live Map", "📈 Analytics", "🚛 Route Optimization", 
        "🔬 AI Classification", "⚙️ System Management"
    ])
    
    with tab1:
        st.subheader("Smart Bin Locations & Status")
        
        # Create and display map
        city_map = create_city_map(bin_data)
        map_data = st_folium(city_map, width=700, height=500)
        
        # Bin status table
        st.subheader("Bin Status Overview")
        df = pd.DataFrame([
            {
                "Bin ID": bin_info['id'],
                "Area": bin_info['area'],
                "Fill Level": f"{bin_info['fill_level']}%",
                "Status": bin_info['status'],
                "Daily Waste": f"{bin_info['daily_waste']} kg",
                "Last Collection": bin_info['last_collection'].strftime("%Y-%m-%d %H:%M"),
                "Temperature": f"{bin_info['temperature']}°C"
            }
            for bin_info in bin_data
        ])
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.subheader("Waste Management Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Fill level chart
            fill_chart = create_fill_level_chart(bin_data)
            st.plotly_chart(fill_chart, use_container_width=True)
        
        with col2:
            # Waste classification chart
            waste_chart = create_waste_classification_chart(bin_data)
            st.plotly_chart(waste_chart, use_container_width=True)
        
        # Historical trends (simulated)
        st.subheader("Historical Trends")
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        trend_data = pd.DataFrame({
            'Date': dates,
            'Total Waste': np.random.normal(1200, 200, len(dates)),
            'Recycling Rate': np.random.normal(65, 10, len(dates)),
            'Collection Efficiency': np.random.normal(85, 8, len(dates))
        })
        
        fig = px.line(trend_data, x='Date', y=['Total Waste', 'Recycling Rate', 'Collection Efficiency'],
                     title="Annual Waste Management Trends")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Garbage Collection Route Optimization")
        
        # Route optimization chart
        route_chart = create_route_optimization_chart()
        st.plotly_chart(route_chart, use_container_width=True)
        
        # Route recommendations
        st.subheader("AI-Powered Route Recommendations")
        
        recommendations = [
            "🎯 Route B shows highest efficiency (92%) - consider as template for other routes",
            "⚠️ Route C has lowest efficiency (78%) - recommend redistribution of bins",
            "🚛 Optimal collection time: 6:00 AM - 10:00 AM (lowest traffic)",
            "📍 Priority collection areas: Connaught Place, Red Fort, India Gate",
            "💡 Estimated fuel savings: 15-20% with optimized routes"
        ]
        
        for rec in recommendations:
            st.info(rec)
    
    with tab4:
        st.subheader("AI Waste Classification System")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Classification Accuracy")
            accuracy_data = {
                "Waste Type": ["Plastic", "Paper", "Glass", "Metal", "Organic"],
                "Accuracy": [94.2, 91.8, 89.5, 96.1, 87.3],
                "Samples": [15420, 12890, 8760, 6540, 18920]
            }
            
            acc_df = pd.DataFrame(accuracy_data)
            fig = px.bar(acc_df, x="Waste Type", y="Accuracy", 
                        title="AI Classification Accuracy by Waste Type",
                        color="Accuracy", color_continuous_scale="Viridis")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### Model Performance")
            st.metric("Overall Accuracy", "93.8%", delta="2.1%")
            st.metric("Processing Speed", "0.3s", delta="-0.1s")
            st.metric("Edge Device Uptime", "99.2%", delta="0.5%")
            
            st.markdown("#### Recent Classifications")
            recent_classifications = pd.DataFrame({
                "Timestamp": pd.date_range(start=datetime.now()-timedelta(hours=2), 
                                         periods=10, freq='12min'),
                "Bin ID": [f"BIN{random.randint(1,8):03d}" for _ in range(10)],
                "Item": random.choices(["Plastic Bottle", "Paper Cup", "Glass Jar", 
                                      "Metal Can", "Food Waste"], k=10),
                "Confidence": [random.randint(85, 99) for _ in range(10)]
            })
            st.dataframe(recent_classifications, use_container_width=True)
    
    with tab5:
        st.subheader("System Management & Configuration")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### System Health")
            
            system_health = {
                "Edge Devices": {"status": "Operational", "count": "8/8", "color": "green"},
                "Cloud Connectivity": {"status": "Stable", "count": "100%", "color": "green"},
                "AI Model": {"status": "Active", "count": "v2.1", "color": "green"},
                "Database": {"status": "Healthy", "count": "99.9%", "color": "green"},
                "MQTT Broker": {"status": "Connected", "count": "8 clients", "color": "green"}
            }
            
            for component, info in system_health.items():
                st.markdown(f"""
                <div style="padding: 10px; border-left: 4px solid {info['color']}; margin: 5px 0; background-color: #f8f9fa;">
                    <strong>{component}:</strong> {info['status']} ({info['count']})
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### Configuration Settings")
            
            collection_threshold = st.slider("Collection Threshold (%)", 50, 95, 85)
            alert_frequency = st.selectbox("Alert Frequency", ["Real-time", "Every 15 min", "Hourly"])
            data_retention = st.selectbox("Data Retention", ["30 days", "90 days", "1 year"])
            
            if st.button("Update Configuration"):
                st.success("Configuration updated successfully!")
        
        # Deployment status
        st.subheader("Deployment Progress")
        
        if phase == "Phase 1 - Pilot Test":
            progress = 100
            st.progress(progress/100)
            st.success("✅ Phase 1 Complete: 8 smart bins deployed in pilot zone")
            
        elif phase == "Phase 2 - City-wide Rollout":
            progress = 65
            st.progress(progress/100)
            st.info(f"🚧 Phase 2 In Progress: {progress}% complete (130/200 bins deployed)")
            
        else:  # Phase 3
            progress = 30
            st.progress(progress/100)
            st.warning(f"📋 Phase 3 Planning: {progress}% complete (expansion to 3 more cities)")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last Updated:** {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')} | **System Status:** 🟢 Operational")

if __name__ == "__main__":
    main()

