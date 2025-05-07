import time
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

tribunais = (
    [f"TRT{i}" for i in range(1, 25)]
    + [f"TRF{i}" for i in range(1, 6)]
    + [f"TJ{uf}" for uf in [
        "AC","AL","AM","AP","BA","CE","DF","ES","GO","MA","MG","MS",
        "MT","PA","PB","PE","PI","PR","RJ","RN","RO","RR","RS","SC","SE","SP","TO"
    ]]
)

empresas = [
    "CONSORCIO SOLAR ENERGIA RRPM",
    "LIVRARIA PRR LTDA",
    "MASTER SOLUCOES EDUCACIONAIS LTDA",
    "MODULO ADMINISTRACAO BAIANA DE CURSOS LTDA",
    "ORGANIZACAO DE CURSOS PRE-VESTIBULAR LTDA",
    "P2R PRE-VESTIBULAR LTDA",
    "PATRIMONIAL F2R ADMINISTRAÇÃO IMOBILIÁRIA LTDA",
    "RRPM CURSOS PREPARATORIOS LTDA",
    "USINA FOTOVOLTAICA RRPM SPE LTDA"
]

# Configura sessão com retry/backoff
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    respect_retry_after_header=False
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)

MAX_PAGES = 500      # 3 × 9
PAUSA = 0.5         # segundos entre requisições

raw_items_data = {}

for empresa in empresas:
    print(f"\n=== Empresa: {empresa} ===")
    raw_items_data[empresa] = []
    seen_ids = set()

    for tribunal in tribunais:
        for page in range(1, MAX_PAGES + 1):
            params = {
                "siglaTribunal": tribunal,
                "nomeParte":     empresa,
                "pagina":        page,
                "itensPor":      100
            }

            try:
                resp = session.get(BASE_URL, params=params)
            except requests.exceptions.InvalidHeader:
                time.sleep(1)
                resp = session.get(BASE_URL, params=params)

            resp.raise_for_status()
            items = resp.json().get("items", [])

            if not items:
                break  # sai da paginação deste tribunal

            new_items = []
            for it in items:
                uid = it.get("numeroComunicacao") or it.get("numeroProcesso")
                if uid not in seen_ids:
                    seen_ids.add(uid)
                    new_items.append(it)

            raw_items_data[empresa].extend(new_items)
            print(f"{tribunal} pág {page}: +{len(new_items)} itens "
                  f"(total: {len(raw_items_data[empresa])})")

            time.sleep(PAUSA)

    print(f"✓ Total coletado para {empresa}: {len(raw_items_data[empresa])} itens")

with open("itens_por_empresa.json", "w", encoding="utf-8") as f:
    json.dump(raw_items_data, f, indent=2, ensure_ascii=False)

print("\nArquivo itens_por_empresa.json gerado com sucesso!")
