from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
from langchain_community.callbacks import StreamlitCallbackHandler
import json
from typing import Dict, Any, List
from pdf_generator import gerar_pdf

# Configuração da página Streamlit
st.set_page_config(page_title="Gerador de Documentação Técnica", layout="wide")
st.title("🚀 Gerador de Documentação Técnica")

# Sidebar para configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    openai_api_key = st.text_input("OpenAI API Key", type="password")
    temperature = st.slider("Temperatura", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
    model_name = st.selectbox("Modelo", ["gpt-3.5-turbo", "gpt-4"])

# Templates de prompts corrigidos
PROMPT_TEMPLATES = {
    "requisitos": """
    Analise a seguinte descrição do sistema e gere requisitos funcionais e não funcionais.
    Retorne APENAS um objeto JSON com requisitos funcionais e não funcionais.
    
    O JSON deve seguir este formato:
    {{
        "requisitos_funcionais": [
            {{"id": "RF01", "descricao": "descrição do requisito", "prioridade": "Alta/Média/Baixa"}}
        ],
        "requisitos_nao_funcionais": [
            {{"id": "RNF01", "descricao": "descrição do requisito", "tipo": "Desempenho/Segurança/Usabilidade"}}
        ]
    }}
    
    Descrição do sistema:
    {descricao_sistema}
    """,
    
    "fluxo": """
    Com base nos requisitos fornecidos, descreva o fluxo de componentes e a arquitetura geral.
    Retorne APENAS um objeto JSON com componentes e seus fluxos.
    
    O JSON deve seguir este formato:
    {{
        "componentes": [
            {{
                "nome": "nome do componente",
                "descricao": "descrição detalhada",
                "responsabilidades": ["responsabilidade 1", "responsabilidade 2"],
                "dependencias": ["dependencia 1", "dependencia 2"]
            }}
        ],
        "fluxos": [
            {{
                "nome": "nome do fluxo",
                "passos": ["passo 1", "passo 2", "passo 3"]
            }}
        ]
    }}
    
    Requisitos:
    {requisitos}
    """,
    
    "apis": """
    Com base no fluxo de componentes, gere um mapa de APIs detalhado.
    Retorne APENAS um objeto JSON com as definições das APIs.
    
    O JSON deve seguir este formato:
    {{
        "apis": [
            {{
                "rota": "/caminho/da/api",
                "metodo": "GET/POST/PUT/DELETE",
                "descricao": "descrição da funcionalidade",
                "parametros": {{
                    "param1": "descrição do parâmetro"
                }},
                "respostas": {{
                    "200": "descrição da resposta de sucesso",
                    "400": "descrição do erro"
                }}
            }}
        ]
    }}
    
    Fluxo de componentes:
    {fluxo_componentes}
    """
}

def ensure_json_response(response: str) -> Dict[str, Any]:
    """
    Garante que a resposta seja um JSON válido.
    Se não for, tenta extrair um JSON válido ou cria um objeto de erro.
    """
    try:
        # Tenta fazer o parse direto
        return json.loads(response)
    except json.JSONDecodeError:
        try:
            # Procura por um objeto JSON válido na string
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
        except:
            # Se tudo falhar, retorna um objeto de erro
            return {
                "erro": "Não foi possível gerar um JSON válido",
                "resposta_original": response
            }

def generate_documentation(description: str, api_key: str, temp: float, model: str):
    if not api_key:
        st.error("Por favor, insira sua API key!")
        return
    
    try:
        # Inicialização do modelo
        llm = ChatOpenAI(
            model=model,
            temperature=temp,
            openai_api_key=api_key,
            streaming=True,
            callbacks=[StreamlitCallbackHandler(st.container())]
        )
        
        # Criação dos prompts
        prompts = {
            name: PromptTemplate.from_template(template)
            for name, template in PROMPT_TEMPLATES.items()
        }
        
        # Criação das chains
        chains = {
            name: (prompt | llm | StrOutputParser())
            for name, prompt in prompts.items()
        }
        
        # Execução das chains com tratamento de erro aprimorado
        with st.spinner("Gerando documentação..."):
            try:
                # Requisitos
                st.subheader("📋 Requisitos do Sistema")
                requisitos_response = chains["requisitos"].invoke({"descricao_sistema": description})
                requisitos_json = ensure_json_response(requisitos_response)
                st.json(requisitos_json)
                
                # Fluxo de Componentes
                st.subheader("🔄 Fluxo de Componentes")
                fluxo_response = chains["fluxo"].invoke({"requisitos": json.dumps(requisitos_json)})
                fluxo_json = ensure_json_response(fluxo_response)
                st.json(fluxo_json)
                
                # Mapa de APIs
                st.subheader("🔌 Mapa de APIs")
                apis_response = chains["apis"].invoke({"fluxo_componentes": json.dumps(fluxo_json)})
                apis_json = ensure_json_response(apis_response)
                st.json(apis_json)
                
                # Criar coluna para os botões de download
                col1, col2 = st.columns(2)
                
                # Gerar e oferecer download do PDF
                try:
                    pdf_buffer = gerar_pdf(requisitos_json, fluxo_json, apis_json)
                    with col1:
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_buffer,
                            file_name="documentacao_tecnica.pdf",
                            mime="application/pdf",
                            help="Baixar documentação em formato PDF"
                        )
                except Exception as pdf_error:
                    st.error(f"Erro ao gerar PDF: {str(pdf_error)}")
                
                # Manter a opção de download do JSON
                with col2:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json.dumps({
                            "requisitos": requisitos_json,
                            "fluxo_componentes": fluxo_json,
                            "mapa_apis": apis_json
                        }, indent=2, ensure_ascii=False),
                        file_name="documentacao_tecnica.json",
                        mime="application/json",
                        help="Baixar documentação em formato JSON"
                    )
                
            except Exception as e:
                st.error(f"Erro ao processar etapa: {str(e)}")
                st.info("Tente ajustar a temperatura ou usar um modelo diferente.")
                
    except Exception as e:
        st.error(f"Erro ao inicializar o modelo: {str(e)}")

# Interface principal
st.header("📝 Descreva seu Sistema")
system_description = st.text_area(
    "Descreva o sistema que você quer documentar:",
    height=200,
    placeholder="Exemplo: Um sistema de e-commerce onde usuários podem visualizar produtos..."
)

if st.button("🎯 Gerar Documentação"):
    if system_description:
        generate_documentation(system_description, openai_api_key, temperature, model_name)
    else:
        st.warning("Por favor, insira uma descrição do sistema!")

# Informações adicionais
st.markdown("---")
st.markdown("""
### 📖 Como usar:
1. Insira sua OpenAI API Key na barra lateral
2. Ajuste as configurações de temperatura e modelo
3. Digite a descrição do seu sistema
4. Clique em 'Gerar Documentação'
5. Baixe o resultado completo em JSON
""")