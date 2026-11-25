<template>
  <div class="space-y-6">
    <ProtocoloDiligenciaBackoffice
      :protocolo="protocolo"
      @abrir-modal="$emit('abrir-diligencia')"
      @atualizado="$emit('atualizar-diligencia')"
    />

    <ProtocoloReaberturasCard :protocolo="protocolo" />

    <!-- Vitais: sempre visíveis -->
    <ProtocoloSlaCobrancaResumo :protocolo="protocolo" />

    <section class="card" aria-labelledby="titulo-cidadao">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
          <UserIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h2 id="titulo-cidadao" class="text-lg font-semibold text-gray-900 dark:text-white">
            Dados do Cidadão
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">Contato e titular do protocolo</p>
        </div>
      </div>
      <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
        <div>
          <dt class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Nome</dt>
          <dd class="mt-1 font-semibold text-gray-900 dark:text-white">{{ protocolo.cidadao?.nome || '—' }}</dd>
        </div>
        <div>
          <dt class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Telefone</dt>
          <dd class="mt-1 text-gray-900 dark:text-white">{{ protocolo.cidadao?.telefone || 'Não informado' }}</dd>
        </div>
        <div v-if="protocolo.cidadao?.email" class="sm:col-span-2">
          <dt class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">E-mail</dt>
          <dd class="mt-1 text-gray-900 dark:text-white break-all">{{ protocolo.cidadao.email }}</dd>
        </div>
      </dl>
    </section>

    <section
      v-if="protocolo.equipamento"
      class="card"
      aria-labelledby="titulo-equipamento"
    >
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-lg bg-cyan-100 dark:bg-cyan-900/30 flex items-center justify-center">
          <BuildingOffice2Icon class="w-6 h-6 text-cyan-700 dark:text-cyan-300" />
        </div>
        <div>
          <h2 id="titulo-equipamento" class="text-lg font-semibold text-gray-900 dark:text-white">
            Equipamento público
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">Local vinculado ao protocolo</p>
        </div>
      </div>
      <dl class="grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm">
        <div>
          <dt class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Nome</dt>
          <dd class="mt-1 font-semibold text-gray-900 dark:text-white">{{ protocolo.equipamento.nome }}</dd>
        </div>
        <div>
          <dt class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Tipo</dt>
          <dd class="mt-1 text-gray-900 dark:text-white">{{ labelTipoEquipamento(protocolo.equipamento.tipo) }}</dd>
        </div>
        <div>
          <dt class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">Bairro</dt>
          <dd class="mt-1 text-gray-900 dark:text-white">{{ protocolo.equipamento.bairro || '—' }}</dd>
        </div>
      </dl>
    </section>

    <section class="card" aria-labelledby="titulo-demanda">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-lg bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center">
          <DocumentTextIcon class="w-6 h-6 text-amber-600 dark:text-amber-400" />
        </div>
        <div>
          <h2 id="titulo-demanda" class="text-lg font-semibold text-gray-900 dark:text-white">
            Descrição da Demanda
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">Resumo registrado na abertura</p>
        </div>
      </div>
      <p class="text-sm text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
        {{ protocolo.descricao?.trim() || 'Nenhuma descrição textual foi registrada para este protocolo.' }}
      </p>
      <p
        v-if="protocolo.resposta_cidadao"
        class="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300"
      >
        <span class="font-semibold text-gray-900 dark:text-white">Última resposta oficial:</span>
        {{ protocolo.resposta_cidadao }}
      </p>
    </section>

    <!-- Secundários (colapsáveis) -->
    <BackofficeAccordion
      titulo="Dados coletados pela IA"
      :subtitulo="subtituloDadosIa"
      :icon="CpuChipIcon"
      icon-wrapper-class="bg-primary-100 dark:bg-primary-900"
      icon-class="text-primary-600 dark:text-primary-400"
      :default-open="false"
      ajuda="Campos estruturados extraídos do chat — úteis para triagem e despacho."
    >
      <div
        v-if="!temDadosColetados"
        class="text-sm text-gray-500 dark:text-gray-400 py-4 text-center border border-dashed border-gray-300 dark:border-gray-600 rounded-lg"
      >
        Nenhum dado estruturado foi registrado neste protocolo.
      </div>
      <div v-else class="overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg">
        <table class="w-full divide-y divide-gray-200 dark:divide-gray-700">
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800">
            <tr
              v-for="(valor, campo) in protocolo.dados_coletados"
              :key="campo"
              class="hover:bg-gray-50 dark:hover:bg-gray-700/40 active:bg-gray-100 dark:active:bg-gray-700/60 transition-colors"
            >
              <td class="px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 w-1/3">
                {{ campo }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">{{ valor }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </BackofficeAccordion>

    <BackofficeAccordion
      titulo="Localização e mapa"
      :subtitulo="enderecoLinha"
      :icon="MapPinIcon"
      icon-wrapper-class="bg-success-100 dark:bg-success-900/50"
      icon-class="text-success-600 dark:text-success-400"
      :default-open="false"
      ajuda="Endereço, referência e coordenadas para equipes de campo."
      @toggle="onMapaAccordionToggle"
    >
      <div class="mb-4 p-4 bg-gray-50 dark:bg-gray-800/80 rounded-lg border border-gray-200 dark:border-gray-700">
        <div class="space-y-2">
          <div class="flex items-start gap-3">
            <BuildingOffice2Icon class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ enderecoLinha }}</p>
              <p v-if="protocolo.localizacao.complemento" class="text-sm text-gray-600 dark:text-gray-400">
                {{ protocolo.localizacao.complemento }}
              </p>
              <p v-if="linhaBairroCidade" class="text-sm text-gray-600 dark:text-gray-400">{{ linhaBairroCidade }}</p>
              <p v-if="protocolo.localizacao.cep" class="text-sm text-gray-500">CEP: {{ protocolo.localizacao.cep }}</p>
            </div>
          </div>
          <div
            v-if="protocolo.localizacao.pontos_referencia"
            class="flex items-start gap-3 pt-2 border-t border-gray-200 dark:border-gray-600"
          >
            <InformationCircleIcon class="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
            <div>
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300">Ponto de referência</p>
              <p class="text-sm text-gray-600 dark:text-gray-400">{{ protocolo.localizacao.pontos_referencia }}</p>
            </div>
          </div>
        </div>
      </div>
      <LocationMap
        v-if="temCoordenadas"
        ref="mapaRef"
        :latitude="coordenadas.latitude"
        :longitude="coordenadas.longitude"
        :draggable="false"
        :zoom="16"
        height="16rem"
      />
      <div
        v-else
        class="relative h-48 flex items-center justify-center bg-gray-100 dark:bg-gray-800/60 rounded-lg border border-gray-300 dark:border-gray-600"
      >
        <h4 class="sr-only">Mapa indisponível</h4>
        <div class="text-center px-4">
          <MapIcon class="w-10 h-10 text-gray-400 mx-auto mb-2 opacity-60" />
          <p class="text-sm text-gray-600 dark:text-gray-400">Coordenadas não disponíveis para exibir o mapa.</p>
        </div>
      </div>
      <p v-if="temCoordenadas" class="mt-2 text-xs text-gray-500 dark:text-gray-400 text-right">
        {{ coordenadasFormatadas }}
      </p>
    </BackofficeAccordion>

    <BackofficeAccordion
      v-if="anexosLista.length"
      titulo="Anexos e evidências"
      :subtitulo="`${anexosLista.length} arquivo(s) no chat`"
      :icon="PhotoIcon"
      icon-wrapper-class="bg-indigo-100 dark:bg-indigo-900/40"
      icon-class="text-indigo-600 dark:text-indigo-400"
      :default-open="false"
      ajuda="Imagens e arquivos enviados pelo cidadão durante o atendimento."
    >
      <ul class="grid grid-cols-2 sm:grid-cols-3 gap-3">
        <li v-for="(anexo, idx) in anexosLista" :key="idx">
          <button
            type="button"
            class="block w-full rounded-lg overflow-hidden border border-gray-200 dark:border-gray-600 hover:opacity-90 dark:hover:border-primary-500/60 active:opacity-95 focus-visible:ring-2 focus-visible:ring-primary-500 dark:focus-visible:ring-primary-400"
            @click="abrirAnexo(anexo.url)"
          >
            <img :src="anexo.url" alt="Anexo da solicitação" class="w-full h-28 object-cover" loading="lazy" />
          </button>
        </li>
      </ul>
    </BackofficeAccordion>

    <BackofficeAccordion
      v-if="historicoTramitacao.length"
      titulo="Histórico de tramitações"
      :subtitulo="`${historicoTramitacao.length} evento(s)`"
      :icon="ClockIcon"
      :default-open="false"
      ajuda="Linha do tempo administrativa do protocolo no backoffice."
    >
      <ol class="relative border-l border-gray-200 dark:border-gray-700 ml-3 space-y-4">
        <li v-for="(ev, i) in historicoTramitacao" :key="i" class="pl-5 text-sm">
          <span class="absolute -left-1.5 mt-1.5 w-3 h-3 rounded-full bg-primary-500" aria-hidden="true" />
          <p class="font-medium text-gray-900 dark:text-white">{{ ev.titulo || ev.status || 'Atualização' }}</p>
          <p v-if="ev.descricao || ev.observacao" class="text-gray-600 dark:text-gray-400 mt-0.5">
            {{ ev.descricao || ev.observacao }}
          </p>
          <time v-if="ev.data" class="text-xs text-gray-500">{{ ev.data }}</time>
        </li>
      </ol>
    </BackofficeAccordion>

    <ChatAuditoria :historico="protocolo.historico_chat || []" />
  </div>
</template>

<script setup>
import ProtocoloDiligenciaBackoffice from '@/components/backoffice/protocolo/ProtocoloDiligenciaBackoffice.vue'
import ProtocoloReaberturasCard from '@/components/backoffice/protocolo/ProtocoloReaberturasCard.vue'
import ProtocoloSlaCobrancaResumo from '@/components/backoffice/protocolo/ProtocoloSlaCobrancaResumo.vue'
import { computed, ref, nextTick } from 'vue'
import {
  CpuChipIcon,
  MapPinIcon,
  BuildingOffice2Icon,
  InformationCircleIcon,
  MapIcon,
  UserIcon,
  DocumentTextIcon,
  PhotoIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'
import ChatAuditoria from './ChatAuditoria.vue'
import LocationMap from '@/components/pwa/LocationMap.vue'
import BackofficeAccordion from '@/components/backoffice/BackofficeAccordion.vue'
import { labelTipoEquipamento } from '@/constants/equipamentosPublicos'

defineEmits(['abrir-diligencia', 'atualizar-diligencia'])

const props = defineProps({
  protocolo: {
    type: Object,
    required: true
  }
})

const mapaRef = ref(null)

function onMapaAccordionToggle(aberto) {
  if (!aberto || !temCoordenadas.value) return
  nextTick(() => {
    mapaRef.value?.invalidateSize?.()
    requestAnimationFrame(() => {
      mapaRef.value?.invalidateSize?.()
      mapaRef.value?.recentralizar?.()
      setTimeout(() => {
        mapaRef.value?.invalidateSize?.()
        mapaRef.value?.recentralizar?.()
      }, 150)
    })
  })
}

const temDadosColetados = computed(() => {
  const dados = props.protocolo?.dados_coletados
  return dados && Object.keys(dados).length > 0
})

const subtituloDadosIa = computed(() =>
  temDadosColetados.value
    ? `${Object.keys(props.protocolo.dados_coletados).length} campo(s)`
    : 'Sem campos estruturados'
)

const historicoTramitacao = computed(() => props.protocolo?.historico_protocolo || [])

const anexosLista = computed(() => {
  const lista = []
  for (const msg of props.protocolo?.historico_chat || []) {
    if (msg.anexo?.url) lista.push(msg.anexo)
  }
  return lista
})

function abrirAnexo(url) {
  if (url) window.open(url, '_blank', 'noopener,noreferrer')
}

const coordenadas = computed(() => {
  const loc = props.protocolo?.localizacao || {}
  const lat = Number(loc.latitude)
  const lng = Number(loc.longitude)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return { latitude: null, longitude: null }
  }
  return { latitude: lat, longitude: lng }
})

const temCoordenadas = computed(
  () => coordenadas.value.latitude != null && coordenadas.value.longitude != null
)

const enderecoLinha = computed(() => {
  const loc = props.protocolo?.localizacao || {}
  const partes = [loc.endereco, loc.numero].filter(Boolean)
  if (partes.length) return partes.join(', ')
  return props.protocolo?.endereco || 'Endereço não informado'
})

const linhaBairroCidade = computed(() => {
  const loc = props.protocolo?.localizacao || {}
  const bairro = loc.bairro || props.protocolo?.bairro || ''
  const cidade = loc.cidade || ''
  const estado = loc.estado || ''
  if (!bairro && !cidade && !estado) return ''
  if (cidade && estado) {
    return bairro ? `${bairro} — ${cidade}/${estado}` : `${cidade}/${estado}`
  }
  return [bairro, cidade, estado].filter(Boolean).join(' — ')
})

const coordenadasFormatadas = computed(() => {
  if (!temCoordenadas.value) return ''
  const { latitude, longitude } = coordenadas.value
  return `Lat ${latitude.toFixed(5)}, Long ${longitude.toFixed(5)} · OpenStreetMap`
})
</script>

<style scoped>
tbody tr {
  transition: background-color 0.15s ease;
}
</style>