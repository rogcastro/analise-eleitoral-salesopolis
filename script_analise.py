import os
import unicodedata
import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------------------
# Unificação de Siglas (Depara Histórico)
# -------------------------------------------------------------------
DEPARA_PARTIDOS = {
    'PCDB': 'PC DO B', 'PCDOB': 'PC DO B',
    'PODE': 'PODEMOS',
    'REP': 'REPUBLICANOS', 'PRB': 'REPUBLICANOS',
    'DEMOCRATA': 'DEM', 'PFL': 'DEM',
    'PMDB': 'MDB',
    'PPB': 'PP', 'PPR': 'PP',
    'PPS': 'CIDADANIA',
    'PR': 'PL',
    'PATRI': 'PATRIOTA', 'PEN': 'PATRIOTA',
    'SD': 'SOLIDARIEDADE',
    'PT DO B': 'AVANTE',
    'PTC': 'AGIR',
    'PSDC': 'DC',
    'MISSAO': 'MISSÃO',
    'UNIAO': 'UNIÃO'
}

# -------------------------------------------------------------------
# Mapeamento do Espectro Político
# -------------------------------------------------------------------
MAPA_PARTIDOS = {
    # ESQUERDA
    'PT': 'Esquerda', 'PSOL': 'Esquerda', 'PC DO B': 'Esquerda',
    'PSTU': 'Esquerda', 'PCO': 'Esquerda', 'PSB': 'Esquerda', 'REDE': 'Esquerda', 
    'UP': 'Esquerda', 'PCB': 'Esquerda', 'PPL': 'Esquerda',

    # CENTRO-DIREITA / DIREITA
    'PV': 'Centro-Direita', 'CIDADANIA': 'Centro-Direita',
    'PL': 'Centro-Direita', 'PP': 'Centro-Direita', 'REPUBLICANOS': 'Centro-Direita',
    'UNIÃO': 'Centro-Direita', 'DEM': 'Centro-Direita', 'PSDB': 'Centro-Direita',
    'MDB': 'Centro-Direita', 'PSD': 'Centro-Direita', 'PTB': 'Centro-Direita',
    'NOVO': 'Centro-Direita', 'PSC': 'Centro-Direita', 'PRTB': 'Centro-Direita',
    'DC': 'Centro-Direita', 'PDC': 'Centro-Direita', 'PATRIOTA': 'Centro-Direita',
    'PODEMOS': 'Centro-Direita', 'PTN': 'Centro-Direita', 'PRP': 'Centro-Direita',
    'PMN': 'Centro-Direita', 'PRONA': 'Centro-Direita', 'PRN': 'Centro-Direita',
    'PMB': 'Centro-Direita', 'AVANTE': 'Centro-Direita', 'SOLIDARIEDADE': 'Centro-Direita',
    'PDT': 'Centro-Direita', 'MISSÃO': 'Centro-Direita', 'AGIR': 'Centro-Direita',
    'PROS': 'Centro-Direita', 'PHS': 'Centro-Direita', 'PSL': 'Centro-Direita',
    'PRD': 'Centro-Direita'
}

VALORES_DESCARTE_VOTOS = [
    'BRANCO', 'NULO', 'VOTO BRANCO', 'VOTO NULO', 'VOTOS BRANCOS', 'VOTOS NULOS',
    '#NULO#', '#NE#', '95', '96', 'NONE', 'NAN', ''
]

def remover_acentos(texto):
    if not isinstance(texto, str):
        return str(texto)
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

def identificar_grupo_cargo(row):
    # Identificação por CD_CARGO (código numérico TSE)
    col_cd = [c for c in row.index if 'CD_CARGO' in c]
    if col_cd and pd.notnull(row[col_cd[0]]):
        try:
            cd = int(row[col_cd[0]])
            if cd == 11:
                return 'Prefeitos', 'Prefeito'
            elif cd == 13:
                return 'Vereadores', 'Vereador'
            elif cd == 1:
                return 'Presidente', 'Presidente'
            elif cd == 3:
                return 'Governadores', 'Governador'
            elif cd == 5:
                return 'Senadores', 'Senador'
            elif cd == 6:
                return 'Deputados', 'Deputado Federal'
            elif cd == 7:
                return 'Deputados', 'Deputado Estadual'
        except:
            pass

    # Identificação por texto
    col_ds = [c for c in row.index if 'DS_CARGO' in c or 'DESCRICAO_CARGO' in c]
    if col_ds and pd.notnull(row[col_ds[0]]):
        txt = remover_acentos(str(row[col_ds[0]])).upper().strip()
        if 'PREFEITO' in txt:
            return 'Prefeitos', 'Prefeito'
        elif 'VEREADOR' in txt:
            return 'Vereadores', 'Vereador'
        elif 'PRESIDENTE' in txt:
            return 'Presidente', 'Presidente'
        elif 'GOVERNADOR' in txt:
            return 'Governadores', 'Governador'
        elif 'SENADOR' in txt:
            return 'Senadores', 'Senador'
        elif 'DEPUTADO FEDERAL' in txt:
            return 'Deputados', 'Deputado Federal'
        elif 'DEPUTADO ESTADUAL' in txt:
            return 'Deputados', 'Deputado Estadual'

    return 'Outros', 'Outros'

def padronizar_sigla(sigla):
    if not isinstance(sigla, str):
        return 'OUTROS'
    sigla_limpa = sigla.upper().strip()
    return DEPARA_PARTIDOS.get(sigla_limpa, sigla_limpa)

def limpar_e_filtrar_dados(df):
    if df.empty:
        return df

    cargos_info = df.apply(identificar_grupo_cargo, axis=1)
    df['GRUPO_CARGO'] = [c[0] for c in cargos_info]
    df['DS_CARGO_LIMP'] = [c[1] for c in cargos_info]

    col_partido = [c for c in df.columns if 'SG_PARTIDO' in c or 'SIGLA_PARTIDO' in c]
    if not col_partido:
        return df

    col_p = col_partido[0]
    df['SG_PARTIDO_BRUTO'] = df[col_p].astype(str).str.upper().str.strip()

    mask_valido = ~df['SG_PARTIDO_BRUTO'].isin(VALORES_DESCARTE_VOTOS)
    df_filtrado = df[mask_valido].copy()

    df_filtrado['SG_PARTIDO_LIMP'] = df_filtrado['SG_PARTIDO_BRUTO'].apply(padronizar_sigla)
    df_filtrado['ESPECTRO'] = df_filtrado['SG_PARTIDO_LIMP'].map(MAPA_PARTIDOS).fillna('Outros')
    
    return df_filtrado

def criar_matriz_votos(df_part):
    if df_part.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df_part = limpar_e_filtrar_dados(df_part)
    if df_part.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    col_ano = [c for c in df_part.columns if 'ANO_ELEICAO' in c or 'ANO' in c][0]
    col_cargo = 'DS_CARGO_LIMP'

    v1 = pd.to_numeric(df_part['QT_VOTOS_NOMINAIS_VALIDOS'], errors='coerce').fillna(0) if 'QT_VOTOS_NOMINAIS_VALIDOS' in df_part.columns else 0
    v2 = pd.to_numeric(df_part['QT_TOTAL_VOTOS_LEG_VALIDOS'], errors='coerce').fillna(0) if 'QT_TOTAL_VOTOS_LEG_VALIDOS' in df_part.columns else 0
    v3 = pd.to_numeric(df_part['QT_VOTOS_NOMINAIS'], errors='coerce').fillna(0) if 'QT_VOTOS_NOMINAIS' in df_part.columns else 0
    v4 = pd.to_numeric(df_part['QT_VOTOS_LEGENDA'], errors='coerce').fillna(0) if 'QT_VOTOS_LEGENDA' in df_part.columns else 0
    v5 = pd.to_numeric(df_part['QT_VOTOS'], errors='coerce').fillna(0) if 'QT_VOTOS' in df_part.columns else 0

    df_part['TOTAL_VOTOS'] = v1 + v2 + v3 + v4 + v5

    if 'NR_TURNO' in df_part.columns:
        df_part['ANO_CARGO'] = df_part[col_ano].astype(str) + ' - ' + df_part[col_cargo].astype(str) + \
            df_part['NR_TURNO'].apply(lambda t: f' ({t}º Turno)' if pd.notnull(t) and str(t).strip() in ['1', '2'] else '')
    else:
        df_part['ANO_CARGO'] = df_part[col_ano].astype(str) + ' - ' + df_part[col_cargo].astype(str)

    matriz = df_part.pivot_table(
        index=['ESPECTRO', 'SG_PARTIDO_LIMP'],
        columns='ANO_CARGO',
        values='TOTAL_VOTOS',
        aggfunc='sum',
        fill_value=0
    )

    matriz_blocos = []
    for espectro, df_sub in matriz.groupby(level=0):
        matriz_blocos.append(df_sub)
        subtotal = df_sub.sum(axis=0)
        subtotal.name = (espectro, f'TOTAL {espectro.upper()}')
        matriz_blocos.append(pd.DataFrame([subtotal], index=pd.MultiIndex.from_tuples([subtotal.name], names=['ESPECTRO', 'SG_PARTIDO_LIMP'])))

    matriz_completa = pd.concat(matriz_blocos) if matriz_blocos else pd.DataFrame()

    totais_gerais = matriz.sum(axis=0)
    linha_total = pd.DataFrame([totais_gerais], index=pd.MultiIndex.from_tuples([('TOTAL GERAL', 'TOTAL VOTOS SALESOPOLIS')], names=['ESPECTRO', 'SG_PARTIDO_LIMP']))

    matriz_final = pd.concat([matriz_completa, linha_total])

    votos_espectro_qtd = df_part.groupby([col_ano, col_cargo, 'ESPECTRO'])['TOTAL_VOTOS'].sum().unstack(fill_value=0)
    votos_espectro_pct = votos_espectro_qtd.div(votos_espectro_qtd.sum(axis=1), axis=0) * 100

    votos_cargos_qtd = df_part.groupby([col_ano, 'GRUPO_CARGO', col_cargo, 'ESPECTRO'])['TOTAL_VOTOS'].sum().unstack(fill_value=0)
    votos_cargos_pct = votos_cargos_qtd.div(votos_cargos_qtd.sum(axis=1), axis=0) * 100

    return matriz_final, votos_espectro_pct, votos_cargos_pct

def processar_eleicoes():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir) if os.path.basename(script_dir) == 'scripts' else script_dir

    caminho_brutos = os.path.join(base_dir, 'dados_brutos')
    caminho_tratados = os.path.join(base_dir, 'dados_tratados')
    caminho_graficos = os.path.join(base_dir, 'graficos')

    if not os.path.exists(caminho_brutos):
        print(f"Erro: A pasta '{caminho_brutos}' não foi encontrada.")
        return

    arquivos = [f for f in os.listdir(caminho_brutos) if f.endswith('.csv')]
    if not arquivos:
        print(f"Aviso: Nenhum arquivo .csv encontrado em '{caminho_brutos}'.")
        return

    list_cand = []
    list_part = []

    for arq in arquivos:
        arq_lower = arq.lower()
        
        if arq_lower.endswith('_br.csv') or ('presidente' in arq_lower and not arq_lower.startswith('presidente_salesopolis_')):
            continue

        caminho = os.path.join(caminho_brutos, arq)
        print(f"Lendo: {arq}...")
        try:
            df = pd.read_csv(caminho, encoding='latin-1', sep=';', low_memory=False)
            df.columns = [str(c).upper().strip() for c in df.columns]

            if arq_lower.startswith('presidente_salesopolis_'):
                df['DS_CARGO'] = 'Presidente'
                df['CD_CARGO'] = 1

            col_muni_pref = [c for c in df.columns if 'NM_MUNICIPIO' in c or 'NOME_MUNICIPIO' in c]
            if col_muni_pref:
                col_muni = col_muni_pref[0]
            elif 'NM_UE' in df.columns:
                col_muni = 'NM_UE'
            else:
                continue

            muni_norm = df[col_muni].astype(str).apply(remover_acentos).str.upper().str.strip()
            df_sales = df[muni_norm == 'SALESOPOLIS'].copy()

            if df_sales.empty:
                continue

            if 'candidato' in arq_lower or 'cand' in arq_lower:
                list_cand.append(df_sales)
            else:
                list_part.append(df_sales)

        except Exception as e:
            print(f"Erro ao ler {arq}: {e}")

    df_cand_total = pd.concat(list_cand, ignore_index=True) if list_cand else pd.DataFrame()
    df_part_total = pd.concat(list_part, ignore_index=True) if list_part else pd.DataFrame()

    cand_por_partido = pd.DataFrame()
    cand_espectro_pct = pd.DataFrame()
    eleitos_espectro_pct = pd.DataFrame()

    if not df_cand_total.empty:
        df_cand_total = limpar_e_filtrar_dados(df_cand_total)
        if not df_cand_total.empty:
            col_partido = 'SG_PARTIDO_LIMP'
            col_ano = [c for c in df_cand_total.columns if 'ANO_ELEICAO' in c or 'ANO' in c][0]
            col_cargo = 'DS_CARGO_LIMP'

            df_muni_cand = df_cand_total[df_cand_total[col_cargo].str.upper().isin(['PREFEITO', 'VEREADOR'])].copy()

            if not df_muni_cand.empty:
                col_id = [c for c in df_muni_cand.columns if 'SQ_CANDIDATO' in c or 'NM_CANDIDATO' in c]
                id_cand = col_id[0] if col_id else col_partido

                cand_unicos = df_muni_cand.drop_duplicates(subset=[col_ano, col_cargo, id_cand])
                cand_por_partido = cand_unicos.groupby([col_ano, col_cargo, 'SG_PARTIDO_LIMP', 'ESPECTRO']).size().reset_index(name='QTD_CANDIDATOS')
                tot_cand = cand_por_partido.groupby([col_ano, col_cargo])['QTD_CANDIDATOS'].transform('sum')
                cand_por_partido['%_CANDIDATOS'] = (cand_por_partido['QTD_CANDIDATOS'] / tot_cand) * 100

                cand_espectro_abs = cand_unicos.groupby([col_ano, col_cargo, 'ESPECTRO']).size().unstack(fill_value=0)
                cand_espectro_pct = cand_espectro_abs.div(cand_espectro_abs.sum(axis=1), axis=0) * 100

                col_sit = [c for c in df_muni_cand.columns if 'DS_SIT_TOT_TURNO' in c or 'DS_SITUACAO_TSE' in c]
                if col_sit:
                    sit_col = col_sit[0]
                    mask_eleito = df_muni_cand[sit_col].astype(str).str.upper().str.startswith('ELEITO')
                    df_eleitos = df_muni_cand[mask_eleito].drop_duplicates(subset=[col_ano, col_cargo, id_cand])

                    if not df_eleitos.empty:
                        eleitos_abs = df_eleitos.groupby([col_ano, col_cargo, 'ESPECTRO']).size().unstack(fill_value=0)
                        eleitos_espectro_pct = eleitos_abs.div(eleitos_abs.sum(axis=1), axis=0) * 100

    matriz_votos, votos_espectro_pct, votos_cargos_pct = criar_matriz_votos(df_part_total)

    os.makedirs(caminho_tratados, exist_ok=True)
    caminho_excel = os.path.join(caminho_tratados, 'resultado_salesopolis.xlsx')
    
    with pd.ExcelWriter(caminho_excel, engine='openpyxl') as writer:
        if not matriz_votos.empty:
            matriz_votos.to_excel(writer, sheet_name='Matriz_Votos_Salesopolis')
        if not votos_espectro_pct.empty:
            votos_espectro_pct.to_excel(writer, sheet_name='Votos_Espectro_%')
        if not eleitos_espectro_pct.empty:
            eleitos_espectro_pct.to_excel(writer, sheet_name='Eleitos_Espectro_%')
        if not cand_por_partido.empty:
            cand_por_partido.to_excel(writer, sheet_name='Candidatos_Por_Partido', index=False)
            cand_espectro_pct.to_excel(writer, sheet_name='Candidatos_Espectro_%')

    print(f"\n✅ Planilha gerada com sucesso em: {caminho_excel}")

    os.makedirs(caminho_graficos, exist_ok=True)
    cores = {'Esquerda': '#d62728', 'Centro-Direita': '#1f77b4', 'Outros': '#7f7f7f'}

    # -------------------------------------------------------------------
    # 1. Gráfico Geral Único
    # -------------------------------------------------------------------
    if not votos_espectro_pct.empty:
        try:
            labels_formatados = [f"{idx[0]} - {idx[1]}" if isinstance(idx, tuple) else str(idx) for idx in votos_espectro_pct.index]
            largura = max(14, len(votos_espectro_pct) * 0.45)
            fig, ax = plt.subplots(figsize=(largura, 7))

            cols_disp = [c for c in ['Esquerda', 'Centro-Direita', 'Outros'] if c in votos_espectro_pct.columns]
            votos_espectro_pct[cols_disp].plot(kind='bar', stacked=True, color=[cores[c] for c in cols_disp], ax=ax, width=0.7)
            
            plt.title('Distribuição dos Votos Válidos em Salesópolis por Espectro Político', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Ano - Cargo', fontsize=11, labelpad=10)
            plt.ylabel('Proporção dos Votos Válidos (%)', fontsize=11)
            plt.legend(title='Espectro Político', bbox_to_anchor=(1.01, 1), loc='upper left')
            ax.set_xticks(range(len(labels_formatados)))
            ax.set_xticklabels(labels_formatados, rotation=55, ha='right', fontsize=9)
            plt.ylim(0, 100)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()

            caminho_img_votos = os.path.join(caminho_graficos, 'grafico_votos_espectro.png')
            plt.savefig(caminho_img_votos, dpi=300, bbox_inches='tight')
            plt.close('all')
            print(f"✅ Gráfico Geral de Votos salvo em: {caminho_img_votos}")
        except Exception as e:
            print(f"⚠️ Aviso ao salvar gráfico geral: {e}")

    # -------------------------------------------------------------------
    # 2. Gráfico Comparativo Facetado por TODOS OS CARGOS (3x2)
    # -------------------------------------------------------------------
    if not votos_cargos_pct.empty:
        try:
            fig, axes = plt.subplots(3, 2, figsize=(16, 14), sharey=True)
            axes = axes.flatten()

            cargos_alvo = ['Prefeitos', 'Vereadores', 'Deputados', 'Senadores', 'Governadores', 'Presidente']

            for i, cargo_grupo in enumerate(cargos_alvo):
                ax = axes[i]
                mask_grupo = [isinstance(idx, tuple) and idx[1] == cargo_grupo for idx in votos_cargos_pct.index]
                df_sub = votos_cargos_pct[mask_grupo].copy()

                if not df_sub.empty:
                    labels = [f"{int(idx[0])}\n{idx[2]}" if isinstance(idx, tuple) else str(idx) for idx in df_sub.index]
                    cols_disp = [c for c in ['Esquerda', 'Centro-Direita', 'Outros'] if c in df_sub.columns]

                    df_sub[cols_disp].plot(
                        kind='bar',
                        stacked=True,
                        color=[cores[c] for c in cols_disp],
                        ax=ax,
                        width=0.6,
                        legend=False
                    )

                    ax.set_xticks(range(len(labels)))
                    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)

                ax.set_title(f'Evolução do Espectro: {cargo_grupo}', fontsize=12, fontweight='bold', pad=10)
                ax.set_xlabel('Ano e Cargo Específico', fontsize=10)
                ax.set_ylabel('Proporção dos Votos Válidos (%)' if i % 2 == 0 else '', fontsize=10)
                ax.set_ylim(0, 100)
                ax.grid(axis='y', linestyle='--', alpha=0.5)

            handles, labels_leg = axes[0].get_legend_handles_labels()
            fig.legend(handles, labels_leg, title='Espectro Político', bbox_to_anchor=(0.5, 1.02), loc='upper center', ncol=3, fontsize=11)

            plt.suptitle('Comparação da Distribuição do Espectro Político dos Votos por Todos os Cargos (Salesópolis)', fontsize=14, fontweight='bold', y=1.04)
            plt.tight_layout()

            caminho_comp = os.path.join(caminho_graficos, 'grafico_comparativo_cargos.png')
            plt.savefig(caminho_comp, dpi=300, bbox_inches='tight')
            plt.close('all')
            print(f"✅ Gráfico Comparativo Completo de Cargos salvo em: {caminho_comp}")
        except Exception as e:
            print(f"⚠️ Aviso ao salvar gráfico comparativo de cargos: {e}")

    # -------------------------------------------------------------------
    # 3. Gráfico de Eleitos por Espectro
    # -------------------------------------------------------------------
    if not eleitos_espectro_pct.empty:
        try:
            labels_eleitos = [f"{idx[0]} - {idx[1]}" if isinstance(idx, tuple) else str(idx) for idx in eleitos_espectro_pct.index]
            largura_eleitos = max(10, len(eleitos_espectro_pct) * 0.5)
            fig, ax = plt.subplots(figsize=(largura_eleitos, 6))

            cols_eleitos = [c for c in ['Esquerda', 'Centro-Direita', 'Outros'] if c in eleitos_espectro_pct.columns]
            eleitos_espectro_pct[cols_eleitos].plot(kind='bar', stacked=True, color=[cores[c] for c in cols_eleitos], ax=ax, width=0.6)
            
            plt.title('Espectro Político dos CANDIDATOS ELEITOS (Salesópolis)', fontsize=14, fontweight='bold', pad=15)
            plt.xlabel('Ano - Cargo', fontsize=11, labelpad=10)
            plt.ylabel('Proporção de Candidatos Eleitos (%)', fontsize=11)
            plt.legend(title='Espectro Político', bbox_to_anchor=(1.01, 1), loc='upper left')
            ax.set_xticks(range(len(labels_eleitos)))
            ax.set_xticklabels(labels_eleitos, rotation=45, ha='right', fontsize=9)
            plt.ylim(0, 100)
            plt.grid(axis='y', linestyle='--', alpha=0.5)
            plt.tight_layout()

            path_eleitos = os.path.join(caminho_graficos, 'grafico_eleitos_espectro.png')
            plt.savefig(path_eleitos, dpi=300, bbox_inches='tight')
            plt.close('all')
            print(f"✅ Gráfico de Candidatos Eleitos salvo em: {path_eleitos}")
        except Exception as e:
            print(f"⚠️ Aviso ao salvar gráfico de eleitos: {e}")

if __name__ == '__main__':
    processar_eleicoes()