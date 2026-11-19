<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-200"
      leave-to-class="opacity-0"
    >
      <div
        v-if="aberto"
        class="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="$emit('fechar')"
      >
        <div
          class="bg-white dark:bg-gray-900 rounded-modal shadow-float w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col border border-gray-200 dark:border-gray-700"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-assinatura-titulo"
        >
          <!-- Header -->
          <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-500 to-primary-600 shrink-0">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3 min-w-0">
                <div class="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shrink-0">
                  <ShieldCheckIcon class="w-6 h-6 text-white" />
                </div>
                <div class="min-w-0">
                  <h2 id="modal-assinatura-titulo" class="text-2xl font-bold text-white">
                    Assinar despacho técnico
                  </h2>
                  <p class="text-primary-100 text-sm mt-0.5 truncate">
                    Protocolo
                    <span class="font-mono font-semibold text-white">{{ solicitacao?.protocoloCodigo || '—' }}</span>
                    · {{ solicitacao?.unidadeNome || 'Secretaria' }}
                    <span v-if="solicitacao?.unidadeSigla" class="opacity-90">({{ solicitacao.unidadeSigla }})</span>
                  </p>
                </div>
              </div>
              <button
                type="button"
                class="text-white/80 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/10 shrink-0"
                aria-label="Fechar"
                @click="$emit('fechar')"
              >
                <XMarkIcon class="w-6 h-6" />
              </button>
            </div>
          </div>

          <!-- Body -->
          <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Card OS / protocolo -->
            <div
              v-if="os"
              class="card bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border-2 border-primary-200 dark:border-primary-800"
            >
              <div class="flex items-start gap-4">
                <div class="flex-shrink-0 w-14 h-14 rounded-xl bg-primary-500 text-white flex items-center justify-center">
                  <BuildingOffice2Icon class="w-7 h-7" />
                </div>
                <div class="flex-1 min-w-0">
                  <div class="flex flex-wrap items-center gap-2 mb-2">
                    <span class="text-sm font-mono font-bold text-primary-600 dark:text-primary-400">
                      {{ solicitacao?.protocoloCodigo || '—' }}
                    </span>
                    <span v-if="os.servico" class="text-sm font-semibold text-gray-900 dark:text-white">
                      {{ os.servico }}
                    </span>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-700 dark:text-gray-300">
                    <div v-if="os.endereco" class="flex items-start gap-2 min-w-0">
                      <MapPinIcon class="w-4 h-4 text-gray-400 shrink-0 mt-0.5" />
                      <span class="break-words">{{ os.endereco }}</span>
                    </div>
                    <div v-if="os.cidadao?.nome" class="flex items-center gap-2 min-w-0">
                      <UserIcon class="w-4 h-4 text-gray-400 shrink-0" />
                      <span class="truncate">{{ os.cidadao.nome }}</span>
                    </div>
                  </div>
                  <p v-if="os.instrucaoOuvidoria" class="text-xs text-gray-600 dark:text-gray-400 mt-3 border-t border-gray-200 dark:border-gray-700 pt-3">
                    <span class="font-semibold uppercase tracking-wide">Instrução da ouvidoria:</span>
                    {{ os.instrucaoOuvidoria }}
                  </p>
                </div>
              </div>
            </div>

            <div class="alert-info">
              <InformationCircleIcon class="w-5 h-5 flex-shrink-0" />
              <div class="min-w-0">
                <strong class="font-semibold">Revisão antes da assinatura</strong>
                <p class="text-sm mt-1">
                  Solicitado por
                  <strong>{{ solicitacao?.solicitanteNome || '—' }}</strong>.
                  Confira o despacho, as evidências de campo e as observações da equipe antes de assinar ou rejeitar.
                </p>
              </div>
            </div>

            <!-- Despacho a assinar -->
            <div>
              <h3 class="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-3">
                <DocumentTextIcon class="w-5 h-5 text-primary-500" />
                Despacho técnico submetido
              </h3>
              <div class="rounded-lg border-2 border-primary-200 dark:border-primary-800 bg-white dark:bg-gray-800 p-4">
                <p class="text-sm text-gray-900 dark:text-white whitespace-pre-wrap leading-relaxed">
                  {{ solicitacao?.despachoTecnico || '—' }}
                </p>
                <p
                  v-if="os?.observacoesExtras && os.observacoesExtras !== solicitacao?.despachoTecnico"
                  class="text-sm text-gray-600 dark:text-gray-400 mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 whitespace-pre-wrap"
                >
                  <span class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 block mb-1">
                    Observações complementares (OS)
                  </span>
                  {{ os.observacoesExtras }}
                </p>
              </div>
            </div>

            <!-- Evidências -->
            <div v-if="os?.evidencias?.length">
              <GaleriaEvidencias :evidencias="os.evidencias" somente-leitura />
            </div>

            <!-- Obs equipe -->
            <div
              v-if="os?.observacoesExecucao"
              class="rounded-lg border border-success-200 dark:border-success-800 bg-success-50 dark:bg-success-900/20 p-4"
            >
              <p class="text-xs font-semibold uppercase tracking-wide text-success-700 dark:text-success-300 mb-2">
                Observações da equipe de campo
              </p>
              <p class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
                {{ os.observacoesExecucao }}
              </p>
            </div>

            <!-- Assinatura / rejeição -->
            <div
              v-if="etapa === 'assinar'"
              class="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4"
            >
              <label class="block text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Senha de assinatura digital *
              </label>
              <input
                v-model="senha"
                type="password"
                class="input max-w-md"
                autocomplete="current-password"
                placeholder="Confirme sua identidade"
                @keydown.enter.prevent="confirmarAssinar"
              />
              <p class="text-xs text-gray-600 dark:text-gray-400 mt-2">
                Use a <strong class="font-semibold">mesma senha do seu login</strong> no sistema (não é uma senha separada).
                Será gerado hash SHA-256 com validade jurídica conforme Lei 14.063/2020.
              </p>
            </div>

            <div v-else class="rounded-lg border border-danger-200 dark:border-danger-800 bg-danger-50 dark:bg-danger-900/20 p-4">
              <label class="block text-sm font-semibold text-gray-800 dark:text-gray-200 mb-2">
                Motivo da rejeição *
              </label>
              <textarea
                v-model="motivoRejeicao"
                class="input min-h-[100px]"
                placeholder="Descreva o que precisa ser corrigido no despacho..."
                rows="4"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-2">Mínimo de 10 caracteres.</p>
            </div>
          </div>

          <!-- Footer -->
          <div class="shrink-0 flex flex-col-reverse sm:flex-row sm:justify-end gap-2 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
            <button type="button" class="btn-secondary" :disabled="processando" @click="$emit('fechar')">
              Cancelar
            </button>
            <template v-if="etapa === 'assinar'">
              <button
                type="button"
                class="btn-secondary text-danger-600 border-danger-300 hover:bg-danger-50 dark:hover:bg-danger-900/20"
                :disabled="processando"
                @click="etapa = 'rejeitar'"
              >
                Rejeitar
              </button>
              <button
                type="button"
                class="btn-primary inline-flex items-center justify-center gap-2"
                :disabled="!senha.trim() || processando"
                @click="confirmarAssinar"
              >
                <ShieldCheckIcon class="w-5 h-5" />
                {{ processando ? 'Assinando…' : 'Assinar digitalmente' }}
              </button>
            </template>
            <template v-else>
              <button type="button" class="btn-secondary" @click="etapa = 'assinar'">
                Voltar
              </button>
              <button
                type="button"
                class="btn-primary bg-danger-600 hover:bg-danger-700 border-danger-600"
                :disabled="motivoRejeicao.trim().length < 10 || processando"
                @click="confirmarRejeitar"
              >
                Confirmar rejeição
              </button>
            </template>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import {
  XMarkIcon,
  ShieldCheckIcon,
  MapPinIcon,
  UserIcon,
  BuildingOffice2Icon,
  InformationCircleIcon,
  DocumentTextIcon
} from '@heroicons/vue/24/outline'
import GaleriaEvidencias from '@/components/backoffice/setorial/GaleriaEvidencias.vue'

const props = defineProps({
  aberto: Boolean,
  solicitacao: { type: Object, default: null },
  processando: { type: Boolean, default: false }
})

const emit = defineEmits(['fechar', 'assinar', 'rejeitar'])

const etapa = ref('assinar')
const senha = ref('')
const motivoRejeicao = ref('')

const os = computed(() => props.solicitacao?.ordemServico || null)

watch(
  () => props.aberto,
  (v) => {
    if (v) {
      etapa.value = 'assinar'
      senha.value = ''
      motivoRejeicao.value = ''
    }
  }
)

function confirmarAssinar() {
  if (!senha.value.trim()) return
  emit('assinar', { senha: senha.value })
}

function confirmarRejeitar() {
  const texto = motivoRejeicao.value.trim()
  if (texto.length < 10) return
  emit('rejeitar', { motivo: texto })
}
</script>