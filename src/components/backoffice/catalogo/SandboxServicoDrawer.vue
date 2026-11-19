<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="aberto"
        class="fixed inset-0 z-[10050] flex justify-end"
        role="dialog"
        aria-modal="true"
        aria-labelledby="sandbox-drawer-title"
      >
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('fechar')" />

        <Transition
          appear
          enter-active-class="transition-transform duration-300 ease-out"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transition-transform duration-200 ease-in"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <div
            v-if="aberto"
            class="relative w-full max-w-4xl h-full bg-white dark:bg-gray-900 shadow-2xl flex flex-col"
          >
            <header
              class="flex-shrink-0 px-6 py-5 border-b border-gray-200 dark:border-gray-800 bg-gradient-to-r from-gray-50 to-white dark:from-gray-900 dark:to-gray-900"
            >
              <div class="flex items-start justify-between gap-4">
                <div>
                  <h2 id="sandbox-drawer-title" class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <DevicePhoneMobileIcon class="w-6 h-6 text-primary-600" />
                    Testar fluxo (sandbox)
                  </h2>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    Simule a conversa do cidadão sem publicar no PWA. Os dados abaixo vêm do último
                    <strong class="font-semibold">save</strong> deste serviço.
                  </p>
                </div>
                <button
                  type="button"
                  class="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-800 transition-colors"
                  aria-label="Fechar sandbox"
                  @click="$emit('fechar')"
                >
                  <XMarkIcon class="w-6 h-6 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
            </header>

            <div class="flex-1 min-h-0 p-6 overflow-y-auto">
              <SandboxChat
                v-if="servicoId"
                :key="`${servicoId}-${sandboxChatKey}`"
                :servico-id="servicoId"
                :nome-servico="nomeServico"
                :tem-rascunho-pendente="temRascunhoPendente"
              />
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, watch } from 'vue'
import { DevicePhoneMobileIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import SandboxChat from './SandboxChat.vue'

const props = defineProps({
  aberto: { type: Boolean, default: false },
  servicoId: { type: String, required: true },
  nomeServico: { type: String, default: 'Serviço' },
  temRascunhoPendente: { type: Boolean, default: false }
})

defineEmits(['fechar'])

const sandboxChatKey = ref(0)

watch(
  () => props.aberto,
  (open) => {
    if (open) sandboxChatKey.value += 1
  }
)
</script>