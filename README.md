# 📊 Análise Eleitoral Histórica de Salesópolis (SP)

Este repositório contém os scripts em Python e os dados consolidados do histórico eleitoral do município de Salesópolis (SP), cobrindo eleições municipais, estaduais e presidenciais.

---

## 📁 Estrutura do Projeto

- `extrair_presidente.py`: Script extrator em lotes (*chunks*) para filtrar arquivos brutos pesados do TSE para o cargo de Presidente.
- `script_analise.py`: Script principal de análise que compila votos, mapeia legendas partidárias por espectro político (Esquerda, Centro-Direita, Brancos e Nulos) e gera os relatórios.
- `dados_tratados/`: Contém a planilha consolidada `resultado_salesopolis.xlsx`.
- `graficos/`: Gráficos gerados em formato `.png`.

---

## 🚀 Como Executar

1. Clone o repositório:
   ```bash
   git clone [https://github.com/seu-usuario/analise-eleitoral-salesopolis.git](https://github.com/seu-usuario/analise-eleitoral-salesopolis.git)