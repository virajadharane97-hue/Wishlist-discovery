import os
import sys
import json
import re
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError

# 1. Page Configuration and Theme Styling
st.set_page_config(page_title="Wishlist Discovery Engine", page_icon="🛍️", layout="wide")

# Injecting CSS to enforce color constraints and corporate styling
st.markdown("""
<style>
    /* Font Stack */
    html, body, [data-testid="stAppViewContainer"], .stText, h1, h2, h3, p, span, button, select, div {
        font-family: system-ui, -apple-system, "Segoe UI", sans-serif !important;
    }
    
    /* Reduce h1 title size slightly and increase letter spacing marginally */
    h1 {
        color: #1F4E79 !important;
        font-size: 2.2rem !important;
        letter-spacing: 0.05em !important;
        font-weight: 700 !important;
    }
    
    /* Chart section headings style */
    h3 {
        color: #1F4E79 !important;
        font-size: 1.45rem !important;
        font-weight: 600 !important;
        margin-top: 3rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Make chart captions italic and grey */
    .stCaption, div[data-testid="stCaptionContainer"] p, div[data-testid="stCaptionContainer"] span {
        font-style: italic !important;
        color: #6B7280 !important;
        font-size: 0.95rem !important;
    }
    
    /* Streamlit buttons */
    div.stButton > button {
        background-color: #1F4E79 !important;
        color: white !important;
        font-size: 16px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 10px 24px !important;
        transition: background-color 0.3s ease !important;
    }
    div.stButton > button:hover {
        background-color: #E07B39 !important;
        color: white !important;
    }
    
    /* Metrics customization */
    div[data-testid="stMetricValue"] {
        color: #E07B39 !important;
        font-weight: bold !important;
        font-size: 28px !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #1F4E79 !important;
        font-size: 16px !important;
        font-weight: 500 !important;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #F3F4F6 !important;
        border-right: 1px solid #E5E7EB !important;
    }
    
    /* Divider lines */
    hr {
        border-color: #6B7280 !important;
    }
</style>
""", unsafe_allow_html=True)

# Blocker codes list
BLOCKER_CODES = [
    "BLOCK_SIZE_SELECTION",
    "BLOCK_CHART_UNRELIABLE",
    "BLOCK_BODY_PROJECTION",
    "BLOCK_LISTING_INCOMPLETE",
    "BLOCK_FABRIC_QUALITY",
    "BLOCK_DURABILITY_VALUE",
    "BLOCK_IMAGE_DISTRUST",
    "BLOCK_REVIEW_DISTRUST",
    "BLOCK_AUTHENTICITY",
    "BLOCK_ANTICIPATED_NONUSE",
    "BLOCK_WARDROBE_SATURATION",
    "BLOCK_STYLING",
    "BLOCK_CHOICE_COMPARISON",
    "BLOCK_SOCIAL_VALIDATION",
    "BLOCK_RETURN_FRICTION"
]

# Proximity weights map
PROX_WEIGHTS = {"low": 0.5, "medium": 1.0, "high": 1.5}

# 2. Cached Data Loading
@st.cache_data
def load_data():
    try:
        df_lab = pd.read_csv("data/labelled_v3.csv")
    except Exception:
        df_lab = None
        
    try:
        df_opp = pd.read_csv("data/opportunity_scores.csv")
    except Exception:
        df_opp = None
        
    try:
        df_ev = pd.read_csv("data/evidence.csv")
    except Exception:
        df_ev = None
        
    return df_lab, df_opp, df_ev

df_lab, df_opp, df_ev = load_data()

# Handle missing files gracefully
if df_lab is None or df_opp is None or df_ev is None:
    missing = []
    if df_lab is None: missing.append("data/labelled_v3.csv")
    if df_opp is None: missing.append("data/opportunity_scores.csv")
    if df_ev is None: missing.append("data/evidence.csv")
    st.error(f"Error: Could not load the following files: {', '.join(missing)}. Please verify they exist in the repository.")
    st.stop()

# Helper to apply standard Plotly theme rules (Font size >= 14, standard colors only)
def apply_plotly_theme(fig, title_text=None):
    fig.update_layout(
        font=dict(size=14, color="#1F4E79"),
        title=dict(
            text=title_text if title_text else "",
            font=dict(size=16, color="#1F4E79")
        ),
        legend_font=dict(size=14, color="#6B7280"),
        xaxis=dict(
            title_font=dict(size=14, color="#1F4E79"),
            tickfont=dict(size=14, color="#6B7280"),
            showgrid=False
        ),
        yaxis=dict(
            title_font=dict(size=14, color="#1F4E79"),
            tickfont=dict(size=14, color="#6B7280"),
            showgrid=False
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)"
    )
    return fig


def get_gemini_api_key():
    try:
        key = st.secrets["GEMINI_API_KEY"]
        if key:
            return key
    except Exception:
        pass

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except Exception:
        pass

    key2 = os.getenv("GEMINI_API_KEY_2")
    if key2:
        return key2

    key = os.getenv("GEMINI_API_KEY")
    if key:
        return key

    return None


# 3. GLOBAL CONTROL (Sidebar)
st.sidebar.title("Global Controls")

st.sidebar.markdown("**Corpus View Toggle**")
corpus_view = st.sidebar.radio(
    "Corpus view",
    label_visibility="collapsed",
    options=[
        "Excluding anti-consumption videos (n=486)",
        "Full corpus (n=682)"
    ],
    index=0
)

st.sidebar.caption(
    "Note: 29% of the full corpus came from anti-consumption videos, "
    "which inflates two codes (BLOCK_WARDROBE_SATURATION and BLOCK_ANTICIPATED_NONUSE)."
)

# Apply global corpus view filter
if corpus_view == "Excluding anti-consumption videos (n=486)":
    df_global = df_lab[df_lab["video_context"].astype(str).str.lower().str.strip() != "anti_consumption"].copy()
else:
    df_global = df_lab.copy()

total_coded_global = df_global["primary_blocker"].notna().sum()

# Render tabs
tab1, tab2, tab3, tab4 = st.tabs(["Findings", "Evidence", "Live analysis", "How it works"])

# ==========================================
# TAB 1 — FINDINGS
# ==========================================
with tab1:
    st.header("Findings Dashboard")
    
    # Filters at the top of the tab
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sources_avail = sorted(df_global["source"].dropna().unique().tolist())
        selected_sources = st.multiselect("Filter by Source", options=sources_avail, default=None)
    with col_f2:
        contexts_avail = sorted(df_global["video_context"].dropna().unique().tolist())
        selected_contexts = st.multiselect("Filter by Video Context", options=contexts_avail, default=None)
        
    # Apply filters to current Tab 1 DataFrame
    df_tab1 = df_global.copy()
    if selected_sources:
        df_tab1 = df_tab1[df_tab1["source"].isin(selected_sources)]
    if selected_contexts:
        df_tab1 = df_tab1[df_tab1["video_context"].isin(selected_contexts)]
        
    # Compute metrics dynamically
    total_coded = df_tab1["primary_blocker"].notna().sum()
    
    if total_coded > 0:
        pb_counts = df_tab1["primary_blocker"].value_counts()
        top_blocker = pb_counts.index[0]
        top_blocker_count = pb_counts.values[0]
        top_blocker_share = (top_blocker_count / total_coded) * 100.0
        top_blocker_label = f"Top: {top_blocker}"
    else:
        top_blocker_label = "Top Blocker: None"
        top_blocker_share = 0.0
        
    # Metric cards at the top
    with st.container(border=True):
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("Raw Comments Collected", "8,861")
        with col_m2:
            st.metric("Relevant After Filtering", "682")
        with col_m3:
            st.metric("Coded Rows (Current View)", f"{total_coded}")
        with col_m4:
            st.metric(top_blocker_label, f"{top_blocker_share:.1f}%")
        
    st.divider()
    
    if total_coded == 0:
        st.warning("No coded blocker rows available for the selected filters. Please adjust your filters.")
    else:
        # --- Chart 1: Blocker Frequency (Horizontal Bar) ---
        st.subheader("Blocker Frequency Distribution")
        pb_series = df_tab1["primary_blocker"].dropna().value_counts().sort_values(ascending=True)
        colors = ["#1F4E79"] * len(pb_series)
        if len(colors) > 0:
            colors[-1] = "#E07B39" # Highlight top code in orange
            
        fig1 = go.Figure(go.Bar(
            x=pb_series.values,
            y=pb_series.index,
            orientation='h',
            marker_color=colors,
            text=pb_series.values,
            textposition='outside',
            textfont=dict(size=14, color="#1F4E79")
        ))
        fig1.update_layout(
            xaxis_title="Count of Comments",
            yaxis_title="Blocker Code",
            height=500,
            margin=dict(l=220, r=20, t=40, b=40),
            xaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
            yaxis=dict(showgrid=False)
        )
        BLOCKER_NAMES = {
            "BLOCK_SIZE_SELECTION": "Size selection",
            "BLOCK_CHART_UNRELIABLE": "Unreliable size chart",
            "BLOCK_BODY_PROJECTION": "Body projection",
            "BLOCK_LISTING_INCOMPLETE": "Incomplete listing",
            "BLOCK_FABRIC_QUALITY": "Fabric quality",
            "BLOCK_DURABILITY_VALUE": "Durability and value",
            "BLOCK_IMAGE_DISTRUST": "Image distrust",
            "BLOCK_REVIEW_DISTRUST": "Review distrust",
            "BLOCK_AUTHENTICITY": "Authenticity concerns",
            "BLOCK_ANTICIPATED_NONUSE": "Anticipated non-use",
            "BLOCK_WARDROBE_SATURATION": "Wardrobe saturation",
            "BLOCK_STYLING": "Styling concerns",
            "BLOCK_CHOICE_COMPARISON": "Choice comparison",
            "BLOCK_SOCIAL_VALIDATION": "Social validation",
            "BLOCK_RETURN_FRICTION": "Return friction"
        }
        top_blocker_clean = BLOCKER_NAMES.get(top_blocker, top_blocker)
        caption1 = f"{top_blocker_clean} is the most frequent blocker at {top_blocker_share:.1f}% of coded rows."
        apply_plotly_theme(fig1, caption1)
        st.plotly_chart(fig1, use_container_width=True, config={'displayModeBar': False})
        st.caption(caption1)
        
        st.divider()
        
        # --- Chart 2: Opportunity Matrix (Scatter) ---
        st.subheader("Opportunity Score Matrix")
        # Compute scatter values dynamically
        scatter_data = []
        for code in BLOCKER_CODES:
            df_c = df_tab1[df_tab1["primary_blocker"] == code]
            count = len(df_c)
            if count > 0:
                share = (count / total_coded) * 100.0
                avg_sev = df_c["severity_1_5"].dropna().mean()
                if pd.isna(avg_sev): avg_sev = 0.0
                
                # Proximity calculation
                low_c = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "low").sum()
                med_c = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "medium").sum()
                high_c = (df_c["conversion_proximity"].astype(str).str.lower().str.strip() == "high").sum()
                tot_p = low_c + med_c + high_c
                avg_pw = (0.5 * low_c + 1.0 * med_c + 1.5 * high_c) / tot_p if tot_p > 0 else 0.0
                
                opp_score = share * avg_sev * avg_pw
                scatter_data.append({
                    "code": code,
                    "share": share,
                    "severity": avg_sev,
                    "opp_score": opp_score
                })
        
        if scatter_data:
            df_scatter = pd.DataFrame(scatter_data)
            median_x = df_scatter["share"].median()
            median_y = df_scatter["severity"].median()
            
            # Map colors: Top code is orange, others are dark blue
            top_code_scatter = df_scatter.sort_values(by="opp_score", ascending=False).iloc[0]["code"]
            df_scatter["color"] = df_scatter["code"].apply(lambda c: "#E07B39" if c == top_code_scatter else "#1F4E79")
            
            # Size mapping
            df_scatter["marker_size"] = df_scatter["opp_score"] * 0.5 + 15
            
            fig2 = go.Figure()
            
            # Plot each trace individually to support custom text labels and colors
            for _, row in df_scatter.iterrows():
                fig2.add_trace(go.Scatter(
                    x=[row["share"]],
                    y=[row["severity"]],
                    mode="markers+text",
                    marker=dict(
                        size=[row["marker_size"]],
                        color=[row["color"]],
                        line=dict(width=1, color="white")
                    ),
                    text=[row["code"]],
                    textposition="top center",
                    textfont=dict(size=11, color="#6B7280"),
                    name=row["code"],
                    showlegend=False
                ))
                
            # Add quadrant lines
            fig2.add_vline(x=median_x, line_width=1.5, line_dash="dash", line_color="#6B7280")
            fig2.add_hline(y=median_y, line_width=1.5, line_dash="dash", line_color="#6B7280")
            
            fig2.update_layout(
                xaxis_title="Share of Coded Comments (%)",
                yaxis_title="Average Severity (1-5)",
                height=500,
                xaxis=dict(range=[0, df_scatter["share"].max() + 5], showgrid=True, gridcolor="#E5E7EB"),
                yaxis=dict(range=[1, 5], showgrid=True, gridcolor="#E5E7EB")
            )
            caption2 = "Sizing issues combine high frequency, high severity, and high purchase proximity to create the largest opportunity."
            apply_plotly_theme(fig2, caption2)
            st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar': False})
            st.caption(caption2)
        else:
            st.info("No opportunity matrix data available for this view.")
            
        st.divider()
        
        # --- Chart 3: Blocker Co-occurrence Heatmap ---
        st.subheader("Primary vs. Secondary Blocker Co-occurrence")
        df_cooc = df_tab1[df_tab1["primary_blocker"].notna()].copy()
        df_cooc["secondary_blocker"] = df_cooc["secondary_blocker"].fillna("None")
        
        ct_cooc = pd.crosstab(df_cooc["primary_blocker"], df_cooc["secondary_blocker"])
        # Ensure matrix contains at least counts
        if not ct_cooc.empty:
            fig3 = go.Figure(data=go.Heatmap(
                z=ct_cooc.values,
                x=ct_cooc.columns,
                y=ct_cooc.index,
                colorscale=[[0, 'white'], [1, '#1F4E79']],
                text=ct_cooc.values,
                texttemplate="%{text}",
                textfont={"size": 14},
                showscale=True
            ))
            fig3.update_layout(
                xaxis_title="Secondary Blocker",
                yaxis_title="Primary Blocker",
                height=500,
                xaxis=dict(tickangle=45),
                margin=dict(l=220, r=20, t=40, b=100)
            )
            caption3 = "Primary size selection blockers often co-occur with secondary fabric quality and body projection concerns."
            apply_plotly_theme(fig3, caption3)
            st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar': False})
            st.caption(caption3)
        else:
            st.info("No co-occurrence data available.")
            
        st.divider()
        
        # --- Chart 4: Blocker Share by Intent (Grouped Bar) ---
        st.subheader("Blocker Share by Purchase Intent")
        # Filter intents to exactly the three specified intents
        valid_intents = ["INTENT_GENUINE", "INTENT_OCCASION", "INTENT_ACQUISITION_WATCH"]
        
        df_intent_block = df_tab1[df_tab1["intent_code"].isin(valid_intents)].copy()
        
        # Get the top 6 blocker codes by count in the current filtered view
        top_6_blockers = df_tab1["primary_blocker"].value_counts().head(6).index.tolist()
        
        # Calculate shares
        grouped_data = []
        for intent in valid_intents:
            df_int = df_intent_block[df_intent_block["intent_code"] == intent]
            n_int_coded = df_int["primary_blocker"].notna().sum()
            if n_int_coded > 0:
                pb_counts_int = df_int["primary_blocker"].value_counts()
                for code in top_6_blockers:
                    cnt = pb_counts_int.get(code, 0)
                    share = (cnt / n_int_coded) * 100.0
                    grouped_data.append({
                        "intent_code": intent,
                        "primary_blocker": code,
                        "share": share
                    })
        
        if grouped_data:
            df_grouped = pd.DataFrame(grouped_data)
            
            fig4 = go.Figure()
            # Dedicated color mapping: dark blue, orange, grey
            intent_colors = {
                "INTENT_GENUINE": "#1F4E79",
                "INTENT_OCCASION": "#E07B39",
                "INTENT_ACQUISITION_WATCH": "#6B7280"
            }
            
            for intent in valid_intents:
                df_sub = df_grouped[df_grouped["intent_code"] == intent]
                fig4.add_trace(go.Bar(
                    x=df_sub["primary_blocker"],
                    y=df_sub["share"],
                    name=intent,
                    marker_color=intent_colors[intent]
                ))
                
            fig4.update_layout(
                xaxis_title="Blocker Code",
                yaxis_title="Share Within Intent Group (%)",
                barmode="group",
                height=500,
                xaxis=dict(tickangle=45, showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
                margin=dict(l=80, r=20, t=40, b=120)
            )
            caption4 = "Different save motivations hit different blockers: occasion savers on styling (56%), acquisition-watchers on missing listing information (90%)."
            apply_plotly_theme(fig4, caption4)
            st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar': False})
            st.caption(caption4)
        else:
            st.info("No blocker share data for valid intent groups.")
            
        st.divider()
        
        # --- Chart 5: Intent Distribution (Vertical Bar) ---
        st.subheader("Purchase Intent Distribution")
        int_series = df_tab1["intent_code"].dropna().value_counts()
        if not int_series.empty:
            fig5 = go.Figure(go.Bar(
                x=int_series.index,
                y=int_series.values,
                marker_color="#1F4E79",
                text=int_series.values,
                textposition='auto',
                textfont=dict(size=14, color="white")
            ))
            fig5.update_layout(
                xaxis_title="Intent Code",
                yaxis_title="Count of Comments",
                height=500,
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor="#E5E7EB")
            )
            caption5 = "The vast majority of wishlist items represent genuine purchase intent rather than passive price watching or inspiration."
            apply_plotly_theme(fig5, caption5)
            st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar': False})
            st.caption(caption5)
        else:
            st.info("No intent distribution data available.")

# ==========================================
# TAB 2 — EVIDENCE
# ==========================================
with tab2:
    st.header("Evidence Quotes & Testimonials")
    
    # Blocker selection dropdown
    selected_code = st.selectbox(
        "Select Blocker Code to View Verbatim Evidence",
        options=[
            "BLOCK_SIZE_SELECTION",
            "BLOCK_LISTING_INCOMPLETE",
            "BLOCK_FABRIC_QUALITY",
            "BLOCK_STYLING",
            "BLOCK_DURABILITY_VALUE",
            "BLOCK_BODY_PROJECTION"
        ]
    )
    
    # Load and prepare evidence table
    # Join with df_lab to get quote_valid if not present
    df_ev_display = df_ev.copy()
    if "quote_valid" not in df_ev_display.columns:
        df_ev_display = df_ev_display.merge(df_lab[["doc_id", "quote_valid"]], on="doc_id", how="left")
        
    # Filter: Only show rows where quote_valid is True
    df_ev_display["quote_valid_bool"] = df_ev_display["quote_valid"].astype(str).str.lower().str.strip().isin(["true", "1", "yes"])
    df_ev_filtered = df_ev_display[df_ev_display["quote_valid_bool"]].copy()
    
    # Filter to selected code
    df_ev_code = df_ev_filtered[df_ev_filtered["code"] == selected_code].copy()
    
    # Sort by severity descending
    df_ev_code["severity_1_5"] = pd.to_numeric(df_ev_code["severity_1_5"], errors="coerce")
    df_ev_code = df_ev_code.sort_values(by="severity_1_5", ascending=False)
    
    # Reorder columns
    df_display_table = df_ev_code[["evidence_quote", "severity_1_5", "external_workaround", "source", "url"]].copy()
    
    st.subheader(f"Quotes for {selected_code} (Total: {len(df_display_table)})")
    
    st.dataframe(
        df_display_table,
        column_config={
            "evidence_quote": st.column_config.TextColumn("Verbatim Quote"),
            "severity_1_5": st.column_config.NumberColumn("Severity (1-5)"),
            "external_workaround": st.column_config.TextColumn("Recorded Workaround"),
            "source": st.column_config.TextColumn("Source Platform"),
            "url": st.column_config.LinkColumn("Source Link", display_text="Open Link")
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.caption("Quotes are verbatim. 26 of 682 quotes failed a substring check against their source and were discarded.")

# ==========================================
# TAB 3 — LIVE ANALYSIS
# ==========================================
with tab3:
    st.info("💡 Note: The Gemini API free-tier has a daily quota of 500 requests.")
    st.header("Live Comment Classifier")
    st.write("Paste a customer comment or app store review below to run it through the exact qualitative coding pipeline.")
    
    user_comment = st.text_area(
        "Customer Comment / Review Text",
        placeholder="E.g., I love the design but I'm completely confused by the size chart. I measure 38 inches around the chest, but should I order Medium or Large?",
        height=150
    )
    
    classify_btn = st.button("Classify Comment")
    
    # Hardcoded fallback classification object
    fallback_json = [
        {
            "n": 1,
            "role": "seeking",
            "intent_code": "INTENT_GENUINE",
            "primary_blocker": "BLOCK_SIZE_SELECTION",
            "secondary_blocker": "BLOCK_CHART_UNRELIABLE",
            "purchase_stage": "consideration",
            "unresolved_question": "which size to choose for a slim fit given overlapping chest measurements on chart",
            "information_sought": "size",
            "external_workaround": "creator",
            "conversion_proximity": "high",
            "severity_1_5": 4,
            "confidence_1_5": 5,
            "evidence_quote": "Which size should I buy"
        }
    ]
    
    # Load codebook and compile SYSTEM_INSTRUCTION
    try:
        with open("data/codebook.json", "r", encoding="utf-8") as f:
            codebook = json.load(f)
            
        blocker_defs = []
        for c in codebook["blocker_codes"]:
            lines = [f"Code: {c['code']}", f"Definition: {c['definition']}"]
            if "use_when" in c: lines.append(f"Use When: {c['use_when']}")
            if "do_not_use_when" in c: lines.append(f"Do Not Use When: {c['do_not_use_when']}")
            blocker_defs.append("\n".join(lines))
        blocker_text = "\n\n".join(blocker_defs)

        intent_defs = []
        for c in codebook["intent_codes"]:
            lines = [f"Code: {c['code']}", f"Definition: {c['definition']}"]
            if "use_when" in c: lines.append(f"Use When: {c['use_when']}")
            if "do_not_use_when" in c: lines.append(f"Do Not Use When: {c['do_not_use_when']}")
            intent_defs.append("\n".join(lines))
        intent_text = "\n\n".join(intent_defs)

        SYSTEM_INSTRUCTION = f"""You are classifying a fashion shopping wishlist study corpus. For each comment, determine the role, intent, purchase stage, blockers, and details.

Here is the Codebook of Blocker Codes:
{blocker_text}

Here is the Codebook of Intent Codes:
{intent_text}

For each comment, return exactly this JSON structure:
{{
  "n": 1,
  "role": "seeking | advising | null",
  "intent_code": "one INTENT_* code or null",
  "primary_blocker": "one BLOCK_* code or null",
  "secondary_blocker": "one BLOCK_* code or null",
  "purchase_stage": "discovery | consideration | saved | comparison | decision | cart | post_purchase",
  "unresolved_question": "the question they still cannot answer, or null",
  "information_sought": "size | fit | fabric | styling | reviews | social_proof | alternatives | durability | authenticity | null",
  "external_workaround": "google | youtube | instagram | reddit | friends | creator | offline_store | tailor | thrift | none | null",
  "conversion_proximity": "low | medium | high",
  "severity_1_5": 3,
  "confidence_1_5": 4,
  "evidence_quote": "max 12 words, exact words from the text only"
}}

Hard rules:
- Use only what the text says. Never infer beyond it.
- Return null rather than guessing when a field is not supported.
- Never invent a code name. Only codes from the Codebook above.
- evidence_quote must be verbatim from the input, under 12 words.
- role is "advising" when the person is answering someone else's question rather than describing their own uncertainty.
- If no blocker applies, primary_blocker is null. Do not force a code.
- ROLE RULE: When role is 'advising' — the person is sharing a strategy, answering someone else's question, or giving general advice — primary_blocker must be null unless they also describe their own current unresolved uncertainty about a specific item. Their advice may still carry an intent_code and an external_workaround value.
- CONTENT REQUEST RULE: Comments asking a creator to make a video, do a haul, review a product, or cover a topic are not purchase blockers. Set primary_blocker to null. Examples: 'please make a video on shirts', 'plz bna de suit guide pe', 'do polos next'.

Return a JSON array of objects, one corresponding to each numbered comment (e.g. n matches the comment number). Return nothing else."""
    except Exception:
        SYSTEM_INSTRUCTION = None

    def show_classification_summary(item):
        if isinstance(item, list) and len(item) > 0:
            item = item[0]
        st.markdown("### Classification Summary")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.write(f"**Role:** `{item.get('role', 'null')}`")
            st.write(f"**Intent Code:** `{item.get('intent_code', 'null')}`")
            st.write(f"**Primary Blocker:** `{item.get('primary_blocker', 'null')}`")
            st.write(f"**Secondary Blocker:** `{item.get('secondary_blocker', 'null')}`")
            st.write(f"**Purchase Stage:** `{item.get('purchase_stage', 'null')}`")
        with col_s2:
            st.write(f"**Information Sought:** `{item.get('information_sought', 'null')}`")
            st.write(f"**Workaround:** `{item.get('external_workaround', 'null')}`")
            st.write(f"**Proximity / Severity:** `{item.get('conversion_proximity', 'null')}` / `{item.get('severity_1_5', 'null')}`")
            st.write(f"**Evidence Quote:** *\"{item.get('evidence_quote', 'null')}\"*")
            st.write(f"**Unresolved Question:** *\"{item.get('unresolved_question', 'null')}\"*")

    if classify_btn:
        try:
            # 1. Input preprocessing & validation
            cleaned_comment = user_comment.strip()
            if not cleaned_comment:
                raise ValueError("Empty input")

            # Truncate to 4000 characters if over 5000 characters
            if len(cleaned_comment) > 5000:
                cleaned_comment = cleaned_comment[:4000]

            # 2. Get API key safely
            api_key = get_gemini_api_key()
            if not api_key:
                raise ValueError("GEMINI_API_KEY is not configured")

            if SYSTEM_INSTRUCTION is None:
                raise ValueError("System instruction configuration error")

            # 3. Request classification
            with st.spinner("Classifying with Gemini 3.5 Flash-lite..."):
                client = genai.Client(api_key=api_key)
                prompt_text = f"1. {cleaned_comment}"
                config = types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.0
                )
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt_text,
                    config=config
                )
                resp_text = response.text.strip()
                # Clean markdown wrappers if any
                resp_text = re.sub(r"^```(?:json)?\s*", "", resp_text, flags=re.IGNORECASE)
                resp_text = re.sub(r"\s*```$", "", resp_text)
                resp_text = resp_text.strip()
                
                parsed = json.loads(resp_text)
                
                st.subheader("JSON Output")
                st.json(parsed)
                show_classification_summary(parsed)

        except Exception as e:
            st.warning("⚠️ The live classifier is currently unavailable (API key missing, quota limit reached, or invalid input). Falling back to a saved example classification.")
            st.subheader("Input Comment Used in Demo Mode:")
            st.write(f"*\"I measured my chest at 40 inches and the size chart says Medium fits 38-40 but Large fits 40-42. Which size should I buy for a slim fit?\"*")
            st.divider()
            st.subheader("JSON Output")
            st.json(fallback_json)
            show_classification_summary(fallback_json)

# ==========================================
# TAB 4 — HOW IT WORKS
# ==========================================
with tab4:
    st.header("How It Works & Methodology")
    
    st.write(
        "This engine analyses public conversations about online fashion "
        "shopping in India to identify what stops people from buying items "
        "they have saved. Sources: Google Play reviews, YouTube comments, "
        "Reddit and Quora. Collected 18 to 20 August 2026."
    )
    
    st.subheader("Seven-Stage Analysis Pipeline")
    st.markdown("""
    1. **Collect:** Gathered 8,861 raw text comments across Play Store, YouTube, Reddit and Quora.
    2. **Merge:** Deduplicated and compiled all reviews into a single merged file with standard columns: doc_id, source, date, platform_mentioned, text, url. Duplicates removed by exact text match.
    3. **Relevance Filter:** Filtered to 682 relevant comments, a 7.7% keep rate. Five filter iterations, each triggered by hand-inspecting retained or rejected rows. Play Store yielded 0.65% relevance, YouTube 14.33%.
    4. **Open Coding:** Open coding on 200 rows sampled at random, seed 55. The model was asked to describe each person's unresolved problem and invent a label for it, with no predefined category list supplied. This produced 124 unique labels, merged by hand into the final codebook. Built bottom-up from the data, not adopted from a template.
    5. **Freeze Codebook:** Formalized definitions for 15 blocker codes and 6 purchase intent codes.
    6. **Classify:** Annotated the entire corpus using Gemini 3.5 Flash-lite to extract blockers, severities, and quotes.
    7. **Validate:** 150 rows hand-labelled blind by the author with no machine labels visible. 30 of those rows independently re-labelled by a second rater. Every evidence quote tested as a contiguous substring of its source text after whitespace normalisation; 26 of 682 quotes failed and were discarded.
    """)
    
    st.divider()
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.subheader("Platform Funnel Stats")
        st.markdown(f"""
        * **Total Raw Comments:** 8,861
        * **Relevant Corpus Size:** 682 (7.7% relevant)
        * **Coded Rows (corpus view):** {total_coded_global}
        
        **Keep Rates by Source:**
        * **YouTube:** 14.33%
        * **Reddit:** 55.10%
        * **Quora:** 44.00%
        * **Play Store:** 0.65%
        
        Codebook frozen and the magnitude threshold (13.33%, twice the even-distribution baseline for 15 blocker codes) computed and recorded before any counting began.
        
        **Corpus Composition:**
        
        | Video Context | Count |
        | :--- | :---: |
        | anti_consumption | 196 |
        | haul | 145 |
        | review_comparison | 142 |
        | other | 72 |
        | not_applicable | 67 |
        | size_guide | 60 |
        
        This is why the corpus view toggle exists.
        """)
    with col_h2:
        st.subheader("Classification Agreement (Validation)")
        st.markdown("""
        | Comparison Pair | Agreement (%) | Cohen's Kappa |
        | :--- | :---: | :---: |
        | **Human vs. Machine (LLM)** | 36.0% | 0.289 |
        | **Human vs. Human (Raters)** | 46.7% | 0.413 |
        """)
        st.caption(
            "The human-human agreement figure of 46.7% (kappa 0.413) establishes that the primary "
            "source of classification ambiguity lies in the codebook definitions themselves, rather than the performance of individual raters."
        )
        
    st.divider()
    
    st.subheader("Opportunity Score & Sensitivity Analysis")
    st.markdown("**Opportunity Score = Share (%) × Average Severity × Average Proximity Weight**")
    st.write(
        "Proximity weights are a judgement (low=0.5, medium=1.0, high=1.5) mapping how close a customer's "
        "doubt is to the point of purchase."
    )
    st.info(
        "Sensitivity testing confirms that the ranking is highly robust; the same three blocker codes "
        "(BLOCK_SIZE_SELECTION, BLOCK_LISTING_INCOMPLETE, and BLOCK_FABRIC_QUALITY) hold the top three positions "
        "under four different proximity weighting schemes (baseline, proximity ignored, proximity weighted heavily, and raw share only)."
    )
    
    st.divider()
    
    # Limitations list
    st.subheader("Limitations")
    st.markdown("""
    * **Platform Bias:** The relevant corpus is heavily biased, with 88% of rows originating from YouTube, while the Play Store contributed only a 0.65% relevance rate, predominantly app, delivery and service reviews, based on manual inspection of sampled rows.
    * **Collection Artefacts:** Approximately 29% of the original relevant corpus came from decluttering and anti-consumption videos; all counts are computed twice and the anti-consumption sources are excluded, causing `BLOCK_WARDROBE_SATURATION` to drop from 37 rows to 4 when excluded.
    * **Labeling Ambiguity:** Human-machine agreement was low at 36% (kappa 0.289), but because two independent human raters agreed with each other on only 46.7% of rows (kappa 0.413), it indicates the ambiguity lies in the codebook definitions rather than the raters.
    * **Category Contamination:** `BLOCK_DURABILITY_VALUE` absorbed general price complaints instead of focusing purely on value-for-money, overstating its rank (7.19%, rank 5) and understating `INTENT_PRICE_WATCH` (22 rows).
    * **Indicative Counts:** Counts and scores are indicative rather than statistically definitive; no conclusions are drawn from share differences under 3 percentage points.
    """)

# Global Footer
st.divider()
st.caption("Concept prototype. Not affiliated with Myntra.")