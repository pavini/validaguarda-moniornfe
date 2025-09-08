# Monitor NFe - ValidaGuarda

**Monitor automático para envio de NFes para o serviço ValidaGuarda da ValidaTech**

Este aplicativo monitora automaticamente pastas em seu computador para detectar novos arquivos XML de NFe (Nota Fiscal Eletrônica) ou arquivos compactados (ZIP, RAR, 7Z) que contenham XMLs, validando e enviando-os para o serviço ValidaGuarda.

Para mais informações sobre os serviços ValidaTech, acesse: **https://validatech.com.br**

---

## 📋 Requisitos do Sistema

- **Windows**: Windows 7 ou superior
- **Mac/Linux**: Qualquer versão recente
- **Python**: Versão 3.8 ou superior (será verificado automaticamente)
- **Internet**: Conexão ativa para envio dos arquivos

---

## 🚀 Como Executar a Aplicação

### Windows
1. Abra a pasta do aplicativo
2. **Clique duas vezes** no arquivo `run.bat`
3. O aplicativo será iniciado automaticamente (o terminal ficará minimizado)

### Mac/Linux
1. Abra o terminal na pasta do aplicativo
2. Execute o comando: `./run.sh`
3. O aplicativo será iniciado

> **Nota**: Na primeira execução, o sistema instalará automaticamente todas as dependências necessárias.

---

## ⚙️ Configuração Inicial

Ao abrir o aplicativo pela primeira vez, você precisará configurar:

### 1. Configurações de Monitoramento
- **Pasta de Monitoramento**: Selecione a pasta onde seus arquivos XML/ZIP de NFe ficam armazenados
  - O sistema monitora automaticamente todas as subpastas
  - Detecta arquivos XML e compactados (ZIP, RAR, 7Z)

- **Pasta de Saída**: Escolha onde os arquivos processados serão organizados
  - `processed/`: Arquivos enviados com sucesso
  - `errors/`: Arquivos com problemas
  - `logs/`: Registros de atividade

### 2. Configuração da API
- **Token de Acesso**: Insira seu token fornecido pela ValidaTech
  - Este token é necessário para autenticar o envio dos arquivos
  - Entre em contato com a ValidaTech para obter seu token

### 3. Opções Adicionais
- **Organizar arquivos automaticamente**: Move arquivos processados para as pastas de saída correspondentes

---

## 📁 Como Usar

### Funcionamento Automático
1. **Configure** as pastas e token conforme explicado acima
2. **Clique em "Iniciar Monitoramento"**
3. **Coloque arquivos XML ou ZIP** na pasta monitorada
4. O sistema **automaticamente**:
   - Detecta novos arquivos
   - Valida a estrutura XML
   - Envia para o ValidaGuarda
   - Move para pasta apropriada (sucesso/erro)
   - Registra todas as operações

### Monitoramento em Tempo Real
- A interface mostra uma **tabela com todos os arquivos processados**
- **Status em tempo real**: Processando, Sucesso, Erro
- **Logs detalhados** de todas as operações
- **Contadores** de arquivos processados, sucessos e erros

### Tipos de Arquivo Suportados
- **XML**: Arquivos diretos de NFe
- **ZIP/RAR/7Z**: Arquivos compactados contendo XMLs
- **Extração recursiva**: Suporta arquivos compactados dentro de outros compactados

---

## 🔍 Interface do Usuário

### Tela Principal
- **Tabela de Arquivos**: Mostra todos os arquivos processados com status
- **Logs**: Área de texto com informações detalhadas em tempo real
- **Contadores**: Estatísticas de processamento
- **Botões de Controle**: Iniciar/Parar monitoramento, limpar logs

### Menu Configurações
- **Arquivo > Configurações**: Acessa todas as opções de configuração
- **Teste de Conexão**: Verifica se o token e API estão funcionando
- **Salvar/Carregar**: Configurações são salvas automaticamente

---

## 📊 Interpretando os Status

| Status | Significado |
|--------|-------------|
| 🔄 **Processando** | Arquivo está sendo analisado e enviado |
| ✅ **Sucesso** | Arquivo enviado com sucesso para ValidaGuarda |
| ❌ **Erro** | Problema no arquivo ou no envio |
| 📁 **Organizado** | Arquivo movido para pasta apropriada |

---

## 🐛 Resolução de Problemas

### Problema: "Python não encontrado"
**Solução**: Instale Python 3.8+ de https://www.python.org/downloads/

### Problema: "Token inválido"
**Solução**: Verifique seu token com a ValidaTech em https://validatech.com.br

### Problema: "Erro ao instalar dependências"
**Solução**: Execute como administrador (Windows) ou use sudo (Mac/Linux)

### Problema: "Arquivos não são detectados"
**Solução**: 
- Verifique se a pasta de monitoramento está correta
- Certifique-se que são arquivos XML válidos de NFe
- Reinicie o monitoramento

### Problema: "Interface não abre"
**Solução**: 
- Verifique se há apenas uma instância rodando
- Reinicie o aplicativo
- Verifique os logs na pasta de saída

---

## 📞 Suporte

Para dúvidas, problemas ou solicitação de token de acesso:

**ValidaTech**
- Site: https://validatech.com.br
- Documentação completa dos serviços ValidaGuarda

---

## 📝 Notas Importantes

- Mantenha seu **token seguro** e não compartilhe
- O aplicativo funciona **24/7** quando ativado
- **Backup** suas configurações regularmente
- Monitore os **logs** para acompanhar o processamento
- **Conectividade** com internet é essencial para funcionamento

---

*Desenvolvido para integração com os serviços ValidaGuarda da ValidaTech*