<template>
  <section class="card overflow-hidden">
  <button
      type="button"
      class="w-full flex items-center justify-between gap-3 text-left -m-2 p-2 rounded-lg hover:bg-gray-50 active:bg-gray-100 dark:hover:bg-gray-800/90 dark:active:bg-gray-700/80 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400 focus-visible:ring-inset"
      :aria-expanded="aberto"
      :aria-controls="panelId"
      @click="alternar"
    >
      <div class="flex items-center gap-3 min-w-0">
        <div
          v-if="icon"
          class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
          :class="iconWrapperClass"
        >
          <component :is="icon" class="w-6 h-6" :class="iconClass" />
        </div>
        <div class="min-w-0 text-left">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 flex-wrap">
            <span>{{ titulo }}</span>
            <ContextualHelpIcon v-if="ajuda" :texto="ajuda" :label="`Ajuda sobre ${titulo}`" />
          </h2>
          <p v-if="subtitulo" class="text-sm text-gray-600 dark:text-gray-400 truncate">
            {{ subtitulo }}
          </p>
        </div>
      </div>
      <ChevronDownIcon
        class="w-5 h-5 text-gray-400 shrink-0 transition-transform duration-200 motion-reduce:transition-none"
        :class="{ 'rotate-180': aberto }"
        aria-hidden="true"
      />
    </button>

    <Transition name="bo-accordion">
      <div v-show="aberto" :id="panelId" class="pt-4">
        <slot />
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ChevronDownIcon } from '@heroicons/vue/24/outline'
import ContextualHelpIcon from '@/components/shared/ContextualHelpIcon.vue'

const props = defineProps({
  titulo: { type: String, required: true },
  subtitulo: { type: String, default: '' },
  icon: { type: Object, default: null },
  iconWrapperClass: {
    type: String,
    default: 'bg-gray-100 dark:bg-gray-700'
  },
  iconClass: {
    type: String,
    default: 'text-gray-600 dark:text-gray-300'
  },
  defaultOpen: { type: Boolean, default: false },
  ajuda: { type: String, default: '' },
  panelId: {
    type: String,
    default: () => `accordion-${Math.random().toString(36).slice(2, 9)}`
  }
})

const emit = defineEmits(['toggle'])

const aberto = ref(props.defaultOpen)

function alternar() {
  aberto.value = !aberto.value
  emit('toggle', aberto.value)
}
</script>

<style scoped>
.bo-accordion-enter-active,
.bo-accordion-leave-active {
  transition: opacity 0.25s ease, max-height 0.3s ease;
  max-height: 2400px;
  overflow: hidden;
}
.bo-accordion-enter-from,
.bo-accordion-leave-to {
  opacity: 0;
  max-height: 0;
}
@media (prefers-reduced-motion: reduce) {
  .bo-accordion-enter-active,
  .bo-accordion-leave-active {
    transition: none;
  }
}
</style>