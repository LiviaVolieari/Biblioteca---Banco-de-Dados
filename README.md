# Biblioteca---Banco-de-Dados
Projeto da matéria de Banco de dados — Sistema de biblioteca com Flask e MySQL

## Como Rodar o Projeto

### 1. Prepare o ambiente Python
```powershell
# Clone o repositório (se ainda não tiver)
git clone https://github.com/LiviaVolieari/Biblioteca---Banco-de-Dados.git
cd Biblioteca---Banco-de-Dados

# Crie e ative o ambiente virtual
python -m venv env
.\env\Scripts\activate  # Windows
# source env/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt
```

### 2. Configure o MySQL


1. Crie o banco usando sua senha:
   ```powershell
   # Se mysql está no PATH:
   mysql -u root -p < database\schema.sql
   
   # OU especifique o caminho completo:
   & 'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe' -u root -p < database\schema.sql
   ```

2. Configure a senha do MySQL (escolha um método):
   - **Temporário** (só na sessão atual do PowerShell):
     ```powershell
     $env:MYSQL_PASSWORD = "sua_senha_aqui"
     ```
   - **Permanente** (variável de ambiente do Windows):
     ```powershell
     setx MYSQL_PASSWORD "sua_senha_aqui"
     ```
   - Ou edite direto em `config/__init__.py` (não recomendado para produção)

### 3. Execute a Aplicação
```powershell
# Com ambiente virtual ativado:
python app.py

# Sem ativar env (caminho completo):
.\env\Scripts\python.exe app.py
```

Acesse http://127.0.0.1:5000 no navegador.

## Estrutura do Projeto
- `app.py` - Ponto de entrada da aplicação
- `config/` - Configurações (Flask, banco de dados)
- `controllers/` - Rotas e lógica de negócio
- `templates/` - Templates HTML (Jinja2)
- `database/` - Esquema SQL e migrations
- `style/` - Arquivos CSS e assets

## Troubleshooting

### Erro de conexão MySQL
1. **Verifique se MySQL está rodando**
   - XAMPP: abra o Control Panel, veja status do MySQL
   - MySQL: use `Get-Service -Name 'MySQL*'`

2. **Teste credenciais**
   - XAMPP: usuário root sem senha é padrão
   - MySQL: confirme usuário/senha:
     ```powershell
     mysql -u root -p -e "SELECT 1;"
     ```

3. **Banco não existe**
   - Erro "Unknown database 'biblioteca'"
   - Execute `database/schema.sql` conforme instruções acima

4. **Porta errada**
   - Padrão é 3306
   - Para mudar: `$env:MYSQL_PORT = "3307"`  # exemplo
