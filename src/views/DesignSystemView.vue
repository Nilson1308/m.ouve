<template>
  <div class="min-h-screen bg-gov-gray-light">
    <!-- Header -->
    <header class="bg-primary-500 text-white shadow-lg">
      <div class="px-4 py-6">
        <h1 class="text-2xl font-bold mb-2">M.Ouve - Design System</h1>
        <p class="text-primary-100">Sistema de cores e componentes v2.0</p>
      </div>
    </header>

    <main class="px-4 py-6 space-y-8 max-w-6xl mx-auto">
      
      <!-- Paleta Primary -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Paleta Primary</h2>
        <div class="grid grid-cols-5 md:grid-cols-11 gap-2">
          <div v-for="shade in [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]" :key="shade" class="text-center">
            <div :class="`bg-primary-${shade} h-16 rounded-lg`"></div>
            <span class="text-xs text-gray-600 mt-1 block">{{ shade }}</span>
          </div>
        </div>
      </section>

      <!-- Cores Semânticas -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Cores Semânticas</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <div class="bg-primary-500 h-16 rounded-lg flex items-center justify-center text-white font-medium">
              Primary
            </div>
          </div>
          <div>
            <div class="bg-success h-16 rounded-lg flex items-center justify-center text-white font-medium">
              Success
            </div>
          </div>
          <div>
            <div class="bg-warning h-16 rounded-lg flex items-center justify-center text-white font-medium">
              Warning
            </div>
          </div>
          <div>
            <div class="bg-danger h-16 rounded-lg flex items-center justify-center text-white font-medium">
              Danger
            </div>
          </div>
        </div>
      </section>

      <!-- Botões -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Botões</h2>
        <div class="flex flex-wrap gap-3">
          <button class="btn-primary">Primário</button>
          <button class="btn-secondary">Secundário</button>
          <button class="btn-success">Sucesso</button>
          <button class="btn-warning">Aviso</button>
          <button class="btn-danger">Perigo</button>
        </div>
      </section>

      <!-- Status Zeladoria -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Status - Zeladoria Urbana</h2>
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <StatusBadge status="triagem_ia" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Triagem automática pela IA</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="validacao" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Em validação humana</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="aguardando_equipe" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Aguardando designação de equipe</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="em_deslocamento" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Equipe a caminho do local</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="em_execucao" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Serviço sendo executado</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="concluido" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Serviço concluído</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="nao_procedente" tipo="zeladoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Solicitação não procedente</span>
          </div>
        </div>
      </section>

      <!-- Status Ouvidoria -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Status - Ouvidoria Institucional</h2>
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <StatusBadge status="triagem" tipo="ouvidoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Em triagem inicial</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="analise" tipo="ouvidoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Em análise detalhada</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="encaminhado" tipo="ouvidoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Encaminhado para setor responsável</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="respondido" tipo="ouvidoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Cidadão recebeu resposta</span>
          </div>
          <div class="flex items-center gap-3">
            <StatusBadge status="arquivado" tipo="ouvidoria" :show-icon="true" />
            <span class="text-sm text-gray-600">Manifestação arquivada</span>
          </div>
        </div>
      </section>

      <!-- Tipos de Manifestação -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Tipos de Manifestação</h2>
        <div class="flex flex-wrap gap-3">
          <span class="badge-manifestacao-denuncia">Denúncia</span>
          <span class="badge-manifestacao-reclamacao">Reclamação</span>
          <span class="badge-manifestacao-sugestao">Sugestão</span>
          <span class="badge-manifestacao-elogio">Elogio</span>
        </div>
      </section>

      <!-- Níveis de Urgência -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Níveis de Urgência (IA)</h2>
        <div class="space-y-3">
          <div class="flex items-center gap-3">
            <span class="badge-urgencia-baixa">Urgência Baixa</span>
            <span class="text-sm text-gray-600">Pode ser resolvido em até 15 dias</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="badge-urgencia-media">Urgência Média</span>
            <span class="text-sm text-gray-600">Deve ser resolvido em até 7 dias</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="badge-urgencia-alta">Urgência Alta</span>
            <span class="text-sm text-gray-600">Requer atenção em 48h</span>
          </div>
          <div class="flex items-center gap-3">
            <span class="badge-urgencia-critica">Urgência Crítica</span>
            <span class="text-sm text-gray-600">Requer atenção imediata</span>
          </div>
        </div>
      </section>

      <!-- Alertas -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Alertas</h2>
        <div class="space-y-3">
          <div class="alert-info">
            <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
            </svg>
            <div>
              <strong class="font-semibold">Informação</strong>
              <p class="text-sm mt-1">Esta é uma mensagem informativa padrão.</p>
            </div>
          </div>

          <div class="alert-success">
            <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <div>
              <strong class="font-semibold">Sucesso</strong>
              <p class="text-sm mt-1">Operação concluída com sucesso!</p>
            </div>
          </div>

          <div class="alert-warning">
            <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            <div>
              <strong class="font-semibold">Atenção</strong>
              <p class="text-sm mt-1">Revise as informações antes de continuar.</p>
            </div>
          </div>

          <div class="alert-danger">
            <svg class="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
            <div>
              <strong class="font-semibold">Erro</strong>
              <p class="text-sm mt-1">Ocorreu um erro ao processar sua solicitação.</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Exemplo de Card com Status -->
      <section class="card">
        <h2 class="text-xl font-bold text-gray-900 mb-4">Exemplo: Card de Protocolo</h2>
        
        <div :class="['card-interactive', getCardBorder('em_execucao')]">
          <div class="flex items-start justify-between mb-3">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="text-xs font-mono text-gray-600">PROT-2024-042</span>
                <StatusBadge status="em_execucao" tipo="zeladoria" :show-icon="true" />
              </div>
              <h3 class="font-semibold text-gray-900">Via Pública - Buraco na Rua</h3>
            </div>
            <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
              <MapIcon class="w-6 h-6 text-white" />
            </div>
          </div>

          <p class="text-sm text-gray-600 mb-3">
            Buraco grande na Avenida Principal, altura do número 500. 
            Oferece risco aos motoristas.
          </p>

          <div class="flex items-center justify-between text-xs text-gray-500">
            <span>Há 2 horas</span>
            <div class="flex items-center gap-2">
              <span class="badge-urgencia-media">Média</span>
              <div class="flex items-center gap-1">
                <MapPinIcon class="w-4 h-4" />
                <PaperClipIcon class="w-4 h-4" />
              </div>
            </div>
          </div>

          <div class="mt-3 pt-3 border-t border-gray-200">
            <div class="flex items-center gap-2 text-sm text-primary-600">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <span class="font-medium">Equipe de Pavimentação Norte</span>
            </div>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <div class="text-center text-sm text-gray-500 dark:text-gray-400 pb-8">
        <p class="font-semibold">M.Ouve Design System v2.0</p>
        <p class="mt-1">Consulte <code class="bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded">COLOR_SYSTEM.md</code> para documentação completa</p>
        <p class="mt-4 text-xs">Marca <strong>M.Ouve</strong></p>
      </div>
    </main>
  </div>
</template>

<script setup>
import StatusBadge from '@/components/shared/StatusBadge.vue'
import { useStatusColors } from '@/composables/useStatusColors'
import { MapIcon, MapPinIcon, PaperClipIcon } from '@heroicons/vue/24/outline'

const { getCardBorderClass } = useStatusColors()

function getCardBorder(status) {
  return getCardBorderClass(status, 'zeladoria')
}
</script>
