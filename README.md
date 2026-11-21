# AETHER

**AETHER** é um projeto experimental de interação gestual para Linux, criado para controlar ações do desktop por meio de movimentos das mãos.

A proposta é aproximar a interação física da navegação em ambientes de janelas: gestos podem acionar cliques, controlar o ponteiro, rolar conteúdo e interagir com janelas e layouts.

## Áreas do projeto

O código é organizado por responsabilidades:

- `vision/` — fundamentos de visão computacional.
- `pointer/` — controle e movimentação do ponteiro.
- `click/` — ações de clique.
- `scroll/` — rolagem.
- `gestures/` — interpretação de gestos.
- `window_move/` — interação com movimentação de janelas.
- `activation/` — ativação do sistema.
- `intents/` e `actions/` — intenção e execução de ações.

## Desenvolvimento

O projeto está em desenvolvimento ativo. A compatibilidade e o comportamento dos gestos dependem do ambiente Linux e do compositor utilizado.

Para executar a suíte de testes no ambiente de desenvolvimento:

```bash
PYTHONPATH=src pytest --ignore=test_scroll.py
```

## Objetivo

Construir uma camada de interação gestual modular, previsível e extensível para o desktop Linux.

---

Desenvolvido por [Hubert Ramos](https://github.com/HubertRamos).
