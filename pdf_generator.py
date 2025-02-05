from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
from typing import Dict, Any

class DocumentacaoTecnicaPDF:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = self.styles['Heading1']
        self.subtitle_style = self.styles['Heading2']
        self.normal_style = self.styles['Normal']
    
    def create_pdf(self, requisitos_json: Dict[str, Any], fluxo_json: Dict[str, Any], apis_json: Dict[str, Any]) -> BytesIO:
        """
        Cria um PDF com a documentação técnica formatada.
        
        Args:
            requisitos_json (dict): Dicionário contendo os requisitos
            fluxo_json (dict): Dicionário contendo o fluxo de componentes
            apis_json (dict): Dicionário contendo o mapa de APIs
            
        Returns:
            BytesIO: Buffer contendo o PDF gerado
        """
        # Criar buffer para o PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        elements = []
        
        # Título principal
        elements.append(Paragraph("Documentação Técnica", self.title_style))
        elements.append(Spacer(1, 30))
        
        # Adicionar seções
        self._add_requisitos_section(elements, requisitos_json)
        self._add_fluxo_section(elements, fluxo_json)
        self._add_apis_section(elements, apis_json)
        
        # Gerar PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer
    
    def _add_requisitos_section(self, elements: list, requisitos_json: Dict[str, Any]):
        """Adiciona a seção de requisitos ao documento"""
        elements.append(Paragraph("1. Requisitos do Sistema", self.subtitle_style))
        elements.append(Spacer(1, 12))
        
        # Requisitos Funcionais
        elements.append(Paragraph("1.1 Requisitos Funcionais", self.styles['Heading3']))
        for req in requisitos_json.get('requisitos_funcionais', []):
            texto = f"ID: {req['id']}\nDescrição: {req['descricao']}\nPrioridade: {req['prioridade']}"
            elements.append(Paragraph(texto, self.normal_style))
            elements.append(Spacer(1, 12))
        
        # Requisitos Não Funcionais
        elements.append(Paragraph("1.2 Requisitos Não Funcionais", self.styles['Heading3']))
        for req in requisitos_json.get('requisitos_nao_funcionais', []):
            texto = f"ID: {req['id']}\nDescrição: {req['descricao']}\nTipo: {req['tipo']}"
            elements.append(Paragraph(texto, self.normal_style))
            elements.append(Spacer(1, 12))
    
    def _add_fluxo_section(self, elements: list, fluxo_json: Dict[str, Any]):
        """Adiciona a seção de fluxo de componentes ao documento"""
        elements.append(Paragraph("2. Fluxo de Componentes", self.subtitle_style))
        elements.append(Spacer(1, 12))
        
        for comp in fluxo_json.get('componentes', []):
            elements.append(Paragraph(f"Componente: {comp['nome']}", self.styles['Heading3']))
            elements.append(Paragraph(f"Descrição: {comp['descricao']}", self.normal_style))
            
            elements.append(Paragraph("Responsabilidades:", self.normal_style))
            for resp in comp['responsabilidades']:
                elements.append(Paragraph(f"• {resp}", self.normal_style))
                
            elements.append(Paragraph("Dependências:", self.normal_style))
            for dep in comp['dependencias']:
                elements.append(Paragraph(f"• {dep}", self.normal_style))
            
            elements.append(Spacer(1, 12))
        
        # Adicionar fluxos
        if 'fluxos' in fluxo_json:
            elements.append(Paragraph("Fluxos:", self.styles['Heading3']))
            for fluxo in fluxo_json['fluxos']:
                elements.append(Paragraph(f"Fluxo: {fluxo['nome']}", self.normal_style))
                for i, passo in enumerate(fluxo['passos'], 1):
                    elements.append(Paragraph(f"{i}. {passo}", self.normal_style))
                elements.append(Spacer(1, 12))
    
    def _add_apis_section(self, elements: list, apis_json: Dict[str, Any]):
        """Adiciona a seção de APIs ao documento"""
        elements.append(Paragraph("3. Mapa de APIs", self.subtitle_style))
        elements.append(Spacer(1, 12))
        
        for api in apis_json.get('apis', []):
            elements.append(Paragraph(f"Rota: {api['rota']}", self.styles['Heading3']))
            elements.append(Paragraph(f"Método: {api['metodo']}", self.normal_style))
            elements.append(Paragraph(f"Descrição: {api['descricao']}", self.normal_style))
            
            if api['parametros']:
                elements.append(Paragraph("Parâmetros:", self.normal_style))
                for param, desc in api['parametros'].items():
                    elements.append(Paragraph(f"• {param}: {desc}", self.normal_style))
            
            elements.append(Paragraph("Respostas:", self.normal_style))
            for code, desc in api['respostas'].items():
                elements.append(Paragraph(f"• {code}: {desc}", self.normal_style))
            
            elements.append(Spacer(1, 12))

# Função auxiliar para facilitar o uso
def gerar_pdf(requisitos: Dict[str, Any], fluxo: Dict[str, Any], apis: Dict[str, Any]) -> BytesIO:
    """
    Função auxiliar para gerar o PDF da documentação técnica.
    
    Args:
        requisitos (dict): Dicionário com os requisitos
        fluxo (dict): Dicionário com o fluxo de componentes
        apis (dict): Dicionário com o mapa de APIs
        
    Returns:
        BytesIO: Buffer contendo o PDF gerado
    """
    gerador = DocumentacaoTecnicaPDF()
    return gerador.create_pdf(requisitos, fluxo, apis)