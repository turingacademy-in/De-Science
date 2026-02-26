import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import json
import time
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io
import base64
import os
from dotenv import load_dotenv
import requests
import random

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
    .node-card {
        background-color: white;
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    .node-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15);
    }
    .success-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .pending-badge {
        background-color: #FFC107;
        color: black;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        margin: 1rem 0;
    }
    .hash-display {
        font-family: 'Courier New', monospace;
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 0.9rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
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
            "stake": "32 ETH"
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
            "stake": "48 ETH"
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
            "stake": "24 ETH"
        },
        {
            "id": "NODE-004",
            "name": "Arctic Climate Station",
            "type": "Environmental Sensor",
            "location": "Svalbard, Norway",
            "status": "pending",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": 456,
            "verified": False,
            "node_address": "0x3eF5A45Cc6634C0532925a3b844Bc454e4438f99c",
            "stake": "8 ETH"
        }
    ]

# Smart Contract Configuration (simulated)
CONTRACT_ADDRESS = "0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t"
CONTRACT_ABI = {
    "anchorData": "function anchorData(bytes32 dataHash, string memory dataType, string memory metadata) public",
    "verifyData": "function verifyData(bytes32 dataHash) public view returns (bool)",
    "getNodeInfo": "function getNodeInfo(address nodeAddress) public view returns (string memory, bool)"
}

# Header section
st.markdown('<h1 class="main-header">🔬 The "De-Science" Ledger</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Decentralized Research & Data Integrity System</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1E88E5/ffffff?text=De-Science+Ledger", use_column_width=True)
    st.markdown("## Network Status")
    
    # Network metrics
    active_nodes = sum(1 for node in st.session_state.research_nodes if node["status"] == "active")
    total_data_points = sum(node["data_points"] for node in st.session_state.research_nodes)
    total_stake = sum(float(node["stake"].split()[0]) for node in st.session_state.research_nodes)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Nodes", active_nodes)
    with col2:
        st.metric("Total Data Points", total_data_points)
    
    st.metric("Total Stake", f"{total_stake} ETH")
    
    st.markdown("---")
    st.markdown("## Quick Actions")
    
    if st.button("🔄 Refresh Blockchain"):
        st.rerun()
    
    if st.button("➕ Add Test Node", use_container_width=True):
        new_node = {
            "id": f"NODE-{random.randint(100, 999)}",
            "name": f"Research Station {random.randint(1, 100)}",
            "type": random.choice(["eDNA Sensor", "Space Telemetry", "Marine eDNA", "Environmental Sensor"]),
            "location": random.choice(["Antarctica", "Moon Base", "Deep Ocean", "Atacama Desert"]),
            "status": "active",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": random.randint(100, 1000),
            "verified": True,
            "node_address": f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:40]}",
            "stake": f"{random.randint(1, 50)} ETH"
        }
        st.session_state.research_nodes.append(new_node)
        st.success("✅ Test node added successfully!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Network Info")
    st.info("""
    **Network:** Sepolia Testnet  
    **Chain ID:** 11155111  
    **Contract:** `0x1a2b...s0t`  
    **Blocks:** 4,567,890  
    **Gas Price:** 25 Gwei
    """)

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Dashboard", 
    "🔗 Data Anchoring", 
    "🔍 Data Verification", 
    "📡 Research Nodes",
    "📊 Architecture"
])

# Tab 1: Dashboard
with tab1:
    st.markdown("## Network Overview")
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Nodes", len(st.session_state.research_nodes), delta=2)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Verified Nodes", sum(1 for node in st.session_state.research_nodes if node["verified"]), delta=1)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Transactions", len(st.session_state.blockchain), delta=5)
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Data Integrity", "100%", delta=0)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Node Distribution by Type")
        node_df = pd.DataFrame(st.session_state.research_nodes)
        node_types = node_df["type"].value_counts().reset_index()
        node_types.columns = ['Type', 'Count']
        fig = px.pie(node_types, values='Count', names='Type', 
                     color_discrete_sequence=px.colors.sequential.Blues_r,
                     title="Research Node Types")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Stake Distribution")
        stake_df = pd.DataFrame([
            {"Node": node["name"][:15] + "...", "Stake": float(node["stake"].split()[0])}
            for node in st.session_state.research_nodes
        ])
        fig = px.bar(stake_df, x='Node', y='Stake', 
                     title="Node Stake (ETH)",
                     color='Stake',
                     color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("### Recent Network Activity")
    
    # Generate some sample activity
    activity_data = []
    for i in range(5):
        node = random.choice(st.session_state.research_nodes)
        tx_hash = hashlib.sha256(f"{random.random()}{time.time()}".encode()).hexdigest()
        activity_data.append({
            "Timestamp": (datetime.now() - pd.Timedelta(minutes=i*15)).strftime("%H:%M:%S"),
            "Node": node["name"],
            "Action": "Data Anchored",
            "Data Type": random.choice(["eDNA", "Telemetry", "Climate", "Marine"]),
            "Transaction": f"0x{tx_hash[:16]}..."
        })
    
    activity_df = pd.DataFrame(activity_data)
    st.dataframe(activity_df, use_container_width=True)

# Tab 2: Data Anchoring
with tab2:
    st.markdown("## Anchor Data to Blockchain")
    st.markdown('<div class="info-box">📝 Upload your research data to create an immutable record on the blockchain. The data hash will be stored permanently.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Upload Data File")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file (CSV, JSON, TXT, or any research data)",
            type=['csv', 'json', 'txt', 'xlsx', 'pdf', 'jpg', 'png']
        )
        
        if uploaded_file is not None:
            # Read file and compute hash
            file_bytes = uploaded_file.getvalue()
            file_hash = hashlib.sha256(file_bytes).hexdigest()
            
            st.markdown("#### File Details:")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Filename:** {uploaded_file.name}")
                st.write(f"**File size:** {len(file_bytes) / 1024:.2f} KB")
            with col_b:
                st.write(f"**File type:** {uploaded_file.type}")
            
            st.markdown("#### SHA-256 Hash:")
            st.code(file_hash, language="text")
    
    with col2:
        st.markdown("### Metadata")
        
        with st.form("anchor_data_form"):
            node_name = st.selectbox(
                "Select Research Node",
                options=[node["name"] for node in st.session_state.research_nodes if node["verified"]]
            )
            
            data_type = st.selectbox(
                "Data Type",
                ["eDNA Sample", "Telemetry Data", "Environmental Reading", 
                 "Climate Data", "Marine Sample", "Space Telemetry"]
            )
            
            location = st.text_input("Location", value="Field Station Alpha")
            
            additional_notes = st.text_area("Additional Notes", 
                                          placeholder="Any additional metadata about this sample...")
            
            submit_button = st.form_submit_button("🔗 Anchor to Blockchain", use_container_width=True)
            
            if submit_button and uploaded_file is not None:
                # Create blockchain transaction
                transaction = {
                    "transaction_hash": f"0x{hashlib.sha256(f'{random.random()}{time.time()}'.encode()).hexdigest()}",
                    "block_number": random.randint(1000000, 2000000),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "node": node_name,
                    "data_type": data_type,
                    "data_hash": file_hash,
                    "filename": uploaded_file.name,
                    "file_size": f"{len(file_bytes) / 1024:.2f} KB",
                    "location": location,
                    "metadata": additional_notes,
                    "status": "confirmed",
                    "gas_used": f"{random.randint(50000, 150000)}"
                }
                
                st.session_state.blockchain.append(transaction)
                st.success("✅ Data anchored successfully to Sepolia Testnet!")
                
                # Show transaction details
                st.balloons()
                st.markdown("#### Transaction Details:")
                st.json(transaction)
    
    if uploaded_file is None:
        st.info("👆 Upload a file to start")

# Tab 3: Data Verification
with tab3:
    st.markdown("## Verify Data Integrity")
    st.markdown('<div class="info-box">🔍 Upload a file to verify that its hash exists on the blockchain, proving it hasn\'t been tampered with.</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Upload File to Verify")
        verify_file = st.file_uploader(
            "Choose a file to verify",
            type=['csv', 'json', 'txt', 'xlsx', 'pdf', 'jpg', 'png'],
            key="verify"
        )
        
        if verify_file is not None:
            # Compute hash of uploaded file
            verify_bytes = verify_file.getvalue()
            verify_hash = hashlib.sha256(verify_bytes).hexdigest()
            
            st.markdown("#### File Hash:")
            st.code(verify_hash, language="text")
            
            # Check if hash exists in blockchain
            found = False
            matching_tx = None
            for tx in st.session_state.blockchain:
                if tx["data_hash"] == verify_hash:
                    found = True
                    matching_tx = tx
                    break
            
            if found:
                st.success("✅ **VERIFIED** - This data hash exists on the blockchain!")
                st.markdown("#### Original Record:")
                st.json(matching_tx)
                
                # Verification badge
                st.markdown("""
                <div style="background-color: #4CAF20; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3>✓ Data Integrity Confirmed</h3>
                    <p>This data has not been tampered with since {}</p>
                </div>
                """.format(matching_tx["timestamp"]), unsafe_allow_html=True)
            else:
                st.error("❌ **NOT FOUND** - This data hash does not exist on the blockchain!")
                st.markdown("""
                <div style="background-color: #f44336; color: white; padding: 1rem; border-radius: 10px; text-align: center;">
                    <h3>⚠ Data Integrity Alert</h3>
                    <p>This data has not been anchored to the blockchain or has been modified.</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Search by Transaction")
        
        search_type = st.radio("Search by:", ["Transaction Hash", "Data Hash", "Node Address"])
        
        if search_type == "Transaction Hash":
            search_term = st.text_input("Enter transaction hash (0x...)")
        elif search_type == "Data Hash":
            search_term = st.text_input("Enter data hash (64 characters)")
        else:
            search_term = st.text_input("Enter node address (0x...)")
        
        if st.button("🔍 Search", use_container_width=True) and search_term:
            results = []
            for tx in st.session_state.blockchain:
                if search_term.lower() in tx.get("transaction_hash", "").lower() or \
                   search_term.lower() in tx.get("data_hash", "").lower() or \
                   search_term.lower() in tx.get("node", "").lower():
                    results.append(tx)
            
            if results:
                st.success(f"Found {len(results)} matching records")
                for tx in results:
                    with st.expander(f"Transaction: {tx['transaction_hash'][:20]}..."):
                        st.json(tx)
            else:
                st.warning("No matching records found")
    
    # Recent verifications
    st.markdown("---")
    st.markdown("### Recently Verified Data")
    
    if st.session_state.blockchain:
        recent_df = pd.DataFrame(st.session_state.blockchain[-5:][::-1])
        st.dataframe(recent_df[['timestamp', 'node', 'data_type', 'data_hash']], use_container_width=True)
    else:
        st.info("No data has been anchored yet")

# Tab 4: Research Nodes
with tab4:
    st.markdown("## Verified Research Nodes")
    st.markdown('<div class="info-box">🌐 These are the trusted research nodes authorized to anchor data to the blockchain.</div>', unsafe_allow_html=True)
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "active", "pending"])
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(set(node["type"] for node in st.session_state.research_nodes)))
    with col3:
        search = st.text_input("Search by name or location", "")
    
    # Apply filters
    filtered_nodes = st.session_state.research_nodes
    
    if status_filter != "All":
        filtered_nodes = [node for node in filtered_nodes if node["status"] == status_filter]
    
    if type_filter != "All":
        filtered_nodes = [node for node in filtered_nodes if node["type"] == type_filter]
    
    if search:
        filtered_nodes = [node for node in filtered_nodes 
                         if search.lower() in node["name"].lower() or 
                         search.lower() in node["location"].lower()]
    
    # Display node statistics
    st.markdown(f"**Showing {len(filtered_nodes)} of {len(st.session_state.research_nodes)} nodes**")
    
    # Display nodes in grid
    cols = st.columns(2)
    for idx, node in enumerate(filtered_nodes):
        with cols[idx % 2]:
            with st.container():
                status_class = "success-badge" if node["status"] == "active" else "pending-badge"
                verified_icon = "✅" if node["verified"] else "⏳"
                
                st.markdown(f'''
                <div class="node-card">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4>{verified_icon} {node["name"]}</h4>
                        <span class="{status_class}">{node["status"].upper()}</span>
                    </div>
                    <p><strong>ID:</strong> {node["id"]}</p>
                    <p><strong>Type:</strong> {node["type"]}</p>
                    <p><strong>Location:</strong> {node["location"]}</p>
                    <p><strong>Node Address:</strong> <span style="font-family: monospace;">{node["node_address"][:10]}...{node["node_address"][-8:]}</span></p>
                    <p><strong>Stake:</strong> {node["stake"]}</p>
                    <p><strong>Data Points:</strong> {node["data_points"]}</p>
                    <p><strong>Last Submission:</strong> {node["last_submission"]}</p>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"View Node Details", key=f"view_{node['id']}"):
                    st.session_state.selected_node = node
                    st.rerun()
    
    # Node details modal
    if 'selected_node' in st.session_state:
        st.markdown("---")
        st.markdown(f"### 📊 Node Details: {st.session_state.selected_node['name']}")
        
        node = st.session_state.selected_node
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Node Information")
            st.json(node)
        
        with col2:
            st.markdown("#### Recent Activity")
            # Filter transactions for this node
            node_txs = [tx for tx in st.session_state.blockchain 
                       if tx["node"] == node["name"]]
            
            if node_txs:
                tx_df = pd.DataFrame(node_txs[-5:])
                st.dataframe(tx_df[['timestamp', 'data_type', 'data_hash']], use_container_width=True)
            else:
                st.info("No recent activity for this node")
        
        if st.button("Close Details", use_container_width=True):
            del st.session_state.selected_node
            st.rerun()
    
    # Add new node section
    st.markdown("---")
    with st.expander("➕ Register New Research Node"):
        st.markdown("#### Node Registration Form")
        
        col1, col2 = st.columns(2)
        with col1:
            new_node_name = st.text_input("Node Name")
            new_node_type = st.selectbox("Node Type", 
                ["eDNA Sensor", "Space Telemetry", "Marine eDNA", "Environmental Sensor"])
            new_node_location = st.text_input("Location")
        
        with col2:
            new_node_stake = st.number_input("Stake Amount (ETH)", min_value=1, max_value=100, value=10)
            new_node_address = st.text_input("Node Address (0x...)", 
                value=f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:40]}")
        
        if st.button("Register Node", use_container_width=True):
            new_node = {
                "id": f"NODE-{random.randint(100, 999)}",
                "name": new_node_name,
                "type": new_node_type,
                "location": new_node_location,
                "status": "pending",
                "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_points": 0,
                "verified": False,
                "node_address": new_node_address,
                "stake": f"{new_node_stake} ETH"
            }
            st.session_state.research_nodes.append(new_node)
            st.success("Node registered successfully! Pending verification...")
            time.sleep(1)
            st.rerun()

# Tab 5: Architecture
with tab5:
    st.markdown("## System Architecture")
    st.markdown("### Data Flow: Edge to Chain")
    
    # Create flow diagram
    fig = go.Figure()
    
    # Add nodes for flow diagram
    nodes = [
        "Edge Device\n(Sensor)",
        "Data Hash\n(SHA-256)",
        "Verified Node\n(Oracle)",
        "Smart Contract",
        "Blockchain\n(Sepolia)"
    ]
    
    # Position nodes
    x_pos = [0, 1, 2, 3, 4]
    y_pos = [0, 0, 0, 0, 0]
    
    # Colors for nodes
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']
    
    # Add nodes
    fig.add_trace(go.Scatter(
        x=x_pos,
        y=y_pos,
        mode='markers+text',
        marker=dict(size=50, color=colors, line=dict(color='white', width=2)),
        text=nodes,
        textposition="bottom center",
        textfont=dict(size=12, color='black'),
        hoverinfo='text',
        showlegend=False
    ))
    
    # Add arrows
    for i in range(len(nodes)-1):
        fig.add_annotation(
            x=(x_pos[i] + x_pos[i+1])/2,
            y=0.1,
            text="→",
            showarrow=False,
            font=dict(size=30, color="gray")
        )
    
    fig.update_layout(
        title="Data Provenance Flow",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 4.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 1]),
        height=300,
        margin=dict(l=20, r=20, t=40, b=40),
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed architecture explanation
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 🌍 Edge Layer
        - **eDNA Sensors**: Collect environmental samples
        - **Space Telemetry**: Gather spacecraft data
        - **Environmental Monitors**: Record climate data
        
        **Process:**
        1. Raw data collection
        2. Local hashing (SHA-256)
        3. Metadata attachment
        """)
        
        st.markdown("""
        #### 🔄 Oracle Layer
        - Verified research nodes
        - Data validation
        - Transaction signing
        
        **Functions:**
        - Verify data integrity
        - Submit to blockchain
        - Monitor network status
        """)
    
    with col2:
        st.markdown("""
        #### ⛓️ Blockchain Layer
        - **Network:** Sepolia Testnet
        - **Contract:** DataProvenance.sol
        - **Storage:** Immutable records
        
        **Smart Contract Functions:**
        - `anchorData()` - Store data hash
        - `verifyData()` - Check existence
        - `getNodeInfo()` - Node details
        """)
        
        st.markdown("""
        #### 📊 Dashboard Layer
        - Real-time monitoring
        - Data verification
        - Node management
        
        **Features:**
        - Transaction explorer
        - Hash verification
        - Node registry
        """)
    
    # Smart Contract Code
    st.markdown("---")
    st.markdown("### Smart Contract (Solidity)")
    
    with st.expander("📜 View DataProvenance.sol"):
        st.code('''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DataProvenance
 * @dev Decentralized research data integrity system
 */
contract DataProvenance {
    struct DataRecord {
        bytes32 dataHash;      // SHA-256 hash of the data
        uint256 timestamp;      // Block timestamp
        string dataType;        // Type of data (eDNA, telemetry, etc.)
        string metadata;        // Additional info (location, sensor ID, etc.)
        address researcher;     // Node that submitted the data
        bool verified;          // Verification status
    }
    
    struct ResearchNode {
        string nodeId;          // Unique identifier
        string nodeType;        // Type of research node
        string location;        // Physical location
        address nodeAddress;    // Ethereum address
        uint256 stake;          // Staked amount for accountability
        bool isActive;          // Node status
        uint256 registrationTime;
    }
    
    // Mappings
    mapping(bytes32 => DataRecord) public records;
    mapping(address => ResearchNode) public nodes;
    mapping(address => bool) public verifiedNodes;
    
    // Arrays
    address[] public nodeAddresses;
    bytes32[] public dataHashes;
    
    // Events
    event DataAnchored(bytes32 indexed dataHash, address indexed researcher, uint256 timestamp, string dataType);
    event NodeRegistered(address indexed nodeAddress, string nodeId, uint256 stake);
    event NodeVerified(address indexed nodeAddress, bool status);
    
    // Modifiers
    modifier onlyVerified() {
        require(verifiedNodes[msg.sender], "Not a verified node");
        _;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Register a new research node
     */
    function registerNode(
        string memory _nodeId,
        string memory _nodeType,
        string memory _location
    ) external payable {
        require(msg.value >= 1 ether, "Minimum stake is 1 ETH");
        require(!nodes[msg.sender].isActive, "Node already registered");
        
        nodes[msg.sender] = ResearchNode({
            nodeId: _nodeId,
            nodeType: _nodeType,
            location: _location,
            nodeAddress: msg.sender,
            stake: msg.value,
            isActive: true,
            registrationTime: block.timestamp
        });
        
        nodeAddresses.push(msg.sender);
        emit NodeRegistered(msg.sender, _nodeId, msg.value);
    }
    
    /**
     * @dev Verify a node (owner only)
     */
    function verifyNode(address _nodeAddress, bool _status) external onlyOwner {
        require(nodes[_nodeAddress].isActive, "Node not registered");
        verifiedNodes[_nodeAddress] = _status;
        emit NodeVerified(_nodeAddress, _status);
    }
    
    /**
     * @dev Anchor data hash to blockchain
     */
    function anchorData(
        bytes32 _dataHash,
        string memory _dataType,
        string memory _metadata
    ) external onlyVerified {
        require(records[_dataHash].timestamp == 0, "Data already anchored");
        
        records[_dataHash] = DataRecord({
            dataHash: _dataHash,
            timestamp: block.timestamp,
            dataType: _dataType,
            metadata: _metadata,
            researcher: msg.sender,
            verified: true
        });
        
        dataHashes.push(_dataHash);
        emit DataAnchored(_dataHash, msg.sender, block.timestamp, _dataType);
    }
    
    /**
     * @dev Verify if data exists
     */
    function verifyData(bytes32 _dataHash) external view returns (bool) {
        return records[_dataHash].timestamp > 0;
    }
    
    /**
     * @dev Get data provenance
     */
    function getProvenance(bytes32 _dataHash) external view returns (
        address researcher,
        uint256 timestamp,
        string memory dataType,
        string memory metadata,
        bool verified
    ) {
        DataRecord memory record = records[_dataHash];
        require(record.timestamp > 0, "Data not found");
        return (
            record.researcher,
            record.timestamp,
            record.dataType,
            record.metadata,
            record.verified
        );
    }
    
    /**
     * @dev Get node information
     */
    function getNodeInfo(address _nodeAddress) external view returns (
        string memory nodeId,
        string memory nodeType,
        string memory location,
        uint256 stake,
        bool isActive,
        bool isVerified
    ) {
        ResearchNode memory node = nodes[_nodeAddress];
        require(node.isActive, "Node not found");
        return (
            node.nodeId,
            node.nodeType,
            node.location,
            node.stake,
            node.isActive,
            verifiedNodes[_nodeAddress]
        );
    }
    
    /**
     * @dev Get total records count
     */
    function getRecordCount() external view returns (uint256) {
        return dataHashes.length;
    }
    
    /**
     * @dev Get node count
     */
    function getNodeCount() external view returns (uint256) {
        return nodeAddresses.length;
    }
}
        ''', language="solidity")
    
    # Deployment Instructions
    st.markdown("### Deployment Instructions")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        #### Prerequisites
        ```bash
        # Install dependencies
        npm install -g hardhat
        npm install @openzeppelin/contracts
        
        # Create project
        mkdir de-science-contract
        cd de-science-contract
        npx hardhat init
        ```
        """)
    
    with col2:
        st.markdown("""
        #### Deploy to Sepolia
        ```bash
        # Configure hardhat.config.js
        # Add Sepolia network
        
        # Deploy
        npx hardhat run scripts/deploy.js --network sepolia
        
        # Verify
        npx hardhat verify --network sepolia <CONTRACT_ADDRESS>
        ```
        """)

# Footer
st.markdown("---")
st.markdown(f'''
<div class="footer">
    <h3>🔬 De-Science Ledger</h3>
    <p>Decentralized Research & Data Integrity System</p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">
        <strong>Smart Contract:</strong> {CONTRACT_ADDRESS[:10]}...{CONTRACT_ADDRESS[-8:]} on Sepolia Testnet<br>
        <strong>Network Status:</strong> 🟢 Operational<br>
        <strong>Total Nodes:</strong> {len(st.session_state.research_nodes)} | 
        <strong>Total Records:</strong> {len(st.session_state.blockchain)}
    </p>
    <p style="font-size: 0.8rem; margin-top: 1rem;">
        Built for Hackathon | Data Provenance Solution | MIT License
    </p>
</div>
''', unsafe_allow_html=True)
