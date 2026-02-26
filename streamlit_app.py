import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import json
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv
import requests
import random
import re

# Page configuration
st.set_page_config(
    page_title="De-Science Ledger",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .login-container {
        max-width: 400px;
        margin: 0 auto;
        padding: 2rem;
        background: white;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    .user-role-badge {
        display: inline-block;
        padding: 0.25rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-left: 0.5rem;
    }
    .role-researcher {
        background-color: #2196F3;
        color: white;
    }
    .role-validator {
        background-color: #4CAF50;
        color: white;
    }
    .role-auditor {
        background-color: #FF9800;
        color: white;
    }
    .role-admin {
        background-color: #9C27B0;
        color: white;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: 600;
    }
    .logout-btn {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'login_time' not in st.session_state:
    st.session_state.login_time = None

# Initialize users database (simulated)
if 'users_db' not in st.session_state:
    st.session_state.users_db = {
        # Default users with different roles
        "researcher1": {
            "password": hash_password("research123"),
            "name": "Dr. Sarah Chen",
            "email": "sarah.chen@research.org",
            "role": "researcher",
            "institution": "Stanford University",
            "node_id": "NODE-001",
            "verified": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        },
        "validator1": {
            "password": hash_password("validate123"),
            "name": "Prof. James Wilson",
            "email": "j.wilson@blockchain-lab.io",
            "role": "validator",
            "institution": "MIT Blockchain Lab",
            "verified": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        },
        "auditor1": {
            "password": hash_password("audit123"),
            "name": "Dr. Maria Garcia",
            "email": "m.garcia@ethics-board.org",
            "role": "auditor",
            "institution": "Research Ethics Board",
            "verified": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        },
        "admin": {
            "password": hash_password("admin123"),
            "name": "System Administrator",
            "email": "admin@de-science.io",
            "role": "admin",
            "institution": "De-Science Foundation",
            "verified": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        },
        "demo_user": {
            "password": hash_password("demo123"),
            "name": "Demo Researcher",
            "email": "demo@example.com",
            "role": "researcher",
            "institution": "Demo University",
            "verified": True,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_login": None
        }
    }

# Initialize registration requests (for new user signups)
if 'registration_requests' not in st.session_state:
    st.session_state.registration_requests = []

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Validate email format
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# Validate password strength
def is_strong_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

# Authentication functions
def authenticate_user(username, password):
    if username in st.session_state.users_db:
        if st.session_state.users_db[username]["password"] == hash_password(password):
            # Update last login
            st.session_state.users_db[username]["last_login"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return True
    return False

def register_user(username, password, name, email, role, institution):
    if username in st.session_state.users_db:
        return False, "Username already exists"
    
    if not is_valid_email(email):
        return False, "Invalid email format"
    
    if not is_strong_password(password):
        return False, "Password must be at least 8 characters with uppercase, lowercase, and numbers"
    
    # Add to registration requests (pending approval)
    request = {
        "username": username,
        "password": hash_password(password),
        "name": name,
        "email": email,
        "role": role,
        "institution": institution,
        "verified": False,
        "request_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending"
    }
    st.session_state.registration_requests.append(request)
    return True, "Registration submitted for approval"

# Get user role badge
def get_role_badge(role):
    badges = {
        "researcher": "🔬 Researcher",
        "validator": "✅ Validator",
        "auditor": "📋 Auditor",
        "admin": "⚙️ Admin"
    }
    return badges.get(role, role)

# Initialize blockchain and research nodes (as before)
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = []
    
if 'research_nodes' not in st.session_state:
    st.session_state.research_nodes = [
        {
            "id": "NODE-001",
            "name": "Amazon Rainforest eDNA Station",
            "type": "eDNA Sensor",
            "location": "Manaus, Brazil",
            "status": "active",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": 1245,
            "verified": True,
            "node_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
            "stake": "32 ETH",
            "owner": "researcher1"
        },
        {
            "id": "NODE-002",
            "name": "Mars Rover Telemetry", 
            "type": "Space Telemetry",
            "location": "Jezero Crater, Mars",
            "status": "active",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": 3567,
            "verified": True,
            "node_address": "0x8aB4F35Cc6634C0532925a3b844Bc454e4438f77a",
            "stake": "48 ETH",
            "owner": "researcher1"
        },
        {
            "id": "NODE-003",
            "name": "Pacific Ocean eDNA Array",
            "type": "Marine eDNA", 
            "location": "Great Barrier Reef",
            "status": "active",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": 892,
            "verified": True,
            "node_address": "0x9cD4F25Cc6634C0532925a3b844Bc454e4438f88b",
            "stake": "24 ETH",
            "owner": "researcher1"
        }
    ]

# Smart Contract Configuration
CONTRACT_ADDRESS = "0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t"

# Helper function to safely extract stake value
def get_stake_value(stake_str):
    try:
        if stake_str and isinstance(stake_str, str):
            return float(stake_str.split()[0])
        return 0
    except (ValueError, IndexError, AttributeError):
        return 0

# Logout function
def logout():
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_role = None
    st.session_state.login_time = None
    st.rerun()

# Login Page
def show_login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.image("https://via.placeholder.com/300x100/1E88E5/ffffff?text=De-Science+Ledger", use_column_width=True)
        st.markdown("### 🔐 Welcome Back")
        st.markdown("Login to access the Decentralized Research Platform")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Login", use_container_width=True)
            with col_b:
                go_to_register = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if authenticate_user(username, password):
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.user_role = st.session_state.users_db[username]["role"]
                    st.session_state.login_time = datetime.now()
                    st.success(f"Welcome back, {st.session_state.users_db[username]['name']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid username or password")
            
            if go_to_register:
                st.session_state.show_register = True
                st.rerun()
        
        st.markdown("---")
        st.markdown("#### Default Login Credentials:")
        
        # Create a DataFrame for default users
        default_users = pd.DataFrame([
            {"Role": "🔬 Researcher", "Username": "researcher1", "Password": "research123"},
            {"Role": "✅ Validator", "Username": "validator1", "Password": "validate123"},
            {"Role": "📋 Auditor", "Username": "auditor1", "Password": "audit123"},
            {"Role": "⚙️ Admin", "Username": "admin", "Password": "admin123"},
            {"Role": "👤 Demo User", "Username": "demo_user", "Password": "demo123"}
        ])
        st.dataframe(default_users, use_container_width=True, hide_index=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# Registration Page
def show_register_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown("### 📝 Create Account")
        st.markdown("Register as a new user (pending approval)")
        
        with st.form("register_form"):
            full_name = st.text_input("Full Name", placeholder="Dr. John Doe")
            email = st.text_input("Email", placeholder="john.doe@institution.edu")
            institution = st.text_input("Institution/Organization", placeholder="University Name")
            
            role = st.selectbox(
                "Select Role",
                ["researcher", "validator", "auditor"],
                format_func=lambda x: {
                    "researcher": "🔬 Researcher - Submit research data",
                    "validator": "✅ Validator - Validate and verify data",
                    "auditor": "📋 Auditor - Audit and monitor system"
                }[x]
            )
            
            username = st.text_input("Username", placeholder="Choose a username")
            password = st.text_input("Password", type="password", 
                                   placeholder="Min 8 chars with uppercase, lowercase & number")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col_a, col_b = st.columns(2)
            with col_a:
                submit = st.form_submit_button("Register", use_container_width=True)
            with col_b:
                back_to_login = st.form_submit_button("Back to Login", use_container_width=True)
            
            if submit:
                if password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = register_user(username, password, full_name, email, role, institution)
                    if success:
                        st.success(message)
                        st.info("Your registration has been submitted for approval. You will be notified once verified.")
                        time.sleep(2)
                        st.session_state.show_register = False
                        st.rerun()
                    else:
                        st.error(message)
            
            if back_to_login:
                st.session_state.show_register = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

# Main App (Authenticated)
def show_main_app():
    # Logout button in sidebar
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"### 👤 Logged in as:")
        st.markdown(f"**{st.session_state.users_db[st.session_state.current_user]['name']}**")
        role = st.session_state.user_role
        role_display = {
            "researcher": "🔬 Researcher",
            "validator": "✅ Validator",
            "auditor": "📋 Auditor",
            "admin": "⚙️ Admin"
        }.get(role, role)
        st.markdown(f"**Role:** {role_display}")
        
        if st.session_state.login_time:
            st.markdown(f"**Login time:** {st.session_state.login_time.strftime('%H:%M:%S')}")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Welcome banner
    st.markdown(f'''
    <div class="welcome-banner">
        <h1>🔬 Welcome back, {st.session_state.users_db[st.session_state.current_user]['name']}!</h1>
        <p>You are logged in as <strong>{role_display}</strong> • {datetime.now().strftime("%B %d, %Y")}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Network metrics
    active_nodes = sum(1 for node in st.session_state.research_nodes if node.get("status") == "active")
    total_data_points = sum(node.get("data_points", 0) for node in st.session_state.research_nodes)
    
    total_stake = 0
    for node in st.session_state.research_nodes:
        stake_value = get_stake_value(node.get("stake", "0 ETH"))
        total_stake += stake_value
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Nodes", len(st.session_state.research_nodes))
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Active Nodes", active_nodes)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Data Points", total_data_points)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Stake", f"{total_stake:.1f} ETH")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Role-based tabs
    if st.session_state.user_role == "admin":
        tabs = ["📊 Dashboard", "🔗 Data Anchoring", "🔍 Verification", "📡 Nodes", "👥 User Management", "📊 Architecture"]
    elif st.session_state.user_role == "validator":
        tabs = ["📊 Dashboard", "🔍 Verification", "📡 Nodes", "📊 Architecture"]
    elif st.session_state.user_role == "auditor":
        tabs = ["📊 Dashboard", "🔍 Audit Log", "📡 Nodes", "📊 Architecture"]
    else:  # researcher
        tabs = ["📊 Dashboard", "🔗 Data Anchoring", "🔍 My Data", "📡 My Nodes", "📊 Architecture"]
    
    tab_objects = st.tabs(tabs)
    
    # Dashboard Tab (all roles)
    with tab_objects[0]:
        show_dashboard()
    
    # Role-specific tabs
    if st.session_state.user_role == "admin":
        with tab_objects[1]:
            show_data_anchoring()
        with tab_objects[2]:
            show_verification()
        with tab_objects[3]:
            show_nodes()
        with tab_objects[4]:
            show_user_management()
        with tab_objects[5]:
            show_architecture()
    
    elif st.session_state.user_role == "validator":
        with tab_objects[1]:
            show_verification()
        with tab_objects[2]:
            show_nodes()
        with tab_objects[3]:
            show_architecture()
    
    elif st.session_state.user_role == "auditor":
        with tab_objects[1]:
            show_audit_log()
        with tab_objects[2]:
            show_nodes()
        with tab_objects[3]:
            show_architecture()
    
    else:  # researcher
        with tab_objects[1]:
            show_data_anchoring()
        with tab_objects[2]:
            show_my_data()
        with tab_objects[3]:
            show_my_nodes()
        with tab_objects[4]:
            show_architecture()

# Dashboard function
def show_dashboard():
    st.markdown("## Network Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Node Distribution by Type")
        node_df = pd.DataFrame(st.session_state.research_nodes)
        if not node_df.empty and 'type' in node_df.columns:
            node_types = node_df["type"].value_counts().reset_index()
            node_types.columns = ['Type', 'Count']
            fig = px.pie(node_types, values='Count', names='Type', 
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Recent Activity")
        activity_data = []
        for i in range(min(5, len(st.session_state.blockchain))):
            tx = st.session_state.blockchain[-(i+1)]
            activity_data.append({
                "Time": tx.get("timestamp", ""),
                "Node": tx.get("node", "Unknown")[:15] + "...",
                "Type": tx.get("data_type", "Unknown")
            })
        
        if activity_data:
            st.dataframe(pd.DataFrame(activity_data), use_container_width=True)
        else:
            st.info("No recent activity")

# Data Anchoring function
def show_data_anchoring():
    st.markdown("## Anchor Data to Blockchain")
    st.markdown('<div class="info-box">📝 Upload your research data to create an immutable record.</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose a file", type=['csv', 'json', 'txt', 'pdf', 'jpg', 'png'])
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.sha256(file_bytes).hexdigest()
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### File Details:")
            st.write(f"**Filename:** {uploaded_file.name}")
            st.write(f"**Size:** {len(file_bytes) / 1024:.2f} KB")
        
        with col2:
            st.markdown("#### SHA-256 Hash:")
            st.code(file_hash[:50] + "...", language="text")
        
        if st.button("🔗 Anchor to Blockchain", use_container_width=True):
            transaction = {
                "transaction_hash": f"0x{hashlib.sha256(f'{random.random()}{time.time()}'.encode()).hexdigest()}",
                "block_number": random.randint(1000000, 2000000),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "node": st.session_state.current_user,
                "data_type": "Research Data",
                "data_hash": file_hash,
                "filename": uploaded_file.name,
                "status": "confirmed"
            }
            st.session_state.blockchain.append(transaction)
            st.success("✅ Data anchored successfully!")
            st.balloons()

# Verification function
def show_verification():
    st.markdown("## Verify Data Integrity")
    verify_file = st.file_uploader("Upload file to verify", type=['csv', 'json', 'txt', 'pdf', 'jpg', 'png'], key="verify")
    
    if verify_file is not None:
        verify_bytes = verify_file.getvalue()
        verify_hash = hashlib.sha256(verify_bytes).hexdigest()
        
        st.markdown("#### File Hash:")
        st.code(verify_hash, language="text")
        
        found = False
        for tx in st.session_state.blockchain:
            if tx.get("data_hash") == verify_hash:
                found = True
                st.success("✅ Data verified! Record found on blockchain")
                st.json(tx)
                break
        
        if not found:
            st.error("❌ Data not found on blockchain")

# My Data function
def show_my_data():
    st.markdown("## My Data Submissions")
    
    my_data = [tx for tx in st.session_state.blockchain if tx.get("node") == st.session_state.current_user]
    
    if my_data:
        df = pd.DataFrame(my_data)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("You haven't submitted any data yet")

# My Nodes function
def show_my_nodes():
    st.markdown("## My Research Nodes")
    
    if st.button("➕ Register New Node", use_container_width=True):
        new_node = {
            "id": f"NODE-{random.randint(100, 999)}",
            "name": f"Personal Node {random.randint(1, 100)}",
            "type": "Research Node",
            "location": "Field Station",
            "status": "pending",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": 0,
            "verified": False,
            "node_address": f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:40]}",
            "stake": "10 ETH",
            "owner": st.session_state.current_user
        }
        st.session_state.research_nodes.append(new_node)
        st.success("Node registration submitted for verification!")
        time.sleep(1)
        st.rerun()

# Audit Log function
def show_audit_log():
    st.markdown("## System Audit Log")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Pending Verifications")
        pending_nodes = [n for n in st.session_state.research_nodes if not n.get("verified")]
        if pending_nodes:
            st.dataframe(pd.DataFrame(pending_nodes))
        else:
            st.info("No pending verifications")
    
    with col2:
        st.markdown("### Recent Activity")
        if st.session_state.blockchain:
            recent = st.session_state.blockchain[-10:]
            st.dataframe(pd.DataFrame(recent))

# User Management function (admin only)
def show_user_management():
    st.markdown("## User Management")
    
    tab1, tab2 = st.tabs(["👥 Registered Users", "📝 Pending Registrations"])
    
    with tab1:
        st.markdown("### Registered Users")
        users_data = []
        for username, data in st.session_state.users_db.items():
            users_data.append({
                "Username": username,
                "Name": data.get("name", ""),
                "Email": data.get("email", ""),
                "Role": data.get("role", ""),
                "Verified": "✅" if data.get("verified") else "❌",
                "Last Login": data.get("last_login", "Never")
            })
        
        if users_data:
            df = pd.DataFrame(users_data)
            st.dataframe(df, use_container_width=True)
    
    with tab2:
        st.markdown("### Pending Registration Requests")
        if st.session_state.registration_requests:
            for req in st.session_state.registration_requests:
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{req['name']}** ({req['username']}) - {req['role']}")
                        st.markdown(f"📧 {req['email']} | 🏛️ {req['institution']}")
                        st.markdown(f"📅 {req['request_date']}")
                    with col2:
                        if st.button("✅ Approve", key=f"approve_{req['username']}"):
                            # Add to users database
                            st.session_state.users_db[req['username']] = {
                                "password": req['password'],
                                "name": req['name'],
                                "email": req['email'],
                                "role": req['role'],
                                "institution": req['institution'],
                                "verified": True,
                                "created_at": req['request_date'],
                                "last_login": None
                            }
                            # Remove from requests
                            st.session_state.registration_requests.remove(req)
                            st.success(f"User {req['username']} approved!")
                            time.sleep(1)
                            st.rerun()
                    with col3:
                        if st.button("❌ Reject", key=f"reject_{req['username']}"):
                            st.session_state.registration_requests.remove(req)
                            st.warning(f"User {req['username']} rejected")
                            time.sleep(1)
                            st.rerun()
                    st.markdown("---")
        else:
            st.info("No pending registration requests")

# Nodes function
def show_nodes():
    st.markdown("## Research Nodes")
    
    for node in st.session_state.research_nodes:
        with st.container():
            status_color = "🟢" if node.get("status") == "active" else "🟡"
            verified = "✅" if node.get("verified") else "⏳"
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"{verified} **{node.get('name')}** {status_color}")
                st.markdown(f"📍 {node.get('location')} | 📊 {node.get('data_points')} data points")
            with col2:
                st.markdown(f"**Stake:** {node.get('stake')}")
            st.markdown("---")

# Architecture function
def show_architecture():
    st.markdown("## System Architecture")
    
    # Flow diagram
    fig = go.Figure()
    
    nodes = ["Edge Device", "Data Hash", "Verified Node", "Smart Contract", "Blockchain"]
    x_pos = [0, 1, 2, 3, 4]
    y_pos = [0, 0, 0, 0, 0]
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
    
    fig.add_trace(go.Scatter(
        x=x_pos, y=y_pos,
        mode='markers+text',
        marker=dict(size=40, color=colors),
        text=nodes,
        textposition="bottom center",
        showlegend=False
    ))
    
    fig.update_layout(
        height=200,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### 🔬 For Researchers
        - Submit data hashes
        - Manage research nodes
        - Track submissions
        """)
    
    with col2:
        st.markdown("""
        #### ✅ For Validators
        - Verify data integrity
        - Validate nodes
        - Monitor network
        """)

# Main app logic
if 'show_register' not in st.session_state:
    st.session_state.show_register = False

if not st.session_state.authenticated:
    if st.session_state.show_register:
        show_register_page()
    else:
        show_login_page()
else:
    show_main_app()

# Footer
st.markdown("---")
st.markdown(f'''
<div class="footer">
    <h3>🔬 De-Science Ledger</h3>
    <p>Decentralized Research & Data Integrity System</p>
    <p style="font-size: 0.8rem;">© 2024 • Built for Hackathon</p>
</div>
''', unsafe_allow_html=True)
