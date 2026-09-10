import requests
import streamlit as st

st.set_page_config(
    page_title="IMDb Style Movie Recommender",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE = "https://image.tmdb.org/t/p/w500"
BACKDROP_BASE = "https://image.tmdb.org/t/p/original"
FALLBACK_POSTER = "https://via.placeholder.com/500x750?text=No+Poster"

try:
    API_KEY = st.secrets["TMDB_API_KEY"]
except Exception:
    st.error("TMDB_API_KEY not found. Add it in Streamlit Secrets.")
    st.stop()

st.markdown("""
<style>
/* ===== GLOBAL THEME ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');

.stApp {
    background: radial-gradient(1200px 600px at 10% -10%, #1b2735 0%, transparent 60%),
                radial-gradient(1000px 500px at 90% -20%, #090a0f 0%, #050608 60%);
    background-color: #050608;
    color: #e6e6e6;
    font-family: 'Inter', sans-serif;
}

/* ===== HERO SECTION ===== */
.hero-section {
    padding: 40px 10px 20px 10px;
    text-align: center;
}
.hero-title {
    font-size: 48px;
    font-weight: 800;
    background: linear-gradient(90deg, #f5c518, #ffb700);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 10px;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    font-size: 18px;
    color: #b0b0b0;
    max-width: 700px;
    margin: 0 auto 20px auto;
    line-height: 1.5;
}

/* ===== SEARCH BOX ===== */
.search-container {
    max-width: 900px;
    margin: 0 auto 30px auto;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.35);
}
.search-label {
    font-weight: 600;
    color: #d0d0d0;
    margin-bottom: 8px;
    font-size: 15px;
}
.stTextInput > div > div > input {
    background-color: #0f1115 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
}
.stSelectbox > div > div {
    background-color: #0f1115 !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
}

/* ===== BUTTONS ===== */
.stButton > button {
    background: linear-gradient(90deg, #f5c518, #ffb700);
    color: #000000 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.6rem 1.2rem !important;
    font-size: 15px !important;
    box-shadow: 0 6px 18px rgba(245,197,24,0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease !important;
}
.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(245,197,24,0.35);
}

/* ===== SECTION TITLES ===== */
.section-title {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    margin: 30px 0 16px 0;
    letter-spacing: -0.3px;
}

/* ===== MOVIE CARDS ===== */
.movie-card {
    background: linear-gradient(180deg, #0f1218 0%, #0a0c10 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 10px 24px rgba(0,0,0,0.35);
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    margin-bottom: 22px;
    min-height: 720px;
    display: flex;
    flex-direction: column;
}
.movie-card:hover {
    transform: translateY(-8px) scale(1.015);
    box-shadow: 0 18px 36px rgba(0,0,0,0.5);
    border-color: rgba(245,197,24,0.35);
}
.movie-poster {
    width: 100%;
    height: 400px;
    object-fit: cover;
    display: block;
    background: #15181f;
}
.movie-content {
    padding: 14px;
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}
.movie-title {
    font-size: 19px;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.3;
    min-height: 52px;
    margin-bottom: 8px;
}
.movie-meta {
    font-size: 13px;
    color: #b8b8b8;
    margin-bottom: 10px;
}
.badges {
    margin-bottom: 12px;
}
.badge {
    display: inline-block;
    background: rgba(245,197,24,0.15);
    color: #f5c518;
    border: 1px solid rgba(245,197,24,0.35);
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin: 2px 6px 2px 0;
}
.overview {
    color: #c7c7c7;
    font-size: 13px;
    line-height: 1.5;
    margin-top: auto;
}

/* ===== DETAIL VIEW ===== */
.detail-container {
    background: linear-gradient(180deg, #0e1117 0%, #0a0c10 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 30px;
    box-shadow: 0 12px 30px rgba(0,0,0,0.4);
}
.detail-header {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-bottom: 20px;
}
.detail-poster {
    width: 220px;
    border-radius: 14px;
    object-fit: cover;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}
.detail-info {
    flex: 1;
    min-width: 260px;
}
.detail-title {
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 6px;
}
.detail-tagline {
    font-size: 16px;
    color: #b0b0b0;
    font-style: italic;
    margin-bottom: 10px;
}
.detail-meta {
    font-size: 14px;
    color: #c0c0c0;
    margin-bottom: 14px;
}
.detail-overview {
    font-size: 15px;
    color: #d0d0d0;
    line-height: 1.6;
    margin-bottom: 16px;
}
.detail-section-title {
    font-size: 18px;
    font-weight: 700;
    color: #f5c518;
    margin: 14px 0 8px 0;
}
.cast-list {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.cast-item {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    padding: 8px 12px;
    font-size: 13px;
    color: #e0e0e0;
}
.back-button {
    margin-top: 16px;
}

/* ===== RADIO BUTTONS ===== */
.stRadio > label {
    color: #d0d0d0 !important;
}
</style>
""", unsafe_allow_html=True)


# =========================
# API FUNCTIONS
# =========================

@st.cache_data(show_spinner=False)
def get_genre_map():
    url = f"{BASE_URL}/genre/movie/list"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params, timeout=20)
    data = response.json()
    return {genre["id"]: genre["name"] for genre in data.get("genres", [])}


@st.cache_data(show_spinner=False)
def search_movies(movie_title, year=None):
    params = {
        "api_key": API_KEY,
        "query": movie_title,
        "language": "en-US",
        "page": 1,
        "include_adult": False
    }
    if year:
        params["year"] = year

    response = requests.get(f"{BASE_URL}/search/movie", params=params, timeout=20)
    data = response.json()
    return data.get("results", [])


@st.cache_data(show_spinner=False)
def get_recommendations(movie_id, mode="recommendations"):
    url = f"{BASE_URL}/movie/{movie_id}/{mode}"
    params = {"api_key": API_KEY, "language": "en-US", "page": 1}
    response = requests.get(url, params=params, timeout=20)
    data = response.json()
    return data.get("results", [])


@st.cache_data(show_spinner=False)
def get_trending_movies():
    response = requests.get(
        f"{BASE_URL}/trending/movie/week",
        params={"api_key": API_KEY},
        timeout=20
    )
    data = response.json()
    return data.get("results", [])


@st.cache_data(show_spinner=False)
def get_movie_details(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "append_to_response": "credits"
    }
    response = requests.get(url, params=params, timeout=20)
    data = response.json()
    return data


@st.cache_data(show_spinner=False)
def get_movie_videos(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/videos"
    params = {"api_key": API_KEY, "language": "en-US"}
    response = requests.get(url, params=params, timeout=20)
    data = response.json()
    return data.get("results", [])


# =========================
# HELPERS
# =========================

def build_poster_url(poster_path):
    if poster_path:
        return f"{IMAGE_BASE}{poster_path}"
    return FALLBACK_POSTER


def build_backdrop_url(backdrop_path):
    if backdrop_path:
        return f"{BACKDROP_BASE}{backdrop_path}"
    return None


def safe_text(text, default="N/A"):
    if text and str(text).strip():
        return str(text)
    return default


def short_overview(text, max_len=170):
    if not text:
        return "No overview available."
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len].rsplit(" ", 1)[0] + "..."


def add_genre_names(movie_list, genre_map):
    for movie in movie_list:
        ids = movie.get("genre_ids", [])
        movie["genre_names"] = [genre_map.get(gid, "Unknown") for gid in ids[:4]]
    return movie_list


def extract_year(date_text):
    if date_text and len(date_text) >= 4:
        return date_text[:4]
    return "N/A"


def normalize_title(title):
    return safe_text(title, "").strip().lower()


def choose_best_match(results, query, year=None):
    if not results:
        return None

    query_norm = normalize_title(query)

    if year:
        exact_title_year = [
            m for m in results
            if normalize_title(m.get("title")) == query_norm and extract_year(m.get("release_date")) == str(year)
        ]
        if exact_title_year:
            return exact_title_year[0]

    exact_title = [
        m for m in results
        if normalize_title(m.get("title")) == query_norm
    ]
    if exact_title:
        return exact_title[0]

    if year:
        same_year = [
            m for m in results
            if extract_year(m.get("release_date")) == str(year)
        ]
        if same_year:
            return same_year[0]

    return results[0]


def get_youtube_trailer_key(videos):
    trailers = [
        v for v in videos
        if v.get("site") == "YouTube" and v.get("type") == "Trailer"
    ]
    if trailers:
        return trailers[0].get("key")
    return None


# =========================
# RENDERERS
# =========================

def render_movie_cards(movie_list, genre_map, columns_count=4, show_details_button=True):
    if not movie_list:
        st.warning("No movies found.")
        return

    movie_list = add_genre_names(movie_list, genre_map)
    cols = st.columns(columns_count, vertical_alignment="top")

    for i, movie in enumerate(movie_list):
        with cols[i % columns_count]:
            title = safe_text(movie.get("title"), "No title")
            poster_url = build_poster_url(movie.get("poster_path"))
            rating = movie.get("vote_average", "N/A")
            release_date = extract_year(movie.get("release_date"))
            overview = short_overview(movie.get("overview"))
            badges = "".join(
                [f"<span class='badge'>{genre}</span>" for genre in movie.get("genre_names", [])]
            )

            st.markdown(
                f"""
                <div class="movie-card">
                    <img class="movie-poster" src="{poster_url}" alt="{title}">
                    <div class="movie-content">
                        <div class="movie-title">{title}</div>
                        <div class="movie-meta">⭐ {rating} | 📅 {release_date}</div>
                        <div class="badges">{badges}</div>
                        <div class="overview">{overview}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if show_details_button:
                if st.button("View details", key=f"details_{movie['id']}"):
                    st.session_state["selected_movie_id"] = movie["id"]
                    st.rerun()


def render_movie_detail(movie_id, genre_map):
    details = get_movie_details(movie_id)
    if not details or "title" not in details:
        st.error("Failed to load movie details.")
        return

    title = safe_text(details.get("title"), "Unknown")
    tagline = details.get("tagline", "")
    overview = details.get("overview", "No overview available.")
    runtime = details.get("runtime")
    release_date = extract_year(details.get("release_date"))
    rating = details.get("vote_average", "N/A")
    status = details.get("status", "N/A")
    poster_url = build_poster_url(details.get("poster_path"))
    backdrop_url = build_backdrop_url(details.get("backdrop_path"))

    genres = details.get("genres", [])
    genre_names = [g["name"] for g in genres]

    credits = details.get("credits", {})
    cast = credits.get("cast", [])[:8]

    videos = get_movie_videos(movie_id)
    trailer_key = get_youtube_trailer_key(videos)

    st.markdown(f"""
    <div class="detail-container">
        <div class="detail-header">
            <img class="detail-poster" src="{poster_url}" alt="{title}">
            <div class="detail-info">
                <div class="detail-title">{title}</div>
                {f'<div class="detail-tagline">{tagline}</div>' if tagline else ''}
                <div class="detail-meta">
                    ⭐ {rating} | 📅 {release_date} | ⏱ {runtime if runtime else 'N/A'} min | {status}
                </div>
                <div class="badges">
                    {"".join([f"<span class='badge'>{g}</span>" for g in genre_names])}
                </div>
            </div>
        </div>

        <div class="detail-overview">{overview}</div>

        {f'''
        <div class="detail-section-title">Trailer</div>
        ''' if trailer_key else ''}
    </div>
    """, unsafe_allow_html=True)

    if trailer_key:
        st.video(f"https://www.youtube.com/watch?v={trailer_key}")

    st.markdown(f"""
    <div class="detail-section-title">Top Cast</div>
    """, unsafe_allow_html=True)

    if cast:
        cast_html = "".join(
            [f"<div class='cast-item'>{c.get('name', 'Unknown')} as {c.get('character', '')}</div>" for c in cast]
        )
        st.markdown(f"""
        <div class="cast-list">
            {cast_html}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.caption("Cast information not available.")

    if st.button("← Back to results", key="back_to_results"):
        st.session_state.pop("selected_movie_id", None)
        st.rerun()


# =========================
# MAIN UI
# =========================

st.markdown("""
<div class="hero-section">
    <div class="hero-title">🎬 IMDb Style Movie Recommender</div>
    <div class="hero-subtitle">
        Discover your next favorite film with smarter search, exact matching, and a cinematic interface.
    </div>
</div>
""", unsafe_allow_html=True)

genre_map = get_genre_map()

# If a movie is selected, show detail view
if "selected_movie_id" in st.session_state:
    render_movie_detail(st.session_state["selected_movie_id"], genre_map)
    st.markdown('<div class="section-title">More like this</div>', unsafe_allow_html=True)
    # Optionally show recommendations for this movie below detail
    recs = get_recommendations(st.session_state["selected_movie_id"], mode="recommendations")
    if recs:
        render_movie_cards(recs[:12], genre_map, columns_count=4, show_details_button=True)
    st.stop()

# Normal search + recommend flow
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    movie_name = st.text_input("", placeholder="Search movies (e.g., Inception)")

with col2:
    year_input = st.text_input("", placeholder="Year (optional)")

st.markdown('</div>', unsafe_allow_html=True)

recommendation_mode = st.radio(
    "Recommendation mode",
    ["recommendations", "similar"],
    horizontal=True
)

search_clicked = st.button("Search & Recommend", use_container_width=False)

if search_clicked:
    if not movie_name.strip():
        st.warning("Please enter a movie title.")
    else:
        parsed_year = None
        if year_input.strip().isdigit():
            parsed_year = int(year_input.strip())

        with st.spinner("Searching movies..."):
            search_results = search_movies(movie_name, parsed_year)

        if not search_results:
            st.error("No matching movie found.")
        else:
            top_results = search_results[:10]

            suggestions = []
            for movie in top_results:
                title = safe_text(movie.get("title"), "No title")
                year = extract_year(movie.get("release_date"))
                original_title = safe_text(movie.get("original_title"), title)
                label = f"{title} ({year})"
                if original_title != title:
                    label += f" • Original: {original_title}"
                suggestions.append(label)

            auto_best = choose_best_match(search_results, movie_name, parsed_year)
            auto_best_label = None
            if auto_best:
                auto_best_title = safe_text(auto_best.get("title"), "No title")
                auto_best_year = extract_year(auto_best.get("release_date"))
                auto_best_label = f"{auto_best_title} ({auto_best_year})"
                if safe_text(auto_best.get("original_title"), auto_best_title) != auto_best_title:
                    auto_best_label += f" • Original: {auto_best.get('original_title')}"

            default_index = 0
            if auto_best_label in suggestions:
                default_index = suggestions.index(auto_best_label)

            st.markdown('<div class="section-title">Select the correct movie</div>', unsafe_allow_html=True)
            selected_label = st.selectbox(
                "",
                suggestions,
                index=default_index
            )

            selected_index = suggestions.index(selected_label)
            selected_movie = top_results[selected_index]

            selected_title = safe_text(selected_movie.get("title"), "Selected movie")
            selected_year = extract_year(selected_movie.get("release_date"))

            st.markdown(
                f'<div class="section-title">Because you liked: {selected_title} ({selected_year})</div>',
                unsafe_allow_html=True
            )

            with st.spinner("Loading recommendations..."):
                recommendations = get_recommendations(selected_movie["id"], mode=recommendation_mode)

            if not recommendations:
                st.warning("No recommendations found for this movie.")
            else:
                render_movie_cards(recommendations[:12], genre_map, columns_count=4, show_details_button=True)

st.markdown('<div class="section-title">🔥 Trending This Week</div>', unsafe_allow_html=True)
with st.spinner("Loading trending movies..."):
    trending_movies = get_trending_movies()

render_movie_cards(trending_movies[:8], genre_map, columns_count=4, show_details_button=True)