from pathlib import Path
from typing import Dict, Optional
from lxml import etree

from application.interfaces.services import IXMLSchemaService
from domain.entities.nfe_document import NFEDocument, NFEType
from domain.entities.validation_result import ValidationResult, ValidationStatus, ValidationType
from domain.services.nfe_validation_service import NFEValidationService


class XMLSchemaService(IXMLSchemaService):
    """XML Schema validation service implementation using lxml"""
    
    def __init__(self, schemas_folder: Optional[Path] = None):
        self._schemas: Dict[str, etree.XMLSchema] = {}
        self._schemas_folder = schemas_folder or Path(__file__).parent.parent.parent / 'schemas'
        self._validation_service = NFEValidationService()
        self._loaded = False
    
    def load_schemas(self) -> bool:
        """Load XSD schemas for validation"""
        try:
            print("🔧 Carregando schemas XSD...")
            print(f"   Diretório: {self._schemas_folder}")
            
            if not self._schemas_folder.exists():
                print(f"❌ Diretório de schemas não existe: {self._schemas_folder}")
                return False
            
            schema_count = 0
            
            # Load NFe schema
            nfe_schema_path = self._schemas_folder / 'leiauteNFe_v4.00.xsd'
            if self._load_schema_file('nfe', nfe_schema_path):
                schema_count += 1
            
            # Load procNFe schema
            proc_schema_path = self._schemas_folder / 'procNFe_v4.00.xsd'
            if self._load_schema_file('procNFe', proc_schema_path):
                schema_count += 1
            
            # Summary
            print(f"📊 Schemas carregados: {schema_count}/2")
            print(f"   Tipos disponíveis: {list(self._schemas.keys())}")
            
            if schema_count == 0:
                print("❌ Nenhum schema foi carregado")
                self._loaded = False
            elif schema_count < 2:
                print("⚠️  Alguns schemas não foram carregados")
                self._loaded = True
            else:
                print("✅ Todos os schemas carregados com sucesso")
                self._loaded = True
            
            return self._loaded
            
        except Exception as e:
            print(f"❌ Erro crítico ao carregar schemas: {e}")
            self._loaded = False
            return False
    
    def validate_against_schema(self, document: NFEDocument) -> ValidationResult:
        """Validate XML document against loaded schemas"""
        result = ValidationResult(
            document_path=str(document.file_path),
            status=ValidationStatus.SUCCESS
        )
        
        try:
            if not self._loaded or not self._schemas:
                result.add_error(
                    ValidationType.SCHEMA,
                    "Schemas XSD não carregados",
                    "Execute load_schemas() primeiro"
                )
                return result
            
            if not document.exists():
                result.add_error(
                    ValidationType.SCHEMA,
                    "Arquivo não encontrado",
                    f"O arquivo {document.filename} não existe"
                )
                return result
            
            # Detect document type
            doc_type = self._validation_service.detect_document_type(document)
            
            if doc_type == NFEType.UNKNOWN:
                result.add_error(
                    ValidationType.SCHEMA,
                    "Tipo de documento não reconhecido",
                    "Não foi possível determinar se é NFe ou procNFe"
                )
                return result
            
            # Get appropriate schema
            schema_key = 'nfe' if doc_type == NFEType.NFE else 'procNFe'
            schema = self._schemas.get(schema_key)
            
            if not schema:
                result.add_error(
                    ValidationType.SCHEMA,
                    f"Schema não disponível para {doc_type.value}",
                    f"Schema {schema_key} não foi carregado"
                )
                return result
            
            # Parse XML document
            xml_doc = self._parse_xml_document(document)
            if xml_doc is None:
                result.add_error(
                    ValidationType.SCHEMA,
                    "Erro ao analisar XML",
                    "Não foi possível fazer o parsing do documento XML"
                )
                return result
            
            print(f"🔍 Iniciando validação XSD para: {document.filename}")
            print(f"   Schema usado: {schema_key}")
            print(f"   Tipo de documento: {doc_type.value}")
            
            # Validate against schema
            if schema.validate(xml_doc):
                result.schema_valid = True
                print(f"✅ Validação de schema bem-sucedida: {document.filename}")
            else:
                result.schema_valid = False
                
                print(f"❌ Falha na validação de schema: {document.filename} - {len(schema.error_log)} erro(s)")
                print("📋 Detalhes dos erros:")
                
                # Add schema validation errors with detailed logging
                for i, error in enumerate(schema.error_log, 1):
                    error_msg = f"Erro de schema: {error.message}"
                    error_detail = f"Linha {error.line}, Coluna {error.column}" if error.line and error.column else f"Linha {error.line}" if error.line else "Posição não especificada"
                    
                    result.add_error(
                        ValidationType.SCHEMA,
                        error_msg,
                        error_detail,
                        error.line
                    )
                    
                    print(f"   {i:2d}. {error.message}")
                    print(f"       Posição: {error_detail}")
                    if hasattr(error, 'path') and error.path:
                        print(f"       XPath: {error.path}")
                
                # Log a summary for debugging
                print(f"⚠️  RESUMO: {document.filename} falhou na validação XSD com {len(schema.error_log)} erro(s)")
                print(f"   Primeiros erros: {[e.message[:50] + '...' if len(e.message) > 50 else e.message for e in schema.error_log[:3]]}")
            
            return result
            
        except Exception as e:
            result.add_error(
                ValidationType.SCHEMA,
                "Erro inesperado na validação de schema",
                str(e)
            )
            return result
    
    def has_schemas_loaded(self) -> bool:
        """Check if schemas are loaded and ready"""
        return self._loaded and len(self._schemas) > 0
    
    def _load_schema_file(self, schema_key: str, schema_path: Path) -> bool:
        """Load a specific schema file"""
        try:
            print(f"   Carregando schema {schema_key}: {schema_path.name}")
            
            if not schema_path.exists():
                print(f"   ⚠️  Arquivo não encontrado: {schema_path.name}")
                return False
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_doc = etree.parse(f)
            
            schema = etree.XMLSchema(schema_doc)
            self._schemas[schema_key] = schema
            
            print(f"   ✅ Schema {schema_key} carregado")
            return True
            
        except etree.XMLSchemaParseError as e:
            print(f"   ❌ Erro no parsing do schema {schema_key}: {e}")
            return False
        except Exception as e:
            print(f"   ❌ Erro ao carregar schema {schema_key}: {e}")
            return False
    
    def _parse_xml_document(self, document: NFEDocument) -> Optional[etree._Element]:
        """Parse XML document with multiple encoding attempts and better error handling"""
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        
        for encoding in encodings:
            try:
                # Method 1: Try reading as bytes first (avoids encoding declaration issues)
                try:
                    with open(document.file_path, 'rb') as f:
                        xml_bytes = f.read()
                    
                    # Parse directly from bytes
                    return etree.fromstring(xml_bytes)
                    
                except etree.XMLSyntaxError:
                    # If binary parsing fails, try text parsing
                    pass
                
                # Method 2: Read as text and encode to bytes
                with open(document.file_path, 'r', encoding=encoding) as f:
                    xml_content = f.read()
                
                # Convert to bytes to avoid "Unicode strings with encoding declaration" error
                xml_bytes = xml_content.encode('utf-8')
                
                # Parse XML from bytes
                return etree.fromstring(xml_bytes)
                
            except UnicodeDecodeError:
                continue
            except etree.XMLSyntaxError as e:
                print(f"   ❌ Erro de sintaxe XML ({encoding}): {e}")
                # Try next encoding instead of returning None immediately
                continue
            except Exception as e:
                print(f"   ❌ Erro ao analisar XML ({encoding}): {e}")
                continue
        
        print(f"   ❌ Não foi possível fazer parse do XML com nenhum encoding")
        return None
    
    def get_loaded_schemas(self) -> Dict[str, str]:
        """Get information about loaded schemas"""
        return {key: f"Schema {key} carregado" for key in self._schemas.keys()}