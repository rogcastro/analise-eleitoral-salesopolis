import os
import unicodedata
import pandas as pd

MAPA_NUMEROS_HISTORICO = {
    13: 'PT', 22: 'PL', 45: 'PSDB', 15: 'MDB', 11: 'PP', 25: 'DEM', 12: 'PDT',
    40: 'PSB', 50: 'PSOL', 65: 'PC DO B', 18: 'REDE', 30: 'NOVO', 55: 'PSD',
    10: 'REPUBLICANOS', 14: 'PTB', 19: 'PODEMOS', 20: 'PSC', 23: 'CIDADANIA',
    43: 'PV', 51: 'PATRIOTA', 70: 'AVANTE', 77: 'SOLIDARIEDADE', 28: 'PRTB',
    17: 'PSL', 16: 'PSTU', 29: 'PCO', 21: 'PCB', 27: 'DC', 31: 'PHS',
    33: 'PMN', 35: 'PMB', 36: 'PTC', 44: 'UNIÃO', 54: 'PPL', 56: 'PRONA'
}

VALORES_DESCARTE = [
    'BRANCO', 'NULO', 'VOTO BRANCO', 'VOTO NULO', 'VOTOS BRANCOS', 'VOTOS NULOS',
    '#NULO#', '#NE#', '95', '96', 'NONE', 'NAN', ''
]

def remover_acentos(texto):
    if not isinstance(texto, str):
        return str(texto)
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def extrair_numero_partido(val):
    if pd.isna(val):
        return None
    val_str = str(val).split('.')[0].strip()
    if not val_str.isdigit():
        return None
    if val_str in ['95', '96']:
        return None
    if len(val_str) >= 2:
        return int(val_str[:2])
    elif len(val_str) == 1:
        return int(val_str)
    return None

def extrair_presidente():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'scripts' else script_dir
    caminho_brutos = os.path.join(base_dir, 'dados_brutos')

    if not os.path.exists(caminho_brutos):
        print(f"Erro: A pasta '{caminho_brutos}' não foi encontrada.")
        return

    arquivos = [
        f for f in os.listdir(caminho_brutos) 
        if f.endswith('.csv') 
        and (f.lower().endswith('_br.csv') or 'presidente' in f.lower()) 
        and not f.startswith('presidente_salesopolis_')
    ]

    if not arquivos:
        print("⚠️ Nenhum arquivo bruto de Presidente pendente em dados_brutos/.")
        return

    for arq in arquivos:
        caminho_origem = os.path.join(caminho_brutos, arq)
        digits = "".join([c for c in arq if c.isdigit()])
        ano_str = digits[:4] if len(digits) >= 4 else "historico"
        caminho_saida = os.path.join(caminho_brutos, f"presidente_salesopolis_{ano_str}.csv")

        print(f"\n⏳ Extraindo Salesópolis do arquivo pesado: {arq}...")
        chunks_salesopolis = []

        try:
            for chunk in pd.read_csv(caminho_origem, encoding='latin-1', sep=';', chunksize=100000, low_memory=False):
                chunk.columns = [str(c).upper().strip() for c in chunk.columns]

                col_muni_pref = [c for c in chunk.columns if 'NM_MUNICIPIO' in c or 'NOME_MUNICIPIO' in c]
                if col_muni_pref:
                    col_muni = col_muni_pref[0]
                elif 'NM_UE' in chunk.columns:
                    col_muni = 'NM_UE'
                else:
                    continue

                muni_norm = chunk[col_muni].astype(str).apply(remover_acentos).str.upper().str.strip()
                df_sales = chunk[muni_norm == 'SALESOPOLIS'].copy()

                if not df_sales.empty:
                    col_sg = [c for c in df_sales.columns if 'SG_PARTIDO' in c or 'SIGLA_PARTIDO' in c]
                    col_nr = [c for c in df_sales.columns if 'NR_VOTAVEL' in c or 'NR_CANDIDATO' in c or 'NR_PARTIDO' in c]

                    # Filtra brancos e nulos por número do votável (95/96)
                    if col_nr:
                        nr_series = df_sales[col_nr[0]].astype(str).str.split('.').str[0].str.strip()
                        df_sales = df_sales[~nr_series.isin(['95', '96'])].copy()

                    if df_sales.empty:
                        continue

                    sigla_original = None
                    if col_sg:
                        sigla_original = df_sales[col_sg[0]].astype(str).str.upper().str.strip()
                        sigla_original = sigla_original.replace(VALORES_DESCARTE, None)

                    sigla_convertida = None
                    if col_nr:
                        nums_part = df_sales[col_nr[0]].apply(extrair_numero_partido)
                        sigla_convertida = nums_part.map(MAPA_NUMEROS_HISTORICO)

                    if sigla_convertida is not None and sigla_original is not None:
                        df_sales['SG_PARTIDO'] = sigla_convertida.fillna(sigla_original)
                    elif sigla_convertida is not None:
                        df_sales['SG_PARTIDO'] = sigla_convertida
                    elif sigla_original is not None:
                        df_sales['SG_PARTIDO'] = sigla_original

                    # Remove registros que permaneceram sem partido válido (brancos/nulos não identificados)
                    df_sales = df_sales[df_sales['SG_PARTIDO'].notnull()].copy()
                    df_sales = df_sales[~df_sales['SG_PARTIDO'].astype(str).str.upper().str.strip().isin(VALORES_DESCARTE)].copy()

                    if not df_sales.empty:
                        chunks_salesopolis.append(df_sales)

            if chunks_salesopolis:
                df_final = pd.concat(chunks_salesopolis, ignore_index=True)
                df_final['DS_CARGO'] = 'Presidente'
                df_final.to_csv(caminho_saida, index=False, sep=';', encoding='latin-1')
                print(f"✅ Sucesso! {len(df_final)} registros válidos extraídos de Salesópolis.")
                print(f"📄 Arquivo gerado: {caminho_saida}")
            else:
                print(f"⚠️ Nenhum registro válido de votação nominal para Salesópolis em {arq}.")

        except Exception as e:
            print(f"Erro ao processar {arq}: {e}")

if __name__ == '__main__':
    extrair_presidente()