<template>
  <div class="min-h-screen pb-24 bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 high-contrast:from-black high-contrast:to-black">
    <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/95 dark:bg-gray-900/95 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft safe-area-inset-top">
      <div class="px-4 py-3 flex items-center gap-3">
        <button type="button" class="btn-icon flex-shrink-0 min-h-[44px] min-w-[44px]" aria-label="Voltar ao perfil" @click="voltar">
          <ChevronLeftIcon class="w-6 h-6" aria-hidden="true" />
        </button>
        <div class="flex-1 min-w-0">
          <h1 class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Central de Ajuda
          </h1>
          <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white">
            Tudo o que você precisa para usar o M.Ouve com tranquilidade
          </p>
        </div>
        <QuestionMarkCircleIcon class="w-8 h-8 text-primary-500 dark:text-primary-400 shrink-0 opacity-80" aria-hidden="true" />
      </div>
    </header>

    <main id="conteudo-principal" tabindex="-1" class="px-4 py-6 max-w-2xl mx-auto space-y-4">
      <section class="card bg-primary-50/60 dark:bg-primary-950/30 border border-primary-200/80 dark:border-primary-800/50 p-4" aria-labelledby="intro-ajuda">
        <h2 id="intro-ajuda" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-1">
          Olá! Estamos aqui para ajudar
        </h2>
        <p class="text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white leading-relaxed">
          O M.Ouve é o canal digital da ouvidoria. Abaixo você encontra respostas rápidas sobre solicitações, protocolos, chat com a assistente e notificações.
        </p>
      </section>

      <div class="space-y-3" role="list" aria-label="Perguntas frequentes">
        <div v-for="item in faq" :key="item.id" role="listitem">
          <PwaFaqItem
            :id-base="item.id"
            :pergunta="item.pergunta"
            :resposta="item.resposta"
          />
        </div>
      </div>

      <p class="text-xs text-center text-gray-500 dark:text-gray-400 pt-4">
        Precisa de mais apoio? Procure a ouvidoria do município pelos canais oficiais de atendimento presencial.
      </p>
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ChevronLeftIcon, QuestionMarkCircleIcon } from '@heroicons/vue/24/outline'
import PwaFaqItem from '@/components/pwa/PwaFaqItem.vue'

const router = useRouter()

const faq = [
  {
    id: 'nova-solicitacao',
    pergunta: 'Como abrir uma nova solicitação?',
    resposta:
      'Toque em Nova na barra inferior, escolha o tipo de serviço (categoria) e siga o assistente. Você pode conversar em linguagem natural, enviar fotos e indicar o local. Ao final, o sistema gera seu protocolo.'
  },
  {
    id: 'acompanhar',
    pergunta: 'Como acompanhar o andamento do meu protocolo?',
    resposta:
      'No Início, veja a lista dos seus protocolos. Toque em um deles para ver detalhes, etapas e respostas da prefeitura. Você também pode receber avisos por notificação quando o status mudar.'
  },
  {
    id: 'chat-ia',
    pergunta: 'Como interagir com a Inteligência Artificial no chat?',
    resposta:
      'Responda às perguntas da assistente com calma. Use os botões de opção quando aparecerem, envie localização ou fotos se solicitado e revise o resumo antes de confirmar. Se demorar um pouco, aguarde — a IA está processando sua mensagem.'
  },
  {
    id: 'notificacoes',
    pergunta: 'Como ativar as notificações no meu celular?',
    resposta:
      'Abra Avisos ou o detalhe do protocolo e toque em Ativar notificações. No iPhone, instale o app pela opção Compartilhar → Adicionar à Tela de Início antes de ativar os avisos push.'
  },
  {
    id: 'csat',
    pergunta: 'Como avaliar o atendimento (satisfação)?',
    resposta:
      'Quando sua solicitação for concluída, abra o protocolo. Você verá a opção de avaliar com nota e comentário. Sua opinião ajuda a melhorar os serviços públicos — leva menos de um minuto.'
  }
]

function voltar() {
  router.push({ name: 'pwa-perfil' })
}
</script>