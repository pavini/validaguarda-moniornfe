from abc import ABC, abstractmethod
from typing import Optional

from ..entities.nfe_document import NFEDocument, NFEType
from ..entities.validation_result import ValidationResult, ValidationStatus, ValidationType
from ..value_objects.nfe_key import NFEKey


class INFEValidationService(ABC):
    """Interface for NFe validation service"""
    
    @abstractmethod
    def detect_document_type(self, document: NFEDocument) -> NFEType:
        """Detect the type of NFe document"""
        pass
    
    @abstractmethod
    def extract_nfe_key(self, xml_content: str) -> Optional[NFEKey]:
        """Extract NFe key from XML content"""
        pass
    
    @abstractmethod
    def validate_schema(self, document: NFEDocument) -> ValidationResult:
        """Validate document against XSD schema"""
        pass
    
    @abstractmethod
    def validate_structure(self, document: NFEDocument) -> ValidationResult:
        """Validate basic document structure"""
        pass


class NFEValidationService(INFEValidationService):
    """Domain service for NFe validation logic"""
    
    def detect_document_type(self, document: NFEDocument) -> NFEType:
        """Detect if XML is NFe or procNFe based on content"""
        if not document.exists() or not document.is_xml:
            return NFEType.UNKNOWN
        
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            
            for encoding in encodings:
                try:
                    content = document.file_path.read_text(encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                return NFEType.UNKNOWN
            
            # Check root element
            if '<nfeProc' in content or '<procNFe' in content:
                return NFEType.PROC_NFE
            elif '<NFe' in content or '<infNFe' in content:
                return NFEType.NFE
            else:
                return NFEType.UNKNOWN
                
        except Exception:
            return NFEType.UNKNOWN
    
    def extract_nfe_key(self, xml_content: str) -> Optional[NFEKey]:
        """Extract NFe key from XML content using regex patterns"""
        if not xml_content:
            return None
        
        import re
        
        # Patterns to find NFe key (chNFe or Id attribute)
        patterns = [
            r'<chNFe>(\d{44})</chNFe>',
            r'Id="NFe(\d{44})"',
            r'id="NFe(\d{44})"',
            r'<infNFe[^>]*Id="NFe(\d{44})"',
            r'<infNFe[^>]*id="NFe(\d{44})"'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, xml_content)
            if match:
                key_value = match.group(1)
                return NFEKey.from_string(key_value)
        
        return None
    
    def validate_structure(self, document: NFEDocument) -> ValidationResult:
        """Validate basic document structure and content"""
        result = ValidationResult(
            document_path=str(document.file_path),
            status=ValidationStatus.SUCCESS
        )
        
        # Check if file exists
        if not document.exists():
            result.add_error(
                ValidationType.STRUCTURE,
                "Arquivo não encontrado",
                f"O arquivo {document.filename} não existe"
            )
            return result
        
        # Check if file is too small
        if document.file_size < 100:  # Less than 100 bytes is suspicious
            result.add_error(
                ValidationType.STRUCTURE,
                "Arquivo muito pequeno",
                f"Arquivo tem apenas {document.file_size} bytes"
            )
            return result
        
        # Check if file is too large (5MB limit)
        if document.file_size > 5 * 1024 * 1024:
            result.add_error(
                ValidationType.STRUCTURE,
                "Arquivo muito grande",
                f"Arquivo tem {document.file_size / (1024*1024):.1f}MB (limite 5MB)"
            )
            return result
        
        # For XML files, check basic structure
        if document.is_xml:
            try:
                # Try to read file content
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                xml_content = None
                
                for encoding in encodings:
                    try:
                        xml_content = document.file_path.read_text(encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                
                if not xml_content:
                    result.add_error(
                        ValidationType.STRUCTURE,
                        "Erro de encoding",
                        "Não foi possível ler o arquivo com nenhum encoding suportado"
                    )
                    return result
                
                # Check for XML declaration
                xml_stripped = xml_content.strip()
                if not xml_stripped.startswith('<?xml'):
                    result.add_error(
                        ValidationType.STRUCTURE,
                        "Declaração XML ausente",
                        "Arquivo não possui declaração XML válida"
                    )
                
                # Check for NFe content
                if '<NFe' not in xml_content and '<nfeProc' not in xml_content:
                    result.add_error(
                        ValidationType.STRUCTURE,
                        "Conteúdo NFe não encontrado",
                        "Arquivo não parece conter dados de NFe"
                    )
                
                # Try to extract and validate NFe key
                nfe_key = self.extract_nfe_key(xml_content)
                if nfe_key:
                    result.nfe_key = str(nfe_key)
                else:
                    result.add_error(
                        ValidationType.STRUCTURE,
                        "Chave NFe não encontrada",
                        "Não foi possível extrair a chave da NFe do arquivo"
                    )
                
            except Exception as e:
                result.add_error(
                    ValidationType.STRUCTURE,
                    "Erro na leitura do arquivo",
                    str(e)
                )
        
        return result
    
    def validate_schema(self, document: NFEDocument) -> ValidationResult:
        """Validate document against XSD schema - to be implemented by infrastructure"""
        # This is a domain service method that defines the contract
        # The actual implementation will be in the infrastructure layer
        result = ValidationResult(
            document_path=str(document.file_path),
            status=ValidationStatus.SKIPPED
        )
        
        result.add_error(
            ValidationType.SCHEMA,
            "Validação de schema não implementada",
            "Esta funcionalidade será implementada na camada de infraestrutura"
        )
        
        return result