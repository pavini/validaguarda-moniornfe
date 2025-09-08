# Monitor de Validação de NF-e

Aplicativo desktop multiplataforma para monitoramento e validação de arquivos XML de NF-e.

## Compatibilidade

✅ **Windows** (7, 10, 11)  
✅ **macOS** (10.14+)  
✅ **Linux** (Ubuntu, CentOS, etc.)

## Requisitos

- Python 3.8+ 
- Bibliotecas listadas em `requirements.txt`

## Instalação

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Schema NFe (automático)
O aplicativo baixa automaticamente o schema `leiauteNFe_v4.00.xsd` do repositório PyNFe quando necessário.

### 3. Criar ícone (opcional)
```bash
pip install Pillow
python create_icon.py
```

Isso criará:
- `icon.png` - Ícone geral
- `icon.icns` - Ícone para macOS
- `icon.ico` - Ícone para Windows

## Executar

### Modo desenvolvimento
```bash
python main.py
```

### Gerar executável
```bash
python build.py
```

O executável será criado em `dist/`:
- **Windows**: `MonitorNFE-Windows.exe`
- **macOS**: `MonitorNFE-Darwin.app` 
- **Linux**: `MonitorNFE-Linux`

## Funcionalidades

- ✅ Monitoramento em tempo real de pastas
- ✅ Validação de estrutura XML contra schema XSD
- ✅ Verificação de assinatura digital
- ✅ Interface gráfica intuitiva
- ✅ Resultados em tabela com histórico
- ✅ Multiplataforma (Windows/Mac/Linux)

## Como usar

1. Execute o aplicativo
2. Clique em "Procurar" para selecionar pasta
3. Clique "Iniciar Monitoramento" 
4. Adicione arquivos XML à pasta monitorada
5. Veja os resultados na tabela

## Estrutura do projeto

```
monitor_nfe/
├── main.py           # Aplicação principal
├── build.py          # Script de build
├── requirements.txt  # Dependências Python
├── README.md         # Este arquivo
├── schemas/          # Schemas XSD
│   └── nfe_v4.00.xsd # Schema oficial (baixar)
└── examples/         # Exemplos de XML
```

## Troubleshooting

### Schema não encontrado
- Verifique se `schemas/nfe_v4.00.xsd` existe
- Baixe do portal oficial da SEFAZ

### Erro de permissão no macOS
```bash
sudo xattr -rd com.apple.quarantine MonitorNFE-Darwin.app
```

### Erro no Windows
- Execute como Administrador se necessário
- Verifique antivírus (pode bloquear executável não assinado)