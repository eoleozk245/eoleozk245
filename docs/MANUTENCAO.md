# Como manter este perfil

Guia rápido de como cada parte do perfil funciona e como mexer nela.

## Mapa dos arquivos

| Arquivo / pasta | O que é |
| --- | --- |
| `README.md` | A página do perfil. Edite à mão. |
| `assets/` | SVGs estáticos (banner, cabeçalhos de seção, cards, rodapé). **Gerados** por `scripts/build_assets.py`. Para mudar o nome de uma seção, edite a lista `SECTIONS` nesse script. |
| `scripts/theme.py` | Cores e fontes. Mudar aqui muda o visual de todos os SVGs. |
| `scripts/build_assets.py` | Gera os SVGs de `assets/`. Rodar na sua máquina quando quiser mudar algo. |
| `scripts/generate_dashboard.py` | Roda no GitHub Actions. Gera `overview.svg` e `activity.svg` com dados reais da API e põe fundo escuro na cobrinha. |
| `.github/workflows/profile-assets.yml` | O workflow (cobrinha + dashboard). |
| Branch `output` | Criado pelo workflow. Guarda `snake-dark.svg`, `overview.svg` e `activity.svg`. **Não edite à mão**, ele é recriado a cada execução. |

## O workflow

- **Quando roda:** todo dia (06:17 UTC), a cada push em `main` que mexa no workflow ou nos scripts, e manualmente.
- **Rodar na mão:** aba **Actions** → **Profile assets** → **Run workflow**.
- **Permissões:** só `contents: write` (para atualizar o branch `output`). Nenhum segredo é usado: o `GITHUB_TOKEN` é fornecido pelo próprio GitHub.
- **Se falhar:** os arquivos antigos do branch `output` continuam no ar. Abra a execução com ❌ na aba Actions e leia o log do passo que falhou.
- **Atenção:** o GitHub pausa workflows agendados em repositórios públicos sem atividade por 60 dias. Se isso acontecer, é só reativar na aba Actions ou clicar em **Run workflow**.

## Serviços externos usados no README

| Serviço | Onde aparece | Se sair do ar |
| --- | --- | --- |
| [github-readme-stats](https://github.com/anuraghazra/github-readme-stats) (`github-readme-stats.vercel.app`) | Card de estatísticas e card de linguagens | Os dois cards ficam quebrados. Dá para hospedar a própria instância no Vercel. |
| [streak-stats](https://github.com/DenverCoder1/github-readme-streak-stats) (`streak-stats.demolab.com`) | Card de sequência | Só esse card quebra. |
| [Skill Icons](https://skillicons.dev) | Ícones de linguagens e ferramentas | Os ícones quebram. Alternativa: Devicon via jsDelivr. |
| [Skills Icons (syvixor)](https://skills.syvixor.com) | Ícones de contato (Instagram e WhatsApp). É um fork do Skill Icons que tem o WhatsApp, que o original não tem. | Os ícones de contato quebram, mas os links continuam certos. Alternativa: trocar pelo Skill Icons (Instagram) ou por um badge do Shields.io. |
| [Shields.io](https://shields.io) | Badges de interesses (seção Sobre mim) | Os badges quebram. |
| [Platane/snk](https://github.com/Platane/snk) | Cobrinha (dentro do workflow) | O workflow falha e a cobrinha antiga continua no ar. |

Esses cards têm cache: depois de um commit ou contribuição nova, pode levar algumas horas para o número mudar.

> O `github-readme-activity-graph` foi testado e **não** foi usado porque estava fora do ar (erro 402). O gráfico de atividade é gerado pelo próprio workflow.

## Adicionar um projeto novo

1. Abra `scripts/build_assets.py` e acrescente um item na lista `PROJECTS` (nome do repositório, 3 linhas curtas de descrição e as tecnologias). Escreva só o que dá para comprovar no repositório.
2. Rode `python3 scripts/build_assets.py` (Python 3, sem instalar nada).
3. No `README.md`, troque o card `placeholder.svg` pelo novo card, seguindo o modelo dos outros (link para o repositório + `<img src="assets/cards/NOME.svg">`).
4. Faça o commit.

## Atualizar contatos

Os contatos ficam na seção **Contato** do `README.md`, em grupos com título (**Redes sociais** e **Mensagens**) e só com ícones, no mesmo estilo de quadradinho das tecnologias. Para acrescentar LinkedIn ou e-mail, ponha o ícone dentro do grupo certo, ao lado dos que já existem:

```html
<a href="https://www.instagram.com/eoleozk"><img src="https://skills.syvixor.com/api/icons?i=instagram&theme=dark" alt="Instagram" /></a>
<a href="https://www.linkedin.com/in/SEU-USUARIO"><img src="https://skills.syvixor.com/api/icons?i=linkedin&theme=dark" alt="LinkedIn" /></a>
```

```html
<a href="https://wa.link/qjufj8"><img src="https://skills.syvixor.com/api/icons?i=whatsapp&theme=dark" alt="WhatsApp" /></a>
<a href="mailto:SEU-EMAIL"><img src="https://skills.syvixor.com/api/icons?i=gmail&theme=dark" alt="E-mail" /></a>
```

## Mudar o visual

Edite as cores em `scripts/theme.py`, rode `python3 scripts/build_assets.py` e faça o commit. Para o dashboard e a cobrinha, a próxima execução do workflow já aplica as cores novas.
