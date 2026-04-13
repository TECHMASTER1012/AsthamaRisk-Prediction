import plotly.graph_objects as go

def plot_time_series(df, y_col, title, color):
    fig = go.Figure()
    
    # Convert hex to rgba for fillcolor compatibility
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    fill_color = f"rgba({r}, {g}, {b}, 0.2)"

    # Create the area gradient by using fill='tozeroy'
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df[y_col],
        mode='lines',
        name=title,
        line=dict(color=color, width=3, shape='spline'),
        fill='tozeroy',
        fillcolor=fill_color,
        hovertemplate="<b>%{x}</b><br>%{y:.2f}<extra></extra>"
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(family="Inter, sans-serif", size=16, color="#FAFAFA")),
        xaxis=dict(showgrid=False, zeroline=False, visible=False),
        yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', zeroline=False),
        template="plotly_dark",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        height=280,
        hovermode="x unified"
    )
    return fig
