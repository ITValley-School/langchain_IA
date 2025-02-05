from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict
from langchain_core.runnables import RunnablePassthrough

# Definindo estruturas de dados para garantir respostas formatadas
class RequisitosFuncionais(BaseModel):
    id: str = Field(description="Identificador único do requisito")
    descricao: str = Field(description="Descrição detalhada do requisito")
    prioridade: str = Field(description="Prioridade do requisito: Alta, Média ou Baixa")

class RequisitosNaoFuncionais(BaseModel):
    id: str = Field(description="Identificador único do requisito")
    tipo: str = Field(description="Tipo do requisito: Desempenho, Segurança, Usabilidade, etc")
    descricao: str = Field(description="Descrição detalhada do requisito")

class Requisitos(BaseModel):
    funcionais: List[RequisitosFuncionais] = Field(description="Lista de requisitos funcionais")
    nao_funcionais: List[RequisitosNaoFuncionais] = Field(description="Lista de requisitos não funcionais")

class Componente(BaseModel):
    nome: str = Field(description="Nome do componente")
    descricao: str = Field(description="Descrição do componente")
    dependencias: List[str] = Field(description="Lista de dependências do componente")

class API(BaseModel):
    rota: str = Field(description="Rota da API")
    metodo: str = Field(description="Método HTTP")
    descricao: str = Field(description="Descrição da funcionalidade")
    parametros: Dict = Field(description="Parâmetros de entrada")
    resposta: Dict = Field(description="Estrutura da resposta")

# Configuração do modelo
def get_llm():
    return ChatOpenAI(
        model="gpt-4",
        temperature=0.7
    )

# Criando os parsers
requisitos_parser = PydanticOutputParser(pydantic_object=Requisitos)
componente_parser = PydanticOutputParser(pydantic_object=Componente)
api_parser = PydanticOutputParser(pydantic_object=API)

# Templates dos prompts
REQUISITOS_TEMPLATE = """
Com base na seguinte descrição de sistema, gere requisitos funcionais e não funcionais detalhados:

DESCRIÇÃO:
{descricao_sistema}

{format_instructions}

Seja específico e detalhado na descrição dos requisitos.
"""

COMPONENTES_TEMPLATE = """
Com base nos requisitos abaixo, descreva os componentes do sistema:

REQUISITOS:
{requisitos}

{format_instructions}

Forneça uma descrição detalhada de cada componente e suas interações.
"""

API_TEMPLATE = """
Com base nos componentes descritos, defina as APIs necessárias:

COMPONENTES:
{componentes}

{format_instructions}

Detalhe cada endpoint com seus métodos, parâmetros e respostas esperadas.
"""

# Criando as chains
def create_documentation_chain():
    llm = get_llm()
    
    # Chain de Requisitos
    requisitos_prompt = PromptTemplate(
        template=REQUISITOS_TEMPLATE,
        input_variables=["descricao_sistema"],
        partial_variables={"format_instructions": requisitos_parser.get_format_instructions()}
    )
    
    requisitos_chain = (
        requisitos_prompt 
        | llm 
        | requisitos_parser
    )
    
    # Chain de Componentes
    componentes_prompt = PromptTemplate(
        template=COMPONENTES_TEMPLATE,
        input_variables=["requisitos"],
        partial_variables={"format_instructions": componente_parser.get_format_instructions()}
    )
    
    componentes_chain = (
        componentes_prompt 
        | llm 
        | componente_parser
    )
    
    # Chain de APIs
    api_prompt = PromptTemplate(
        template=API_TEMPLATE,
        input_variables=["componentes"],
        partial_variables={"format_instructions": api_parser.get_format_instructions()}
    )
    
    api_chain = (
        api_prompt 
        | llm 
        | api_parser
    )
    
    # Chain completa
    return {
        "requisitos": requisitos_chain,
        "componentes": componentes_chain,
        "apis": api_chain
    }

# Função principal para gerar documentação
def generate_documentation(descricao_sistema: str):
    chains = create_documentation_chain()
    
    # Gerando documentação em etapas
    try:
        # 1. Requisitos
        print("\n🔹 Gerando Requisitos...")
        requisitos = chains["requisitos"].invoke({"descricao_sistema": descricao_sistema})
        print(requisitos.model_dump_json(indent=2))
        
        # 2. Componentes
        print("\n🔹 Gerando Componentes...")
        componentes = chains["componentes"].invoke({"requisitos": requisitos.model_dump_json()})
        print(componentes.model_dump_json(indent=2))
        
        # 3. APIs
        print("\n🔹 Gerando APIs...")
        apis = chains["apis"].invoke({"componentes": componentes.model_dump_json()})
        print(apis.model_dump_json(indent=2))
        
        return {
            "requisitos": requisitos,
            "componentes": componentes,
            "apis": apis
        }
        
    except Exception as e:
        print(f"Erro ao gerar documentação: {str(e)}")
        return None

# Exemplo de uso
if __name__ == "__main__":
    descricao_sistema = """
    Um sistema de e-commerce onde usuários podem visualizar produtos, 
    adicionar ao carrinho e finalizar compras.
    O sistema deve suportar múltiplos métodos de pagamento e 
    integração com serviços de entrega.
    Administradores podem gerenciar estoque, pedidos e usuários.
    """
    
    documentacao = generate_documentation(descricao_sistema)