import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import matplotlib.pyplot as plt

# Ingredient calorie database (per 100g)
INGREDIENT_CALORIES = {
    "beef_patty": 250,
    "chicken_patty": 165,
    "veggie_patty": 180,
    "fish_fillet": 140,
    "sausage": 270,
    "bacon": 540,
    "cheddar_cheese": 400,
    "mozzarella_cheese": 280,
    "bun": 270,
    "bread": 265,
    "tortilla": 300,
    "lettuce": 15,
    "tomato": 18,
    "onions": 40,
    "pickles": 11,
    "mayo": 680,
    "ketchup": 112,
    "mustard": 66,
    "bbq_sauce": 120,
    "tartar_sauce": 200,
    "grilled_chicken": 165,
    "potatoes": 77,
    "oil": 884,
    "pizza_base": 270,
    "tomato_sauce": 29,
    "cheese": 400,
    "meat": 250,
    "vegetables": 30,
    "eggs": 155,
    "butter": 717,
    "milk": 42,
    "flour": 364,
    "sugar": 387,
    "chocolate": 535,
    "cream": 345,
    "pasta": 131,
    "rice": 130,
    "beans": 127,
    "avocado": 160,
    "salsa": 36,
    "sour_cream": 193,
    "seafood": 85,
    "salmon": 208,
    "tuna": 130,
    "shrimp": 99,
    "noodles": 138
}

# Food ingredients mapping
FOOD_INGREDIENTS = {
    "hamburger": {
        "beef_patty": 100,
        "bun": 80,
        "lettuce": 20,
        "tomato": 30,
        "onions": 15,
        "pickles": 10,
        "ketchup": 15,
        "mustard": 10
    },
    "cheeseburger": {
        "beef_patty": 100,
        "bun": 80,
        "cheddar_cheese": 30,
        "lettuce": 20,
        "tomato": 30,
        "onions": 15,
        "pickles": 10,
        "mayo": 15
    },
    "bacon_burger": {
        "beef_patty": 100,
        "bacon": 30,
        "cheddar_cheese": 30,
        "bun": 80,
        "lettuce": 20,
        "tomato": 30,
        "onions": 15,
        "bbq_sauce": 20
    },
    "veggie_burger": {
        "veggie_patty": 100,
        "bun": 80,
        "lettuce": 20,
        "tomato": 30,
        "onions": 15,
        "pickles": 10,
        "mayo": 15
    },
    "chicken_burger": {
        "grilled_chicken": 100,
        "bun": 80,
        "lettuce": 20,
        "tomato": 30,
        "mayo": 15,
        "onions": 15
    },
    "fish_burger": {
        "fish_fillet": 100,
        "bun": 80,
        "lettuce": 20,
        "tartar_sauce": 25,
        "pickles": 10
    },
    "hot_dog": {
        "sausage": 100,
        "bun": 60,
        "ketchup": 15,
        "mustard": 10,
        "onions": 15
    },
    "pizza": {
        "pizza_base": 150,
        "tomato_sauce": 50,
        "mozzarella_cheese": 80,
        "oil": 10
    },
    "french_fries": {
        "potatoes": 200,
        "oil": 20
    },
    "club_sandwich": {
        "bread": 100,
        "chicken_patty": 80,
        "bacon": 20,
        "lettuce": 15,
        "tomato": 20,
        "mayo": 15
    },
    "caesar_salad": {
        "lettuce": 100,
        "cheddar_cheese": 30,
        "bread": 30,
        "mayo": 20
    },
    "sushi": {
        "rice": 100,
        "fish_fillet": 50,
        "vegetables": 20,
        "noodles": 30
    },
    "tacos": {
        "tortilla": 50,
        "beef_patty": 80,
        "lettuce": 20,
        "tomato": 20,
        "cheese": 20,
        "salsa": 15,
        "sour_cream": 15
    },
    "pasta": {
        "pasta": 200,
        "tomato_sauce": 100,
        "cheese": 30,
        "oil": 15
    },
    "grilled_salmon": {
        "salmon": 200,
        "oil": 10,
        "vegetables": 50
    }
}

# Page configuration
st.set_page_config(
    page_title="Food Ingredient & Calorie Analyzer",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)

def calculate_total_calories(food_name):
    """Calculate total calories for a food item based on ingredients"""
    ingredients = FOOD_INGREDIENTS.get(food_name, {})
    total_calories = 0
    ingredient_details = []
    
    for ingredient, weight_grams in ingredients.items():
        cal_per_100g = INGREDIENT_CALORIES.get(ingredient, 0)
        calories = (cal_per_100g * weight_grams) / 100
        total_calories += calories
        ingredient_details.append({
            'ingredient': ingredient,
            'weight': weight_grams,
            'calories_per_100g': cal_per_100g,
            'calories': round(calories, 2)
        })
    
    return total_calories, ingredient_details

def create_ingredient_graph(food_name, ingredients_data):
    """Create a networkx graph showing food -> ingredients relationship"""
    G = nx.DiGraph()
    
    # Add main food node
    G.add_node(food_name, node_type='food', calories=sum(item['calories'] for item in ingredients_data))
    
    # Add ingredient nodes and edges
    for item in ingredients_data:
        ingredient = item['ingredient']
        calories = item['calories']
        G.add_node(ingredient, node_type='ingredient', calories=calories, weight=item['weight'])
        G.add_edge(food_name, ingredient, weight=item['weight'])
    
    return G

def plot_ingredient_graph(G, food_name):
    """Visualize the ingredient graph using matplotlib"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Separate nodes by type
    food_nodes = [node for node, data in G.nodes(data=True) if data.get('node_type') == 'food']
    ingredient_nodes = [node for node, data in G.nodes(data=True) if data.get('node_type') == 'ingredient']
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, nodelist=food_nodes, node_color='#FF6B6B', 
                          node_size=3000, alpha=0.9, ax=ax, label='Food Item')
    nx.draw_networkx_nodes(G, pos, nodelist=ingredient_nodes, node_color='#4ECDC4', 
                          node_size=2000, alpha=0.8, ax=ax, label='Ingredients')
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                          arrowsize=20, width=2, alpha=0.6, ax=ax,
                          connectionstyle='arc3,rad=0.1')
    
    # Draw labels
    labels = {}
    for node, data in G.nodes(data=True):
        if data.get('node_type') == 'food':
            labels[node] = f"{node.replace('_', ' ').title()}\n{data['calories']:.0f} kcal"
        else:
            labels[node] = f"{node.replace('_', ' ')}\n{data['calories']:.1f} kcal\n({data['weight']}g)"
    
    nx.draw_networkx_labels(G, pos, labels, font_size=9, font_weight='bold', ax=ax)
    
    ax.set_title(f"🍴 Ingredient Flow Graph: {food_name.replace('_', ' ').title()}", 
                fontsize=16, fontweight='bold', pad=20)
    ax.axis('off')
    ax.legend(loc='upper left', fontsize=10)
    
    plt.tight_layout()
    return fig

# Title
st.title("🍔 Food Ingredient & Calorie Analyzer")
st.markdown("### Enter a food name to analyze its ingredients and calorie breakdown")

# Sidebar
with st.sidebar:
    st.header("📋 Instructions")
    st.markdown("""
    1. Enter a food name (e.g., "hamburger", "pizza")
    2. Click **Analyze** to view results
    3. Explore ingredient graph and calorie breakdown
    
    **Available Foods:**
    - hamburger, cheeseburger, bacon_burger
    - veggie_burger, chicken_burger, fish_burger
    - hot_dog, pizza, french_fries
    - club_sandwich, caesar_salad
    - sushi, tacos, pasta, grilled_salmon
    """)
    
    st.markdown("---")
    st.markdown("**Powered by Deep Learning**")
    st.markdown("*Graph-Based Nutrition Analysis*")
    st.markdown("Supervisor: Dr. Brahadeesh Sankarnarayanan")

# Main content
st.markdown("---")

# Input section
col_input, col_space = st.columns([2, 1])

with col_input:
    food_input = st.text_input(
        "🍴 Enter Food Name:",
        value="hamburger",
        placeholder="e.g., hamburger, pizza, tacos",
        help="Enter the name of the food item you want to analyze"
    )
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    with col_btn1:
        analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)
    with col_btn2:
        reset_btn = st.button("🔄 Reset", use_container_width=True)

if reset_btn:
    st.session_state.clear()
    st.rerun()

st.markdown("---")

if analyze_btn or st.session_state.get('analyzed', False):
    food_name = food_input.strip().lower().replace(' ', '_')
    
    if not food_name:
        st.error("❌ Please enter a food name")
    elif food_name not in FOOD_INGREDIENTS:
        st.error(f"❌ Food '{food_name}' not found in database. Available foods: {', '.join(FOOD_INGREDIENTS.keys())}")
    else:
        st.session_state['analyzed'] = True
        st.session_state['food_name'] = food_name
        
        # Calculate calories
        total_calories, ingredient_details = calculate_total_calories(food_name)
        
        # Create graph
        G = create_ingredient_graph(food_name, ingredient_details)
        
        # Display results
        st.success(f"✅ Analysis Complete: **{food_name.replace('_', ' ').title()}**")
        
        # Total calories metric
        col_met1, col_met2, col_met3 = st.columns(3)
        with col_met1:
            st.metric("🔥 Total Calories", f"{total_calories:.2f} kcal", 
                     help="Total calories based on all ingredients")
        with col_met2:
            st.metric("🧩 Ingredients", len(ingredient_details),
                     help="Number of ingredients in this food")
        with col_met3:
            total_weight = sum(item['weight'] for item in ingredient_details)
            st.metric("⚖️ Total Weight", f"{total_weight}g",
                     help="Total weight of all ingredients")
        
        st.markdown("---")
        
        # Two column layout for graph and table
        col_graph, col_table = st.columns([1.5, 1])
        
        with col_graph:
            st.subheader("🌐 Ingredient Flow Graph")
            fig_graph = plot_ingredient_graph(G, food_name)
            st.pyplot(fig_graph)
            plt.close()
        
        with col_table:
            st.subheader("📋 Ingredient Breakdown")
            
            # Create DataFrame
            df = pd.DataFrame(ingredient_details)
            df['ingredient'] = df['ingredient'].str.replace('_', ' ').str.title()
            df.columns = ['Ingredient', 'Weight (g)', 'Cal/100g', 'Calories']
            
            # Style the dataframe
            st.dataframe(
                df.style.background_gradient(subset=['Calories'], cmap='Reds')
                  .format({'Weight (g)': '{:.0f}', 'Cal/100g': '{:.0f}', 'Calories': '{:.2f}'}),
                use_container_width=True,
                hide_index=True
            )
            
            # Summary stats
            st.markdown("### 📊 Summary")
            highest_cal_ingredient = max(ingredient_details, key=lambda x: x['calories'])
            st.info(f"""
            **Highest Calorie Ingredient:**  
            🥇 {highest_cal_ingredient['ingredient'].replace('_', ' ').title()}  
            → {highest_cal_ingredient['calories']:.2f} kcal ({highest_cal_ingredient['weight']}g)
            """)
        
        # Visualizations
        st.markdown("---")
        st.markdown("## 📈 Interactive Visualizations")
        
        tab1, tab2, tab3 = st.tabs(["🥧 Calorie Distribution", "📊 Weight vs Calories", "🎯 Ingredient Composition"])
        
        with tab1:
            # Pie chart of calorie distribution
            df_viz = pd.DataFrame(ingredient_details)
            df_viz['ingredient'] = df_viz['ingredient'].str.replace('_', ' ').str.title()
            
            fig_pie = px.pie(
                df_viz,
                values='calories',
                names='ingredient',
                title=f'Calorie Distribution in {food_name.replace("_", " ").title()}',
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with tab2:
            # Scatter plot: weight vs calories
            fig_scatter = px.scatter(
                df_viz,
                x='weight',
                y='calories',
                size='calories',
                color='ingredient',
                title='Ingredient Weight vs Calorie Contribution',
                labels={'weight': 'Weight (g)', 'calories': 'Calories (kcal)'},
                hover_data=['calories_per_100g']
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with tab3:
            # Bar chart comparing all metrics
            fig_bar = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Calories per Ingredient', 'Weight per Ingredient'),
                specs=[[{'type': 'bar'}, {'type': 'bar'}]]
            )
            
            # Sort by calories
            df_sorted = df_viz.sort_values('calories', ascending=True)
            
            fig_bar.add_trace(
                go.Bar(
                    y=df_sorted['ingredient'],
                    x=df_sorted['calories'],
                    orientation='h',
                    marker_color='indianred',
                    name='Calories'
                ),
                row=1, col=1
            )
            
            fig_bar.add_trace(
                go.Bar(
                    y=df_sorted['ingredient'],
                    x=df_sorted['weight'],
                    orientation='h',
                    marker_color='lightseagreen',
                    name='Weight'
                ),
                row=1, col=2
            )
            
            fig_bar.update_layout(
                height=500,
                showlegend=False,
                title_text=f"Ingredient Analysis: {food_name.replace('_', ' ').title()}"
            )
            fig_bar.update_xaxes(title_text="Calories (kcal)", row=1, col=1)
            fig_bar.update_xaxes(title_text="Weight (g)", row=1, col=2)
            
            st.plotly_chart(fig_bar, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: white; padding: 20px;'>
        <p><strong>Powered by Deep Learning • Graph-Based Nutrition Analysis</strong></p>
        <p style='font-size: 0.9em;'>Supervisor: Dr. Brahadeesh Sankarnarayanan (brahadeesh@iitj.ac.in)</p>
    </div>
    """,
    unsafe_allow_html=True
)
