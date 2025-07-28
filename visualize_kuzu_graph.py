#!/usr/bin/env python3
"""
Kuzu Graph Visualization Tool
Visualizes the knowledge graph created by Cognee using various methods
"""

import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from cognee_integration.enhanced_cognee_manager import EnhancedCogneeManager

class KuzuGraphVisualizer:
    def __init__(self):
        self.cognee_manager = EnhancedCogneeManager()
        self.graph_info = self.cognee_manager.get_knowledge_graph_info()
        self.graph_path = None
        
        if not self.graph_info.get('error'):
            self.graph_path = self.graph_info.get('graph_path', '')
    
    def check_kuzu_availability(self):
        """Check if Kuzu is available and accessible"""
        try:
            import kuzu
            print("✅ Kuzu Python client available")
            
            if self.graph_path and Path(self.graph_path).exists():
                print(f"✅ Kuzu database found at: {self.graph_path}")
                print(f"📊 Database size: {self.graph_info.get('graph_size_mb', 0)} MB")
                return True
            else:
                print(f"❌ Kuzu database not found at: {self.graph_path}")
                return False
                
        except ImportError:
            print("❌ Kuzu Python client not installed")
            print("💡 Install with: pip install kuzu")
            return False
    
    def explore_kuzu_structure(self):
        """Explore the structure of the Kuzu database"""
        try:
            import kuzu
            
            if not self.graph_path or not Path(self.graph_path).exists():
                print("❌ Kuzu database path not available")
                return None
            
            print(f"🔍 Exploring Kuzu database structure...")
            
            # Connect to Kuzu database
            db = kuzu.Database(self.graph_path)
            conn = kuzu.Connection(db)
            
            # Get all node tables
            result = conn.execute("SHOW TABLES")
            tables = []
            while result.hasNext():
                tables.append(result.getNext())
            
            print(f"📋 Found {len(tables)} tables:")
            
            structure_info = {
                "tables": [],
                "total_nodes": 0,
                "total_relationships": 0
            }
            
            for table in tables:
                table_name = table[0]
                table_type = table[1] if len(table) > 1 else "unknown"
                
                print(f"  - {table_name} ({table_type})")
                
                try:
                    # Count records in each table
                    count_result = conn.execute(f"MATCH (n:{table_name}) RETURN count(n)")
                    count = 0
                    if count_result.hasNext():
                        count = count_result.getNext()[0]
                    
                    structure_info["tables"].append({
                        "name": table_name,
                        "type": table_type,
                        "count": count
                    })
                    
                    if table_type.lower() == "node":
                        structure_info["total_nodes"] += count
                    elif table_type.lower() == "rel":
                        structure_info["total_relationships"] += count
                        
                except Exception as e:
                    print(f"    ⚠️ Could not count records: {e}")
            
            conn.close()
            
            print(f"\n📊 Database Summary:")
            print(f"   Total Nodes: {structure_info['total_nodes']}")
            print(f"   Total Relationships: {structure_info['total_relationships']}")
            
            return structure_info
            
        except Exception as e:
            print(f"❌ Error exploring Kuzu structure: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_graph_data(self):
        """Extract graph data for visualization"""
        try:
            import kuzu
            
            if not self.graph_path or not Path(self.graph_path).exists():
                return None, None
            
            print(f"📊 Extracting graph data for visualization...")
            
            db = kuzu.Database(self.graph_path)
            conn = kuzu.Connection(db)
            
            nodes = []
            edges = []
            
            # Try to get all nodes with a general query
            try:
                # This is a generic approach - might need adjustment based on actual schema
                result = conn.execute("MATCH (n) RETURN n LIMIT 100")
                
                node_id = 0
                while result.hasNext():
                    node_data = result.getNext()[0]
                    nodes.append({
                        "id": node_id,
                        "label": str(node_data)[:50] + "..." if len(str(node_data)) > 50 else str(node_data),
                        "data": str(node_data)
                    })
                    node_id += 1
                    
            except Exception as e:
                print(f"⚠️ Could not extract nodes with generic query: {e}")
            
            # Try to get relationships
            try:
                result = conn.execute("MATCH (a)-[r]->(b) RETURN a, r, b LIMIT 50")
                
                edge_id = 0
                while result.hasNext():
                    edge_data = result.getNext()
                    edges.append({
                        "id": edge_id,
                        "source": edge_id * 2,  # Simplified - would need proper node mapping
                        "target": edge_id * 2 + 1,
                        "label": str(edge_data[1]) if len(edge_data) > 1 else "related",
                        "data": str(edge_data)
                    })
                    edge_id += 1
                    
            except Exception as e:
                print(f"⚠️ Could not extract relationships: {e}")
            
            conn.close()
            
            print(f"✅ Extracted {len(nodes)} nodes and {len(edges)} edges")
            return nodes, edges
            
        except Exception as e:
            print(f"❌ Error extracting graph data: {e}")
            return None, None
    
    def create_networkx_visualization(self, nodes, edges, output_file="kuzu_graph.png"):
        """Create visualization using NetworkX and Matplotlib"""
        try:
            G = nx.Graph()
            
            # Add nodes
            for node in nodes:
                G.add_node(node["id"], label=node["label"])
            
            # Add edges
            for edge in edges:
                if edge["source"] < len(nodes) and edge["target"] < len(nodes):
                    G.add_edge(edge["source"], edge["target"], label=edge["label"])
            
            plt.figure(figsize=(12, 8))
            
            # Use spring layout for better visualization
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Draw nodes
            nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                                 node_size=1000, alpha=0.7)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, alpha=0.5, edge_color='gray')
            
            # Draw labels
            labels = {node["id"]: node["label"][:20] for node in nodes}
            nx.draw_networkx_labels(G, pos, labels, font_size=8)
            
            plt.title("Kuzu Knowledge Graph Visualization")
            plt.axis('off')
            plt.tight_layout()
            
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"✅ NetworkX visualization saved as {output_file}")
            
            plt.show()
            
        except Exception as e:
            print(f"❌ Error creating NetworkX visualization: {e}")
    
    def create_plotly_visualization(self, nodes, edges, output_file="kuzu_graph.html"):
        """Create interactive visualization using Plotly"""
        try:
            # Create NetworkX graph for layout calculation
            G = nx.Graph()
            
            for node in nodes:
                G.add_node(node["id"])
            
            for edge in edges:
                if edge["source"] < len(nodes) and edge["target"] < len(nodes):
                    G.add_edge(edge["source"], edge["target"])
            
            # Calculate positions
            pos = nx.spring_layout(G, k=1, iterations=50)
            
            # Extract coordinates
            node_x = [pos[node["id"]][0] for node in nodes]
            node_y = [pos[node["id"]][1] for node in nodes]
            
            # Create edge traces
            edge_x = []
            edge_y = []
            
            for edge in edges:
                if edge["source"] < len(nodes) and edge["target"] < len(nodes):
                    x0, y0 = pos[edge["source"]]
                    x1, y1 = pos[edge["target"]]
                    edge_x.extend([x0, x1, None])
                    edge_y.extend([y0, y1, None])
            
            # Create edge trace
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='gray'),
                hoverinfo='none',
                mode='lines'
            )
            
            # Create node trace
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                hoverinfo='text',
                text=[node["label"][:20] for node in nodes],
                textposition="middle center",
                hovertext=[f"Node: {node['label']}<br>Data: {node['data'][:100]}..." 
                          for node in nodes],
                marker=dict(
                    size=20,
                    color='lightblue',
                    line=dict(width=2, color='darkblue')
                )
            )
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace],
                          layout=go.Layout(
                              title=dict(text="Interactive Kuzu Knowledge Graph", font=dict(size=16)),
                              showlegend=False,
                              hovermode='closest',
                              margin=dict(b=20,l=5,r=5,t=40),
                              annotations=[ dict(
                                  text="Cognee Knowledge Graph built with Kuzu",
                                  showarrow=False,
                                  xref="paper", yref="paper",
                                  x=0.005, y=-0.002,
                                  xanchor='left', yanchor='bottom',
                                  font=dict(color='gray', size=12)
                              )],
                              xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                              yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
                          )
                         )
            
            fig.write_html(output_file)
            print(f"✅ Interactive Plotly visualization saved as {output_file}")
            
            # Also show in browser if possible
            fig.show()
            
        except Exception as e:
            print(f"❌ Error creating Plotly visualization: {e}")
    
    def create_mock_visualization(self):
        """Create a mock visualization when no real graph data is available"""
        print("📊 Creating mock knowledge graph visualization...")
        
        # Create sample nodes representing typical Cognee knowledge graph
        mock_nodes = [
            {"id": 0, "label": "Samsung TV", "data": "Product node for Samsung TV"},
            {"id": 1, "label": "Power Issues", "data": "Issue category node"},
            {"id": 2, "label": "Screen Flickering", "data": "Specific problem node"},
            {"id": 3, "label": "Firmware Update", "data": "Solution category node"},
            {"id": 4, "label": "Motion Plus Settings", "data": "Technical setting node"},
            {"id": 5, "label": "User Manual", "data": "Document source node"},
            {"id": 6, "label": "FAQ Document", "data": "Document source node"},
            {"id": 7, "label": "Support Agent", "data": "Human expert node"},
        ]
        
        mock_edges = [
            {"id": 0, "source": 0, "target": 1, "label": "has_issue"},
            {"id": 1, "source": 0, "target": 2, "label": "has_problem"},
            {"id": 2, "source": 2, "target": 3, "label": "solved_by"},
            {"id": 3, "source": 3, "target": 4, "label": "involves"},
            {"id": 4, "source": 5, "target": 0, "label": "documents"},
            {"id": 5, "source": 6, "target": 1, "label": "explains"},
            {"id": 6, "source": 7, "target": 3, "label": "provides"},
        ]
        
        print("✅ Creating NetworkX visualization...")
        self.create_networkx_visualization(mock_nodes, mock_edges, "mock_kuzu_graph.png")
        
        print("✅ Creating interactive Plotly visualization...")
        self.create_plotly_visualization(mock_nodes, mock_edges, "mock_kuzu_graph.html")
        
        return mock_nodes, mock_edges

def main():
    """Main function to visualize Kuzu graph"""
    print("🕸️ Kuzu Graph Visualization Tool")
    print("=" * 40)
    
    visualizer = KuzuGraphVisualizer()
    
    # Check availability
    if not visualizer.check_kuzu_availability():
        print("\n💡 Since Kuzu database is not accessible, creating mock visualization...")
        visualizer.create_mock_visualization()
        return
    
    # Explore structure
    structure = visualizer.explore_kuzu_structure()
    
    if structure and (structure["total_nodes"] > 0 or structure["total_relationships"] > 0):
        # Extract real data
        nodes, edges = visualizer.extract_graph_data()
        
        if nodes and edges:
            print("\n🎨 Creating visualizations...")
            visualizer.create_networkx_visualization(nodes, edges)
            visualizer.create_plotly_visualization(nodes, edges)
        else:
            print("\n💡 No graph data extracted, creating mock visualization...")
            visualizer.create_mock_visualization()
    else:
        print("\n💡 No graph data found, creating mock visualization to show potential structure...")
        visualizer.create_mock_visualization()
    
    print("\n✅ Visualization complete!")
    print("\nFiles created:")
    print("  - kuzu_graph.png (static image)")
    print("  - kuzu_graph.html (interactive)")
    print("  - mock_kuzu_graph.png (example static)")
    print("  - mock_kuzu_graph.html (example interactive)")

if __name__ == "__main__":
    main() 