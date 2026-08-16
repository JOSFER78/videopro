"""
core/youtube_niche_explorer.py — Motor de Ingesta, Scraping y Detección de Océanos Azules para VideoPro Studio
Zero Google API Keys. 100% Nativo, Rápido y Resiliente.
"""

import json
import re
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, List, Any
import streamlit as st
import pandas as pd


class YouTubeSuggestHarvester:
    """Extrae sugerencias en tiempo real mediante la API pública de autocompletado de YouTube."""
    
    BASE_URL = "https://suggestqueries.google.com/complete/search"
    
    @staticmethod
    def get_suggestions(query: str, lang: str = "es", country: str = "es") -> List[str]:
        for client in ("firefox", "chrome"):
            params = {
                "client": client,
                "ds": "yt",
                "q": query,
                "hl": lang,
                "gl": country
            }
            url = f"{YouTubeSuggestHarvester.BASE_URL}?{urllib.parse.urlencode(params)}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            }
            try:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=4.0) as resp:
                    data = json.loads(resp.read().decode('utf-8'))
                    if isinstance(data, list) and len(data) > 1 and data[1]:
                        return [item if isinstance(item, str) else item[0] for item in data[1]]
            except Exception:
                pass
        
        # Fallback a palabras clave semilla si la frase de cola larga no retorna sugerencias
        words = query.strip().split()
        if len(words) > 1:
            return YouTubeSuggestHarvester.get_suggestions(" ".join(words[:2]), lang, country)
        return []

    @classmethod
    def expand_alphabet_soup(cls, base_query: str, lang: str = "es", country: str = "es", max_chars: int = 5) -> List[Dict[str, Any]]:
        """Aplica la técnica de Sopa de Letras para encontrar micro-nichos derivados."""
        results = []
        seed_suggestions = cls.get_suggestions(base_query, lang, country)
        for s in seed_suggestions:
            results.append({"keyword": s, "tipo": "Directa", "profundidad": 0})
        
        alphabet = ['a', 'b', 'c', 'd', 'e', 'vs', '4k', '2026', 'como', 'por que']
        for char in alphabet[:max_chars]:
            extended_query = f"{base_query} {char}"
            subs = cls.get_suggestions(extended_query, lang, country)
            for sub in subs[:3]:
                if sub not in [r["keyword"] for r in results]:
                    results.append({"keyword": sub, "tipo": f"Expansión '{char}'", "profundidad": 1})
        return results


class YouTubeSearchScraper:
    """Scraper nativo de resultados de búsqueda de YouTube mediante parseo de ytInitialData."""
    
    SEARCH_URL = "https://www.youtube.com/results"
    
    @staticmethod
    def _parse_time_ago_to_days(time_str: str) -> int:
        time_str = time_str.lower()
        num_match = re.search(r'(\d+)', time_str)
        num = int(num_match.group(1)) if num_match else 1
        
        if 'hora' in time_str or 'hour' in time_str or 'minuto' in time_str or 'minute' in time_str:
            return 1
        elif 'día' in time_str or 'dia' in time_str or 'day' in time_str:
            return num
        elif 'semana' in time_str or 'week' in time_str:
            return num * 7
        elif 'mes' in time_str or 'month' in time_str:
            return num * 30
        elif 'año' in time_str or 'ano' in time_str or 'year' in time_str:
            return num * 365
        return 30

    @staticmethod
    def _parse_views_to_int(views_str: str) -> int:
        if not views_str:
            return 0
        clean = views_str.replace('.', '').replace(',', '.').upper()
        
        match_k = re.search(r'([\d\.]+)\s*K', clean)
        if match_k:
            return int(float(match_k.group(1)) * 1_000)
        
        match_m = re.search(r'([\d\.]+)\s*M', clean)
        if match_m:
            return int(float(match_m.group(1)) * 1_000_000)
            
        digits = re.sub(r'[^\d]', '', views_str)
        return int(digits) if digits else 0

    @classmethod
    def search_videos(cls, query: str, limit: int = 20, max_results: int = None) -> List[Dict[str, Any]]:
        effective_limit = max_results if max_results is not None else limit
        params = {"search_query": query}
        url = f"{cls.SEARCH_URL}?{urllib.parse.urlencode(params)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "es-ES,es;q=0.9,en;q=0.8"
        }
        
        req = urllib.request.Request(url, headers=headers)
        html_content = ""
        try:
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                html_content = resp.read().decode('utf-8', errors='ignore')
        except Exception:
            return []

        json_data = None
        patterns = [
            r'var ytInitialData\s*=\s*({.+?});</script>',
            r'window\["ytInitialData"\]\s*=\s*({.+?});',
            r'ytInitialData\s*=\s*({.+?});'
        ]
        
        for pat in patterns:
            match = re.search(pat, html_content)
            if match:
                try:
                    json_data = json.loads(match.group(1))
                    break
                except json.JSONDecodeError:
                    continue

        if not json_data:
            return []

        videos = []
        try:
            contents = json_data.get("contents", {})\
                .get("twoColumnSearchResultsRenderer", {})\
                .get("primaryContents", {})\
                .get("sectionListRenderer", {})\
                .get("contents", [])
                
            for section in contents:
                items = section.get("itemSectionRenderer", {}).get("contents", [])
                for item in items:
                    v_render = item.get("videoRenderer")
                    if not v_render:
                        continue
                    
                    video_id = v_render.get("videoId", "")
                    title = v_render.get("title", {}).get("runs", [{}])[0].get("text", "")
                    
                    views_text = v_render.get("viewCountText", {}).get("simpleText", "")
                    if not views_text and "runs" in v_render.get("viewCountText", {}):
                        views_text = "".join([r.get("text", "") for r in v_render["viewCountText"]["runs"]])
                    
                    time_text = v_render.get("publishedTimeText", {}).get("simpleText", "Reciente")
                    duration_text = v_render.get("lengthText", {}).get("simpleText", "00:00")
                    channel_name = v_render.get("ownerText", {}).get("runs", [{}])[0].get("text", "Desconocido")
                    
                    badges = []
                    for b in v_render.get("badges", []):
                        badge_label = b.get("metadataBadgeRenderer", {}).get("label", "")
                        if badge_label:
                            badges.append(badge_label)
                            
                    is_4k = any("4K" in b or "UHD" in b for b in badges)
                    views_count = cls._parse_views_to_int(views_text)
                    days_ago = cls._parse_time_ago_to_days(time_text)
                    daily_views = round(views_count / max(1, days_ago), 1)

                    videos.append({
                        "video_id": video_id,
                        "title": title,
                        "channel": channel_name,
                        "views": views_count,
                        "views_text": views_text if views_text else f"{views_count:,} vistas",
                        "days_ago": days_ago,
                        "published_text": time_text,
                        "duration": duration_text,
                        "is_4k": is_4k,
                        "daily_views": daily_views,
                        "url": f"https://www.youtube.com/watch?v={video_id}"
                    })
                    if len(videos) >= effective_limit:
                        break
                if len(videos) >= effective_limit:
                    break
        except Exception:
            pass

        return videos


class NicheOpportunityAnalyzer:
    """Calcula las métricas de Blue Ocean y genera diagnósticos estratégicos."""
    
    @classmethod
    def analyze_niche(cls, query: str, videos: List[Dict[str, Any]], suggestions: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not videos:
            return {
                "boi_score": 0,
                "demand_score": 0,
                "saturation_score": 100,
                "quality_deficit": 0,
                "category": "Sin Datos",
                "category_color": "#94a3b8",
                "avg_daily_views": 0,
                "upload_velocity_week": 0,
                "rpm_estimate": "$0.00",
                "insights": ["No se obtuvieron suficientes datos en tiempo real para este término."]
            }
            
        total_videos = len(videos)
        total_views = sum(v["views"] for v in videos)
        avg_daily = sum(v["daily_views"] for v in videos) / max(1, total_videos)
        
        sugg_count = len(suggestions)
        demand_score = min(100.0, (sugg_count * 5.0) + (avg_daily / 150.0))
        
        videos_last_7_days = sum(1 for v in videos if v["days_ago"] <= 7)
        upload_velocity_week = videos_last_7_days
        saturation_score = min(100.0, (videos_last_7_days / max(1, total_videos)) * 120.0)
        
        non_4k_ratio = sum(1 for v in videos if not v["is_4k"]) / max(1, total_videos)
        old_videos_ratio = sum(1 for v in videos if v["days_ago"] >= 365) / max(1, total_videos)
        quality_deficit = (non_4k_ratio * 50.0) + (old_videos_ratio * 50.0)
        
        small_channels_high_views = sum(1 for v in videos if v["views"] > 40000 and v["days_ago"] <= 90)
        scor_multiplier = 1.0 + min(0.30, (small_channels_high_views / max(1, total_videos)) * 0.8)
        
        raw_boi = (0.40 * demand_score + 0.35 * (100.0 - saturation_score) + 0.25 * quality_deficit) * scor_multiplier
        boi_score = max(5.0, min(98.5, round(raw_boi, 1)))
        
        if boi_score >= 75.0:
            category = "🟢 Blue Ocean Puro (Alta Oportunidad)"
            color = "#22c55e"
        elif boi_score >= 50.0:
            category = "🟡 Océano Templado (Requiere Diferenciación)"
            color = "#eab308"
        else:
            category = "🔴 Red Ocean Saturado (Alta Competencia)"
            color = "#ef4444"
            
        rpm_val = 18.50
        q_lower = query.lower()
        if any(w in q_lower for w in ["history", "historia", "space", "espacio", "science", "ciencia", "reconstruction"]):
            rpm_val = 24.50
        elif any(w in q_lower for w in ["tech", "ai", "ia", "software", "finance", "business"]):
            rpm_val = 32.00
            
        insights = []
        if quality_deficit > 60:
            insights.append(f"🎯 **Déficit de Calidad Detectado:** El {non_4k_ratio*100:.0f}% de los vídeos en el top no están en 4K UHD. La entrega 4K de VideoPro dominará el ranking.")
        if old_videos_ratio > 0.30:
            insights.append(f"⏳ **Contenido Desactualizado:** Un {old_videos_ratio*100:.0f}% de los vídeos tienen más de 1 año. El algoritmo premiará la novedad.")
        if upload_velocity_week <= 2:
            insights.append("🌊 **Baja Saturación Semanal:** Menos de 3 vídeos nuevos por semana. Ventana de entrada despejada.")
        else:
            insights.append(f"⚡ **Alta Frecuencia:** {upload_velocity_week} vídeos nuevos esta semana. Requiere miniatura y gancho tritemporal disruptivo.")

        return {
            "boi_score": boi_score,
            "demand_score": round(demand_score, 1),
            "saturation_score": round(saturation_score, 1),
            "quality_deficit": round(quality_deficit, 1),
            "category": category,
            "category_color": color,
            "avg_daily_views": int(avg_daily),
            "upload_velocity_week": upload_velocity_week,
            "rpm_estimate": f"${rpm_val:.2f}",
            "insights": insights
        }


def render_live_niche_explorer():
    """Renderiza el módulo del Explorador de Nichos en Vivo dentro de VideoPro Studio."""
    st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(30,41,59,0.7) 0%, rgba(15,23,42,0.8) 100%); 
                    border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px; margin-bottom: 20px;">
            <h3 style="color: #f8fafc; margin: 0 0 6px 0; font-size: 20px; display: flex; align-items: center; gap: 10px;">
                🔍 Explorador de Nichos YouTube en Tiempo Real
                <span style="font-size: 11px; background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); padding: 2px 8px; border-radius: 20px;">ZERO-API ENGINE</span>
            </h3>
            <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                Extracción autónoma de tendencias, velocidad de visualizaciones y cálculo cuantitativo de <strong>Blue Oceans</strong> sin consumir cuotas de Google Cloud.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    col_input, col_geo, col_btn = st.columns([6, 2, 2], vertical_alignment="bottom")
    with col_input:
        query = st.text_input("Término o Concepto Semilla:", value="Ancient Rome 4k Drone Reconstruction", placeholder="Ej: Deep Ocean Creatures 4k, Cyberpunk City Timelapse")
    with col_geo:
        geo = st.selectbox("Mercado / Idioma:", [("es", "es", "🇪🇸 España / ES"), ("en", "us", "🇺🇸 USA / Global EN"), ("de", "de", "🇩🇪 Alemania / DE")], format_func=lambda x: x[2])
    with col_btn:
        search_trigger = st.button("⚡ Explorar en Vivo", type="primary", use_container_width=True)
        
    if search_trigger or ("last_niche_data" in st.session_state and st.session_state.get("last_niche_query") == query):
        if search_trigger:
            with st.spinner("Scrapeando YouTube en vivo y procesando métricas..."):
                lang, country, _ = geo
                suggestions = YouTubeSuggestHarvester.expand_alphabet_soup(query, lang=lang, country=country, max_chars=6)
                videos = YouTubeSearchScraper.search_videos(query, limit=20)
                analysis = NicheOpportunityAnalyzer.analyze_niche(query, videos, suggestions)
                
                st.session_state["last_niche_data"] = {
                    "suggestions": suggestions,
                    "videos": videos,
                    "analysis": analysis
                }
                st.session_state["last_niche_query"] = query

        data = st.session_state.get("last_niche_data")
        if not data:
            return

        analysis = data["analysis"]
        videos = data["videos"]
        suggestions = data["suggestions"]
        
        st.markdown("#### 📊 Diagnóstico de Oportunidad de Mercado")
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        
        kpi1.metric(
            label="Blue Ocean Index (BOI)", 
            value=f"{analysis['boi_score']}/100", 
            delta=analysis["category"].split()[0] + " " + ("Óptimo" if analysis['boi_score'] >= 75 else "Competido")
        )
        kpi2.metric(
            label="Velocidad Promedio", 
            value=f"{analysis['avg_daily_views']:,} v/día", 
            delta=f"{analysis['upload_velocity_week']} vídeos nuevos/sem"
        )
        kpi3.metric(
            label="Déficit de Calidad (4K/Edad)", 
            value=f"{analysis['quality_deficit']}%", 
            delta="Oportunidad 4K" if analysis['quality_deficit'] > 50 else "Alta Calidad Existente"
        )
        kpi4.metric(
            label="RPM Estimado Tier 1", 
            value=analysis["rpm_estimate"], 
            delta="Nicho High-Yield"
        )
        
        st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.6); border-left: 4px solid {analysis['category_color']}; padding: 12px 16px; border-radius: 6px; margin: 15px 0;">
                <div style="font-weight: 700; color: {analysis['category_color']}; font-size: 14px; margin-bottom: 4px;">
                    {analysis['category']}
                </div>
                <div style="font-size: 13px; color: #cbd5e1;">
                    {'<br>'.join(analysis['insights'])}
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        tab_vids, tab_keys, tab_blueprint = st.tabs([
            "🎬 Vídeos Competidores en Vivo", 
            "🔤 Palabras Clave y Autocompletado", 
            "🚀 Blueprint de Producción VideoPro"
        ])
        
        with tab_vids:
            if videos:
                df = pd.DataFrame(videos)[["title", "channel", "views_text", "published_text", "duration", "daily_views", "is_4k", "url"]]
                df.columns = ["Título", "Canal", "Vistas", "Publicado", "Duración", "Vistas/Día", "Es 4K", "Enlace"]
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No se encontraron vídeos disponibles.")
                
        with tab_keys:
            st.markdown("##### 🌳 Árbol de Búsquedas Autocompletadas (YouTube Search Suggest)")
            c_s1, c_s2 = st.columns([1, 1])
            mid = len(suggestions) // 2
            with c_s1:
                for s in suggestions[:mid]:
                    st.markdown(f"- 🏷️ **{s['keyword']}** (`{s['tipo']}`)")
            with c_s2:
                for s in suggestions[mid:]:
                    st.markdown(f"- 🏷️ **{s['keyword']}** (`{s['tipo']}`)")
                    
        with tab_blueprint:
            st.markdown("##### 🎥 Estrategia de Dominación para VideoPro Studio")
            st.markdown(f"""
            1. **Gancho Tritemporal (0:00 - 0:45):** Iniciar con una toma aérea de reconstrucción hiperrealista utilizando **Freeze 3D** en el punto de máxima tensión dramática.
            2. **Colorimetría y Formato Master:** Exportar a **4K UHD (3840x2160) en ACEScg / DCI-P3**, superando el déficit técnico del {analysis['quality_deficit']}% de los competidores actuales.
            3. **Diseño Sonoro Espacial:** Mezcla de efectos de sonido binaurales (foley de viento, multitudes, resonancia acústica) masterizada a **-14 LUFS** estricto bajo norma EBU R128.
            4. **Estructura de Retención:** Insertar 2 pausas de retención orgánica para mid-rolls en los minutos 4:15 y 8:30 sincronizadas con cambios de era en Remotion.
            """)
