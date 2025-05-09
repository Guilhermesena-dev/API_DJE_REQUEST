import time
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import math

BASE_URL = "https://comunicaapi.pje.jus.br/api/v1/comunicacao"

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

PAUSA = 0.5           # segundos entre requisições
ITEMS_PER_PAGE = 100  # itens por página

raw_items_data = {}

for empresa in empresas:
    print(f"\n=== Empresa: {empresa} ===")
    raw_items_data[empresa] = []

    # 1) primeira requisição para obter 'count'
    params0 = {
        "nomeParte":      empresa,
        "pagina":         1,
        "itensPorPagina": ITEMS_PER_PAGE
    }
    resp0 = session.get(BASE_URL, params=params0)
    resp0.raise_for_status()
    total = resp0.json().get("count", 0)
    if total == 0:
        print("Nenhum registro encontrado.")
        continue

    total_pages = math.ceil(total / ITEMS_PER_PAGE)
    print(f"Total de registros: {total} em {total_pages} página(s).")

    # 2) itera todas as páginas, sem deduplicar
    for page in range(1, total_pages + 1):
        params = {
            "nomeParte":      empresa,
            "pagina":         page,
            "itensPorPagina": ITEMS_PER_PAGE
        }
        resp = session.get(BASE_URL, params=params)
        resp.raise_for_status()
        items = resp.json().get("items", [])

        raw_items_data[empresa].extend(items)
        print(f" pág {page:>3}: +{len(items):>3} itens "
              f"(total coletado: {len(raw_items_data[empresa])})")
        time.sleep(PAUSA)

    print(f"✓ Total final para {empresa}: {len(raw_items_data[empresa])} itens")

# salva tudo num JSON
with open("itens_por_empresa.json", "w", encoding="utf-8") as f:
    json.dump(raw_items_data, f, indent=2, ensure_ascii=False)

print("\nArquivo itens_por_empresa.json gerado com sucesso!")
