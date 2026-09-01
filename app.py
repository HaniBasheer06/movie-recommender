import os
import requests
import streamlit as st
from dotenv import load_dotenv, find_dotenv
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

env_path = find_dotenv()
load_dotenv(env_path)

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="IMDb Style Movie Recommender", page_icon="🎬", layout="wide")

if not API_KEY:
    st.error("TMDB_API_KEY not found. Add it in your .env file.")
    st.stop()


def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=5,
        connect=5,
        read=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 MovieRecommender/1.0",
        "Accept": "application/json"
    })
    return session


session = create_session()


def safe_get(url, params):
    try:
        response = session.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Network/API error: {e}")
        return None


def search_movies(query):
    url = f"{BASE_URL}/search/movie"
    params = {
        "api_key": API_KEY,
        "query": query,
        "language": "en-US",
        "page": 1,
        "include_adult": False
    }
    data = safe_get(url, params)
    return data.get("results", []) if data else []


def get_movie_recommendations(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/recommendations"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": 1
    }
    data = safe_get(url, params)
    return data.get("results", []) if data else []


def get_similar_movies(movie_id):
    url = f"{BASE_URL}/movie/{movie_id}/similar"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": 1
    }
    data = safe_get(url, params)
    return data.get("results", []) if data else []


def get_trending_movies():
    url = f"{BASE_URL}/trending/movie/week"
    params = {
        "api_key": API_KEY,
        "language": "en-US",
        "page": 1
    }
    data = safe_get(url, params)
    return data.get("results", []) if data else []


def get_genre_map():
    url = f"{BASE_URL}/genre/movie/list"
    params = {
        "api_key": API_KEY,
        "language": "en-US"
    }
    data = safe_get(url, params)
    if data and "genres" in data:
        return {genre["id"]: genre["name"] for genre in data["genres"]}
    return {}


def poster_url(poster_path):
    if poster_path:
        return f"{IMAGE_BASE_URL}{poster_path}"
    return None


def format_movie_label(movie):
    title = movie.get("title", "Unknown Title")
    release_date = movie.get("release_date", "")
    year = release_date[:4] if release_date else "N/A"
    return f"{title} ({year})"


def render_genre_badges(genre_ids, genre_map):
    if not genre_ids:
        return '<div class="genre-wrap"><span class="genre-badge">Unknown</span></div>'

    badges = []
    for gid in genre_ids[:3]:
        genre_name = genre_map.get(gid, "Unknown")
        badges.append(f'<span class="genre-badge">{genre_name}</span>')

    return f'<div class="genre-wrap">{" ".join(badges)}</div>'


st.markdown("""
<style>
.stApp {
    background-color: #0d0d0d;
    color: white;
}

.block-container {
    max-width: 1380px;
    padding-top: 0.8rem;
    padding-bottom: 2rem;
}

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #121212;
    border: 1px solid #232323;
    padding: 14px 22px;
    border-radius: 14px;
    margin-bottom: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 18px;
}

.logo-box {
    background: #f5c518;
    color: black;
    font-weight: 900;
    font-size: 22px;
    padding: 8px 16px;
    border-radius: 10px;
    line-height: 1;
}

.nav-item {
    color: #dddddd;
    font-size: 15px;
    font-weight: 600;
}

.nav-right {
    color: #f5c518;
    font-size: 14px;
    font-weight: 700;
}

.hero {
    background: linear-gradient(135deg, rgba(245,197,24,0.14), rgba(255,255,255,0.02)),
                linear-gradient(90deg, #181818, #101010);
    border: 1px solid #2a2a2a;
    border-radius: 22px;
    padding: 42px 36px;
    margin-bottom: 28px;
    box-shadow: 0 12px 32px rgba(0,0,0,0.28);
}

.hero-kicker {
    color: #f5c518;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 10px;
}

.hero-title {
    font-size: 52px;
    font-weight: 900;
    color: white;
    line-height: 1.05;
    margin-bottom: 14px;
}

.hero-text {
    color: #d7d7d7;
    font-size: 18px;
    max-width: 760px;
    line-height: 1.6;
    margin-bottom: 18px;
}

.hero-badges {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 12px;
}

.hero-badge {
    background: #1f1f1f;
    color: #f5c518;
    border: 1px solid #353535;
    padding: 8px 14px;
    border-radius: 999px;
    font-size: 13px;
    font-weight: 700;
}

.section-title {
    font-size: 28px;
    font-weight: 800;
    color: #f5c518;
    margin: 22px 0 14px 0;
}

.small-note {
    color: #bcbcbc;
    margin-bottom: 8px;
}

.movie-card {
    background-color: #171717;
    border: 1px solid #2a2a2a;
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 18px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.22);
    min-height: 470px;
    transition: transform 0.28s ease, box-shadow 0.28s ease, border-color 0.28s ease;
}

.movie-card:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 0 18px 30px rgba(0,0,0,0.35);
    border-color: #f5c518;
}

.movie-title {
    font-size: 18px;
    font-weight: 700;
    color: white;
    margin-top: 10px;
    margin-bottom: 6px;
}

.movie-meta {
    color: #f5c518;
    font-size: 14px;
    margin-bottom: 10px;
}

.movie-overview {
    color: #d0d0d0;
    font-size: 14px;
    line-height: 1.5;
    margin-top: 10px;
}

.genre-wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 4px;
    margin-bottom: 6px;
}

.genre-badge {
    background: rgba(245, 197, 24, 0.12);
    color: #f5c518;
    border: 1px solid rgba(245, 197, 24, 0.35);
    padding: 5px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    display: inline-block;
}

div.stButton > button {
    background-color: #f5c518;
    color: black;
    font-weight: 800;
    border-radius: 10px;
    border: none;
    padding: 0.65rem 1.3rem;
}

div.stButton > button:hover {
    background-color: #ffd54d;
    color: black;
}

[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div,
[data-testid="stRadio"] {
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="navbar">
    <div class="nav-left">
        <div class="logo-box">IMDb</div>
        <div class="nav-item">Home</div>
        <div class="nav-item">Movies</div>
        <div class="nav-item">Trending</div>
        <div class="nav-item">Top Rated</div>
        <div class="nav-item">Watchlist</div>
    </div>
    <div class="nav-right">Movie Discovery Experience</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-kicker">Find your next favorite film</div>
    <div class="hero-title">Discover movies with an IMDb-style experience</div>
    <div class="hero-text">
        Search for a film, pick the exact title, and get smart recommendations or similar movies
        with a cinematic dark interface, bold highlights, and poster-first browsing.
    </div>
    <div class="hero-badges">
        <div class="hero-badge">Live TMDb Search</div>
        <div class="hero-badge">Smart Recommendations</div>
        <div class="hero-badge">Similar Titles</div>
        <div class="hero-badge">Trending This Week</div>
    </div>
</div>
""", unsafe_allow_html=True)

genre_map = get_genre_map()

st.markdown('<div class="section-title">Search Movies</div>', unsafe_allow_html=True)
movie_query = st.text_input("Search for a movie", placeholder="Example: Interstellar")

if "search_results" not in st.session_state:
    st.session_state.search_results = []

if "trending_movies" not in st.session_state:
    st.session_state.trending_movies = get_trending_movies()

if st.button("Search"):
    if movie_query.strip():
        st.session_state.search_results = search_movies(movie_query.strip())
        if not st.session_state.search_results:
            st.warning("No movies found or network issue occurred.")
    else:
        st.warning("Please enter a movie name.")

st.markdown('<div class="section-title">Trending This Week</div>', unsafe_allow_html=True)
st.markdown('<div class="small-note">Fresh picks powered by live movie trends.</div>', unsafe_allow_html=True)

trending = st.session_state.trending_movies[:4]
trend_cols = st.columns(4)

for i, movie in enumerate(trending):
    with trend_cols[i]:
        st.markdown('<div class="movie-card">', unsafe_allow_html=True)
        img = poster_url(movie.get("poster_path"))
        if img:
            st.image(img, use_container_width=True)

        st.markdown(f'<div class="movie-title">{movie.get("title", "Unknown")}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="movie-meta">⭐ {movie.get("vote_average", "N/A")} | 📅 {movie.get("release_date", "N/A")}</div>',
            unsafe_allow_html=True
        )
        st.markdown(render_genre_badges(movie.get("genre_ids", []), genre_map), unsafe_allow_html=True)

        overview = movie.get("overview", "No overview available.")
        if len(overview) > 120:
            overview = overview[:120] + "..."
        st.markdown(f'<div class="movie-overview">{overview}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.search_results:
    options = {
        format_movie_label(movie): movie
        for movie in st.session_state.search_results[:10]
    }

    st.markdown('<div class="section-title">Selected Movie</div>', unsafe_allow_html=True)
    selected_label = st.selectbox("Choose the correct movie", list(options.keys()))
    selected_movie = options[selected_label]

    col1, col2 = st.columns([1, 2])

    with col1:
        img = poster_url(selected_movie.get("poster_path"))
        if img:
            st.image(img, use_container_width=True)

    with col2:
        st.markdown(f"### {selected_movie.get('title', 'Unknown')}")
        st.write(f"**Release Date:** {selected_movie.get('release_date', 'N/A')}")
        st.write(f"**Rating:** ⭐ {selected_movie.get('vote_average', 'N/A')}")
        st.markdown(render_genre_badges(selected_movie.get("genre_ids", []), genre_map), unsafe_allow_html=True)
        st.write(f"**Overview:** {selected_movie.get('overview', 'No overview available.')}")

    mode = st.radio(
        "Choose recommendation type",
        ["Recommendations", "Similar Movies"],
        horizontal=True
    )

    if st.button("Show Results"):
        movie_id = selected_movie["id"]

        if mode == "Recommendations":
            results = get_movie_recommendations(movie_id)
        else:
            results = get_similar_movies(movie_id)

        if not results:
            st.warning("No recommendations found or network issue occurred.")
        else:
            st.markdown(f'<div class="section-title">{mode}</div>', unsafe_allow_html=True)
            cols = st.columns(4)

            for i, movie in enumerate(results[:8]):
                with cols[i % 4]:
                    st.markdown('<div class="movie-card">', unsafe_allow_html=True)

                    img = poster_url(movie.get("poster_path"))
                    if img:
                        st.image(img, use_container_width=True)

                    st.markdown(f'<div class="movie-title">{movie.get("title", "Unknown")}</div>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="movie-meta">⭐ {movie.get("vote_average", "N/A")} | 📅 {movie.get("release_date", "N/A")}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown(render_genre_badges(movie.get("genre_ids", []), genre_map), unsafe_allow_html=True)

                    overview = movie.get("overview", "No overview available.")
                    if len(overview) > 140:
                        overview = overview[:140] + "..."

                    st.markdown(f'<div class="movie-overview">{overview}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
