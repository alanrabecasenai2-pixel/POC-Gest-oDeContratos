import os
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import streamlit as st

# --- 1. CONFIGURAÇÃO DA PÁGINA (DEVE SER A PRIMEIRA CHAMADA) ---
st.set_page_config(
    page_title="Gestão de Contratos — PoC SENAI",
    page_icon="📋",
    layout="wide",
)

# Caminho do CSV
CSV_PATH = os.path.join("data", "contratos.csv")

# --- 2. FUNÇÕES DE DADOS E PERSISTÊNCIA ---
def criar_base_ficticia():
    """Gera uma base inicial com aproximadamente 25 contratos fictícios."""
    hoje = date.today()
    dados_iniciais = []
    
    empresas = [
        "Alpha Tecnologia Ltda", "Beta Limpeza e Conservação S.A.", "Gamma Segurança Eletrônica",
        "Delta Consultoria Jurídica S/S", "Epsilon Alimentos e Catering", "Omega Soluções",
        "Zeta Cloud", "Sigma Engenharia", "Nova Publicidade", "Kapa Logística",
        "Lambda Systems", "Theta Manutenção", "Pi Consultoria", "Atlas Comércio",
        "Horizonte Alimentos", "Vanguarda Seguros", "Phoenix Treinamentos", "Global Service",
        "Prime Solutions", "Nexus Energia", "Vertex Telecom", "Summit Tech",
        "Polaris Log", "Titan Construções", "Orion Marketing"
    ]
    areas = ["TI", "RH", "Financeiro", "Operações", "Jurídico", "Marketing"]
    naturezas = ["Serviços", "Tecnologia", "Manutenção", "Consultoria", "Licenciamento"]
    riscos = ["Baixo", "Médio", "Alto"]
    
    for i in range(1, 26):
        dias_offset_inicio = - (i * 15)
        if i % 5 == 0:
            termino = hoje - timedelta(days=i)  # Vencido
        elif i % 4 == 0:
            termino = hoje + timedelta(days=5)  # Próximo do vencimento
        elif i == 3:
            termino = hoje  # Vence hoje
        else:
            termino = hoje + timedelta(days=120 + (i * 5))  # Vigente

        dados_iniciais.append({
            "id_contrato": f"CONT-{i:03d}",
            "numero_contrato": f"CTR-2026/{i:03d}",
            "cnpj": f"{i:02d}.123.456/0001-{i:02d}",
            "razao_social": empresas[i - 1],
            "objeto": f"Prestação de serviços especializados em {naturezas[i % len(naturezas)]}",
            "natureza": naturezas[i % len(naturezas)],
            "area_demandante": areas[i % len(areas)],
            "centro_custo": f"CC-{100 * (i % 5 + 1)}",
            "responsavel": f"Responsável {i}",
            "valor_estimado": float(15000 + (i * 4500)),
            "data_inicio": str(hoje + timedelta(days=dias_offset_inicio)),
            "data_termino": str(termino),
            "risco_compliance": riscos[i % len(riscos)],
            "situacao_manual": "Normal"
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
        return df
    except Exception as e:
        st.error(f"Erro ao carregar os dados: {e}")
        return pd.DataFrame()

def salvar_dados(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv(CSV_PATH, index=False)

# --- 3. REGRAS DE NEGÓCIO E CÁLCULO DE VIGÊNCIA ---
def calcular_status_linha(row):
    if str(row.get("situacao_manual", "Normal")).lower() == "encerrado":
        return "Encerrado"
    
    try:
        data_term = datetime.strptime(str(row["data_termino"]), "%Y-%m-%d").date()
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
        data_term = datetime.strptime(str(data_termino_str), "%Y-%m-%d").date()
        return (data_term - date.today()).days
    except ValueError:
        return 0

def validar_cnpj(cnpj):
    import re
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    return len(cnpj_limpo) == 14

# --- 4. INTERFACE (SIDEBAR E NAVEGAÇÃO) ---
st.sidebar.title("Navegação")
menu = st.sidebar.radio(
    "Ir para:",
    [
        "Dashboard",
        "Cadastro de Contratos",
        "Acompanhamento",
        "Relatórios e Exportação",
    ],
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Aviso:** Este protótipo utiliza exclusivamente dados fictícios para fins"
    " educacionais (SENAI)."
)

# Carrega os dados globais
df_contratos = carregar_dados()

if df_contratos.empty:
    st.warning("A base de dados está vazia ou ocorreu um erro ao carregar.")
else:
    # Adiciona colunas calculadas dinamicamente
    df_contratos["dias_restantes"] = df_contratos["data_termino"].apply(calcular_dias_restantes)
    df_contratos["situacao"] = df_contratos.apply(calcular_status_linha, axis=1)

    # ==========================================
    # 1. DASHBOARD
    # ==========================================
    if menu == "Dashboard":
        st.title("📊 Dashboard de Gestão de Contratos")
        st.markdown("Visão geral dos indicadores e métricas contratuais atualizadas em tempo real.")

        total_contratos = len(df_contratos)
        vigentes = len(df_contratos[df_contratos["situacao"] == "Vigente"])
        proximos = len(df_contratos[df_contratos["situacao"] == "Próximo do vencimento"])
        vencidos = len(df_contratos[df_contratos["situacao"].isin(["Vencido"])])
        valor_total = df_contratos["valor_estimado"].sum()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Total", total_contratos)
        col2.metric("Vigentes", vigentes)
        col3.metric("Próx. Vencimento", proximos)
        col4.metric("Vencidos", vencidos, delta_color="inverse")
        
        # Formatação segura de moeda para evitar erros de renderização
        valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        col5.metric("Valor Total", valor_formatado)

        st.markdown("---")

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("Contratos por Área Demandante")
            df_area = df_contratos["area_demandante"].value_counts().reset_index()
            df_area.columns = ["Área", "Quantidade"]
            fig_area = px.bar(
                df_area, x="Área", y="Quantidade", text="Quantidade", color="Área",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_area, use_container_width=True)

        with c2:
            st.subheader("Distribuição por Risco de Compliance")
            df_risco = df_contratos["risco_compliance"].value_counts().reset_index()
            df_risco.columns = ["Risco", "Quantidade"]
            fig_risco = px.pie(
                df_risco, names="Risco", values="Quantidade", hole=0.4, color="Risco",
                color_discrete_map={"Baixo": "green", "Médio": "orange", "Alto": "red"}
            )
            st.plotly_chart(fig_risco, use_container_width=True)

        st.subheader("Quantidade de Contratos por Situação")
        df_situacao = df_contratos["situacao"].value_counts().reset_index()
        df_situacao.columns = ["Situação", "Quantidade"]
        fig_sit = px.bar(
            df_situacao, x="Situação", y="Quantidade", text="Quantidade", color="Situação"
        )
        st.plotly_chart(fig_sit, use_container_width=True)

    # ==========================================
    # 2. CADASTRO DE CONTRATOS
    # ==========================================
    elif menu == "Cadastro de Contratos":
        st.title("➕ Cadastro de Novo Contrato")
        st.markdown("Preencha o formulário abaixo para incluir um novo contrato.")

        with st.form("form_cadastro"):
            col1, col2 = st.columns(2)

            with col1:
                novo_id = f"CONT-{len(df_contratos) + 1:03d}"
                st.text_input("ID do Contrato (Automático)", value=novo_id, disabled=True)

                numero_contrato = st.text_input("Número do Contrato * (ex: CTR-2026/100)")
                cnpj = st.text_input("CNPJ * (ex: 00.000.000/0001-00)")
                razao_social = st.text_input("Razão Social *")
                objeto = st.text_area("Objeto ou Resumo do Contrato *")
                natureza = st.selectbox(
                    "Natureza do Contrato",
                    ["Serviços", "Tecnologia", "Manutenção", "Consultoria", "Licenciamento", "Outro"]
                )

            with col2:
                area_demandante = st.selectbox(
                    "Área Demandante",
                    ["TI", "RH", "Financeiro", "Operações", "Jurídico", "Marketing", "Outro"]
                )
                centro_custo = st.text_input("Centro de Custo (ex: CC-101)")
                responsavel = st.text_input("Responsável pelo Contrato")
                valor_estimado = st.number_input("Valor Estimado (R$) *", min_value=0.0, step=1000.0)
                data_inicio = st.date_input("Data de Início da Vigência")
                data_termino = st.date_input("Data de Término da Vigência")
                risco_compliance = st.selectbox("Risco de Compliance", ["Baixo", "Médio", "Alto"])

            submitted = st.form_submit_button("Salvar Contrato")

            if submitted:
                erros = []
                if not numero_contrato.strip():
                    erros.append("O número do contrato é obrigatório.")
                elif numero_contrato in df_contratos["numero_contrato"].values:
                    erros.append("Já existe um contrato cadastrado com esse número.")

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
                        "id_contrato": novo_id,
                        "numero_contrato": numero_contrato,
                        "cnpj": cnpj,
                        "razao_social": razao_social,
                        "objeto": objeto,
                        "natureza": natureza,
                        "area_demandante": area_demandante,
                        "centro_custo": centro_custo,
                        "responsavel": responsavel,
                        "valor_estimado": valor_estimado,
                        "data_inicio": str(data_inicio),
                        "data_termino": str(data_termino),
                        "risco_compliance": risco_compliance,
                        "situacao_manual": "Normal"
                    }

                    df_novo = pd.concat(
                        [df_contratos.drop(columns=["dias_restantes", "situacao"]), pd.DataFrame([novo_registro])],
                        ignore_index=True
                    )
                    salvar_dados(df_novo)
                    st.success("Contrato cadastrado com sucesso! Atualize a página para visualizar.")
                    st.balloons()

    # ==========================================
    # 3. ACOMPANHAMENTO
    # ==========================================
    elif menu == "Acompanhamento":
        st.title("📂 Acompanhamento e Gestão de Contratos")
        st.markdown("Pesquise, filtre, edite ou exclua os contratos cadastrados.")

        col_pesq, col_f1, col_f2, col_f3 = st.columns([2, 1, 1, 1])

        with col_pesq:
            termo_busca = st.text_input("🔍 Pesquisar (Número, CNPJ ou Razão Social)")

        with col_f1:
            filtro_area = st.selectbox("Área", ["Todas"] + list(df_contratos["area_demandante"].unique()))

        with col_f2:
            filtro_risco = st.selectbox("Risco", ["Todos"] + list(df_contratos["risco_compliance"].unique()))

        with col_f3:
            filtro_situacao = st.selectbox("Situação", ["Todas"] + list(df_contratos["situacao"].unique()))

        df_filtrado = df_contratos.copy()

        if termo_busca:
            termo = termo_busca.lower()
            df_filtrado = df_filtrado[
                df_filtrado["numero_contrato"].str.lower().str.contains(termo) |
                df_filtrado["cnpj"].str.lower().str.contains(termo) |
                df_filtrado["razao_social"].str.lower().str.contains(termo)
            ]

        if filtro_area != "Todas":
            df_filtrado = df_filtrado[df_filtrado["area_demandante"] == filtro_area]

        if filtro_risco != "Todos":
            df_filtrado = df_filtrado[df_filtrado["risco_compliance"] == filtro_risco]

        if filtro_situacao != "Todas":
            df_filtrado = df_filtrado[df_filtrado["situacao"] == filtro_situacao]

        st.markdown(f"**Total exibido:** {len(df_filtrado)} contratos")

        colunas_exibicao = [
            "id_contrato", "numero_contrato", "razao_social",
            "area_demandante", "valor_estimado", "risco_compliance",
            "data_termino", "dias_restantes", "situacao"
        ]
        st.dataframe(df_filtrado[colunas_exibicao], use_container_width=True)

        st.markdown("---")
        st.subheader("⚙️ Gerenciar Contrato Específico")

        ids_disponiveis = df_contratos["id_contrato"].tolist()
        contrato_selecionado = st.selectbox("Selecione o ID do Contrato para Editar ou Excluir", ids_disponiveis)

        if contrato_selecionado:
            dados_contrato = df_contratos[df_contratos["id_contrato"] == contrato_selecionado].iloc[0]

            with st.form("form_edicao"):
                st.write(f"Editando: **{contrato_selecionado} - {dados_contrato['razao_social']}**")
                
                novo_status_manual = st.selectbox(
                    "Situação Manual",
                    ["Normal", "Encerrado"],
                    index=0 if dados_contrato["situacao_manual"] == "Normal" else 1
                )
                novo_valor = st.number_input("Valor Estimado (R$)", value=float(dados_contrato["valor_estimado"]))
                novo_responsavel = st.text_input("Responsável", value=str(dados_contrato["responsavel"]))

                col_b1, col_b2 = st.columns(2)
                salvar_edicao = col_b1.form_submit_button("Atualizar Contrato")
                excluir_contrato = col_b2.form_submit_button("Excluir Contrato")

                if salvar_edicao:
                    df_atual = df_contratos.copy()
                    idx = df_atual[df_atual["id_contrato"] == contrato_selecionado].index[0]
                    df_atual.loc[idx, "situacao_manual"] = novo_status_manual
                    df_atual.loc[idx, "valor_estimado"] = novo_valor
                    df_atual.loc[idx, "responsavel"] = novo_responsavel

                    df_para_salvar = df_atual.drop(columns=["dias_restantes", "situacao"])
                    salvar_dados(df_para_salvar)
                    st.success("Contrato atualizado com sucesso! Recarregue a página.")

                if excluir_contrato:
                    df_atual = df_contratos.copy()
                    df_atual = df_atual[df_atual["id_contrato"] != contrato_selecionado]
                    df_para_salvar = df_atual.drop(columns=["dias_restantes", "situacao"])
                    salvar_dados(df_para_salvar)
                    st.success("Contrato excluído com sucesso! Recarregue a página.")

    # ==========================================
    # 4. RELATÓRIOS E EXPORTAÇÃO
    # ==========================================
    elif menu == "Relatórios e Exportação":
        st.title("📈 Relatórios e Exportação de Dados")
        st.markdown("Visualize resumos consolidados e baixe a base completa em CSV.")

        st.subheader("Resumo por Situação")
        resumo_sit = df_contratos["situacao"].value_counts().reset_index()
        resumo_sit.columns = ["Situação", "Quantidade"]
        st.dataframe(resumo_sit, use_container_width=True)

        st.subheader("Resumo por Área Demandante")
        resumo_area = df_contratos.groupby("area_demandante").agg(
            quantidade=("id_contrato", "count"),
            valor_total=("valor_estimado", "sum")
        ).reset_index()
        st.dataframe(resumo_area, use_container_width=True)

        st.markdown("---")
        st.subheader("📥 Baixar Base de Dados Completa")
        
        csv_export = df_contratos.drop(columns=["dias_restantes", "situacao"]).to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Baixar contratos.csv",
            data=csv_export,
            file_name="contratos.csv",
            mime="text/csv",
        )
