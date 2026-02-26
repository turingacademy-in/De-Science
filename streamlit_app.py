# streamlit_app.py
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
from web3 import Web3
import random

# Page configuration
st.set_page_config(
    page_title="De-Science Ledger",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .node-card {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .success-badge {
        background-color: #4CAF50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
    }
    .pending-badge {
        background-color: #FFC107;
        color: black;
        padding: 0.25rem 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
    }
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 10px;
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
            "last_submission": "2024-01-15 14:30:22",
            "data_points": 1245,
            "verified": True,
            "node_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"
        },
        {
            "id": "NODE-002",
            "name": "Mars Rover Telemetry",
            "type": "Space Telemetry",
            "location": "Jezero Crater, Mars",
            "status": "active", 
            "last_submission": "2024-01-15 15:45:10",
            "data_points": 3567,
            "verified": True,
            "node_address": "0x8aB4F35Cc6634C0532925a3b844Bc454e4438f77a"
        },
        {
            "id": "NODE-003",
            "name": "Pacific Ocean eDNA Array",
            "type": "Marine eDNA",
            "location": "Great Barrier Reef",
            "status": "active",
            "last_submission": "2024-01-15 13:15:33",
            "data_points": 892,
            "verified": True,
            "node_address": "0x9cD4F25Cc6634C0532925a3b844Bc454e4438f88b"
        },
        {
            "id": "NODE-004",
            "name": "Arctic Climate Station",
            "type": "Environmental Sensor",
            "location": "Svalbard, Norway",
            "status": "pending",
            "last_submission": "2024-01-14 22:10:45",
            "data_points": 456,
            "verified": False,
            "node_address": "0x3eF5A45Cc6634C0532925a3b844Bc454e4438f99c"
        }
    ]

# Header section
st.markdown('<h1 class="main-header">🔬 The "De-Science" Ledger</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Decentralized Research & Data Integrity System</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/300x100/1E88E5/ffffff?text=De-Science+Ledger", use_column_width=True)
    st.markdown("## Network Status")
    
    # Network metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Active Nodes", sum(1 for node in st.session_state.research_nodes if node["status"] == "active"))
    with col2:
        st.metric("Total Data Points", sum(node["data_points"] for node in st.session_state.research_nodes))
    
    st.markdown("---")
    st.markdown("## Quick Actions")
    
    if st.button("🔄 Refresh Blockchain"):
        st.rerun()
    
    if st.button("➕ Add Test Node"):
        new_node = {
            "id": f"NODE-{random.randint(100, 999)}",
            "name": f"New Research Station {random.randint(1, 100)}",
            "type": random.choice(["eDNA Sensor", "Space Telemetry", "Marine eDNA", "Environmental Sensor"]),
            "location": random.choice(["Antarctica", "Moon Base", "Deep Ocean", "Atacama Desert"]),
            "status": "active",
            "last_submission": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_points": random.randint(100, 1000),
            "verified": True,
            "node_address": f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:40]}"
        }
        st.session_state.research_nodes.append(new_node)
        st.success("Test node added!")
        time.sleep(1)
        st.rerun()
    
    st.markdown("---")
    st.markdown("### Network Info")
    st.info("""
    **Network:** Sepolia Testnet  
    **Chain ID:** 11155111  
    **Blocks:** 4,567,890  
    **Last Block:** 2 sec ago
    """)

# Main content area with tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🔗 Blockchain Explorer", "📡 Research Nodes", "📊 Data Flow Diagram"])

# Tab 1: Dashboard
with tab1:
    st.markdown("## Network Overview")
    
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
            st.metric("Verified Nodes", sum(1 for node in st.session_state.research_nodes if node["verified"]))
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Transactions", len(st.session_state.blockchain))
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        with st.container():
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Data Integrity", "100%")
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Node Distribution by Type")
        node_types = pd.DataFrame(st.session_state.research_nodes)["type"].value_counts()
        fig = px.pie(values=node_types.values, names=node_types.index, 
                     color_discrete_sequence=px.colors.sequential.Blues_r)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Recent Data Submissions")
        # Simulate recent submissions
        recent_data = pd.DataFrame({
            "Time": pd.date_range(end=datetime.now(), periods=10, freq="H"),
            "Data Points": np.random.randint(10, 100, 10)
        })
        fig = px.line(recent_data, x="Time", y="Data Points", 
                     title="Data Points Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.markdown("### Recent Network Activity")
    activity_data = []
    for i in range(5):
        activity_data.append({
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Node": random.choice(st.session_state.research_nodes)["name"],
            "Action": "Data Anchored",
            "Transaction": f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()[:16]}..."
        })
    
    activity_df = pd.DataFrame(activity_data)
    st.dataframe(activity_df, use_container_width=True)

# Tab 2: Blockchain Explorer
with tab2:
    st.markdown("## Blockchain Explorer")
    st.markdown("### Smart Contract Interaction")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### Anchor New Data")
        
        # Form for anchoring data
        with st.form("anchor_data_form"):
            node_name = st.selectbox(
                "Select Research Node",
                options=[node["name"] for node in st.session_state.research_nodes]
            )
            
            data_type = st.selectbox(
                "Data Type",
                ["eDNA Sample", "Telemetry Data", "Environmental Reading", "Sensor Calibration"]
            )
            
            data_value = st.text_area("Data Value (JSON format)", 
                                      value='{"temperature": 25.5, "humidity": 60, "timestamp": "2024-01-15T12:00:00Z"}')
            
            submit_button = st.form_submit_button("Anchor to Blockchain")
            
            if submit_button:
                # Create transaction
                transaction = {
                    "transaction_hash": f"0x{hashlib.sha256(str(random.random()).encode()).hexdigest()}",
                    "block_number": random.randint(1000000, 2000000),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "node": node_name,
                    "data_type": data_type,
                    "data_hash": hashlib.sha256(data_value.encode()).hexdigest(),
                    "status": "confirmed"
                }
                
                st.session_state.blockchain.append(transaction)
                st.success(f"Data anchored successfully! Transaction: {transaction['transaction_hash'][:20]}...")
                
                # Show transaction details
                st.json(transaction)
    
    with col2:
        st.markdown("#### Smart Contract Info")
        st.info("""
        **Contract Address:**  
        `0x1a2b3c4d5e6f7g8h9i0j...`
        
        **Deployed on:** Sepolia Testnet  
        **Contract Name:** DataProvenance  
        **Owner:** 0x742d35Cc6634C0532925...
        
        **Functions:**  
        • anchorData()  
        • verifyData()  
        • getProvenance()
        """)
    
    st.markdown("---")
    
    # Blockchain explorer table
    st.markdown("### Recent Blockchain Transactions")
    
    if st.session_state.blockchain:
        explorer_df = pd.DataFrame(st.session_state.blockchain[::-1])  # Reverse to show newest first
        st.dataframe(explorer_df, use_container_width=True)
        
        # Transaction details
        st.markdown("### Transaction Details")
        selected_tx = st.selectbox("Select Transaction to View Details", 
                                   options=[tx["transaction_hash"][:20] + "..." for tx in st.session_state.blockchain])
        
        if selected_tx:
            tx = next(tx for tx in st.session_state.blockchain if selected_tx[:-3] in tx["transaction_hash"])
            st.json(tx)
    else:
        st.info("No transactions yet. Use the form above to anchor data.")

# Tab 3: Research Nodes
with tab3:
    st.markdown("## Verified Research Nodes")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "active", "pending"])
    with col2:
        type_filter = st.selectbox("Filter by Type", ["All"] + list(set(node["type"] for node in st.session_state.research_nodes)))
    with col3:
        search = st.text_input("Search Node", "")
    
    # Display nodes
    filtered_nodes = st.session_state.research_nodes
    
    if status_filter != "All":
        filtered_nodes = [node for node in filtered_nodes if node["status"] == status_filter]
    
    if type_filter != "All":
        filtered_nodes = [node for node in filtered_nodes if node["type"] == type_filter]
    
    if search:
        filtered_nodes = [node for node in filtered_nodes if search.lower() in node["name"].lower() or search.lower() in node["location"].lower()]
    
    # Display nodes in grid
    cols = st.columns(2)
    for idx, node in enumerate(filtered_nodes):
        with cols[idx % 2]:
            with st.container():
                st.markdown(f'''
                <div class="node-card">
                    <h4>{node["name"]}</h4>
                    <p><strong>ID:</strong> {node["id"]}</p>
                    <p><strong>Type:</strong> {node["type"]}</p>
                    <p><strong>Location:</strong> {node["location"]}</p>
                    <p><strong>Status:</strong> <span class="{'success-badge' if node['status'] == 'active' else 'pending-badge'}">{node["status"]}</span></p>
                    <p><strong>Last Submission:</strong> {node["last_submission"]}</p>
                    <p><strong>Data Points:</strong> {node["data_points"]}</p>
                    <p><strong>Verified:</strong> {"✅" if node["verified"] else "❌"}</p>
                    <p><strong>Node Address:</strong> {node["node_address"][:20]}...</p>
                </div>
                ''', unsafe_allow_html=True)
                
                if st.button(f"View Details", key=f"view_{node['id']}"):
                    st.session_state.selected_node = node
                    st.rerun()
    
    # Node details modal
    if 'selected_node' in st.session_state:
        st.markdown("---")
        st.markdown(f"### Node Details: {st.session_state.selected_node['name']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Node Information")
            st.json(st.session_state.selected_node)
        
        with col2:
            st.markdown("#### Recent Data Submissions")
            # Simulate recent submissions for this node
            submissions = []
            for i in range(5):
                submissions.append({
                    "timestamp": (datetime.now() - pd.Timedelta(hours=i)).strftime("%Y-%m-%d %H:%M:%S"),
                    "data_hash": hashlib.sha256(str(random.random()).encode()).hexdigest()[:20] + "...",
                    "data_type": random.choice(["eDNA", "Temperature", "Humidity", "Pressure"]),
                    "block_number": random.randint(1000000, 2000000)
                })
            st.dataframe(pd.DataFrame(submissions), use_container_width=True)
        
        if st.button("Close Details"):
            del st.session_state.selected_node
            st.rerun()

# Tab 4: Data Flow Diagram
with tab4:
    st.markdown("## Data Flow: Edge to Chain")
    
    # Create flow diagram using plotly
    fig = go.Figure()
    
    # Add nodes
    nodes = ["Edge Device\n(Sensor)", "Edge Gateway", "Data Oracle", "Smart Contract", "Blockchain"]
    x_positions = [0, 1, 2, 3, 4]
    y_positions = [0, 0, 0, 0, 0]
    
    # Add node markers
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers+text',
        marker=dict(size=40, color=['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336']),
        text=nodes,
        textposition="bottom center",
        hoverinfo='text',
        showlegend=False
    ))
    
    # Add arrows
    for i in range(len(nodes)-1):
        fig.add_annotation(
            x=(x_positions[i] + x_positions[i+1])/2,
            y=0,
            text="→",
            showarrow=False,
            font=dict(size=30, color="gray")
        )
    
    fig.update_layout(
        title="Data Provenance Flow",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Detailed flow description
    st.markdown("---")
    st.markdown("### Detailed Flow Description")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 1. Edge Layer
        - **eDNA Sensors**: Collect environmental DNA samples
        - **Space Telemetry**: Gather spacecraft data
        - **Environmental Monitors**: Record climate data
        
        **Data Format:** Raw sensor readings, timestamps, GPS coordinates
        """)
        
        st.markdown("""
        #### 2. Edge Gateway
        - Aggregates data from multiple sensors
        - Performs initial validation
        - Adds metadata and timestamps
        - Encrypts sensitive data
        """)
        
        st.markdown("""
        #### 3. Data Oracle
        - Verifies data integrity
        - Creates data hash
        - Formats for blockchain
        - Manages node identity
        """)
    
    with col2:
        st.markdown("""
        #### 4. Smart Contract
        - **Function:** anchorData()
        - Records data hash
        - Stores provenance metadata
        - Emits events for verification
        """)
        
        st.markdown("""
        #### 5. Blockchain
        - Permanent immutable record
        - Timestamped transactions
        - Publicly verifiable
        - Decentralized storage
        """)
        
        st.code("""
// Smart Contract Pseudocode
function anchorData(
    bytes32 dataHash,
    string memory dataType,
    uint256 timestamp
) public {
    require(isRegisteredNode(msg.sender));
    
    DataProvenance memory provenance = DataProvenance({
        dataHash: dataHash,
        submitter: msg.sender,
        timestamp: block.timestamp,
        dataType: dataType
    });
    
    provenanceRecords[dataHash] = provenance;
    emit DataAnchored(dataHash, msg.sender);
}
        """, language="solidity")
    
    # Technical diagram
    st.markdown("---")
    st.markdown("### System Architecture")
    
    # Create a more detailed architecture diagram
    fig2 = go.Figure()
    
    # Add components
    components = {
        "Sensors": (0, 2, "eDNA\nSensors"),
        "Gateway": (1, 2, "Edge\nGateway"),
        "Oracle": (2, 2, "Data\nOracle"),
        "Contract": (3, 2, "Smart\nContract"),
        "Chain": (4, 2, "Blockchain"),
        "Dashboard": (2, 0, "Research\nDashboard")
    }
    
    for name, (x, y, label) in components.items():
        fig2.add_trace(go.Scatter(
            x=[x],
            y=[y],
            mode='markers+text',
            marker=dict(size=30, color='lightblue'),
            text=[label],
            textposition="middle center",
            name=name,
            showlegend=False
        ))
    
    # Add connections
    connections = [
        [(0, 2), (1, 2)],
        [(1, 2), (2, 2)],
        [(2, 2), (3, 2)],
        [(3, 2), (4, 2)],
        [(2, 2), (2, 0)]
    ]
    
    for conn in connections:
        fig2.add_shape(
            type="line",
            x0=conn[0][0], y0=conn[0][1],
            x1=conn[1][0], y1=conn[1][1],
            line=dict(color="gray", width=2, dash="dot")
        )
    
    fig2.update_layout(
        title="De-Science System Architecture",
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 4.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 2.5]),
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    st.plotly_chart(fig2, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    <p><strong>De-Science Ledger</strong> - Decentralized Research & Data Integrity System</p>
    <p>Smart Contract deployed on Sepolia Testnet | Network Status: Operational</p>
    <p style="font-size: 0.8rem; color: #666;">This is a demonstration interface for hackathon purposes</p>
</div>
""", unsafe_allow_html=True)

# Add sample smart contract code in an expander
with st.expander("📜 View Sample Smart Contract (Solidity)"):
    st.code('''
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataProvenance {
    struct DataRecord {
        bytes32 dataHash;
        address submitter;
        uint256 timestamp;
        string dataType;
        string metadata;
        bool verified;
    }
    
    struct ResearchNode {
        string nodeId;
        string nodeType;
        string location;
        address nodeAddress;
        bool isActive;
        uint256 registrationTime;
    }
    
    mapping(bytes32 => DataRecord) public records;
    mapping(address => ResearchNode) public nodes;
    address[] public nodeAddresses;
    
    event DataAnchored(bytes32 indexed dataHash, address indexed submitter, uint256 timestamp);
    event NodeRegistered(address indexed nodeAddress, string nodeId);
    
    modifier onlyRegisteredNode() {
        require(nodes[msg.sender].isActive, "Node not registered");
        _;
    }
    
    function registerNode(string memory _nodeId, string memory _nodeType, string memory _location) public {
        require(!nodes[msg.sender].isActive, "Node already registered");
        
        nodes[msg.sender] = ResearchNode({
            nodeId: _nodeId,
            nodeType: _nodeType,
            location: _location,
            nodeAddress: msg.sender,
            isActive: true,
            registrationTime: block.timestamp
        });
        
        nodeAddresses.push(msg.sender);
        emit NodeRegistered(msg.sender, _nodeId);
    }
    
    function anchorData(
        bytes32 _dataHash,
        string memory _dataType,
        string memory _metadata
    ) public onlyRegisteredNode {
        require(records[_dataHash].timestamp == 0, "Data already anchored");
        
        records[_dataHash] = DataRecord({
            dataHash: _dataHash,
            submitter: msg.sender,
            timestamp: block.timestamp,
            dataType: _dataType,
            metadata: _metadata,
            verified: true
        });
        
        emit DataAnchored(_dataHash, msg.sender, block.timestamp);
    }
    
    function verifyData(bytes32 _dataHash) public view returns (bool) {
        return records[_dataHash].timestamp > 0;
    }
    
    function getProvenance(bytes32 _dataHash) public view returns (
        address submitter,
        uint256 timestamp,
        string memory dataType,
        bool verified
    ) {
        DataRecord memory record = records[_dataHash];
        return (
            record.submitter,
            record.timestamp,
            record.dataType,
            record.verified
        );
    }
    
    function getNodeCount() public view returns (uint256) {
        return nodeAddresses.length;
    }
}
    ''', language="solidity")

# Add deployment instructions
with st.expander("🚀 Deployment Instructions"):
    st.markdown("""
    ### Deploy to Sepolia Testnet
    
    1. **Prerequisites**
       - Install MetaMask
       - Get Sepolia ETH from a faucet
       - Install Hardhat or Remix IDE
    
    2. **Deployment Steps**
    ```bash
    # Using Hardhat
    npx hardhat run scripts/deploy.js --network sepolia
    ```
    
    3. **Verify Contract**
    ```bash
    npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS
    ```
    
    4. **Update Streamlit App**
    - Replace contract address in the app
    - Update ABI if needed
    - Configure Web3 provider
    """)

# Add a note about running the app
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📱 Run this app
```bash
streamlit run streamlit_app.py
