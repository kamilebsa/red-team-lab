# Red Team Lab

Laboratório educacional de reconhecimento controlado para estudos de
Segurança da Informação e operações Red Team autorizadas.

## Funcionalidades

- Verificação de portas TCP no loopback IPv4.
- Rejeição de alvos que não sejam endereços de loopback.
- Validação de portas entre 1 e 65535.
- Relatórios JSON com data, alvo e resultados.
- Testes automatizados com unittest.

## Requisitos

- Python 3.10 ou superior.
- Nenhuma dependência externa para o módulo atual.

## Execução

Verificar as portas padrão:

    python -m src.recon.port_check

Escolher as portas:

    python -m src.recon.port_check --ports 22,80,8000,8080

O alvo padrão é 127.0.0.1. Nesta versão, outros endereços são
rejeitados.

## Testes

    python -m unittest discover -s tests -v

## Relatórios

O relatório é salvo em reports/port-check.json.
Os relatórios gerados localmente não são enviados ao Git.

## Limitações

- Verifica apenas conexões TCP.
- Não identifica com certeza o serviço de uma porta.
- "closed_or_filtered" não diferencia porta fechada de filtrada.
- Os testes de portas abertas e fechadas usam mocks.
- Não é uma ferramenta completa de varredura ou exploração.

Utilize somente sistemas próprios ou com autorização explícita.
