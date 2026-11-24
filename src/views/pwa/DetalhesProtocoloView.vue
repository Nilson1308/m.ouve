<template>
  <div class="min-h-screen pb-16 overflow-x-hidden max-w-[100vw]">
  <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft safe-area-inset">
      <div class="px-4 sm:px-6 py-3 flex items-center gap-2 sm:gap-3 min-w-0">
        <button type="button" @click="voltar" class="btn-icon shrink-0" aria-label="Voltar ao início">
          <ChevronLeftIcon class="w-5 h-5 text-gray-700 dark:text-gray-200 high-contrast:text-yellow-300" aria-hidden="true" />
        </button>
        <p class="flex-1 min-w-0 text-base sm:text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 truncate">
          Detalhes do protocolo
        </p>
        <div class="flex items-center gap-1 sm:gap-2 shrink-0">
          <PwaA11yMenu />
          <ThemeToggle surface="light" />
        </div>
      </div>
    </header>

    <div
      v-if="protocolosStore.loading"
      class="flex flex-col justify-center items-center py-24 gap-3"
      role="status"
      aria-live="polite"
    >
      <span class="sr-only">Carregando detalhes do protocolo</span>
      <div
        class="animate-spin motion-reduce:animate-none rounded-full h-12 w-12 border-4 border-primary-500 high-contrast:border-yellow-300 border-t-transparent"
        aria-hidden="true"
      />
    </div>

    <main
      v-else-if="!protocolo"
      id="conteudo-principal"
      tabindex="-1"
      class="px-6 py-12 max-w-lg mx-auto"
    >
      <div class="card text-center py-10 animate-scale-in motion-reduce:animate-none">
        <ExclamationCircleIcon class="w-16 h-16 mx-auto text-red-500 dark:text-red-400 mb-4" aria-hidden="true" />
        <h1 class="text-xl font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-2">
          Protocolo não encontrado
        </h1>
        <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white mb-6">
          O protocolo que você procura não existe ou foi removido.
        </p>
        <button type="button" @click="voltar" class="btn-primary min-h-[44px]">Voltar ao início</button>
      </div>
    </main>

    <main
      v-else
      id="conteudo-principal"
      tabindex="-1"
      class="px-4 sm:px-6 py-6 max-w-2xl mx-auto space-y-5 animate-fade-in motion-reduce:animate-none min-w-0"
    >
      <!-- Hero -->
      <section class="card p-0 overflow-hidden" aria-labelledby="sec-status-protocolo">
        <div
          class="relative px-5 py-6 sm:px-6 bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 dark:from-primary-700 dark:to-primary-900 high-contrast:from-black high-contrast:to-black high-contrast:border-b-4 high-contrast:border-yellow-300"
        >
          <div
            class="absolute inset-0 opacity-[0.07] bg-[radial-gradient(circle_at_20%_20%,white_1px,transparent_1px)] bg-[length:24px_24px]"
            aria-hidden="true"
          />
          <div class="relative flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between min-w-0">
            <div class="min-w-0 flex-1">
              <p id="sec-status-protocolo" class="text-xs font-semibold uppercase tracking-wider text-primary-100 high-contrast:text-yellow-300 mb-1">
                Número do protocolo
              </p>
              <div class="flex flex-wrap items-center gap-2">
                <h1 class="text-2xl sm:text-3xl font-mono font-bold text-white high-contrast:text-yellow-300 break-all">
                  {{ protocolo.id }}
                </h1>
                <button
                  type="button"
                  @click="copiarProtocolo"
                  class="inline-flex items-center justify-center gap-1.5 px-3 py-2 min-h-[44px] min-w-[44px] rounded-badge text-xs font-medium bg-white/15 hover:bg-white/25 text-white high-contrast:bg-yellow-300 high-contrast:text-black high-contrast:hover:bg-yellow-200 transition-colors motion-reduce:transition-none focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-offset-2 focus-visible:ring-offset-primary-700"
                  :aria-label="copiado ? 'Número do protocolo copiado' : 'Copiar número do protocolo'"
                >
                  <ClipboardDocumentIcon class="w-4 h-4 shrink-0" aria-hidden="true" />
                  {{ copiado ? 'Copiado!' : 'Copiar' }}
                </button>
              </div>
            </div>
            <StatusBadge
              :status="protocolo.status"
              :tipo="protocolo.tipo"
              surface="primary"
              size="lg"
              show-icon
              class="self-start shrink-0 !ring-2 !ring-white/30 max-w-full"
              :aria-label="`Status do protocolo: ${rotuloStatus}`"
            />
          </div>
        </div>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-5 border-t border-gray-100 dark:border-gray-700 high-contrast:border-yellow-300/40">
          <div class="flex items-start gap-3 min-w-0">
            <div class="w-9 h-9 rounded-button bg-primary-50 dark:bg-primary-900/30 flex items-center justify-center shrink-0" aria-hidden="true">
              <CalendarDaysIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
            </div>
            <div class="min-w-0">
              <p class="text-xs font-medium text-gray-500 dark:text-gray-400 high-contrast:text-gray-300">Abertura</p>
              <time
                :datetime="isoData(protocolo.dataCriacao)"
                class="text-sm font-semibold text-gray-900 dark:text-white high-contrast:text-white break-words"
              >
                {{ formatarDataCompleta(protocolo.dataCriacao) }}
              </time>
            </div>
          </div>
          <div class="flex items-start gap-3 min-w-0">
            <div class="w-9 h-9 rounded-button bg-amber-50 dark:bg-amber-900/20 flex items-center justify-center shrink-0" aria-hidden="true">
              <ClockIcon class="w-5 h-5 text-amber-600 dark:text-amber-400" />
            </div>
            <div class="min-w-0">
              <p class="text-xs font-medium text-gray-500 dark:text-gray-400 high-contrast:text-gray-300">Última atualização</p>
              <time
                :datetime="isoData(protocolo.dataAtualizacao)"
                class="text-sm font-semibold text-gray-900 dark:text-white high-contrast:text-white break-words"
              >
                {{ formatarDataCompleta(protocolo.dataAtualizacao) }}
              </time>
            </div>
          </div>
        </div>
      </section>

      <div class="sr-only" aria-live="polite" aria-atomic="true">{{ anuncioCopia }}</div>

      <!-- Progresso -->
      <section class="card min-w-0" aria-labelledby="titulo-andamento">
        <h2 id="titulo-andamento" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-4">
          Andamento
        </h2>
        <ol class="flex items-center justify-between gap-1" aria-label="Etapas do andamento do protocolo">
          <li
            v-for="(etapa, index) in etapasAndamento"
            :key="etapa.key"
            class="flex flex-1 flex-col items-center text-center min-w-0"
            :aria-current="etapa.ativa ? 'step' : undefined"
          >
            <div
              :class="[
                'w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold transition-colors motion-reduce:transition-none',
                etapa.ativa
                  ? 'bg-primary-600 text-white shadow-button high-contrast:bg-yellow-300 high-contrast:text-black'
                  : etapa.concluida
                    ? 'bg-success text-white high-contrast:bg-yellow-300 high-contrast:text-black'
                    : 'bg-gray-100 text-gray-400 dark:bg-gray-700 dark:text-gray-500'
              ]"
              aria-hidden="true"
            >
              <CheckIcon v-if="etapa.concluida && !etapa.ativa" class="w-5 h-5" />
              <span v-else>{{ index + 1 }}</span>
            </div>
            <span
              class="mt-2 text-[10px] sm:text-xs font-medium leading-tight max-w-[4.5rem] break-words"
              :class="etapa.ativa || etapa.concluida ? 'text-gray-900 dark:text-white high-contrast:text-white' : 'text-gray-400'"
            >
              <span v-if="etapa.ativa" class="sr-only">Etapa atual: </span>
              {{ etapa.label }}
            </span>
          </li>
        </ol>
        <div
          class="mt-4 h-1.5 rounded-full bg-gray-100 dark:bg-gray-700 overflow-hidden"
          role="progressbar"
          :aria-valuenow="progressoPercentual"
          aria-valuemin="0"
          aria-valuemax="100"
          :aria-label="`Progresso do atendimento: ${progressoPercentual} por cento`"
        >
          <div
            class="h-full rounded-full bg-gradient-to-r from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 transition-all duration-500 motion-reduce:transition-none"
            :style="{ width: `${progressoPercentual}%` }"
          />
        </div>
      </section>

      <PwaWebPushNudge
        heading-suffix="protocolo"
        descricao="Ative as notificações para ser avisado sobre o andamento desta solicitação."
      />

      <ProtocoloDiligenciaCard
        v-if="protocolo && (protocolo.diligenciaAtiva || protocolo.diligencia_ativa)"
        :protocolo-id="protocolo.codigo || props.id"
        :diligencia-ativa="protocolo.diligenciaAtiva || protocolo.diligencia_ativa"
        @respondido="onDiligenciaRespondida"
      />

      <section
        v-if="diligenciasHistorico.length"
        class="card min-w-0"
        aria-labelledby="titulo-historico-diligencias"
      >
        <h2
          id="titulo-historico-diligencias"
          class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-4"
        >
          Histórico de complementações
        </h2>
        <ul class="space-y-4">
          <li
            v-for="d in diligenciasHistorico"
            :key="d.id"
            class="rounded-card border border-gray-200 dark:border-gray-700 p-4 text-sm"
          >
            <div class="flex flex-wrap items-center gap-2 mb-2">
              <span class="text-xs font-bold uppercase text-gray-500">
                {{ labelStatusDiligencia(d.status) }}
              </span>
              <time v-if="d.criado_em" class="text-xs text-gray-500" :datetime="d.criado_em">
                {{ formatarDataCompleta(d.criado_em) }}
              </time>
            </div>
            <p class="text-gray-800 dark:text-gray-200 whitespace-pre-line">
              <span class="font-semibold">Pergunta:</span> {{ d.pergunta }}
            </p>
            <p
              v-if="d.resposta_cidadao"
              class="mt-2 text-gray-700 dark:text-gray-300 whitespace-pre-line"
            >
              <span class="font-semibold">Sua resposta:</span> {{ d.resposta_cidadao }}
            </p>
            <DiligenciaAnexosGrade v-if="d.anexos?.length" :anexos="d.anexos" />
          </li>
        </ul>
      </section>

      <ProtocoloCobrancaCard
        v-if="protocolo"
        :protocolo-id="protocolo.codigo || props.id"
        :pode-cobrar="Boolean(protocolo.podeCobrar ?? protocolo.pode_cobrar)"
        :motivo="protocolo.motivoBloqueioCobranca ?? protocolo.motivo_bloqueio_cobranca"
        :qtd-cobrancas="Number(protocolo.qtdCobrancasCidadao ?? protocolo.qtd_cobrancas_cidadao ?? 0)"
        :proxima-cobranca-em="protocolo.proximaCobrancaEm ?? protocolo.proxima_cobranca_em"
        @atualizado="onCobrancaAtualizada"
      />

      <ProtocoloCsatCard
        v-if="exibirCsat"
        :protocolo-id="props.id"
        :pode-avaliar="podeAvaliarCsat"
        :avaliacao="protocolo.avaliacao"
        @avaliado="onProtocoloAvaliado"
        @avaliado-resposta="onRespostaAvaliacao"
      />

      <ProtocoloReaberturaCsatCard
        v-if="protocolo && exibirFluxoReabertura"
        :protocolo="protocolo"
        :protocolo-id="props.id"
        :sugerir-reabertura-csat="sugerirReaberturaAposCsat"
        @reaberto="onProtocoloReaberto"
        @toast="anuncioReabertura = $event"
      />

      <p v-if="anuncioReabertura" class="sr-only" role="status" aria-live="polite">{{ anuncioReabertura }}</p>

      <!-- Tipo -->
      <section class="card flex items-center gap-4 min-w-0" aria-labelledby="titulo-categoria">
        <div
          class="w-14 h-14 rounded-avatar flex items-center justify-center shadow-soft shrink-0"
          :class="protocolo.tipo === 'zeladoria'
            ? 'bg-gradient-to-br from-teal-500 to-teal-600'
            : 'bg-gradient-to-br from-primary-500 to-primary-600'"
          aria-hidden="true"
        >
          <BuildingOffice2Icon v-if="protocolo.tipo === 'zeladoria'" class="w-7 h-7 text-white" />
          <ChatBubbleLeftRightIcon v-else class="w-7 h-7 text-white" />
        </div>
        <div class="min-w-0">
          <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
            {{ protocolo.tipo === 'zeladoria' ? 'Zeladoria urbana' : 'Ouvidoria institucional' }}
          </p>
          <h2 id="titulo-categoria" class="text-xl font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 break-words">
            {{ protocolo.categoria }}
          </h2>
        </div>
      </section>

      <!-- Descrição -->
      <section class="card min-w-0" aria-labelledby="titulo-descricao">
        <h2 id="titulo-descricao" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-4 flex items-center gap-2">
          <DocumentTextIcon class="w-5 h-5 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 shrink-0" aria-hidden="true" />
          Descrição
        </h2>

        <div v-if="descricaoPrincipal" class="mb-4">
          <p class="text-gray-700 dark:text-gray-300 high-contrast:text-white leading-relaxed text-base break-words whitespace-pre-line">
            {{ descricaoPrincipal }}
          </p>
        </div>

        <div
          v-if="camposExibicao.length"
          class="pt-4 border-t border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300/40"
        >
          <h3 class="text-xs font-bold uppercase tracking-wide text-gray-500 dark:text-gray-400 high-contrast:text-yellow-300 mb-3">
            Detalhes da solicitação
          </h3>
          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-3">
            <div v-for="campo in camposExibicao" :key="campo.chave" class="flex flex-col min-w-0">
              <dt class="text-xs font-semibold text-gray-600 dark:text-gray-400 high-contrast:text-gray-300 mb-1 break-words">
                {{ campo.rotulo }}
              </dt>
              <dd class="text-sm font-medium text-gray-900 dark:text-white high-contrast:text-white break-words">
                {{ campo.valor }}
              </dd>
            </div>
          </dl>
        </div>
      </section>

      <!-- Localização -->
      <section v-if="protocolo.localizacao" class="card min-w-0" aria-labelledby="titulo-localizacao">
        <div class="flex items-start justify-between gap-2 mb-4 flex-wrap">
          <h2 id="titulo-localizacao" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 flex items-center gap-2">
            <MapPinIcon class="w-5 h-5 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 shrink-0" aria-hidden="true" />
            Localização
          </h2>
          <a
            :href="linkMapa"
            target="_blank"
            rel="noopener noreferrer"
            class="text-xs font-semibold text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 hover:underline shrink-0 min-h-[44px] inline-flex items-center focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-button px-1"
          >
            Abrir no mapa (nova aba)
          </a>
        </div>
        <p class="font-medium text-gray-900 dark:text-white high-contrast:text-white mb-1 break-words">
          {{ protocolo.localizacao.endereco }}
        </p>
        <p class="text-xs text-gray-500 dark:text-gray-400 high-contrast:text-gray-300 mb-4 font-mono break-all">
          {{ protocolo.localizacao.latitude.toFixed(6) }}, {{ protocolo.localizacao.longitude.toFixed(6) }}
        </p>
        <LocationMap
          v-if="protocolo.localizacao.latitude != null && protocolo.localizacao.longitude != null"
          :latitude="protocolo.localizacao.latitude"
          :longitude="protocolo.localizacao.longitude"
          height="13rem"
        />
        <p v-else class="text-sm text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950/30 rounded-card p-3">
          Coordenadas não disponíveis; a equipe validará o endereço informado.
        </p>
      </section>

      <!-- Anexos -->
      <section v-if="protocolo.anexos?.length" class="card min-w-0" aria-labelledby="titulo-anexos">
        <h2 id="titulo-anexos" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-4 flex items-center gap-2">
          <PhotoIcon class="w-5 h-5 text-primary-600 dark:text-primary-400 shrink-0" aria-hidden="true" />
          Fotos anexadas ({{ protocolo.anexos.length }})
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <template v-for="(anexo, index) in protocolo.anexos" :key="anexo.id || index">
            <button
              v-if="anexoEhImagem(anexo)"
              type="button"
              class="group relative aspect-square rounded-card overflow-hidden bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 high-contrast:border-yellow-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2"
              :aria-label="`Ampliar imagem: ${altAnexo(anexo, index)}`"
              @click="abrirLightbox(index, $event)"
            >
              <img
                :src="anexo.url"
                :alt="altAnexo(anexo, index)"
                class="w-full h-full object-cover group-hover:scale-105 motion-reduce:group-hover:scale-100 transition-transform duration-300 motion-reduce:transition-none"
                loading="lazy"
              />
              <span class="absolute top-2 left-2 w-6 h-6 rounded-full bg-primary-600 text-white text-xs font-bold flex items-center justify-center high-contrast:bg-yellow-300 high-contrast:text-black" aria-hidden="true">
                {{ index + 1 }}
              </span>
            </button>
            <a
              v-else
              :href="anexo.url"
              target="_blank"
              rel="noopener noreferrer"
              class="group relative aspect-square rounded-card overflow-hidden bg-gray-100 dark:bg-gray-800 border border-gray-200 dark:border-gray-600 high-contrast:border-yellow-300 flex flex-col items-center justify-center gap-2 p-3 min-h-[44px] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
              :aria-label="`Abrir anexo ${anexo.nome || index + 1} em nova aba`"
            >
              <PhotoIcon class="w-10 h-10 text-gray-400" aria-hidden="true" />
              <span class="text-xs text-center break-words w-full px-1">{{ anexo.nome }}</span>
            </a>
          </template>
        </div>
      </section>

      <!-- Equipe -->
      <section v-if="protocolo.equipe" class="card bg-gradient-to-r from-primary-50/80 to-transparent dark:from-primary-900/20 border-primary-100 dark:border-primary-800 min-w-0" aria-labelledby="titulo-equipe">
        <div class="flex items-center gap-4 min-w-0">
          <div class="w-12 h-12 rounded-avatar bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center shadow-button shrink-0" aria-hidden="true">
            <UserGroupIcon class="w-6 h-6 text-white" />
          </div>
          <div class="min-w-0">
            <h2 id="titulo-equipe" class="text-xs font-semibold uppercase text-primary-700 dark:text-primary-300">Equipe responsável</h2>
            <p class="text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 break-words">
              {{ protocolo.equipe }}
            </p>
          </div>
        </div>
      </section>

      <!-- Resolução -->
      <section v-if="protocolo.resolucao" class="card bg-gradient-to-r from-success/10 to-transparent dark:from-green-900/20 border-green-100 dark:border-green-800 min-w-0" aria-labelledby="titulo-resolucao">
        <div class="flex gap-3 min-w-0">
          <div class="w-10 h-10 rounded-full bg-success flex items-center justify-center shrink-0 high-contrast:bg-yellow-300" aria-hidden="true">
            <CheckCircleIcon class="w-6 h-6 text-white high-contrast:text-black" />
          </div>
          <div class="min-w-0">
            <h2 id="titulo-resolucao" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-1">Resolução</h2>
            <p class="text-gray-700 dark:text-gray-300 high-contrast:text-white leading-relaxed break-words">
              {{ protocolo.resolucao }}
            </p>
          </div>
        </div>
      </section>

      <!-- Timeline -->
      <section class="card min-w-0" aria-labelledby="titulo-historico">
        <h2 id="titulo-historico" class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-5">
          Histórico e acionamentos
        </h2>
        <ol class="space-y-0" aria-label="Histórico de andamento do protocolo">
          <li
            v-for="(evento, i) in timelineCompleta"
            :key="evento.id || i"
            class="flex gap-4 min-w-0"
            :aria-current="evento.tipo === 'active' ? 'step' : undefined"
          >
            <div class="flex flex-col items-center" aria-hidden="true">
              <div
                :class="[
                  'w-9 h-9 rounded-full flex items-center justify-center shrink-0 ring-2 ring-offset-2',
                  evento.tipo === 'done' ? 'bg-success text-white high-contrast:bg-yellow-300 high-contrast:text-black ring-green-200 dark:ring-green-800 ring-offset-white dark:ring-offset-gray-800' :
                  evento.tipo === 'active' ? 'bg-primary-600 text-white high-contrast:bg-yellow-300 high-contrast:text-black ring-primary-200 dark:ring-primary-800 ring-offset-white dark:ring-offset-gray-800' :
                  evento.tipo === 'ordem_servico' ? 'bg-amber-500 text-white high-contrast:bg-yellow-400 high-contrast:text-black ring-amber-200 dark:ring-amber-800 ring-offset-white dark:ring-offset-gray-800' :
                  'bg-gray-100 dark:bg-gray-700 text-gray-400 ring-gray-200 dark:ring-gray-600 ring-offset-white dark:ring-offset-gray-800'
                ]"
              >
                <component :is="evento.icon" class="w-4 h-4" />
              </div>
              <div v-if="i < timelineCompleta.length - 1" class="w-0.5 flex-1 min-h-[2rem] bg-gray-200 dark:bg-gray-600 high-contrast:bg-yellow-300/50 my-1" />
            </div>
            <div class="pb-6 pt-1 min-w-0 flex-1">
              <p v-if="evento.tipo === 'active'" class="sr-only">Etapa vigente do protocolo</p>
              <div v-if="evento.tipo === 'ordem_servico'" class="bg-amber-50 dark:bg-amber-900/20 high-contrast:bg-transparent border border-amber-200 dark:border-amber-800 high-contrast:border-yellow-300 rounded-card p-3">
                <div class="flex items-start gap-2 mb-2">
                  <TruckIcon class="w-5 h-5 text-amber-600 dark:text-amber-400 high-contrast:text-yellow-300 flex-shrink-0 mt-0.5" aria-hidden="true" />
                  <div class="flex-1 min-w-0">
                    <p class="font-bold text-amber-900 dark:text-amber-100 high-contrast:text-yellow-300 break-words">
                      {{ evento.titulo }}
                    </p>
                    <p v-if="evento.secretaria" class="text-xs text-amber-700 dark:text-amber-300 high-contrast:text-white high-contrast:font-bold mt-0.5 break-words">
                      {{ evento.secretaria }}
                    </p>
                  </div>
                </div>
                <p v-if="evento.subtitulo" class="text-sm text-amber-800 dark:text-amber-200 high-contrast:text-white high-contrast:font-bold break-words">
                  {{ evento.subtitulo }}
                </p>
                <div v-if="evento.data" class="mt-2 flex items-center gap-2 flex-wrap">
                  <ClockIcon class="w-3.5 h-3.5 text-amber-600 dark:text-amber-400 shrink-0" aria-hidden="true" />
                  <time
                    v-if="evento.dataIso"
                    :datetime="evento.dataIso"
                    class="text-xs text-amber-600 dark:text-amber-400 high-contrast:text-yellow-300 font-mono font-semibold"
                  >
                    {{ evento.data }}
                  </time>
                  <p v-else class="text-xs text-amber-600 dark:text-amber-400 high-contrast:text-yellow-300 font-mono font-semibold">
                    {{ evento.data }}
                  </p>
                </div>
              </div>

              <div
                v-else-if="evento.tipo === 'reabertura'"
                class="rounded-card border border-orange-200 dark:border-orange-800 bg-orange-50/80 dark:bg-orange-950/30 p-3"
              >
                <p class="font-semibold text-orange-900 dark:text-orange-100 break-words">{{ evento.titulo }}</p>
                <p v-if="evento.metaCsat" class="text-xs font-semibold text-amber-800 dark:text-amber-200 mt-1">
                  Nota CSAT de origem: {{ evento.metaCsat }} estrela(s)
                </p>
                <p class="text-sm text-orange-900/90 dark:text-orange-100/90 mt-1 whitespace-pre-line break-words">{{ evento.subtitulo }}</p>
                <DiligenciaAnexosGrade v-if="evento.anexos?.length" :anexos="evento.anexos" class="mt-3" />
                <time
                  v-if="evento.data && evento.dataIso"
                  :datetime="evento.dataIso"
                  class="text-xs text-orange-700 dark:text-orange-300 mt-2 font-mono block"
                >
                  {{ evento.data }}
                </time>
              </div>

              <div v-else>
                <p class="font-semibold text-gray-900 dark:text-white high-contrast:text-white break-words">{{ evento.titulo }}</p>
                <p v-if="evento.subtitulo" class="text-sm text-gray-500 dark:text-gray-400 high-contrast:text-gray-300 mt-0.5 break-words">
                  {{ evento.subtitulo }}
                </p>
                <time
                  v-if="evento.data && evento.dataIso"
                  :datetime="evento.dataIso"
                  class="text-xs text-gray-400 dark:text-gray-500 high-contrast:text-white high-contrast:font-bold mt-1 font-mono block"
                >
                  {{ evento.data }}
                </time>
                <p v-else-if="evento.data" class="text-xs text-gray-400 dark:text-gray-500 high-contrast:text-white high-contrast:font-bold mt-1 font-mono">
                  {{ evento.data }}
                </p>
              </div>
            </div>
          </li>
        </ol>
      </section>
    </main>

    <!-- Lightbox de imagens -->
    <Teleport to="body">
      <div
        v-if="lightboxAberto && anexoLightbox"
        class="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/80 high-contrast:bg-black"
        role="dialog"
        aria-modal="true"
        :aria-label="`Visualização ampliada: ${altAnexo(anexoLightbox, lightboxIndice)}`"
        @click.self="fecharLightbox"
      >
        <div class="relative max-w-full max-h-full w-full flex flex-col items-center gap-4 min-w-0">
          <div class="flex w-full max-w-lg justify-end gap-2">
            <a
              :href="anexoLightbox.url"
              target="_blank"
              rel="noopener noreferrer"
              download
              class="btn-icon min-h-[44px] min-w-[44px] bg-white/10 border-white/30 hover:bg-white/20"
              aria-label="Baixar ou abrir imagem em tamanho original"
            >
              <ArrowTopRightOnSquareIcon class="w-5 h-5 text-white high-contrast:text-yellow-300" aria-hidden="true" />
            </a>
            <button
              ref="fecharLightboxRef"
              type="button"
              class="btn-icon min-h-[44px] min-w-[44px] bg-white/10 border-white/30 hover:bg-white/20"
              aria-label="Fechar visualização da imagem"
              @click="fecharLightbox"
            >
              <XMarkIcon class="w-6 h-6 text-white high-contrast:text-yellow-300" aria-hidden="true" />
            </button>
          </div>
          <img
            :src="anexoLightbox.url"
            :alt="altAnexo(anexoLightbox, lightboxIndice)"
            class="max-h-[70vh] max-w-full w-auto h-auto object-contain rounded-card border-2 border-white/20 high-contrast:border-yellow-300"
          />
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useProtocolosStore } from '@/stores/protocolos'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import LocationMap from '@/components/pwa/LocationMap.vue'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import PwaA11yMenu from '@/components/pwa/PwaA11yMenu.vue'
import ProtocoloCsatCard from '@/components/pwa/protocolo/ProtocoloCsatCard.vue'
import ProtocoloReaberturaCsatCard from '@/components/pwa/protocolo/ProtocoloReaberturaCsatCard.vue'
import { mapCamposReaberturaProtocolo } from '@/utils/reaberturaHelpers'
import ProtocoloCobrancaCard from '@/components/pwa/protocolo/ProtocoloCobrancaCard.vue'
import ProtocoloDiligenciaCard from '@/components/pwa/protocolo/ProtocoloDiligenciaCard.vue'
import DiligenciaAnexosGrade from '@/components/diligencia/DiligenciaAnexosGrade.vue'
import PwaWebPushNudge from '@/components/pwa/PwaWebPushNudge.vue'
import { labelStatusDiligencia } from '@/utils/diligenciaHelpers'
import {
  ChevronLeftIcon,
  ExclamationCircleIcon,
  BuildingOffice2Icon,
  ChatBubbleLeftRightIcon,
  MapPinIcon,
  PhotoIcon,
  UserGroupIcon,
  CheckCircleIcon,
  PlusIcon,
  ClockIcon,
  TruckIcon,
  CheckIcon,
  CalendarDaysIcon,
  DocumentTextIcon,
  ClipboardDocumentIcon,
  XMarkIcon,
  ArrowTopRightOnSquareIcon,
  ArrowUturnLeftIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  id: {
    type: String,
    required: true
  }
})

const router = useRouter()
const protocolosStore = useProtocolosStore()
const protocolo = ref(null)
const copiado = ref(false)
const anuncioCopia = ref('')
const anuncioReabertura = ref('')
const sugerirReaberturaAposCsat = ref(false)

const lightboxAberto = ref(false)
const lightboxIndice = ref(0)
const fecharLightboxRef = ref(null)
let lightboxTriggerEl = null

const anexoLightbox = computed(() => {
  const lista = protocolo.value?.anexos
  if (!lista?.length) return null
  return lista[lightboxIndice.value] || null
})

const podeAvaliarCsat = computed(() => Boolean(protocolo.value?.podeAvaliar ?? protocolo.value?.pode_avaliar))

const exibirCsat = computed(() => {
  if (!protocolo.value) return false
  return podeAvaliarCsat.value || Boolean(protocolo.value.avaliacao)
})

function onProtocoloAvaliado(avaliacao) {
  if (!protocolo.value) return
  protocolo.value = {
    ...protocolo.value,
    avaliacao,
    podeAvaliar: false,
    pode_avaliar: false
  }
}

function onRespostaAvaliacao(resposta) {
  if (!protocolo.value || !resposta) return
  sugerirReaberturaAposCsat.value = Boolean(resposta.sugerir_reabertura_csat)
  protocolo.value = {
    ...protocolo.value,
    ...mapCamposReaberturaProtocolo(resposta),
    podeAvaliar: Boolean(resposta.pode_avaliar ?? protocolo.value.podeAvaliar),
    pode_avaliar: Boolean(resposta.pode_avaliar ?? protocolo.value.pode_avaliar)
  }
}

const exibirFluxoReabertura = computed(() => {
  if (!protocolo.value || protocolo.value.status !== 'resolvido') return false
  const motivo = protocolo.value.motivoBloqueioReabertura ?? protocolo.value.motivo_bloqueio_reabertura
  if (['janela_expirada', 'desabilitado', 'nao_concluido'].includes(motivo)) return false
  return (
    Boolean(protocolo.value.podeReabrir ?? protocolo.value.pode_reabrir) ||
    motivo === 'limite_atingido' ||
    sugerirReaberturaAposCsat.value ||
    Boolean(protocolo.value.sugerirReaberturaCsat ?? protocolo.value.sugerir_reabertura_csat) ||
    (protocolo.value.reaberturas?.length || 0) > 0
  )
})

async function onProtocoloReaberto(payload) {
  const result = await protocolosStore.buscarProtocolo(props.id)
  if (result.success) {
    protocolo.value = result.protocolo
  } else if (payload && protocolo.value) {
    const proto = payload.protocolo || payload
    const mapped = mapCamposReaberturaProtocolo(proto)
    protocolo.value = { ...protocolo.value, ...mapped, ...proto }
  }
  sugerirReaberturaAposCsat.value = false
}

async function onDiligenciaRespondida() {
  const result = await protocolosStore.buscarProtocolo(props.id)
  if (result.success) {
    protocolo.value = result.protocolo
  }
}

async function onCobrancaAtualizada(patch) {
  const result = await protocolosStore.buscarProtocolo(props.id)
  if (result.success) {
    protocolo.value = result.protocolo
  } else if (protocolo.value && patch) {
    protocolo.value = {
      ...protocolo.value,
      ...patch,
      podeCobrar: patch.pode_cobrar ?? false,
      pode_cobrar: patch.pode_cobrar ?? false,
      motivoBloqueioCobranca: patch.motivo_bloqueio_cobranca,
      motivo_bloqueio_cobranca: patch.motivo_bloqueio_cobranca,
      qtdCobrancasCidadao: patch.qtd_cobrancas_cidadao,
      qtd_cobrancas_cidadao: patch.qtd_cobrancas_cidadao,
      proximaCobrancaEm: patch.proxima_cobranca_em,
      proxima_cobranca_em: patch.proxima_cobranca_em
    }
  }
}

const rotuloStatus = computed(() => {
  if (!protocolo.value) return ''
  const status = protocolo.value.status
  const tipo = protocolo.value.tipo
  const mapaZeladoria = {
    em_analise: 'Em análise',
    em_andamento: 'Equipe em deslocamento',
    resolvido: 'Resolvido',
    rejeitado: 'Não procedente'
  }
  const mapaOuvidoria = {
    em_analise: 'Em triagem',
    resolvido: 'Respondido'
  }
  if (tipo === 'zeladoria') return mapaZeladoria[status] || status
  return mapaOuvidoria[status] || status
})

const linkMapa = computed(() => {
  if (!protocolo.value?.localizacao) return '#'
  const { latitude, longitude } = protocolo.value.localizacao
  return `https://www.google.com/maps?q=${latitude},${longitude}`
})

const descricaoPrincipal = computed(() => {
  const texto = (protocolo.value?.descricao || '').trim()
  return texto || null
})

const camposExibicao = computed(() => {
  const api = protocolo.value?.camposSolicitacao || protocolo.value?.campos_solicitacao
  if (Array.isArray(api) && api.length) {
    return api.map((c) => ({
      chave: c.chave,
      rotulo: c.rotulo || c.chave,
      valor: formatarValor(c.valor)
    }))
  }

  const dados = protocolo.value?.dados_dinamicos
  if (!dados || typeof dados !== 'object') return []

  const CHAVES_IGNORAR = new Set(['bairro', 'cidade'])
  const lista = []
  for (const [chave, valor] of Object.entries(dados)) {
    if (chave.startsWith('_') || valor === null || valor === undefined || valor === '') continue
    const txt = formatarValor(valor)
    if (descricaoPrincipal.value && txt === descricaoPrincipal.value.trim()) continue
    if (CHAVES_IGNORAR.has(chave) && protocolo.value?.localizacao?.endereco) continue
    lista.push({ chave, rotulo: formatarChave(chave), valor: txt })
  }
  return lista
})

const etapasAndamento = computed(() => {
  const status = protocolo.value?.status
  const ordem = ['recebido', 'analise', 'execucao', 'concluido']
  let indiceAtivo = 1
  if (status === 'em_analise') indiceAtivo = 1
  else if (status === 'aguardando_cidadao') indiceAtivo = 2
  else if (status === 'em_andamento') indiceAtivo = 2
  else if (status === 'resolvido') indiceAtivo = 3

  const labels = ['Recebido', 'Em análise', 'Em campo', 'Concluído']
  return ordem.map((key, i) => ({
    key,
    label: labels[i],
    ativa: i === indiceAtivo,
    concluida: i < indiceAtivo || (status === 'resolvido' && i <= 3)
  }))
})

const progressoPercentual = computed(() => {
  const status = protocolo.value?.status
  if (status === 'em_analise') return 35
  if (status === 'em_andamento') return 70
  if (status === 'resolvido') return 100
  return 15
})

const historico = computed(() => {
  if (!protocolo.value) return []
  const p = protocolo.value
  const items = [
    {
      id: 'criacao',
      titulo: 'Protocolo criado',
      subtitulo: 'Solicitação registrada no sistema',
      data: formatarDataCompleta(p.dataCriacao),
      dataIso: isoData(p.dataCriacao),
      icon: PlusIcon,
      tipo: 'done',
      timestamp: new Date(p.dataCriacao).getTime()
    }
  ]
  if (p.status !== 'em_analise') {
    items.push({
      id: 'atendimento',
      titulo: p.status === 'resolvido' ? 'Atendimento concluído' : 'Equipe em atendimento',
      subtitulo: p.equipe ? `Responsável: ${p.equipe}` : 'Demanda em processamento',
      data: null,
      dataIso: null,
      icon: p.status === 'resolvido' ? CheckCircleIcon : TruckIcon,
      tipo: p.status === 'resolvido' ? 'done' : 'active',
      timestamp: Date.now()
    })
  } else {
    items.push({
      id: 'analise',
      titulo: 'Em análise',
      subtitulo: 'Aguardando triagem e encaminhamento',
      data: null,
      dataIso: null,
      icon: ClockIcon,
      tipo: 'active',
      timestamp: Date.now()
    })
  }
  if (p.status === 'resolvido') {
    items.push({
      id: 'encerrado',
      titulo: 'Encerrado',
      subtitulo: p.resolucao || 'Protocolo finalizado',
      data: formatarDataCompleta(p.dataAtualizacao),
      dataIso: isoData(p.dataAtualizacao),
      icon: CheckCircleIcon,
      tipo: 'done',
      timestamp: new Date(p.dataAtualizacao).getTime()
    })
  }
  return items
})

const diligenciasHistorico = computed(() => {
  const lista = protocolo.value?.diligencias || []
  const ativaId = protocolo.value?.diligenciaAtiva?.id || protocolo.value?.diligencia_ativa?.id
  return lista.filter(
    (d) =>
      d.status !== 'aguardando_cidadao' &&
      (!ativaId || String(d.id) !== String(ativaId))
  )
})

const timelineCompleta = computed(() => {
  const items = [...historico.value]

  const diligencias = protocolo.value?.diligencias || []
  diligencias.forEach((d) => {
    if (d.status === 'aguardando_cidadao') return
    items.push({
      id: `diligencia-${d.id}`,
      tipo: d.status === 'respondida' ? 'done' : 'active',
      titulo: `Diligência — ${labelStatusDiligencia(d.status)}`,
      subtitulo: d.resposta_cidadao
        ? `Pergunta: ${d.pergunta?.slice(0, 120) || ''} — Resposta: ${d.resposta_cidadao.slice(0, 160)}`
        : d.pergunta,
      data: d.criado_em ? formatarDataCompleta(d.criado_em) : null,
      dataIso: d.criado_em ? isoData(d.criado_em) : null,
      icon: DocumentTextIcon,
      timestamp: d.criado_em ? new Date(d.criado_em).getTime() : Date.now()
    })
  })

  const reaberturas = protocolo.value?.reaberturas || []
  reaberturas.forEach((r) => {
    items.push({
      id: `reabertura-${r.id}`,
      tipo: 'reabertura',
      titulo: 'Contestação — solicitação reaberta',
      subtitulo: r.motivo,
      metaCsat: r.notaCsatOrigem ?? r.nota_csat_origem,
      anexos: r.anexos,
      data: r.criado_em ? formatarDataCompleta(r.criado_em) : null,
      dataIso: r.criado_em ? isoData(r.criado_em) : null,
      icon: ArrowUturnLeftIcon,
      timestamp: r.criado_em ? new Date(r.criado_em).getTime() : Date.now()
    })
  })

  if (protocolo.value?.ordens_servico && Array.isArray(protocolo.value.ordens_servico)) {
    protocolo.value.ordens_servico.forEach((ordem) => {
      items.push({
        id: `ordem-${ordem.id}`,
        tipo: 'ordem_servico',
        titulo: ordem.status === 'CONCLUIDA' ? 'Ordem de Serviço Concluída' : 'Ordem de Serviço Acionada',
        subtitulo: ordem.descricao || 'Equipe especializada em campo',
        secretaria: ordem.secretaria || 'Secretaria Municipal',
        data: ordem.criado_em ? formatarDataCompleta(ordem.criado_em) : null,
        dataIso: ordem.criado_em ? isoData(ordem.criado_em) : null,
        icon: ordem.status === 'CONCLUIDA' ? CheckCircleIcon : TruckIcon,
        timestamp: ordem.criado_em ? new Date(ordem.criado_em).getTime() : Date.now()
      })
    })
  }

  return items.sort((a, b) => a.timestamp - b.timestamp)
})

onMounted(async () => {
  const result = await protocolosStore.buscarProtocolo(props.id)
  if (result.success) {
    protocolo.value = result.protocolo
  }
  document.addEventListener('keydown', onEscapeLightbox)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onEscapeLightbox)
})

function onEscapeLightbox(event) {
  if (event.key === 'Escape' && lightboxAberto.value) {
    event.preventDefault()
    fecharLightbox()
  }
}

function voltar() {
  router.push({ name: 'pwa-dashboard' })
}

async function copiarProtocolo() {
  if (!protocolo.value?.id) return
  try {
    await navigator.clipboard.writeText(protocolo.value.id)
    copiado.value = true
    anuncioCopia.value = 'Número do protocolo copiado'
    setTimeout(() => {
      copiado.value = false
      anuncioCopia.value = ''
    }, 2500)
  } catch {
    anuncioCopia.value = 'Não foi possível copiar o número. Tente selecionar manualmente.'
    setTimeout(() => { anuncioCopia.value = '' }, 3000)
  }
}

function abrirLightbox(index, event) {
  lightboxIndice.value = index
  lightboxTriggerEl = event.currentTarget
  lightboxAberto.value = true
  nextTick(() => fecharLightboxRef.value?.focus())
}

function fecharLightbox() {
  lightboxAberto.value = false
  nextTick(() => lightboxTriggerEl?.focus())
}

function anexoEhImagem(anexo) {
  const tipo = (anexo.tipo || '').toLowerCase()
  if (tipo.startsWith('image/')) return true
  return /\.(jpe?g|png|gif|webp|heic)$/i.test(anexo.url || '')
}

function altAnexo(anexo, index) {
  const dataRef =
    protocolo.value?.dataCriacao && formatarDataCompleta(protocolo.value.dataCriacao).split(',')[0]
  const dataTexto = dataRef || 'data não informada'
  const nome = anexo.nome || `anexo ${index + 1}`
  return `Foto anexada ao protocolo em ${dataTexto}: ${nome}`
}

function isoData(dataISO) {
  if (!dataISO) return ''
  const data = new Date(dataISO)
  return Number.isNaN(data.getTime()) ? '' : data.toISOString()
}

function formatarDataCompleta(dataISO) {
  const data = new Date(dataISO)
  return data.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatarChave(chave) {
  return chave
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letra) => letra.toUpperCase())
}

function formatarValor(valor) {
  if (typeof valor === 'boolean') {
    return valor ? 'Sim' : 'Não'
  }
  if (Array.isArray(valor)) {
    return valor.join(', ')
  }
  if (typeof valor === 'object' && valor !== null) {
    return JSON.stringify(valor)
  }
  return String(valor)
}
</script>