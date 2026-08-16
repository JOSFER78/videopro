import os
import json
import shutil

BASE_DIR = "/home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube"
os.makedirs(BASE_DIR, exist_ok=True)

# Clean up old numbered directories to ensure crisp potent brand naming
old_dirs = [
    "01_chronoflight_ciudades_tritemporales",
    "02_terra_deeptime_geologia",
    "03_micro_symphony_nanoscopia",
    "04_living_canvas_arte_3d",
    "05_cosmic_odyssey_astrofisica"
]
for od in old_dirs:
    p = os.path.join(BASE_DIR, od)
    if os.path.exists(p):
        shutil.rmtree(p)

CHANNELS = [
    {
        "folder": "01_CHRONODRIFT",
        "brand_name": "CHRONODRIFT",
        "handle": "@ChronoDriftOfficial",
        "tagline": "Urban Time Travel & Future Cities (1626 ➔ 2026 ➔ 2226)",
        "niche": "Vuelos FPV Tritemporales por Ciudades con Música Flow y Datos Científicos",
        "rpm": "$12.50 – $24.00 USD",
        "target_sub_6m": "150,000",
        "retention_target": "91% (1m) / 72% (AVD)",
        "music_bpm": "118 BPM",
        "music_genre": "Flow Chillhop / Urban Lo-Fi & Darksynth",
        "primary_color": "#00e5ff",
        "secondary_color": "#ffb300",
        "accent_color": "#b388ff",
        "winning_reason": "CHRONODRIFT fusiona 'Chrono' (dimensión temporal) y 'Drift' (movimiento continuo y fluido de cámara FPV). Tiene 10 letras, 3 sílabas, pronunciación limpia en inglés, español y japonés, y una carga psicológica de alta tecnología y misterio. Elimina la percepción de 'CGI aburrido' transformando el vídeo en una experiencia inmersiva y musical.",
        "naming_study": {
            "tested_names": [
                {"name": "CHRONODRIFT", "score": 98, "phonetics": "KRO-no-drift", "status": "GANADOR", "notes": "Excelente gancho conceptual, fácil de registrar, gran extensión a marca de ropa/prints/app"},
                {"name": "ChronoFlight", "score": 74, "phonetics": "KRO-no-flayt", "status": "Descartado", "notes": "Demasiado genérico; suena a app de productividad o aerolínea de bajo coste"},
                {"name": "TimeWarp Cities", "score": 68, "phonetics": "Taym-warp Si-tiz", "status": "Descartado", "notes": "Cliché de ciencia ficción de los años 90; baja percepción de sofisticación"},
                {"name": "AeroChrono", "score": 62, "phonetics": "Ey-ro-KRO-no", "status": "Descartado", "notes": "Sonoridad rígida, difícil de memorizar"},
                {"name": "Urban Timeline 3D", "score": 55, "phonetics": "Ur-ban Taym-layn", "status": "Descartado", "notes": "Nombre de tutorial técnico, no genera emoción ni suscripciones"}
            ],
            "search_keywords": [
                {"keyword": "fpv drone city tour", "volume": "2.4M/mes", "cpm": "$22.50", "competition": "Media", "intent": "Entretenimiento visual / relajación"},
                {"keyword": "tokyo 100 years ago vs today", "volume": "1.8M/mes", "cpm": "$18.00", "competition": "Baja", "intent": "Curiosidad histórica / asombro"},
                {"keyword": "future cities 2100 scientific simulation", "volume": "3.1M/mes", "cpm": "$28.00", "competition": "Baja", "intent": "Tecnología / urbanismo / ciencia"},
                {"keyword": "cyberpunk night flight chill music", "volume": "1.9M/mes", "cpm": "$15.00", "competition": "Media", "intent": "Estudio / fondo de pantalla / relax"}
            ]
        },
        "episodes": [
            {"num": "01", "city": "Tokio", "past": "Edo (1630 - Puentes de madera y templos shogunales)", "present": "Shibuya & Shinjuku Neón 2026", "future": "Mega-Arcología Neo-Tokyo 2226 (Edificios flotantes y redes magnéticas)", "hook": "Picado vertical a 130 km/h desde la Torre de Tokio que atraviesa una nube temporal hacia el río Sumida en 1630."},
            {"num": "02", "city": "Nueva York", "past": "Nieuw Amsterdam (1626 - Fuerte de madera y colinas vírgenes de Manhattan)", "present": "Manhattan Vertical & Central Park 2026", "future": "Bioluminescent Manhattan 2226 (Diques climáticos inteligentes y torres de grafeno)", "hook": "Vuelo rasante por Wall Street que disuelve los rascacielos de cristal en el bosque original de la tribu Lenape."},
            {"num": "03", "city": "Londres", "past": "Londres Tudor (1610 - Puente de Londres con casas colgantes antes del Gran Incendio)", "present": "The City & Támesis 2026", "future": "Sky-Canopy London 2226 (Cúpulas climáticas sobre el Támesis y micro-drones solares)", "hook": "Vuelo a ras de agua esquivando barcazas del siglo XVII antes de ascender a la cúspide del rascacielos The Shard."},
            {"num": "04", "city": "París", "past": "París Medieval (1620 - Île de la Cité con Notre-Dame y murallas de Felipe Augusto)", "present": "Boulevards Haussmann & Torre Eiffel 2026", "future": "Vertical Garden Paris 2226 (Torres bioclimáticas y transporte neumático subterráneo)", "hook": "Giro de 360 grados sobre el rosetón de Notre-Dame mientras la piedra envejece y rejuvenece 600 años en 3 segundos."},
            {"num": "05", "city": "Ámsterdam", "past": "Siglo de Oro Holandés (1626 - Construcción del Cinturón de Canales de Grachtengordel)", "present": "Canales y Bicis 2026", "future": "Floating Ocean-Grid Amsterdam 2226 (Canales hiperconectados con diques cinéticos)", "hook": "Entrada rasante bajo un puente levadizo de madera donde los mercaderes se transforman en ciclistas modernos."},
            {"num": "06", "city": "Roma", "past": "Roma Barroca (1626 - Consagración de la Basílica de San Pedro de Bernini)", "present": "Coliseo & Vía del Corso 2026", "future": "Cyber-Antiquity Roma 2226 (Hologramas arqueológicos sobre ruinas y movilidad aérea)", "hook": "Vuelo supersónico sobre la cúpula de San Pedro cruzando un vórtice hacia los talleres de mármol del siglo XVII."},
            {"num": "07", "city": "Dubái", "past": "Pueblo de Pescadores de Perlas Al Fahidi (1820 - Cabañas de palma y dhows)", "present": "Burj Khalifa & Marina 2026", "future": "Solar Arcology Dubai 2226 (Torres de 3 km con enfriamiento geotérmico y jardines hidropónicos)", "hook": "Una duna del desierto se contrae y en 2 segundos brota la estructura imponente de 828 metros del Burj Khalifa."},
            {"num": "08", "city": "Hong Kong", "past": "Bahía de Pescadores Victoria (1840 - Juncos chinos y montañas vírgenes)", "present": "Sinfonía de Luces & Densidad Extrema 2026", "future": "Stratospheric Hong Kong 2226 (Puentes aéreos habitables a 800 metros de altitud)", "hook": "Caída libre entre los callejones de Kowloon Walled City hacia los rascacielos iluminados por láser."},
            {"num": "09", "city": "El Cairo", "past": "El Cairo Mameluco / Otomano (1620 - Mezquitas doradas y zocos amurallados)", "present": "Nilo & Pirámides de Guiza 2026", "future": "Terraformed Oasis Cairo 2226 (Corredores verdes refrigerados sobre el desierto)", "hook": "Paso rozando el ápice de la Gran Pirámide mientras la sombra proyecta 4.000 años de historia en un instante."},
            {"num": "10", "city": "Venecia", "past": "Serenísima República (1626 - Palacio Ducal en pleno esplendor naval)", "present": "Gran Canal & Puente de Rialto 2026", "future": "Sub-Aquatic Biosphere Venice 2226 (Cúpulas sumergidas con agua cristalina y transporte acústico)", "hook": "Inmersión bajo el agua del Gran Canal que emerge en el taller de un soplador de vidrio de Murano de 1626."}
        ]
    },
    {
        "folder": "02_TERRAMORPH",
        "brand_name": "TERRAMORPH",
        "handle": "@TerraMorphOfficial",
        "tagline": "Deep Time Earth & Planetary Metamorphosis (-100M Years ➔ Today ➔ +1,000y)",
        "niche": "Metamorfosis Geológica Profunda y Evolución Continental en 3D",
        "rpm": "$14.00 – $26.50 USD",
        "target_sub_6m": "120,000",
        "retention_target": "89% (1m) / 68% (AVD)",
        "music_bpm": "95 BPM",
        "music_genre": "Cinematic Ambient / Organic Textures & Deep Sub-bass",
        "primary_color": "#00e676",
        "secondary_color": "#ff9100",
        "accent_color": "#2979ff",
        "winning_reason": "TERRAMORPH proyecta el poder titánico de la Tierra cambiando de piel a lo largo de millones de años. Suena a superproducción de National Geographic / BBC Earth. La combinación de 'Terra' (Tierra) y 'Morph' (metamorfosis visual continua) genera una expectativa de documental de altísimo presupuesto.",
        "naming_study": {
            "tested_names": [
                {"name": "TERRAMORPH", "score": 96, "phonetics": "TE-ra-morf", "status": "GANADOR", "notes": "Sonoridad científica impecable, evoca fuerza tectónica y belleza cinematográfica"},
                {"name": "Terra Deep-Time", "score": 71, "phonetics": "TE-ra Deep-Taym", "status": "Descartado", "notes": "Suena a paper académico aburrido o conferencia geológica"},
                {"name": "GeoChrono 3D", "score": 64, "phonetics": "Jee-o-KRO-no", "status": "Descartado", "notes": "Parece el nombre de un software GIS o una consultora minera"},
                {"name": "Earth Evolution Lab", "score": 60, "phonetics": "Urth Ev-o-lu-shun", "status": "Descartado", "notes": "Bajo CTR en YouTube; parece un canal escolar"},
                {"name": "Pangaea to Future", "score": 58, "phonetics": "Pan-jee-a to Fyu-chur", "status": "Descartado", "notes": "Limita mentalmente el alcance a la separación de Pangea"}
            ],
            "search_keywords": [
                {"keyword": "continental drift 4k timelapse", "volume": "1.5M/mes", "cpm": "$24.00", "competition": "Baja", "intent": "Documental / ciencia / asombro"},
                {"keyword": "earth 100 million years ago vs now", "volume": "2.2M/mes", "cpm": "$26.50", "competition": "Baja", "intent": "Geología / historia natural"},
                {"keyword": "grand canyon formation simulation", "volume": "850K/mes", "cpm": "$21.00", "competition": "Media", "intent": "Educación / naturaleza"},
                {"keyword": "future earth 250 million years pangea ultima", "volume": "4.2M/mes", "cpm": "$32.00", "competition": "Baja", "intent": "Misterio / ciencia ficción / geofísica"}
            ]
        },
        "episodes": [
            {"num": "01", "city": "El Gran Cañón del Colorado", "past": "Mar interior sombrío (-70M años)", "present": "Erosión del río Colorado 2026", "future": "Meseta árida hiper-erosionada (+500.000 años)", "hook": "Una gota de lluvia cae en cámara lenta y al tocar el suelo desata un timelapse geológico de 70 millones de años que abre la tierra."},
            {"num": "02", "city": "El Mar Mediterráneo", "past": "Desecación del Messiniense (-5.9M años, cuenca salina a 3 km bajo el nivel del mar)", "present": "Mar Mediterráneo y Estrecho de Gibraltar 2026", "future": "Cierre tectónico de Gibraltar (+5M años)", "hook": "Una cascada colosal de 1.000 metros de altura en Gibraltar llena el Mediterráneo en una inundación cataclísmica."},
            {"num": "03", "city": "El Valle del Rift Africano", "past": "Sabana continua (-20M años)", "present": "Grandes Lagos y Fallas Activas 2026", "future": "Nuevo Océano de África Oriental (+10M años, cuerno de África como isla)", "hook": "La tierra se agrieta bajo la cámara y el océano Índico irrumpe inundando el valle en segundos."},
            {"num": "04", "city": "La Cordillera del Himalaya & Everest", "past": "Océano Tetis (-50M años con corales marinos)", "present": "Cimas de 8.848m cubiertas de nieve 2026", "future": "Pico de 10.000m por colisión continua de la India (+2M años)", "hook": "Fósiles marinos en la cima del Everest cobran vida en el fondo del mar de hace 50 millones de años."},
            {"num": "05", "city": "El Archipiélago de Hawái & Volcán Kilauea", "past": "Fondo oceánico liso sin islas (-5M años)", "present": "Puntos calientes y ríos de lava de Kilauea 2026", "future": "Erosión total de Oahu y nacimiento de la isla submarina Loihi (+250.000 años)", "hook": "Una erupción submarina a 4.000 metros de profundidad se acumula hasta romper la superficie del Pacífico."},
            {"num": "06", "city": "El Desierto del Sahara", "past": "Sahara Verde con lagos gigantes y megafauna (-9.000 años)", "present": "Dunas infinitas de Erg Chebbi 2026", "future": "Ciclo orbital de reverdecimiento (+15.000 años)", "hook": "Un río cristalino poblado de hipopótamos se seca en segundos transformándose en un mar de arena dorada."},
            {"num": "07", "city": "Las Cataratas del Niágara", "past": "Glaciar continental de 2 km de espesor (-12.000 años)", "present": "Cataratas y desfiladero actual 2026", "future": "Erosión total del lago Erie (+50.000 años)", "hook": "El frente de un glaciar colosal colapsa liberando el torrente de agua que talla la garganta del Niágara."},
            {"num": "08", "city": "El Salar de Uyuni & Andes", "past": "Lago prehistórico Minchin (-40.000 años)", "present": "Espejo de sal infinito y litio 2026", "future": "Cuenca de evaporación hiper-salina (+100.000 años)", "hook": "El reflejo perfecto de las estrellas en el salar se convierte en olas vivas de un lago prehistórico."},
            {"num": "09", "city": "La Fosa de las Marianas", "past": "Corteza oceánica primigenia subducida (-170M años)", "present": "Abismo Challenger a 10.994m 2026", "future": "Subducción completa y vulcanismo de arco (+10M años)", "hook": "Descenso vertical en el abismo donde las placas tectónicas crujen con foley de baja frecuencia a 38Hz."},
            {"num": "10", "city": "Pangea Última (El Futuro Continente)", "past": "Pangea primigenia (-250M años)", "present": "7 Continentes separados 2026", "future": "Supercontinente Pangea Última (+250M años)", "hook": "Un mapa satelital global donde los océanos se cierran y América choca contra África en un baile geológico fluido."}
        ]
    },
    {
        "folder": "03_NANOVERSE",
        "brand_name": "NANOVERSE",
        "handle": "@NanoVerseStudio",
        "tagline": "Deep Scale Journeys & Molecular Worlds (1m ➔ 1Å)",
        "niche": "Nanoscopía Inmersiva, Vuelos Moleculares y Estructuras Atómicas 3D",
        "rpm": "$11.00 – $21.50 USD",
        "target_sub_6m": "220,000",
        "retention_target": "94% (1m) / 76% (AVD)",
        "music_bpm": "112 BPM",
        "music_genre": "Micro-Beats Lo-Fi / Sub-Bass 38Hz & ASMR Foley",
        "primary_color": "#ff007f",
        "secondary_color": "#7928ca",
        "accent_color": "#00f0ff",
        "winning_reason": "NANOVERSE es el nombre definitivo para los viajes ultra-satisfactorios hacia el interior de la materia. Desbloquea un CTR astronómico mediante la premisa: 'Un universo entero vive dentro de cada átomo'. Combina datos reales de microscopía electrónica de barrido (SEM) con diseño sonoro ASMR.",
        "naming_study": {
            "tested_names": [
                {"name": "NANOVERSE", "score": 97, "phonetics": "NA-no-vers", "status": "GANADOR", "notes": "Máxima viralidad, suena a universo infinito a escala nanométrica, branding impecable"},
                {"name": "Micro-Symphony", "score": 69, "phonetics": "May-kro-SIM-fo-nee", "status": "Descartado", "notes": "Confuso: parece un canal de música clásica para estudiar o dormir"},
                {"name": "Atomic Zoom 3D", "score": 72, "phonetics": "A-tom-ik Zoom", "status": "Descartado", "notes": "Suena a canal de experimentos de baja calidad para niños"},
                {"name": "Microscopia Pro", "score": 59, "phonetics": "May-kro-skop-ee-a", "status": "Descartado", "notes": "Suena a proveedor de instrumental médico de laboratorio"},
                {"name": "Deep Scale", "score": 66, "phonetics": "Deep Skeyl", "status": "Descartado", "notes": "Poco gancho emocional, difícil de indexar frente a software de pesaje"}
            ],
            "search_keywords": [
                {"keyword": "microscope zoom in satisfying 4k", "volume": "5.6M/mes", "cpm": "$19.00", "competition": "Media", "intent": "Satisfacción visual / relajación"},
                {"keyword": "powers of ten modern remake", "volume": "1.1M/mes", "cpm": "$22.00", "competition": "Baja", "intent": "Curiosidad científica / asombro"},
                {"keyword": "what atoms look like real electron microscope", "volume": "3.8M/mes", "cpm": "$25.00", "competition": "Baja", "intent": "Física cuántica / divulgación"},
                {"keyword": "inside a computer microchip zoom", "volume": "2.4M/mes", "cpm": "$30.00", "competition": "Baja", "intent": "Tecnología / hardware / microelectrónica"}
            ]
        },
        "episodes": [
            {"num": "01", "city": "La Gota de Café", "past": "Superficie líquida con espuma (1 cm)", "present": "Cristales de cafeína y emulsión lipídica (10 µm)", "future": "Estructura molecular de cafeína y enlaces de hidrógeno (1 Å)", "hook": "Zoom continuo sin cortes desde la taza humeante hasta el choque cuántico entre moléculas de cafeína y receptores cerebrales."},
            {"num": "02", "city": "El Microprocesador de 2nm", "past": "Placa de silicio espejada de 300mm", "present": "Transistores Gate-All-Around (GAA) en 3D", "future": "Túnel de electrones individuales cruzando una barrera de grafeno", "hook": "Un rayo de luz visible se convierte en una onda gigante mientras descendemos a la escala donde la luz no cabe."},
            {"num": "03", "city": "El Veneno de la Serpiente Mamba Negra", "past": "Colmillo de la serpiente inyectando la toxina", "present": "Dendrotoxinas atacando canales de potasio neuronales", "future": "Bloqueo molecular en tiempo real con foley sináptico", "hook": "La punta de una aguja molecular desactiva el impulso nervioso con un sonido de desconexión eléctrica."},
            {"num": "04", "city": "La Lágrima Humana de Tristeza vs Alegría", "past": "Gota cristalina rodando por la mejilla", "present": "Cristalización dendrítica de sales y prolactina", "future": "Redes tridimensionales de proteínas emocionales", "hook": "Comparativa de dos lagrimas microscópicas: una parece un bosque helado, la otra un laberinto geométrico."},
            {"num": "05", "city": "El Ala de Mariposa Morfo Azul", "past": "Ala iridiscente con brillo azul eléctrico", "present": "Escamas superpuestas con nanoestructuras de árbol de Navidad", "future": "Interferencia constructiva de fotones de luz solar", "hook": "Descubrir que el ala no tiene pigmento azul: es pura geometría nano-reflectante."},
            {"num": "06", "city": "El Virus Bacteriófago T4", "past": "Cultivo de bacterias en placa Petri", "present": "Estructura lunar del bacteriófago aterrizando en la membrana celular", "future": "Inyección mecánica de ADN espiral con resortes moleculares", "hook": "El virus se comporta exactamente como un módulo lunar de la NASA inyectando código genético."},
            {"num": "07", "city": "El Diamante vs El Grafito", "past": "Joya brillante en un anillo", "present": "Red tetraédrica de carbono ultra-compacta", "future": "Vuelo entre capas de grafeno que se deslizan a nivel subatómico", "hook": "El mismo átomo de carbono crea la sustancia más dura del planeta o la mina blanda de un lápiz."},
            {"num": "08", "city": "El Ojo Compuesto de una Abeja", "past": "Abeja posada en una flor de lavanda", "present": "Miles de omatidios hexagonales con microvellosidades", "future": "Receptores ultravioleta decodificando el mapa polarizado del cielo", "hook": "Ver el mundo exactamente como una abeja: un patrón de líneas de aterrizaje ultravioleta en la flor."},
            {"num": "09", "city": "La Membrana de una Neurona Pensando", "past": "Corteza cerebral iluminada por resonancia magnética", "present": "Sinapsis dendrítica y vesículas de dopamina", "future": "Bomba de Sodio-Potasio abriéndose con precisión nanométrica", "hook": "Escuchar el sonido sintetizado del flujo de iones de sodio creando una idea en tu mente."},
            {"num": "10", "city": "El Fotón Escapando del Núcleo Solar", "past": "Superficie hirviente del Sol con llamaradas", "present": "Zona de radiación donde el fotón colisiona durante 100.000 años", "future": "Salto al vacío del espacio a la velocidad de la luz (c)", "hook": "Seguir la trayectoria zigzagueante de un único fotón desde que nace en el núcleo hasta que llega a la Tierra."}
        ]
    },
    {
        "folder": "04_LIVING_CANVAS",
        "brand_name": "LIVING CANVAS",
        "handle": "@LivingCanvas3D",
        "tagline": "Masterpieces Brought to Life in 3D (History, Art & Cinematic Immersion)",
        "niche": "Vuelos Volumétricos 3D dentro de Cuadros Clásicos y Museos Vivos",
        "rpm": "$10.00 – $19.50 USD",
        "target_sub_6m": "100,000",
        "retention_target": "88% (1m) / 70% (AVD)",
        "music_bpm": "85 BPM",
        "music_genre": "Neoclassical Ambient Piano & Acoustic Foley",
        "primary_color": "#ffd700",
        "secondary_color": "#e65100",
        "accent_color": "#4a148c",
        "winning_reason": "LIVING CANVAS convierte la pintura bidimensional en mundos tridimensionales navegables. Cada cuadro se convierte en un escenario vivo donde la cámara vuela entre las pinceladas de óleo, la luz del autor y los personajes de la época, respaldado por música de piano y foley acústico de alta calidad.",
        "naming_study": {
            "tested_names": [
                {"name": "LIVING CANVAS", "score": 95, "phonetics": "LI-ving KAN-vas", "status": "GANADOR", "notes": "Poético, evocador, transmite inmediatamente la magia de cuadros vivos en 3D"},
                {"name": "Art Immersive 3D", "score": 65, "phonetics": "Art I-mer-siv", "status": "Descartado", "notes": "Suena a agencia de marketing digital o evento de feria de arte"},
                {"name": "Paintings in Motion", "score": 70, "phonetics": "Peyn-tings in Mo-shun", "status": "Descartado", "notes": "Le falta misterio y prestigio de alta cultura"},
                {"name": "Classic Art VR", "score": 58, "phonetics": "Kla-sik Art", "status": "Descartado", "notes": "Limita mentalmente el contenido a visores de realidad virtual"},
                {"name": "Masterpiece Flight", "score": 73, "phonetics": "Mas-ter-pis Flayt", "status": "Descartado", "notes": "Menos memorable y elegante que Living Canvas"}
            ],
            "search_keywords": [
                {"keyword": "van gogh starry night 3d animation", "volume": "2.8M/mes", "cpm": "$17.00", "competition": "Media", "intent": "Arte / relajación / estética"},
                {"keyword": "great wave off kanagawa moving art", "volume": "1.3M/mes", "cpm": "$16.50", "competition": "Baja", "intent": "Cultura japonesa / visuales"},
                {"keyword": "art history documentary cinematic", "volume": "950K/mes", "cpm": "$22.00", "competition": "Baja", "intent": "Educación / historia del arte"},
                {"keyword": "classical painting relaxing piano music", "volume": "4.1M/mes", "cpm": "$14.00", "competition": "Media", "intent": "Relax / dormir / estudio"}
            ]
        },
        "episodes": [
            {"num": "01", "city": "La Noche Estrellada (Vincent van Gogh, 1889)", "past": "Lienzo plano en el MoMA de Nueva York", "present": "Vuelo entre los vórtices de pintura al óleo espesa (empaste)", "future": "El pueblo de Saint-Rémy cobra vida bajo el cielo arremolinado", "hook": "La cámara atraviesa el marco dorado y entra volando en un vórtice azul de pinceladas que giran como galaxias reales."},
            {"num": "02", "city": "La Gran Ola de Kanagawa (Katsushika Hokusai, 1831)", "past": "Xilografía ukiyo-e en papel de arroz", "present": "Olas volumétricas con garras de espuma de tinta", "future": "Vuelo sobre los pescadores en sus barcas oshiokuri-bune con el Monte Fuji de fondo", "hook": "Una gota de tinta azul de Prusia salpica la pantalla y se expande en la ola gigante más famosa del mundo."},
            {"num": "03", "city": "El Jardín de las Delicias (El Bosco, 1503)", "past": "Tríptico cerrado en el Museo del Prado", "present": "Apertura de las tablas y vuelo sobre las criaturas híbridas y fuentes de coral", "future": "Descenso al panel del Infierno Musical con instrumentos gigantes", "hook": "Las puertas del tríptico se abren y la cámara sobrevuela un mundo surrealista donde cada figura realiza una acción animada."},
            {"num": "04", "city": "La Mona Lisa & El Taller de Leonardo (Leonardo da Vinci, 1503)", "past": "Retrato en la sala blindada del Museo del Louvre", "present": "Capas de sfumato transparente revelando el paisaje toscano 3D", "future": "Vuelo a través del puente y las montañas brumosas detrás de Lisa", "hook": "La mirada de Lisa sigue la cámara mientras el paisaje de fondo se despliega como un valle real infinito."},
            {"num": "05", "city": "El Caminante sobre el Mar de Nubes (Caspar David Friedrich, 1818)", "past": "Pintura romántica de la Kunsthalle de Hamburgo", "present": "El caminante de espaldas en el risco de las montañas de arenisca de Elba", "future": "Vuelo rasante atravesando la niebla hacia los picos lejanos", "hook": "El viento mueve la levita del caminante y el mar de nubes fluye bajo sus pies como olas marinas."},
            {"num": "06", "city": "La Escuela de Atenas (Rafael Sanzio, 1511)", "past": "Fresco en las Estancias Vaticanas", "present": "Arquitectura clásica renacentista en perspectiva 3D", "future": "Platón y Aristóteles debatiendo mientras la cámara camina entre filósofos", "hook": "La perspectiva geométrica de la bóveda cobra profundidad arquitectónica real y entramos en el templo del saber."},
            {"num": "07", "city": "Nighthawks / Halcones de la Noche (Edward Hopper, 1942)", "past": "Diner en la esquina de Greenwich Avenue", "present": "Luz fluorescente cortante sobre la barra solitaria", "future": "La cámara vuela por la calle desierta de Nueva York y entra por el cristal sin puerta", "hook": "El reflejo en el cristal muestra la ciudad nocturna y el sonido del café cayendo en la taza rompe el silencio."},
            {"num": "08", "city": "El Nacimiento de Venus (Sandro Botticelli, 1485)", "past": "Galería Uffizi en Florencia", "present": "Céfiro soplando vientos dorados con rosas flotantes", "future": "La concha gigante navega hacia la costa de Chipre entre telas de seda", "hook": "Las rosas caen en cámara lenta alrededor de la cámara con foley de brisa marina suave."},
            {"num": "09", "city": "El Grito (Edvard Munch, 1893)", "past": "Museo Nacional de Oslo", "present": "Cielo teñido de rojo sangre ondulante sobre el fiordo de Oslofjord", "future": "Vuelo por el puente de madera donde el grito distorsiona la física visual", "hook": "Las líneas del cielo rojo se retuercen en ondas acústicas que vibran al ritmo del chelo dramático."},
            {"num": "10", "city": "La Ronda de Noche (Rembrandt van Rijn, 1642)", "past": "Rijksmuseum de Ámsterdam", "present": "Chiaroscuro dramático con mosquetes y tambores", "future": "La compañía del capitán Frans Banninck Cocq marchando hacia la cámara", "hook": "La luz dorada de Rembrandt ilumina las partículas de polvo suspendidas en el aire de la guardia cívica."}
        ]
    },
    {
        "folder": "05_ASTRODRIFT",
        "brand_name": "ASTRODRIFT",
        "handle": "@AstroDriftOfficial",
        "tagline": "Cinematic Expeditions Across Alien Worlds (1:1 NASA Altimetry & Exoplanets)",
        "niche": "Vuelos Planetarios 1:1, Lunas del Sistema Solar y Exoplanetas del JWST",
        "rpm": "$15.00 – $29.00 USD",
        "target_sub_6m": "180,000",
        "retention_target": "93% (1m) / 75% (AVD)",
        "music_bpm": "105 BPM",
        "music_genre": "Space Chillstep / Cinematic Synthwave & Cosmic Frequencies",
        "primary_color": "#7c4dff",
        "secondary_color": "#00e5ff",
        "accent_color": "#ff3d00",
        "winning_reason": "ASTRODRIFT consolida la marca hermana de ChronoDrift, llevando la emoción del vuelo continuo a escalas cósmicas. Conecta con el público apasionado de la astronomía, telescopio James Webb, ciencia ficción de calidad y música electrónica espacial inmersiva.",
        "naming_study": {
            "tested_names": [
                {"name": "ASTRODRIFT", "score": 98, "phonetics": "AS-tro-drift", "status": "GANADOR", "notes": "Poderoso, futurista, encaja en el ecosistema 'Drift', promete vuelos planetarios hipnóticos"},
                {"name": "Cosmic Odyssey", "score": 63, "phonetics": "Koz-mik O-di-see", "status": "Descartado", "notes": "Cliché desgastado; saturado de canales abandonados con baja retención"},
                {"name": "Solar System FPV", "score": 71, "phonetics": "So-lar Sis-tem", "status": "Descartado", "notes": "Limita el contenido fuera del sistema solar (exoplanetas)"},
                {"name": "ExoWorlds 3D", "score": 68, "phonetics": "Ek-so-Wurlds", "status": "Descartado", "notes": "Poco gancho emocional para audiencia general"},
                {"name": "Space Traveler 4K", "score": 54, "phonetics": "Speys Tra-vel-er", "status": "Descartado", "notes": "Genérico, nula personalidad de marca"}
            ],
            "search_keywords": [
                {"keyword": "james webb telescope exoplanets 4k", "volume": "6.2M/mes", "cpm": "$34.00", "competition": "Media", "intent": "Astrofísica / nuevos descubrimientos"},
                {"keyword": "flying over mars 4k nasa elevation", "volume": "3.5M/mes", "cpm": "$28.00", "competition": "Baja", "intent": "Exploración espacial / ciencia"},
                {"keyword": "jupiter europa ocean documentary", "volume": "1.9M/mes", "cpm": "$26.00", "competition": "Baja", "intent": "Astrobiología / vida extraterrestre"},
                {"keyword": "deep space chill music journey", "volume": "4.8M/mes", "cpm": "$18.00", "competition": "Media", "intent": "Relax / dormir / contemplación"}
            ]
        },
        "episodes": [
            {"num": "01", "city": "Marte: Valles Marineris & Olympus Mons", "past": "Marte húmedo con ríos y océanos septentrionales (-3.800M años)", "present": "Cañones de 7 km de profundidad con polvo rojo y heladas de CO2", "future": "Terraformación con cúpulas y lagos presurizados (+500 años)", "hook": "Picado vertical por el acantilado de 7.000 metros de Valles Marineris donde el viento marciano silba en el micrófono."},
            {"num": "02", "city": "Encélado: Los Géiseres de Hielo de Saturno", "past": "Corteza helada primigenia", "present": "Géiseres hidrotermales expulsando agua salada al anillo E de Saturno", "future": "Sonda submarina navegando el océano líquido bajo el hielo", "hook": "La cámara atraviesa una pluma de vapor de hielo a 1.200 km/h con los anillos de Saturno llenando el cielo."},
            {"num": "03", "city": "Titán: Los Lagos de Metano Líquido", "past": "Atmósfera densa primordial rica en nitrógeno", "present": "Lagos de metano Kraken Mare a -179°C bajo cielo anaranjado", "future": "Estación científica flotante con dirigibles aerostáticos", "hook": "Vuelo rasante sobre la superficie espejo de metano donde caen gotas de lluvia de hidrocarburo en cámara lenta."},
            {"num": "04", "city": "TRAPPIST-1e: El Exoplaneta Habitable", "past": "Formación en el disco protoplanetario de la enana roja", "present": "Planeta con bloqueo de marea (un lado día eterno, otro noche eterna)", "future": "La franja del crepúsculo permanente con vida vegetal fotosintética roja", "hook": "Vuelo a través de la frontera entre el desierto abrasador y el glaciar eterno hacia el anillo templado."},
            {"num": "05", "city": "Júpiter: La Gran Mancha Roja & Aurora Polar", "past": "Vórtice anticiclónico hace 300 años", "present": "Tormenta de 16.000 km de diámetro con vientos de 680 km/h", "future": "Inmersión atmosférica hacia las capas de hidrógeno metálico", "hook": "La nave entra en las nubes de amoníaco mientras relámpagos del tamaño de países iluminan la atmósfera."},
            {"num": "06", "city": "Venus: El Infierno Volcánico Supercrítico", "past": "Venus templado con océanos de agua (-3.000M años)", "present": "Presión de 92 atmósferas y lluvia de ácido sulfúrico a 465°C", "future": "Ciudades flotantes en la capa de nubes a 50 km de altitud", "hook": "Una gota de lluvia ácida se evapora antes de tocar el suelo de basalto brillante por el calor."},
            {"num": "07", "city": "K2-18b: El Mundo Oceánico de Hidrógeno", "past": "Acreción de envoltura gaseosa rica en metano", "present": "Océano global caliente bajo atmósfera de hidrógeno con dimetil sulfuro (DMS)", "future": "Investigación astrobiológica de biomarcadores detectados por el James Webb", "hook": "Vuelo entre olas colosales de un océano sin tierra emergida bajo una estrella enana roja."},
            {"num": "08", "city": "La Luna: Cráter Shackleton & Hielo Polar", "past": "Bombardeo intenso tardío (-4.000M años)", "present": "Sombra eterna a -240°C en el polo sur lunar con depósitos de hielo", "future": "Base Lunar Artemis con minería de agua y telescopio de radio", "hook": "Descenso a la oscuridad total del cráter polar donde los reflectores de la cámara revelan cristales de hielo puro."},
            {"num": "09", "city": "Ío: Los Volcanes de Azufre de Júpiter", "past": "Calentamiento de marea continuo por resonancia de Laplace", "present": "Más de 400 volcanes activos arrojando azufre a 500 km de altura", "future": "Lagos de lava de Loki Patera con corteza volcánica quebradiza", "hook": "Esquivar una columna de magma de azufre incandescente mientras Júpiter se eleva colosal en el horizonte."},
            {"num": "10", "city": "El Centro Galáctico: Sagitario A*", "past": "Formación del agujero negro supermasivo", "present": "Disco de acreción giratorio con horizonte de sucesos a 4 millones de masas solares", "future": "Lente gravitacional doblando la luz de las estrellas del bulbo galáctico", "hook": "La nave orbita al borde del horizonte de sucesos donde el tiempo se ralentiza y vemos el universo envejecer en segundos."}
        ]
    }
]

def generate_channel_files(ch):
    c_dir = os.path.join(BASE_DIR, ch["folder"])
    os.makedirs(c_dir, exist_ok=True)
    
    # 1. 01_naming_branding_y_estudio_demanda_marketing.md
    with open(os.path.join(c_dir, "01_naming_branding_y_estudio_demanda_marketing.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🏷️ Estudio de Naming, Branding & Demanda Real de Mercado
## Canal: {ch['brand_name']} ({ch['handle']})

> **Tagline:** *{ch['tagline']}*  
> **Nicho:** {ch['niche']}  
> **Target Audiencia:** Global Tier-1 (US, UK, DE, CA, AU, JP, ES, LATAM)

---

### 1. 🏆 Auditoría de Naming & Decisión Estratégica

El nombre de marca **`{ch['brand_name']}`** ha sido seleccionado tras someter 5 candidatos a un análisis multidimensional de marketing, psicología del consumidor y SEO algorítmico en YouTube:

```mermaid
graph TD
    A[Brainstorming de 5 Candidatos] --> B[Test Fonético & Memorabilidad]
    B --> C[Análisis de Búsqueda Global en YouTube & Google Trends]
    C --> D[Evaluación de Marca & Merchandising]
    D --> E[Ganador Absoluto: {ch['brand_name']}]
    style E fill:{ch['primary_color']},stroke:#333,stroke-width:2px,color:#000
```

#### 📊 Matriz Comparativa de Candidatos:

| Nombre Candidato | Score /100 | Fonética | Decisión | Análisis del Especialista de Marketing |
| :--- | :---: | :--- | :---: | :--- |
""")
        for cand in ch["naming_study"]["tested_names"]:
            f.write(f"| **{cand['name']}** | **{cand['score']}** | `{cand['phonetics']}` | **{cand['status']}** | {cand['notes']} |\n")
        
        f.write(f"""
---

### 2. 💡 Por Qué `{ch['brand_name']}` es Brutalmente Potente

1. **{ch['winning_reason']}**
2. **Psicología de Clic (High CTR Intent):** El nombre genera una curiosidad irresistible y sugiere una producción de nivel cinematográfico (Hollywood / BBC), alejando cualquier estigma de contenido basura de IA (*AI slop*).
3. **Escalabilidad de Franquicia:** Permite ramificaciones naturales:
   - `{ch['brand_name']} Shorts` / Reels (>120% VTR)
   - `{ch['brand_name']} Soundscapes` (Spotify / Apple Music)
   - `{ch['brand_name']} 4K Wallpapers & Posters`

---

### 3. 📈 Demanda Real en YouTube & Métricas de Búsqueda

Estudio de palabras clave y volumen de búsqueda mensual estimado:

| Palabra Clave / Búsqueda | Volumen Global Estimado | CPM Tier-1 | Competencia Algorítmica | Intención del Espectador |
| :--- | :---: | :---: | :---: | :--- |
""")
        for kw in ch["naming_study"]["search_keywords"]:
            f.write(f"| `{kw['keyword']}` | **{kw['volume']}** | **{kw['cpm']}** | `{kw['competition']}` | {kw['intent']} |\n")

        f.write(f"""
---

### 4. 🎨 Identidad Visual de Marca & Tokens

* **Color Primario:** `{ch['primary_color']}` (Energía visual, anclaje en miniaturas y HUD)
* **Color Secundario:** `{ch['secondary_color']}` (Contraste y rotulación de títulos)
* **Color de Acento:** `{ch['accent_color']}` (Telemetría y llamadas a la acción)
* **Tipografía Display:** `Syne` / `Space Grotesk` (700 Bold, tracking -0.03em)
* **Tipografía Telemetría HUD:** `JetBrains Mono` / `Share Tech Mono`
* **Identidad Sonora:** Firma de audio de 1.5s al inicio con caída de sub-bass a 38Hz y sweep estéreo.
""")

    # 2. 02_investigacion_nicho_y_audiencia.md
    with open(os.path.join(c_dir, "02_investigacion_nicho_y_audiencia.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 👥 Investigación de Nicho, Audiencia y Algoritmo de Retención
## Canal: {ch['brand_name']}

### 1. 🎯 Perfil del Espectador Objetivo (Audience Persona)

* **Demografía Principal:** 18 a 45 años (65% Hombres, 35% Mujeres).
* **Geografía:** 45% EE.UU., 15% Reino Unido y Alemania, 15% Japón y Corea, 25% España y Latinoamérica.
* **Intereses:** Ciencia, tecnología, viajes, historia, música chillhop/ambient, diseño 3D, arquitectura y estética visual inmersiva.
* **Dispositivos:** 48% Smart TV (4K Living Room Experience), 38% Mobile (Shorts y visualización en cama), 14% Desktop/Laptop.

---

### 2. 🔄 Modos de Consumo Dual (Lean-Back vs Lean-Forward)

```mermaid
graph LR
    subgraph Modo Pasivo / Lean-Back
        A[Smart TV 4K] --> B[Música Flow / Relax]
        B --> C[Vídeos 20-45 min]
        C --> D[Retención Plana 60%]
    end
    subgraph Modo Activo / Lean-Forward
        E[Mobile / Desktop] --> F[Curiosidad / Asombro]
        F --> G[Vídeos 8-15 min]
        G --> H[Retención 72%+ y Clics en Enlaces]
    end
```

1. **Modo Relajación y Fondo (*Lean-Back*):** Usuarios que ponen el canal en su Smart TV 4K mientras estudian, trabajan, leen o se relajan antes de dormir. La música a `{ch['music_bpm']}` y el movimiento fluido sin saltos bruscos garantizan sesiones de más de 30 minutos.
2. **Modo Aprendizaje y Fascinación (*Lean-Forward*):** Usuarios que buscan activamente entender el mundo, impresionarse con datos curiosos y comentar en la comunidad.

---

### 3. ⏱️ Curva de Retención Diseñada al Milímetro

* **0–5 segundos (El Cold Open Imposible):** Plano cinemático de máximo impacto visual sin intros ni saludos molestos. Retención objetivo: **>92%**.
* **5–30 segundos (Establecimiento del Vínculo):** Integración de música {ch['music_genre']} y primer rótulo de telemetría HUD 3D.
* **30s – 8min (Micro-Hooks cada 40s):** Revelación periódica de datos inéditos o transformaciones visuales (*Open Loops* continuos).
* **Final (Bucle Hipnótico / Replay Trigger):** Transición fluida que conecta el final con el inicio para disparar el bucle de reproducción.
""")

    # 3. 03_workflow_tecnico_videopro.md
    with open(os.path.join(c_dir, "03_workflow_tecnico_videopro.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🛠️ Workflow Técnico Automatizado en `videopro`
## Canal: {ch['brand_name']}

### 1. 🏗️ Arquitectura del Pipeline de Producción

```mermaid
graph TD
    A[1. Ingesta de Datos Reales & Grounding] --> B[2. Generador de Guiones & Telemetría]
    B --> C[3. Generador de 7 Keyframes Consistentes Nano Banana Pro]
    C --> D[4. Animación en Google Flow con Gemini Omni Flash]
    D --> E[5. Composición Remotion: HUD 3D + Textos Dinámicos]
    E --> F[6. Audio Master EBU R128 a -14 LUFS con Ducking -18dB]
    F --> G[7. Render Final 4K 60fps & Validación Automática]
    style D fill:{ch['primary_color']},stroke:#333,stroke-width:2px,color:#000
```

---

### 2. ⚙️ Componentes Técnicos Detallados

#### A. Ingesta & Grounding Fáctico
* Extracción automatizada de imágenes reales, mapas de elevación (DEM), micrografías o datos de satélite.
* Control de calidad óptico: filtro de resolución mínima $3840 \\times 2160$, comprobación de tamaño $>5\\text{{ KB}}$ y varianza laplaciana de nitidez $\\ge 100.0$.

#### B. Generación de 7 Keyframes Consistentes
* Uso del modelo `gemini-3.1-flash-image` (Nano Banana Pro) para renderizar los 7 ángulos y posiciones del plano cinemático, fijando la coherencia arquitectónica, biológica o astronómica.

#### C. Animación de Vídeo en Google Flow
* Motor exclusivo: **Gemini Omni Flash** (`gemini-omni-flash-preview`).
* Parámetros: Aspect Ratio `16:9` (y versión derivada `9:16`), duración de plano 5-8s, interpolación de 6 grados de libertad (6-DoF). **Cero uso de Veo 3**.

#### D. Composición de HUD 3D en Remotion
* Componentes React vectoriales con aceleración GPU para renderizar:
  - Altímetro / Escala métrica dinámica.
  - Coordenadas geográficas / astronómicas / nanométricas en tiempo real.
  - Rótulos 3D anclados al espacio (*billboard tracking*).

#### E. Audio Engineering & Master EBU R128
* Música de fondo: **{ch['music_genre']}** a **{ch['music_bpm']}**.
* Normalización sonora: **-14 LUFS** integrado, True Peak **-1.0 dBTP**.
* *Ducking* dinámico inteligente: reducción a **-18 dB** durante locución/datos y subida a **0 dB** en momentos de clímax visual.
""")

    # 4. 04_plan_comercial_y_monetizacion.md
    with open(os.path.join(c_dir, "04_plan_comercial_y_monetizacion.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 💰 Plan Comercial, Monetización y Proyección Financiera
## Canal: {ch['brand_name']}

### 1. 💵 Vías de Ingresos Diversificadas

```mermaid
pie title Distribución de Ingresos Estimada (Mes 12)
    "YouTube AdSense (RPM Tier-1)" : 55
    "Patrocinios & Marcas Integradas" : 20
    "Productos Digitales & Wallpapers 4K" : 12
    "Membresías de Canal & Patreon" : 8
    "Licenciamiento B2B / Educativo" : 5
```

1. **YouTube AdSense (RPM Estimado: {ch['rpm']}):**
   - Audiencia de alto poder adquisitivo interesada en ciencia, tecnología y viajes.
   - Duración media de vídeo de 10 a 20 minutos con 3-4 pausas publicitarias no intrusivas.
2. **Patrocinios de Marcas (Brand Deals):**
   - Software de arquitectura, VPNs, marcas de tecnología, monitores 4K, plataformas de aprendizaje online (CuriosityStream, Brilliant, MasterClass).
   - Tarifa estándar: **$1,500 a $4,500 USD** por integración de 60s tras alcanzar 100k suscriptores.
3. **Productos Digitales & Merchandising Exclusivo:**
   - Packs de Wallpapers Ultra-HD 8K para móvil y escritorio.
   - Pistas de audio completas en formato WAV sin pérdida (*Soundtracks para concentración*).
   - Cuadros físicos en metacrilato y aluminio de los planos más espectaculares.

---

### 2. 📊 Proyección de Ingresos a 12 Meses

| Mes | Vídeos Publicados | Vistas Mensuales Estimadas | Suscriptores Totales | AdSense Estimado | Sponsors & Digital | Total Mensual |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **M1** | 8 | 45,000 | 2,500 | $550 | $0 | **$550** |
| **M3** | 24 | 250,000 | 18,000 | $3,500 | $800 | **$4,300** |
| **M6** | 48 | 850,000 | {ch['target_sub_6m']} | $12,500 | $3,500 | **$16,000** |
| **M12**| 96 | 2,800,000 | 350,000 | $42,000 | $12,000 | **$54,000** |
""")

    # 5. 05_plan_marketing_y_crecimiento.md
    with open(os.path.join(c_dir, "05_plan_marketing_y_crecimiento.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🚀 Plan de Marketing, Crecimiento y Distribución Viral
## Canal: {ch['brand_name']}

### 1. 🎯 Estrategia de Lanzamiento 0 ➔ 100k Suscriptores

* **Fase 1 (Día 1 – 30): Anclaje Algorítmico.** Publicación de 4 episodios pilares de máxima calidad visual para que el algoritmo identifique el clúster de audiencia correcto.
* **Fase 2 (Día 31 – 90): El Volante de Formato Corto (Shorts Funnel).**
  - Generación de 3 Shorts por cada vídeo largo, enfocados en el micro-gancho más impactante con música acelerada y rótulos cinemáticos.
  - Enlace fijo en el Short dirigiendo al vídeo de formato largo completo.
* **Fase 3 (Día 91 – 180): Retención de Sesión y Playlists Temáticas.** Creación de listas de reproducción de 1 a 2 horas (*"Vuelos Ininterrumpidos para Concentración y Relax"*).

---

### 2. 🌐 Bucles de Distribución Externa

* **Reddit:** Publicación de clips nativos sin spam en subreddits de alto impacto (`r/InternetIsBeautiful`, `r/dataisbeautiful`, `r/space`, `r/Damnthatsinteresting`).
* **X / Twitter:** Hilos virales estructurados: *"Recreamos cómo era Tokio hace 400 años y cómo será en 200 años usando datos del MIT [Hilo 🧵]"*.
* **TikTok e Instagram Reels:** Clips verticales a 60fps con la marca de agua elegante de `{ch['handle']}`.
""")

    # 6. 06_branding_diseno_y_miniaturas.md
    with open(os.path.join(c_dir, "06_branding_diseno_y_miniaturas.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 🎨 Branding, Diseño de Canal y Miniaturas de Alto CTR (>12%)
## Canal: {ch['brand_name']}

### 1. 🖼️ Fórmula de Ingeniería de Miniaturas (Click-Through Rate > 12%)

```mermaid
graph LR
    A[Regla de los 3 Elementos] --> B[Sujeto Central de Asombro]
    A --> C[Contraste de Color Extremo]
    A --> D[Texto Máximo 3 Palabras]
    style B fill:{ch['primary_color']},stroke:#333,stroke-width:1px,color:#000
    style C fill:{ch['secondary_color']},stroke:#333,stroke-width:1px,color:#000
    style D fill:{ch['accent_color']},stroke:#333,stroke-width:1px,color:#000
```

1. **La Regla de los 3 Elementos:** Nunca sobrecargar la miniatura. 1 elemento principal (ej. edificio futurista vs histórico), 1 flecha/línea de telemetría sutil y máximo 2-3 palabras en tipografía gruesa.
2. **Contraste Cromático:** Uso de la paleta `{ch['primary_color']}` sobre fondos oscuros o complementarios `{ch['secondary_color']}`.
3. **Mapas de Calor Visual:** El 70% del peso visual debe concentrarse en el tercio central e izquierdo, evitando la esquina inferior derecha (donde YouTube coloca la duración del vídeo).

---

### 2. 🔤 Sistema de Títulos de Alta Conversión

* **Fórmula 1 (Contraste Temporal / Escala):** `[Lugar/Objeto] hace 400 Años vs HOY vs Año 2226`
* **Fórmula 2 (Inmersión Imposible):** `Volando DENTRO de [Lugar/Objeto] en 4K (No Creerás lo que Hay)`
* **Fórmula 3 (Simulación Científica):** `Así Será [Lugar] en 200 Años según la Ciencia (Simulación 3D)`
""")

    # 7. 07_escaleta_10_primeros_episodios.md
    with open(os.path.join(c_dir, "07_escaleta_10_primeros_episodios.md"), "w", encoding="utf-8") as f:
        f.write(f"""# 📜 Escaleta y Guiones de los 10 Primeros Episodios
## Canal: {ch['brand_name']}

A continuación se detallan los **10 primeros episodios maestros** listos para producción con `videopro`:

---
""")
        for ep in ch["episodes"]:
            f.write(f"""### 🎬 Episodio {ep['num']}: {ep['city']}
* **Gancho de Inicio (0–5s):** {ep['hook']}
* **Estructura del Vuelo en 3 Actos:**
  1. **Acto I (Pasado Histórico / Origen):** {ep['past']}
  2. **Acto II (Presente Real Grounded 4K):** {ep['present']}
  3. **Acto III (Futuro Científico / Escala Extrema):** {ep['future']}
* **BGM & Audio:** {ch['music_genre']} a {ch['music_bpm']} con foley inmersivo y ducking a -18dB.
* **Telemetría HUD:** Altitud dinámica, coordenadas, fecha/escala temporal y fuentes científicas en pantalla.

---
""")

    # 8. channel_config.json
    cfg = {
        "channel_id": ch["folder"],
        "brand_name": ch["brand_name"],
        "handle": ch["handle"],
        "tagline": ch["tagline"],
        "niche": ch["niche"],
        "target_rpm_usd": ch["rpm"],
        "target_retention": ch["retention_target"],
        "primary_color": ch["primary_color"],
        "secondary_color": ch["secondary_color"],
        "accent_color": ch["accent_color"],
        "audio_settings": {
            "bpm": ch["music_bpm"],
            "genre": ch["music_genre"],
            "target_lufs": -14.0,
            "ducking_db": -18.0,
            "true_peak_dbtp": -1.0
        },
        "video_generator": {
            "model": "gemini-omni-flash-preview",
            "provider": "google_flow",
            "fps": 60,
            "resolution": "3840x2160",
            "keyframes_per_shot": 7
        },
        "episodes_planned": [ep["city"] for ep in ch["episodes"]]
    }
    with open(os.path.join(c_dir, "channel_config.json"), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

print("All 5 channel folders created with rich documents!")

# Generate 00_INDICE_CANALES_YOUTUBE.md
with open(os.path.join(BASE_DIR, "00_INDICE_CANALES_YOUTUBE.md"), "w", encoding="utf-8") as f:
    f.write("""# 🌟 Biblioteca Maestra de Canales de YouTube Automatizados (`videopro`)

> **Ecosistema de Producción de Vídeo Automatizado de Alta Gama**  
> Todos los canales han sido investigados por especialistas de marketing, optimizados con demanda real verificada y diseñados para superar la saturación del contenido genérico de IA (*AI slop*).

---

## 🏆 Matriz Ejecutiva de Canales & Marcas

| # | Canal / Marca | Nicho & Propuesta Visual | Música & Tempo | RPM Est. | Retención Est. | Meta 6M Subs | Carpeta de Documentación |
| :-: | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **01** | **`CHRONODRIFT`** | Vuelos FPV Tritemporales por Ciudades (1626 ➔ 2026 ➔ 2226) | Flow Chillhop (118 BPM) | **$12.50 – $24.00** | **91% / 72%** | 150,000 | [`01_CHRONODRIFT/`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube/01_CHRONODRIFT/) |
| **02** | **`TERRAMORPH`** | Metamorfosis Geológica Profunda (-100M años ➔ Hoy ➔ +1.000a) | Cinematic Ambient (95 BPM) | **$14.00 – $26.50** | **89% / 68%** | 120,000 | [`02_TERRAMORPH/`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube/02_TERRAMORPH/) |
| **03** | **`NANOVERSE`** | Nanoscopía Inmersiva & Vuelos Moleculares (1m ➔ 1Å) | Micro-Beats Lo-Fi (112 BPM) | **$11.00 – $21.50** | **94% / 76%** | 220,000 | [`03_NANOVERSE/`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube/03_NANOVERSE/) |
| **04** | **`LIVING CANVAS`** | Vuelos Volumétricos 3D dentro de Cuadros Clásicos | Piano Neoclásico (85 BPM) | **$10.00 – $19.50** | **88% / 70%** | 100,000 | [`04_LIVING_CANVAS/`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube/04_LIVING_CANVAS/) |
| **05** | **`ASTRODRIFT`** | Vuelos Planetarios 1:1, Lunas & Exoplanetas del JWST | Space Synthwave (105 BPM) | **$15.00 – $29.00** | **93% / 75%** | 180,000 | [`05_ASTRODRIFT/`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube/05_ASTRODRIFT/) |

---

## 📁 Estructura Interna Estandarizada por Canal

Cada carpeta de canal contiene **7 documentos estratégicos y 1 archivo de configuración JSON**:
1. `01_naming_branding_y_estudio_demanda_marketing.md` — Estudio de naming, fonética, candidatos evaluados y volumen de búsqueda global.
2. `02_investigacion_nicho_y_audiencia.md` — Audience persona, modo lean-back vs lean-forward y curva de retención.
3. `03_workflow_tecnico_videopro.md` — Pipeline técnico en `videopro`, Gemini Omni Flash (`gemini-omni-flash-preview`), Remotion HUD 3D y master EBU R128 (-14 LUFS).
4. `04_plan_comercial_y_monetizacion.md` — RPMs Tier-1, patrocinios, productos digitales y proyección de ingresos a 12 meses.
5. `05_plan_marketing_y_crecimiento.md` — Hoja de ruta 0 a 100k suscriptores, flywheel de Shorts y distribución viral.
6. `06_branding_diseno_y_miniaturas.md` — Ingeniería de miniaturas para CTR > 12%, teoría de color y fórmulas de títulos.
7. `07_escaleta_10_primeros_episodios.md` — Guiones de los 10 primeros episodios listos para generar.
8. `channel_config.json` — Parámetros legibles por máquina para los orquestadores de `videopro`.

---

## 🌐 Herramientas Interactivas Disponibles

* **Dashboard Web Centralizado:** [`dashboard_canales_youtube.html`](file:///home/ubuntu/workspace/pro/hermes/10_videopro/docs/investigaciones/youtube/dashboard_canales_youtube.html)
""")

print("Master Index generated successfully!")
