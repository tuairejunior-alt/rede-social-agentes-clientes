# Guia de Troubleshooting - Rede Social Agentes e Clientes

## 🔴 Erros Comuns e Soluções

### 1. Erro: "No module named 'flask'"

**Causa:** Dependências Python não instaladas corretamente

**Solução:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

### 2. Erro: "Cannot find module 'react'"

**Causa:** Node.js não está instalado ou dependências npm não foram instaladas

**Solução:**
```bash
# Instale Node.js: https://nodejs.org/
cd frontend
rm -rf node_modules package-lock.json
npm install
```

---

### 3. Erro: "Port 3000 already in use"

**Causa:** Outra aplicação está usando a porta 3000

**Solução (Windows):**
```bash
netstat -ano | findstr :3000
taskkill /PID <PID> /F
npm start
```

**Solução (Mac/Linux):**
```bash
lsof -i :3000
kill -9 <PID>
npm start
```

**Ou use outra porta:**
```bash
PORT=3001 npm start
```

---

### 4. Erro: "Port 5000 already in use"

**Causa:** Outra aplicação está usando a porta 5000

**Solução (Windows):**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
python run.py
```

**Solução (Mac/Linux):**
```bash
lsof -i :5000
kill -9 <PID>
python run.py
```

**Ou mude a porta em backend/run.py:**
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

### 5. Erro: "psycopg2 error - connection refused"

**Causa:** PostgreSQL não está instalado ou rodando

**Solução:**

1. **Instale PostgreSQL:** https://www.postgresql.org/download/

2. **Inicie o PostgreSQL:**
   - Windows: Procure "SQL Shell" ou use `pg_ctl start`
   - Mac: `brew services start postgresql`
   - Linux: `sudo service postgresql start`

3. **Crie o banco de dados:**
```bash
createdb rede_social_dev
```

4. **Configure backend/.env:**
```env
DATABASE_URL=postgresql://seu_usuario:sua_senha@localhost:5432/rede_social_dev
```

---

### 6. Erro: "CORS error" no navegador

**Mensagem:** "Access to XMLHttpRequest has been blocked by CORS policy"

**Solução:** O backend já tem CORS configurado. Verifique:

1. Backend está rodando: `http://localhost:5000`
2. Frontend `.env` tem a URL correta:
```env
REACT_APP_API_URL=http://localhost:5000/api
```

3. Se o erro persiste, reinicie ambos os servidores.

---

### 7. Erro: "ModuleNotFoundError: No module named 'app'"

**Causa:** Ambiente virtual não está ativado ou estrutura de diretórios errada

**Solução:**
```bash
cd backend
source venv/bin/activate  # Ativar ambiente virtual
python run.py
```

---

### 8. Erro: "npm ERR! code EACCES"

**Causa:** Problemas de permissão no npm

**Solução:**
```bash
# Mac/Linux
sudo chown -R $(whoami) ~/.npm
npm cache clean --force

# Windows
npm cache clean --force
npm install -g npm@latest
```

---

### 9. Erro: ".env file not found"

**Solução:**
```bash
# Backend
cd backend
cp .env.example .env

# Frontend
cd frontend
cp .env.example .env
```

---

### 10. Erro: "Unexpected token < in JSON"

**Causa:** API está retornando HTML em vez de JSON (erro de servidor)

**Solução:**
1. Verifique se o backend está rodando
2. Verifique os logs do backend para erros
3. Reinicie o backend

---

## 🚀 Setup Completo (Começar do Zero)

### Windows:
```bash
# Executar script de setup
setup.bat
```

### Mac/Linux:
```bash
# Dar permissão ao script
chmod +x setup.sh

# Executar script de setup
./setup.sh
```

### Manual:

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edite .env com suas credenciais PostgreSQL
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
cp .env.example .env
npm start
```

---

## ✅ Checklist de Verificação

- [ ] Python 3.8+ instalado: `python --version`
- [ ] Node.js instalado: `npm --version`
- [ ] PostgreSQL instalado e rodando
- [ ] Backend rodando em: `http://localhost:5000`
- [ ] Frontend rodando em: `http://localhost:3000`
- [ ] `.env` configurado corretamente em ambos
- [ ] Nenhuma porta 3000 ou 5000 em uso
- [ ] Banco de dados `rede_social_dev` criado

---

## 🆘 Se nada funcionar:

1. **Limpe tudo e comece novamente:**
```bash
# Backend
cd backend
rm -rf venv
rm -rf __pycache__
rm .env

# Frontend
cd frontend
rm -rf node_modules
rm package-lock.json
rm .env
```

2. **Siga o setup completo acima**

3. **Se ainda não funcionar, envie:**
   - Sistema Operacional
   - Versão do Python (`python --version`)
   - Versão do Node.js (`npm --version`)
   - Mensagem de erro completa
   - Screenshot do erro

