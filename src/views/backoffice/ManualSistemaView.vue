<template>
  <div class="px-4 sm:px-6 lg:px-8 py-8 max-w-5xl mx-auto">
    <header
      class="mb-8 rounded-2xl border border-slate-200/80 dark:border-slate-700/80 bg-white/80 dark:bg-slate-900/70 backdrop-blur-xl p-6 shadow-sm"
    >
      <div class="flex items-start gap-4">
        <div class="p-3 rounded-xl bg-gradient-to-br from-primary-500/20 to-cyan-500/20 border border-primary-500/30">
          <BookOpenIcon class="w-8 h-8 text-primary-600 dark:text-primary-400" aria-hidden="true" />
        </div>
        <div>
          <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Manual do Sistema</h1>
          <p class="text-sm text-slate-600 dark:text-slate-400 mt-1 max-w-2xl leading-relaxed">
            Guia operacional do M.Ouve (Ouv.IA) para gestores e servidores. Consulte quando precisar relembrar fluxos, painéis ou permissões.
          </p>
        </div>
      </div>
    </header>

    <div
      class="flex flex-wrap gap-2 p-1 rounded-xl bg-slate-100 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 mb-6"
      role="tablist"
      aria-label="Seções do manual"
    >
      <button
        v-for="sec in secoes"
        :key="sec.id"
        type="button"
        role="tab"
        :aria-selected="abaAtiva === sec.id"
        :aria-controls="`painel-${sec.id}`"
        class="flex items-center gap-2 flex-1 min-w-[10rem] justify-center py-2.5 px-3 rounded-lg text-sm font-semibold transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
        :class="
          abaAtiva === sec.id
            ? 'bg-white dark:bg-slate-900 text-primary-600 dark:text-primary-400 shadow-sm'
            : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
        "
        @click="abaAtiva = sec.id"
      >
        <component :is="sec.icon" class="w-5 h-5 shrink-0" aria-hidden="true" />
        <span class="truncate">{{ sec.tituloCurto }}</span>
      </button>
    </div>

    <section
      v-for="sec in secoes"
      v-show="abaAtiva === sec.id"
      :id="`painel-${sec.id}`"
      :key="sec.id"
      role="tabpanel"
      :aria-labelledby="`tab-${sec.id}`"
      class="space-y-4"
    >
      <article
        v-for="(bloco, idx) in sec.blocos"
        :key="idx"
        class="rounded-xl border border-slate-200/80 dark:border-slate-700/80 bg-white/90 dark:bg-slate-900/60 backdrop-blur-md p-5 shadow-sm"
      >
        <h2 class="text-base font-semibold text-slate-900 dark:text-white flex items-center gap-2 mb-2">
          <component :is="bloco.icon || sec.icon" class="w-5 h-5 text-primary-500 dark:text-primary-400 shrink-0" aria-hidden="true" />
          {{ bloco.titulo }}
        </h2>
        <p
          v-for="(paragrafo, pIdx) in bloco.paragrafos"
          :key="pIdx"
          class="text-sm text-slate-600 dark:text-slate-300 leading-relaxed"
          :class="{ 'mt-2': pIdx > 0 }"
        >
          {{ paragrafo }}
        </p>
        <ul v-if="bloco.itens?.length" class="mt-3 space-y-2 list-disc list-inside text-sm text-slate-600 dark:text-slate-300">
          <li v-for="(item, iIdx) in bloco.itens" :key="iIdx">{{ item }}</li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  BookOpenIcon,
  ChartBarSquareIcon,
  ClipboardDocumentListIcon,
  WrenchScrewdriverIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

const abaAtiva = ref('visao')

const secoes = [
  {
    id: 'visao',
    tituloCurto: 'Dashboards',
    icon: ChartBarSquareIcon,
    blocos: [
      {
        titulo: 'Visão Executiva — TMA e SLA',
        paragrafos: [
          'O painel de Eficiência consolida indicadores de desempenho: TMA (tempo médio de atendimento), taxa de SLA cumprido, protocolos em atraso e unidades com gargalos.',
          'Use os ícones de ajuda (i) nos cartões para entender cada métrica. Atualize os dados quando precisar apresentar números em reuniões.'
        ]
      },
      {
        titulo: 'Matriz de Qualidade e mapas',
        icon: ChartBarSquareIcon,
        paragrafos: [
          'A matriz cruza volume, satisfação (CSAT) e tempo por unidade. A Visão Territorial e os clusters de IA ajudam a enxergar demandas geográficas e oportunidades de Super OS.'
        ]
      },
      {
        titulo: 'Triagem e bloqueios (inelegibilidade)',
        icon: ShieldCheckIcon,
        paragrafos: [
          'Mostra sessões barradas pela IA por regras de elegibilidade — reduz carga na fila humana e documenta o “escudo” automático de triagem.'
        ]
      }
    ]
  },
  {
    id: 'mesa',
    tituloCurto: 'Mesa / Kanban',
    icon: ClipboardDocumentListIcon,
    blocos: [
      {
        titulo: 'Colunas do Kanban',
        paragrafos: [
          'Novos/Triagem: protocolos recém-abertos. Em Andamento: scatter-gather com setores trabalhando. Aguardando validação: gather completo, pronto para resposta ao cidadão. Concluídos: encerrados ou arquivados.'
        ],
        itens: [
          'Despache para acionar secretarias (scatter).',
          'Valide apenas quando todos os nós estiverem encerrados.',
          'Use o mapa de clusters para criar Super OS e agrupar demandas similares.'
        ]
      },
      {
        titulo: 'Super OS (incidente mestre)',
        paragrafos: [
          'Protocolos integrados à Super OS têm gestão centralizada. A âncora perde despacho individual — o trabalho ocorre no incidente mestre para ganho de escala em crises ou lotes.'
        ]
      }
    ]
  },
  {
    id: 'catalogo',
    tituloCurto: 'Catálogo',
    icon: WrenchScrewdriverIcon,
    blocos: [
      {
        titulo: 'Form Builder e serviços',
        paragrafos: [
          'Em Configurações → Catálogo, crie ou edite serviços com o construtor visual: seções, campos, regras de elegibilidade e versões.',
          'Use o sandbox de chat para testar o fluxo conversacional antes de publicar. Modelos da biblioteca aceleram novos serviços.'
        ],
        itens: [
          'Defina unidade responsável e SLA por serviço.',
          'Marque se o serviço permite clusterização para IA.',
          'Mantenha textos padrão alinhados às respostas oficiais.'
        ]
      }
    ]
  },
  {
    id: 'rbac',
    tituloCurto: 'Permissões',
    icon: ShieldCheckIcon,
    blocos: [
      {
        titulo: 'RBAC e segregação por unidade',
        paragrafos: [
          'Cada perfil de acesso carrega permissões granulares (ex.: mesa_trabalho.ler, painel_setorial.ler, configuracoes.ler). O escopo de dados limita protocolos e dashboards à secretaria/unidade do servidor.',
          'Super administradores enxergam o ambiente completo; gestores de unidade veem apenas o que pertence à sua pasta organizacional.'
        ],
        itens: [
          'Painel Setorial: fila de OS da própria secretaria.',
          'Notificações internas: eventos de despacho e formalização relevantes ao seu papel.',
          'Sem permissão adequada, o sistema redireciona para Acesso negado — solicite ajuste ao administrador.'
        ]
      }
    ]
  }
]
</script>