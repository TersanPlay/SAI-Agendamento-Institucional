# Project Instructions


1. Todas as respostas devem ser fornecidas em português pt-br.
2. Utilize linguagem clara, objetiva e técnica, adequada ao contexto.
3. Mantenha consistência nos termos, evitando variações desnecessárias.
4. Sempre que possível, acrescente exemplos práticos para facilitar a compreensão.
5. Estruture as informações em tópicos, isso melhorar a legibilidade.

### Boas Práticas ao Remover um APP ou Módulo

1. Planejamento Prévio

Mapeie dependências: verifique se outros módulos usam dados de "Participantes" (ex.: relatórios, certificados, estatísticas).

Analise impacto nos usuários: considere se a remoção afetará fluxos existentes (cadastros, exportações, convites).


2. Arquitetura e Código

Modularização: mantenha o código do módulo isolado para facilitar remoção sem comprometer outros recursos.

Desativação gradual: primeiro desabilite o acesso ao módulo, depois remova o código.

Testes de regressão: rode a suíte de testes automatizados para garantir que nada foi quebrado.

3. Comunicação e Documentação

Atualize a documentação: manuais, help desk e treinamentos devem refletir a mudança.

4. Pós-remoção

Monitore erros: após retirar o módulo ou APP, acompanhe logs.


analise menus e interfaces: elimine links, botões ou rotas quebradas.