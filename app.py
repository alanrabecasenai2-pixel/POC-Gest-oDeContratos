# Inicio do projeto
import os
import pandas as pd
from datetime import date, timedelta

# Caminho padrão para o arquivo CSV de contratos
CSV_PATH = os.path.join("data", "contratos.csv")

def criar_base_ficticia():
    """Gera uma base inicial com aproximadamente 25 contratos fictícios."""
    hoje = date.today()
    
    dados_iniciais = [
        {
            "id_contrato": "CONT-001",
            "numero_contrato": "CTR-2026/001",
            "cnpj": "12.345.678/0001-90",
            "razao_social": "Alpha Tecnologia Ltda",
            "objeto": "Licenciamento de software de gestão ERP",
            "natureza": "Tecnologia",
            "area_demandante": "TI",
            "centro_custo": "CC-101",
            "responsavel": "Carlos Silva",
            "valor_estimado": 120000.00,
            "data_inicio": str(hoje - timedelta(days=180)),
            "data_termino": str(hoje + timedelta(days=180)),
            "risco_compliance": "Baixo",
            "situacao_manual": "Normal"
        },
        {
            "id_contrato": "CONT-002",
            "numero_contrato": "CTR-2026/002",
            "cnpj": "98.765.432/0001-12",
            "razao_social": "Beta Limpeza e Conservação S.A.",
            "objeto": "Serviços continuados de limpeza predial",
            "natureza": "Serviços",
            "area_demandante": "Operações",
            "centro_custo": "CC-202",
            "responsavel": "Ana Souza",
            "valor_estimado": 85000.50,
            "data_inicio": str(hoje - timedelta(days=350)),
            "data_termino": str(hoje + timedelta(days=15)),
            "risco_compliance": "Médio",
            "situacao_manual": "Normal"
        },
        {
            "id_contrato": "CONT-003",
            "numero_contrato": "CTR-2026/003",
            "cnpj": "45.123.789/0001-44",
            "razao_social": "Gamma Segurança Eletrônica",
            "objeto": "Manutenção de câmeras e controle de acesso",
            "natureza": "Manutenção",
            "area_demandante": "Segurança",
            "centro_custo": "CC-303",
            "responsavel": "Marcos Lima",
            "valor_estimado": 45000.00,
            "data_inicio": str(hoje - timedelta(days=400)),
            "data_termino": str(hoje), # Vence hoje
            "risco_compliance": "Alto",
            "situacao_manual": "Normal"
        },
        {
            "id_contrato": "CONT-004",
            "numero_contrato": "CTR-2026/004",
            "cnpj": "11.223.344/0001-55",
            "razao_social": "Delta Consultoria Jurídica S/S",
            "objeto": "Assessoria jurídica em direito contratual",
            "natureza": "Consultoria",
            "area_demandante": "Jurídico",
            "centro_custo": "CC-404",
            "responsavel": "Juliana Mendes",
            "valor_estimado": 150000.00,
            "data_inicio": str(hoje - timedelta(days=400)),
            "data_termino": str(hoje - timedelta(days=10)), # Vencido
            "risco_compliance": "Baixo",
            "situacao_manual": "Normal"
        },
        {
            "id_contrato": "CONT-005",
            "numero_contrato": "CTR-2026/005",
            "cnpj": "55.443.322/0001-88",
            "razao_social": "Epsilon Alimentos e Catering",
            "objeto": "Fornecimento de refeições para refeitório",
            "natureza": "Serviços",
            "area_demandante": "RH",
            "centro_custo": "CC-505",
            "responsavel": "Fernanda Costa",
            "valor_estimado": 300000.00,
            "data_inicio": str(hoje - timedelta(days=100)),
            "data_termino": str(hoje + timedelta(days=265)),
            "risco_compliance": "Médio",
            "situacao_manual": "Encerrado"
        },
        # Gerando mais 20 contratos repetindo padrões variados para completar a base
    ]
    
    # Preenchendo até 25 contratos fictícios variados
    areas = ["TI", "RH", "Financeiro", "Operações", "Jurídico", "Marketing"]
    naturezas = ["Serviços", "Tecnologia", "Manutenção", "Consultoria", "Licenciamento"]
    riscos = ["Baixo", "Médio", "Alto"]
    empresas = [
        "Omega Soluções", "Zeta Cloud", "Sigma Engenharia", "Nova Publicidade",
        "Kapa Logística", "Lambda Systems", "Theta Manutenção", "Pi Consultoria",
        "Atlas Comércio", "Horizonte Alimentos", "Vanguarda Seguros", "Phoenix Treinamentos",
        "Global Service", "Prime Solutions", "Nexus Energia", "Vertex Telecom",
        "Summit Tech", "Polaris Log", "Titan Construções", "Orion Marketing"
    ]
    
    for i in range(6, 26):
        dias_offset_inicio = - (i * 15)
        dias_offset_termino = (i * 10) - 100
        
        # Variando os status de término para testar alertas
        if i % 5 == 0:
            termino = hoje - timedelta(days=i) # Vencido
        elif i % 4 == 0:
            termino = hoje + timedelta(days=5) # Próximo do vencimento
        else:
            termino = hoje + timedelta(days=120 + i) # Vigente

        dados_iniciais.append({
            "id_contrato": f"CONT-{i:03d}",
            "numero_contrato": f"CTR-2026/{i:03d}",
            "cnpj": f"{i:02d}.123.456/0001-{i:02d}",
            "razao_social": empresas[i - 6],
            "objeto": f"Prestação de serviços especializados em {naturezas[i % len(naturezas)]}",
            "natureza": naturezas[i % len(naturezas)],
            "area_demandante": areas[i % len(areas)],
            "centro_custo": f"CC-{100 * (i % 5 + 1)}",
            "responsavel": f"Responsável {i}",
            "valor_estimado": float(15000 + (i * 3500)),
            "data_inicio": str(hoje + timedelta(days=dias_offset_inicio)),
            "data_termino": str(termino),
            "risco_compliance": riscos[i % len(riscos)],
            "situacao_manual": "Normal"
        })

    df = pd.DataFrame(dados_iniciais)
    return df

def carregar_dados():
    """Lê o arquivo CSV. Se não existir, cria a base fictícia e salva."""
    os.makedirs("data", exist_ok=True)
    if not os.path.exists(CSV_PATH):
        df = criar_base_ficticia()
        salvar_dados(df)
    else:
        df = pd.read_csv(CSV_PATH)
    return df

def salvar_dados(df):
    """Salva o DataFrame atualizado no arquivo CSV."""
    os.makedirs("data", exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
