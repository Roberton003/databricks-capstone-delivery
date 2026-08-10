# Contributing

Este documento guia como contribuir para este projeto.

## 📝 Como contribuir

Este é um projeto de conclusão do Databricks AI Bootcamp. O código é mantido como portfolio profissional.

### Reportando Bugs

Se encontrar um bug:

1. Verifique se já foi reportado em [Issues](../../issues)
2. Se não, crie um issue com:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. real
   - Ambiente (Python, OS, versões)

### Sugerindo Melhorias

Para melhorias:

1. Abra um issue descrevendo o problema/ideia
2. Discuta a abordagem antes de implementar
3. Se aprovado, envie um PR com:
   - Testes (se aplicável)
   - Documentação atualizada
   - Commit messages claras

## 🏗️ Desenvolvimento

### Setup Local (para desenvolvimento)

Este projeto é projetado para rodar no Databricks Workspace. Para desenvolvimento local:

```bash
# 1. Clone este repositório
git clone https://github.com/SEU_USUARIO/databricks-capstone-delivery.git
cd databricks-capstone-delivery

# 2. Crie e ative ambiente virtual
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure secrets (apenas para desenvolvimento local)
python setup_secrets.py
```

### Testes

```bash
# Validar sintaxe Python
python -m compileall .

# Validar YAML
python -c "import yaml; yaml.safe_load(open('app.yaml'))"
```

## 🔄 Pull Requests

1. Crie uma branch para sua feature: `git checkout -b feature/nome-da-feature`
2. Commit suas mudanças: `git commit -m "feat: adiciona nova feature"`
3. Push para a branch: `git push origin feature/nome-da-feature`
4. Abra um Pull Request

### Padrão de Commit

Este projeto usa [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

```
<tipo>: <descrição>

[opcional corpo]

[opcional footer]
```

Tipos:
- `feat`: nova feature
- `fix`: correção de bug
- `docs`: apenas mudanças em documentação
- `style`: mudanças que não afetam o significado (formatação, pontos e vírgulas, etc)
- `refactor`: mudança de código que não corrige bug nem adiciona feature
- `perf`: mudança de código que melhora performance
- `test`: adição ou correção de testes
- `chore`: tarefas de manutenção

## 📋 Checklist de PR

- [ ] Testes passando (se aplicável)
- [ ] Documentação atualizada
- [ ] ChangeLog atualizado (para versões)
- [ ] Commit messages seguem padrão
- [ ] PR tem título claro e descritivo

## 🧪 Testes de Qualidade

Antes de submeter:

```bash
# 1. Sintaxe Python
python -m compileall .

# 2. Sintaxe YAML
python -c "import yaml; [yaml.safe_load(open(f)) for f in ['app.yaml', 'databricks.yml']]"

# 3. Código estilo (flakes se instalado)
flake8 .  # opcional
```

## 📞 Contato

Para dúvidas sobre este projeto:

- [Issues](../../issues)
- [Email](mailto:roberto@example.com)

---

*Este projeto foi desenvolvido como parte do Databricks AI Bootcamp.*