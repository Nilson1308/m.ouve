<template>
  <div class="space-y-6">
    <section class="card">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-lg bg-orange-100 dark:bg-orange-900 flex items-center justify-center">
          <MapIcon class="w-6 h-6 text-orange-600 dark:text-orange-400" />
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Mapa do incidente</h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Centroide e {{ superOs.quantidadeProtocolos }} chamados na região
          </p>
        </div>
      </div>
      <MapaSuperOSCluster
        :centroide="superOs.centroide"
        :filhos="superOs.protocolosFilhos"
        height="20rem"
      />
    </section>

    <section v-if="superOs.descricaoGeral" class="card">
      <h2 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Descrição consolidada</h2>
      <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap leading-relaxed">
        {{ superOs.descricaoGeral }}
      </p>
    </section>

    <section class="card">
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-1">
        Cidadãos afetados
      </h2>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Sanfonas com dados coletados e chat de cada protocolo filho
      </p>

      <div class="space-y-3 max-h-[32rem] overflow-y-auto pr-1">
        <div
          v-for="(filho, idx) in superOs.protocolosFilhos"
          :key="filho.id"
          class="rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden"
        >
          <button
            type="button"
            class="w-full flex items-center justify-between gap-3 px-4 py-3 bg-gray-50 dark:bg-gray-800/80 hover:bg-gray-100 dark:hover:bg-gray-750 text-left"
            @click="toggle(idx)"
          >
            <div class="min-w-0">
              <p class="text-sm font-semibold text-gray-900 dark:text-white">
                {{ filho.codigo }} · {{ filho.cidadao?.nome || 'Cidadão' }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 truncate">
                {{ filho.endereco || 'Sem endereço' }}
              </p>
            </div>
            <ChevronDownIcon
              class="w-5 h-5 text-gray-400 shrink-0 transition-transform"
              :class="{ 'rotate-180': abertos[idx] }"
            />
          </button>

          <div v-show="abertos[idx]" class="px-4 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 space-y-4">
            <div
              v-if="Object.keys(filho.dados_coletados || {}).length"
              class="overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg"
            >
              <table class="w-full text-sm">
                <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                  <tr v-for="(valor, campo) in filho.dados_coletados" :key="campo">
                    <td class="px-3 py-2 font-medium text-gray-600 dark:text-gray-400 w-1/3 bg-gray-50 dark:bg-gray-800">
                      {{ campo }}
                    </td>
                    <td class="px-3 py-2 text-gray-900 dark:text-white">{{ valor }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <ChatAuditoria :historico="filho.historico_chat || []" />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { MapIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'
import MapaSuperOSCluster from './MapaSuperOSCluster.vue'
import ChatAuditoria from '@/components/backoffice/protocolo/ChatAuditoria.vue'

defineProps({
  superOs: { type: Object, required: true }
})

const abertos = reactive({})

function toggle(idx) {
  abertos[idx] = !abertos[idx]
}
</script>