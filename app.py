from datetime import date, datetime, timedelta
import os
import pandas as pd
import plotly.express as px
import streamlit as st

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="Gestão de Contratos — PoC SENAI",
    page_icon="📋",
    layout="wide",
)

# Caminho do CSV
CSV_PATH = os.path.join("data", "contratos.csv")

# --- FUNÇÕES DE DADOS E PERSISTÊNCIA ---


def criar_base_ficticia():
  """Gera uma base inicial com aproximadamente 25 contratos fictícios."""
  hoje = date.today()
  dados_iniciais = []

  empresas = [
      "Alpha Tecnologia Ltda",
      "Beta Limpeza e Conservação S.A.",
      "Gamma Segurança Eletrônica",
      "Delta Consultoria Jurídica S/S",
      "Epsilon Alimentos e Catering",
      "Omega Soluções",
      "Zeta Cloud",
      "Sigma Engenharia",
      "Nova Publicidade",
      "Kapa Logística",
      "Lambda Systems",
      "Theta Manutenção",
      "Pi Consultoria",
      "Atlas Comércio",
      "Horizonte Alimentos",
      "Vanguarda Seguros",
      "Phoenix Treinamentos",
      "Global Service",
      "Prime Solutions",
      "Nexus Energia",
      "Vertex Telecom",
      "Summit Tech",
      "Polaris Log",
      "Titan Construções",
      "Orion Marketing",
  ]
  areas = ["TI", "RH", "Financeiro", "Operações", "Jurídico", "Marketing"]
  naturezas = [
      "Serviços",
      "Tecnologia",
      "Manutenção",
      "Consultoria",
      "Licenciamento",
  ]
  riscos = ["Baixo", "Médio", "Alto"]

  for i in range(1, 26):
    dias_offset_inicio = -(i * 15)
    if i % 5 == 0:
      termino = hoje - timedelta(days=i * 5)  # Vencido
    elif i % 4 == 0:
      termino = hoje + timedelta(days=10)  # Próximo do vencimento
    elif i == 3:
      termino = hoje  # Vence hoje
    else:
      termino = hoje + timedelta(days=120 + (i * 5))  # Vigente

    # Padrão EC 001/2027
    num_contrato = f"EC {i:03d}/2027"

    dados_iniciais.append({
        "numero_contrato": num_contrato,
        "cnpj": f"{i:02d}.123.456/0001-{i:02d}",
        "razao_social": empresas[i - 1],
        "objeto": (
            "Prestação de serviços especializados em"
            f" {naturezas[i % len(naturezas)]}"
        ),
        "natureza": naturezas[i % len(naturezas)],
        "area_demandante": areas[i % len(areas)],
        "centro_custo": f"CC-{100 * (i % 5 + 1)}",
        "responsavel": f"Responsável {i}",
        "valor_estimado": float(15000 + (i * 4500)),
        "data_inicio": (hoje + timedelta(days=dias_offset_inicio)).strftime(
            "%Y-%m-%d"
        ),
        "data_termino": termino.strftime("%Y-%m-%d"),
        "risco_compliance": riscos[i % len(riscos)],
        "situacao_manual": "Normal",
    })

  return pd.DataFrame(dados_iniciais)


def carregar_dados():
  try:
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CSV_PATH):
      df = criar_base_ficticia()
      df.to_csv(CSV_PATH, index=False)
    else:
      df = pd.read_csv(CSV_PATH)
      # Limpa e garante que as colunas essenciais existam
      if "numero_contrato" not in df.columns and "id_contrato" in df.columns:
        df = df.rename(columns={"id_contrato": "numero_contrato"})
    return df
  except Exception as e:
    st.error(f"Erro ao carregar os dados: {e}")
    return pd.DataFrame()


def salvar_dados(df):
  os.makedirs("data", exist_ok=True)
  df.to_csv(CSV_PATH, index=False)


# --- REGRAS DE NEGÓCIO E CÁLCULO DE VIGÊNCIA ---
def calcular_status_linha(row):
  if str(row.get("situacao_manual", "Normal")).lower() == "encerrado":
    return "Encerrado"

  data_term_str = str(row["data_termino"]).strip()
  try:
    # Tenta ler formato ISO (YYYY-MM-DD) ou brasileiro (DD/MM/YYYY)
    if "-" in data_term_str:
      data_term = datetime.strptime(data_term_str[:10], "%Y-%m-%d").date()
    else:
      data_term = datetime.strptime(data_term_str[:10], "%d/%m/%Y").date()
  except ValueError:
    return "Erro Data"

  hoje = date.today()
  dias_restantes = (data_term - hoje).days

  if dias_restantes < 0:
    return "Vencido"
  elif dias_restantes == 0:
    return "Vence hoje"
  elif dias_restantes <= 30:
    return "Próximo do vencimento"
  else:
    return "Vigente"


def calcular_dias_restantes(data_termino_str):
  try:
    data_term_str = str(data_termino_str).strip()
    if "-" in data_term_str:
      data_term = datetime.strptime(data_term_str[:10], "%Y-%m-%d").date()
    else:
      data_term = datetime.strptime(data_term_str[:10], "%d/%m/%Y").date()
    return (data_term - date.today()).days
  except ValueError:
    return 0


def formatar_data_br(data_str):
  try:
    data_str = str(data_str).strip()
    if "-" in data_str:
      dt = datetime.strptime(data_str[:10], "%Y-%m-%d")
    else:
      dt = datetime.strptime(data_str[:10], "%d/%m/%Y")
    return dt.strftime("%d/%m/%Y")
  except:
    return data_str


def formatar_moeda(valor):
  try:
    return (
        f"R$ {float(valor):,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )
  except:
    return "R$ 0,00"


def validar_cnpj(cnpj):
  import re

  cnpj_limpo = re.sub(r"\D", "", cnpj)
  return len(cnpj_limpo) == 14


# Estilização de Cores (Caixa inteira para Situação e Texto para Risco)
def estilizar_celulas(val):
  if val == "Vigente":
    return "background-color: #d4edda; color: #155724; font-weight: bold;"
  elif val in ["Próximo do vencimento", "Vence hoje"]:
    return "background-color: #fff3cd; color: #856404; font-weight: bold;"
  elif val == "Vencido":
    return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
  elif val == "Encerrado":
    return "background-color: #e2e3e5; color: #383d41; font-weight: bold;"

  if val == "Baixo":
    return "color: #28a745; font-weight: bold;"
  elif val == "Médio":
    return "color: #d39e00; font-weight: bold;"
  elif val == "Alto":
    return "color: #dc3545; font-weight: bold;"

  return ""


# --- INTERFACE (SIDEBAR E NAVEGAÇÃO) ---
st.sidebar.image(
    "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbzRPHoV9mTfERgq6EfF2AyaVZkzJSmex-RbGYC2vgFvfpr0CiSiEvjscc&s=10",
    width=120,
)
st.sidebar.title("Gestão de Contratos")
st.sidebar.markdown("**PoC Educacional — SENAI**")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Navegação:",
    [
        "Início / Apresentação",
        "Cadastro de Contratos",
        "Acompanhamento",
        "Relatórios e Exportação",
        "Dashboard",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Aviso:** Este protótipo utiliza exclusivamente dados fictícios para fins"
    " educacionais."
)

# Carrega os dados globais
df_contratos = carregar_dados()

if not df_contratos.empty:
  df_contratos["Dias Restantes"] = df_contratos["data_termino"].apply(
      calcular_dias_restantes
  )
  df_contratos["Situação"] = df_contratos.apply(calcular_status_linha, axis=1)

# ==========================================
# 0. INÍCIO / APRESENTAÇÃO
# ==========================================
if menu == "Início / Apresentação":
  col_logo, col_txt = st.columns([1, 3])
  with col_logo:
    st.image(
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQbzRPHoV9mTfERgq6EfF2AyaVZkzJSmex-RbGYC2vgFvfpr0CiSiEvjscc&s=10",
        width=200,
    )
  with col_txt:
    st.title("Sistema de Gestão e Acompanhamento de Contratos")
    st.markdown("### Protótipo de Prova de Conceito (PoC) — SENAI")
    st.markdown(
        "Bem-vindo ao sistema integrador de contratos corporativos fictícios."
        " Utilize o menu lateral para navegar entre o cadastro, acompanhamento,"
        " relatórios gerenciais e o painel de indicadores (Dashboard)."
    )

  st.markdown("---")
  c1, c2, c3 = st.columns(3)
  c1.metric("Contratos Cadastrados", len(df_contratos))
  c2.metric(
      "Contratos Vigentes",
      len(df_contratos[df_contratos["Situação"] == "Vigente"]),
  )
  c3.metric(
      "Valor Global Estimado",
      formatar_moeda(df_contratos["valor_estimado"].sum()),
  )

# ==========================================
# 1. CADASTRO DE CONTRATOS
# ==========================================
elif menu == "Cadastro de Contratos":
  st.title("➕ Cadastro de Novo Contrato")
  st.markdown("Preencha o formulário abaixo para incluir um novo contrato.")

  with st.form("form_cadastro"):
    col1, col2 = st.columns(2)

    with col1:
      proximo_num = f"EC {len(df_contratos) + 1:03d}/2027"
      numero_contrato = st.text_input(
          "Número do Contrato (ID) *", value=proximo_num
      )
      cnpj = st.text_input("CNPJ * (ex: 00.000.000/0001-00)")
      razao_social = st.text_input("Razão Social *")
      objeto = st.text_area("Objeto ou Resumo do Contrato *")
      natureza = st.selectbox(
          "Natureza do Contrato",
          [
              "Serviços",
              "Tecnologia",
              "Manutenção",
              "Consultoria",
              "Licenciamento",
              "Outro",
          ],
      )

    with col2:
      area_demandante = st.selectbox(
          "Área Demandante",
          ["TI", "RH", "Financeiro", "Operações", "Jurídico", "Marketing", "Outro"],
      )
      centro_custo = st.text_input("Centro de Custo (ex: CC-101)")
      responsavel = st.text_input("Responsável pelo Contrato")
      valor_estimado = st.number_input(
          "Valor Estimado (R$) *", min_value=0.0, step=1000.0
      )
      data_inicio = st.date_input("Data de Início da Vigência")
      data_termino = st.date_input("Data de Término da Vigência")
      risco_compliance = st.selectbox(
          "Risco de Compliance", ["Baixo", "Médio", "Alto"]
      )

    submitted = st.form_submit_button("Salvar Contrato")

    if submitted:
      erros = []
      if not numero_contrato.strip():
        erros.append("O número do contrato é obrigatório.")
      elif (
          numero_contrato in df_contratos["numero_contrato"].values
      ):
        erros.append("Já existe um contrato cadastrado com esse número/ID.")

      if not razao_social.strip():
        erros.append("A razão social é obrigatória.")
      if not validar_cnpj(cnpj):
        erros.append("CNPJ inválido ou fora do formato padrão.")
      if valor_estimado <= 0:
        erros.append("O valor estimado deve ser maior que zero.")
      if data_termino < data_inicio:
        erros.append("A data de término não pode ser anterior à data de início.")

      if erros:
        for err in erros:
          st.error(err)
      else:
        novo_registro = {
            "numero_contrato": numero_contrato,
            "cnpj": cnpj,
            "razao_social": razao_social,
            "objeto": objeto,
            "natureza": natureza,
            "area_demandante": area_demandante,
            "centro_custo": centro_custo,
            "responsavel": responsavel,
            "valor_estimado": valor_estimado,
            "data_inicio": data_inicio.strftime("%Y-%m-%d"),
            "data_termino": data_termino.strftime("%Y-%m-%d"),
            "risco_compliance": risco_compliance,
            "situacao_manual": "Normal",
        }

        cols_originais = [
            c
            for c in df_contratos.columns
            if c not in ["Dias Restantes", "Situação"]
        ]
        df_novo = pd.concat(
            [df_contratos[cols_originais], pd.DataFrame([novo_registro])],
            ignore_index=True,
        )
        salvar_dados(df_novo)
        st.success("Contrato cadastrado com sucesso!")
        st.balloons()

# ==========================================
# 2. ACOMPANHAMENTO
# ==========================================
elif menu == "Acompanhamento":
  st.title("📂 Acompanhamento e Gestão de Contratos")
  st.markdown(
      "Pesquise, filtre, edite ou exclua os contratos cadastrados na base."
  )

  col_pesq, col_f1, col_f2, col_f3 = st.columns([2, 1, 1, 1])

  with col_pesq:
    termo_busca = st.text_input(
        "🔍 Pesquisar (Número, CNPJ ou Razão Social)"
    )

  with col_f1:
    filtro_area = st.selectbox(
        "Área", ["Todas"] + list(df_contratos["area_demandante"].unique())
    )

  with col_f2:
    filtro_risco = st.selectbox(
        "Risco", ["Todos"] + list(df_contratos["risco_compliance"].unique())
    )

  with col_f3:
    filtro_situacao = st.selectbox(
        "Situação", ["Todas"] + list(df_contratos["Situação"].unique())
    )

  df_filtrado = df_contratos.copy()

  if termo_busca:
    termo = termo_busca.lower()
    df_filtrado = df_filtrado[
        df_filtrado["numero_contrato"].str.lower().str.contains(termo)
        | df_filtrado["cnpj"].str.lower().str.contains(termo)
        | df_filtrado["razao_social"].str.lower().str.contains(termo)
    ]

  if filtro_area != "Todas":
    df_filtrado = df_filtrado[df_filtrado["area_demandante"] == filtro_area]

  if filtro_risco != "Todos":
    df_filtrado = df_filtrado[df_filtrado["risco_compliance"] == filtro_risco]

  if filtro_situacao != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Situação"] == filtro_situacao]

  st.markdown(f"**Total exibido:** {len(df_filtrado)} contratos")

  # Prepara tabela de exibição formatando as datas para DD/MM/AAAA
  df_exibicao = df_filtrado[[
      "numero_contrato",
      "razao_social",
      "area_demandante",
      "valor_estimado",
      "risco_compliance",
      "data_termino",
      "Dias Restantes",
      "Situação",
  ]].copy()

  df_exibicao["data_termino"] = df_exibicao["data_termino"].apply(
      formatar_data_br
  )
  df_exibicao["valor_estimado"] = df_exibicao["valor_estimado"].apply(
      formatar_moeda
  )

  df_exibicao.columns = [
      "Número do Contrato",
      "Razão Social",
      "Área Demandante",
      "Valor Estimado",
      "Risco Compliance",
      "Data Término",
      "Dias Restantes",
      "Situação",
  ]

  # Aplica cores na caixa (fundo) da Situação e cor na letra do Risco
  st.dataframe(
      df_exibicao.style.applymap(
          estilizar_celulas, subset=["Situação", "Risco Compliance"]
      ),
      use_container_width=True,
  )

  st.markdown("---")
  st.subheader("⚙️ Gerenciar Contrato Específico")

  ids_disponiveis = df_contratos["numero_contrato"].tolist()
  contrato_selecionado = st.selectbox(
      "Selecione o Número/ID do Contrato para Editar ou Excluir",
      ids_disponiveis,
  )

  if contrato_selecionado:
    dados_contrato = df_contratos[
        df_contratos["numero_contrato"] == contrato_selecionado
    ].iloc[0]

    with st.form("form_edicao"):
      st.write(f"Editando Contrato: **{contrato_selecionado} — {dados_contrato['razao_social']}**")

      novo_status_manual = st.selectbox(
          "Situação Manual",
          ["Normal", "Encerrado"],
          index=0 if dados_contrato["situacao_manual"] == "Normal" else 1,
      )
      novo_valor = st.number_input(
          "Valor Estimado (R$)", value=float(dados_contrato["valor_estimado"])
      )
      novo_responsavel = st.text_input(
          "Responsável", value=str(dados_contrato["responsavel"])
      )

      col_b1, col_b2 = st.columns(2)
      salvar_edicao = col_b1.form_submit_button("Atualizar Contrato")
      excluir_contrato = col_b2.form_submit_button("Excluir Contrato")

      if salvar_edicao:
        df_atual = df_contratos.copy()
        idx = df_atual[
            df_atual["numero_contrato"] == contrato_selecionado
        ].index[0]
        df_atual.loc[idx, "situacao_manual"] = novo_status_manual
        df_atual.loc[idx, "valor_estimado"] = novo_valor
        df_atual.loc[idx, "responsavel"] = novo_responsavel

        cols_salvar = [
            c for c in df_atual.columns if c not in ["Dias Restantes", "Situação"]
        ]
        salvar_dados(df_atual[cols_salvar])
        st.success("Contrato atualizado com sucesso! Recarregue a página.")

      if excluir_contrato:
        df_atual = df_contratos.copy()
        df_atual = df_atual[
            df_atual["numero_contrato"] != contrato_selecionado
        ]
        cols_salvar = [
            c for c in df_atual.columns if c not in ["Dias Restantes", "Situação"]
        ]
        salvar_dados(df_atual[cols_salvar])
        st.success("Contrato excluído com sucesso! Recarregue a página.")

# ==========================================
# 3. RELATÓRIOS E EXPORTAÇÃO
# ==========================================
elif menu == "Relatórios e Exportação":
  st.title("📈 Relatórios e Exportação de Dados")
  st.markdown("Visualize resumos consolidados e baixe a base completa em CSV.")

  st.subheader("Resumo por Situação")
  resumo_sit = df_contratos["Situação"].value_counts().reset_index()
  resumo_sit.columns = ["Situação", "Quantidade"]
  st.dataframe(resumo_sit, use_container_width=True)

  st.subheader("Resumo por Área Demandante")
  resumo_area = (
      df_contratos.groupby("area_demandante")
      .agg(
          quantidade=("numero_contrato", "count"),
          valor_total=("valor_estimado", "sum"),
      )
      .reset_index()
  )
  resumo_area["valor_total"] = resumo_area["valor_total"].apply(formatar_moeda)
  resumo_area.columns = [
      "Área Demandante",
      "Quantidade de Contratos",
      "Valor Total Acumulado",
  ]
  st.dataframe(resumo_area, use_container_width=True)

  st.markdown("---")
  st.subheader("📥 Baixar Base de Dados Completa")

  cols_csv = [
      c for c in df_contratos.columns if c not in ["Dias Restantes", "Situação"]
  ]
  csv_export = df_contratos[cols_csv].to_csv(index=False).encode("utf-8")
  st.download_button(
      label="Baixar contratos.csv",
      data=csv_export,
      file_name="contratos.csv",
      mime="text/csv",
  )

# ==========================================
# 4. DASHBOARD (ÚLTIMO ITEM)
# ==========================================
elif menu == "Dashboard":
  st.title("📊 Dashboard de Gestão de Contratos")
  st.markdown(
      "Visão geral dos indicadores e métricas contratuais atualizadas em"
      " tempo real."
  )

  total_contratos = len(df_contratos)
  vigentes = len(df_contratos[df_contratos["Situação"] == "Vigente"])
  proximos = len(
      df_contratos[df_contratos["Situação"] == "Próximo do vencimento"]
  )
  vencidos = len(df_contratos[df_contratos["Situação"].isin(["Vencido"])])
  valor_total = df_contratos["valor_estimado"].sum()

  col1, col2, col3, col4, col5 = st.columns(5)
  col1.metric("Total", total_contratos)
  col2.metric("Vigentes", vigentes)
  col3.metric("Próx. Vencimento", proximos)
  col4.metric("Vencidos", vencidos, delta_color="inverse")
  col5.metric("Valor Total", formatar_moeda(valor_total))

  st.markdown("---")

  c1, c2 = st.columns(2)

  with c1:
    st.subheader("Contratos por Área Demandante")
    df_area = df_contratos["area_demandante"].value_counts().reset_index()
    df_area.columns = ["Área", "Quantidade"]
    fig_area = px.bar(
        df_area,
        x="Área",
        y="Quantidade",
        text="Quantidade",
        color="Área",
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    st.plotly_chart(fig_area, use_container_width=True)

  with c2:
    st.subheader("Distribuição por Risco de Compliance")
    df_risco = df_contratos["risco_compliance"].value_counts().reset_index()
    df_risco.columns = ["Risco", "Quantidade"]
    fig_risco = px.pie(
        df_risco,
        names="Risco",
        values="Quantidade",
        hole=0.4,
        color="Risco",
        color_discrete_map={
            "Baixo": "#28a745",
            "Médio": "#ffc107",
            "Alto": "#dc3545",
        },
    )
    st.plotly_chart(fig_risco, use_container_width=True)

  st.subheader("Quantidade de Contratos por Situação")
  df_situacao = df_contratos["Situação"].value_counts().reset_index()
  df_situacao.columns = ["Situação", "Quantidade"]
  fig_sit = px.bar(
      df_situacao,
      x="Situação",
      y="Quantidade",
      text="Quantidade",
      color="Situação",
      color_discrete_map={
          "Vigente": "#28a745",
          "Próximo do vencimento": "#ffc107",
          "Vence hoje": "#ff851b",
          "Vencido": "#dc3545",
          "Encerrado": "#6c757d",
      },
  )
  st.plotly_chart(fig_sit, use_container_width=True)
