import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mplcursors
from matplotlib.widgets import RectangleSelector
import json



def load_menu_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    menu_items = []
    for restaurant, dishes in data.items():
        for dish in dishes:
            menu_items.append({
                'restaurant': restaurant,
                'name': dish['name'],
                'info': dish['info'],
            })
    return menu_items

def create_embeddings(menu_items, model):
    texts = [item['info'] for item in menu_items]
    return model.encode(texts)

def cluster_menus(menu_embeddings, n_clusters=50):
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    return kmeans.fit_predict(menu_embeddings)

def find_best_cluster(user_preferences, menu_embeddings, clusters, model):
    user_embedding = model.encode([user_preferences])
    cluster_centroids = np.array([menu_embeddings[clusters == i].mean(axis=0) for i in range(max(clusters) + 1)])
    similarities = cosine_similarity(user_embedding, cluster_centroids)[0]
    return np.argmax(similarities)

def rank_dishes_in_cluster(user_preferences, menu_embeddings, menu_items, cluster_labels, best_cluster, model):
    cluster_indices = np.where(cluster_labels == best_cluster)[0]
    cluster_embeddings = menu_embeddings[cluster_indices]
    user_embedding = model.encode([user_preferences])
    
    similarities = cosine_similarity(user_embedding, cluster_embeddings)[0]
    ranked_indices = similarities.argsort()[::-1]
    
    return [(menu_items[cluster_indices[i]], similarities[i]) for i in ranked_indices]

def visualize_clusters(menu_embeddings, cluster_labels, menu_items, recommended_cluster=None):
    # Reduce dimensionality to 2D
    tsne = TSNE(n_components=2, random_state=42)
    embeddings_2d = tsne.fit_transform(menu_embeddings)

    # Create a DataFrame for easier plotting
    df = pd.DataFrame({
        'x': embeddings_2d[:, 0],
        'y': embeddings_2d[:, 1],
        'cluster': cluster_labels,
        'name': [item['name'] for item in menu_items],
        'restaurant': [item['restaurant'] for item in menu_items]
    })

    # Create the plot
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Plot non-recommended clusters
    scatter = ax.scatter(df['x'], df['y'], c=df['cluster'], cmap='tab20', alpha=0.6, s=30)
    
    # Highlight recommended cluster
    if recommended_cluster is not None:
        recommended_df = df[df['cluster'] == recommended_cluster]
        ax.scatter(recommended_df['x'], recommended_df['y'], color='red', s=100, 
                   label=f'Recommended (Cluster {recommended_cluster})')

    # Improve cluster labeling
    for cluster in df['cluster'].unique():
        cluster_points = df[df['cluster'] == cluster]
        center_x = cluster_points['x'].mean()
        center_y = cluster_points['y'].mean()
        is_recommended = cluster == recommended_cluster
        ax.annotate(f'Cluster {cluster}', (center_x, center_y),
                    xytext=(5, 5), textcoords='offset points',
                    fontweight='bold' if is_recommended else 'normal',
                    color='red' if is_recommended else 'black',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))

    ax.set_title('Menu Item Clusters (Recommended Cluster in Red)')
    ax.legend()

    # Add tooltips
    cursor = mplcursors.cursor(scatter, hover=True)
    @cursor.connect("add")
    def on_add(sel):
        index = sel.target.index
        sel.annotation.set_text(f"Dish: {df.iloc[index]['name']}\n"
                                f"Restaurant: {df.iloc[index]['restaurant']}\n"
                                f"Cluster: {df.iloc[index]['cluster']}")
        sel.annotation.get_bbox_patch().set(fc="white", alpha=0.8)

    # Implement zooming functionality
    def line_select_callback(eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        ax.set_xlim(min(x1, x2), max(x1, x2))
        ax.set_ylim(min(y1, y2), max(y1, y2))
        fig.canvas.draw_idle()

    rs = RectangleSelector(ax, line_select_callback, useblit=True,
                           button=[1, 3],  # Left and right mouse buttons
                           minspanx=5, minspany=5,
                           spancoords='pixels',
                           interactive=True)

    plt.show()

def recommend_lunches(user_preferences, data_file, model_name='paraphrase-multilingual-mpnet-base-v2', n_clusters=50):
    menu_items = load_menu_data(data_file)
    model = SentenceTransformer(model_name)
    
    menu_embeddings = create_embeddings(menu_items, model)
    cluster_labels = cluster_menus(menu_embeddings, n_clusters)
    
    best_cluster = find_best_cluster(user_preferences, menu_embeddings, cluster_labels, model)
    
    # Visualize clusters with the recommended cluster highlighted
    visualize_clusters(menu_embeddings, cluster_labels, menu_items, recommended_cluster=best_cluster)
    
    ranked_dishes = rank_dishes_in_cluster(user_preferences, menu_embeddings, menu_items, cluster_labels, best_cluster, model)
    
    print(f"Top recommendations for '{user_preferences}':")
    print(f"Recommended Cluster: {best_cluster}")
    for i, (dish, similarity) in enumerate(ranked_dishes, 1):
        print(f"{i}. {dish['name']} at {dish['restaurant']}")
        print(f"   Description: {dish['info']}")
        print(f"   Similarity score: {similarity:.4f}")
        print()


user_preferences = " Haluan kanaa tai kasvisruokaa"
recommend_lunches(user_preferences, 'menu_data_processed.json')