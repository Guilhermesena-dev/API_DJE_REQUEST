import pandas as pd
import json
import os

# Usa o diretório atual de trabalho (onde o script está sendo executado)
script_dir = os.getcwd()

# Ajuste aqui para o nome do seu arquivo JSON
json_filename = 'itens_por_empresa.json'
json_path = os.path.join(script_dir, json_filename)

if not os.path.exists(json_path):
    raise FileNotFoundError(f"Arquivo JSON não encontrado em: {json_path}")

# Carrega o JSON
with open(json_path, encoding='utf-8') as f:
    data = json.load(f)

# Flatten dos dados
rows = []
for empresa, items in data.items():
    for item in items:
        flat = {
            'empresa': empresa,
            'id': item.get('id'),
            'data_disponibilizacao': item.get('data_disponibilizacao'),
            'siglaTribunal': item.get('siglaTribunal'),
            'tipoComunicacao': item.get('tipoComunicacao'),
            'nomeOrgao': item.get('nomeOrgao'),
            'numero_processo': item.get('numero_processo'),
            'meio': item.get('meio'),
            'tipoDocumento': item.get('tipoDocumento'),
            'nomeClasse': item.get('nomeClasse'),
            'numeroComunicacao': item.get('numeroComunicacao'),
            'status': item.get('status'),
            'destinatarios': json.dumps(item.get('destinatarios', []), ensure_ascii=False),
            'destinatarioadvogados': json.dumps(item.get('destinatarioadvogados', []), ensure_ascii=False),
            'texto': item.get('texto'),
            'link': item.get('link')
        }
        rows.append(flat)

# Cria DataFrame
df = pd.DataFrame(rows)

# Salva em Excel (uma única planilha) no mesmo diretório atual
excel_filename = 'itens_por_empresa.xlsx'
output_path = os.path.join(script_dir, excel_filename)
df.to_excel(output_path, index=False, sheet_name='Dados')

print(f"Arquivo Excel gerado em: {output_path}")
