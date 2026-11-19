<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-600 via-primary-700 to-primary-800 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 high-contrast:from-black high-contrast:to-black flex items-center justify-center p-6 safe-area-inset relative overflow-hidden">
    <div class="absolute top-6 right-6 z-20">
      <ThemeToggle surface="dark" />
    </div>

    <div class="absolute top-20 left-10 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
    <div class="absolute bottom-20 right-10 w-96 h-96 bg-primary-400/10 rounded-full blur-3xl"></div>

    <div class="w-full max-w-md relative z-10 animate-fade-in">
      <div class="text-center mb-8 animate-scale-in">
        <div class="inline-flex items-center justify-center mb-6">
          <img
            :src="BRAND.logos.login"
            :alt="BRAND.name"
            class="h-24 w-auto max-w-[280px] object-contain drop-shadow-2xl"
          />
        </div>
        <p class="text-white/90 dark:text-gray-300 high-contrast:text-white high-contrast:font-bold text-lg font-medium">
          {{ BRAND.tagline }}
        </p>
      </div>

      <div class="bg-white dark:bg-gray-800 high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300 rounded-card shadow-float p-8 animate-slide-up">
        <h2 class="text-2xl font-bold text-center mb-2 text-gray-900 dark:text-white high-contrast:text-yellow-300">
          Bem-vindo(a)
        </h2>
        <p class="text-center text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mb-6">
          Escolha como deseja acessar sua conta
        </p>

        <div v-if="authStore.error" class="mb-4 alert-danger animate-scale-in">
          <ExclamationCircleIcon class="w-5 h-5 flex-shrink-0" />
          <p class="text-sm">{{ authStore.error }}</p>
        </div>

        <div
          v-if="cpfCadastroIndisponivel && abaPadrao === 'cadastro'"
          class="mb-4 rounded-card border-2 border-amber-300 dark:border-amber-600 bg-amber-50 dark:bg-amber-950/40 p-4 space-y-3 animate-scale-in"
        >
          <p class="text-sm font-semibold text-amber-900 dark:text-amber-100">
            {{ cpfCadastroMsg || 'Este CPF já está cadastrado.' }}
          </p>
          <div class="flex flex-wrap gap-2">
            <button type="button" class="btn-primary text-sm py-2 px-4" @click="irParaLoginComCpf('cadastro')">
              Entrar com este CPF
            </button>
            <button type="button" class="btn-secondary text-sm py-2 px-4" @click="abrirRecuperarDesdeCadastro">
              Recuperar senha
            </button>
          </div>
        </div>

        <!-- Gov.br / SSO -->
        <div v-if="!modoPadrao" class="space-y-3">
          <button
            type="button"
            @click="handleGovBrLogin"
            :disabled="authStore.loading"
            class="w-full btn-primary group"
          >
            <CheckBadgeIcon class="w-6 h-6 group-hover:scale-110 transition-transform" />
            <span class="text-base font-semibold">Entrar com Gov.br</span>
          </button>

          <button
            type="button"
            @click="handleSsoLogin"
            :disabled="authStore.loading"
            class="w-full btn-secondary group"
          >
            <BuildingOffice2Icon class="w-6 h-6 group-hover:scale-110 transition-transform" />
            <span class="text-base font-semibold">SSO Municipal</span>
          </button>

          <div class="relative my-6">
            <div class="absolute inset-0 flex items-center">
              <div class="w-full border-t-2 border-gray-200 dark:border-gray-700 high-contrast:border-gray-600"></div>
            </div>
            <div class="relative flex justify-center text-sm">
              <span class="px-4 bg-white dark:bg-gray-800 high-contrast:bg-black text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold rounded-badge font-medium">
                ou
              </span>
            </div>
          </div>

          <button
            type="button"
            @click="abrirModoPadrao('login')"
            :disabled="authStore.loading"
            class="w-full flex flex-col items-center gap-1 py-4 px-6 rounded-button border-2 border-primary-200 dark:border-primary-700 bg-gradient-to-r from-white to-primary-50/80 dark:from-gray-800 dark:to-primary-950/40 shadow-soft hover:shadow-button-hover transition-all duration-300 high-contrast:border-yellow-300 high-contrast:from-black high-contrast:to-gray-900 group"
          >
            <span class="inline-flex items-center gap-2">
              <FingerPrintIcon class="w-6 h-6 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 group-hover:scale-110 transition-transform" />
              <span class="text-base font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300">
                Login padrão
              </span>
            </span>
            <span class="text-xs font-medium text-gray-500 dark:text-gray-400 high-contrast:text-white">
              Acesse com CPF e senha
            </span>
          </button>
        </div>

        <!-- Painel login padrão -->
        <transition name="slide-fade">
          <div v-if="modoPadrao" class="space-y-5">
            <div v-if="abaPadrao !== 'recuperar'" class="text-center">
              <div class="inline-flex p-1 rounded-button bg-gray-100 dark:bg-gray-900/80 high-contrast:bg-gray-950 border border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300 w-full">
                <button
                  type="button"
                  class="flex-1 py-2.5 px-3 rounded-button text-sm font-semibold transition-all duration-300"
                  :class="abaPadrao === 'login'
                    ? 'bg-white dark:bg-gray-800 text-primary-700 dark:text-primary-300 shadow-soft high-contrast:bg-yellow-300 high-contrast:text-black'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'"
                  @click="abaPadrao = 'login'"
                >
                  Já tenho conta
                </button>
                <button
                  type="button"
                  class="flex-1 py-2.5 px-3 rounded-button text-sm font-semibold transition-all duration-300"
                  :class="abaPadrao === 'cadastro'
                    ? 'bg-white dark:bg-gray-800 text-primary-700 dark:text-primary-300 shadow-soft high-contrast:bg-yellow-300 high-contrast:text-black'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'"
                  @click="abaPadrao = 'cadastro'"
                >
                  Criar conta
                </button>
              </div>
            </div>

            <!-- Login CPF + senha -->
            <form
              v-if="abaPadrao === 'login'"
              @submit.prevent="handleLoginPadrao"
              class="space-y-4"
            >
              <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white text-center">
                Informe seu CPF e senha cadastrados
              </p>

              <CardField label="CPF" for-id="login-cpf">
                <div class="relative">
                  <IdentificationIcon class="field-icon" />
                  <input
                    id="login-cpf"
                    v-model="formLogin.cpf"
                    type="text"
                    required
                    autocomplete="username"
                    class="input pl-11"
                    placeholder="000.000.000-00"
                    maxlength="14"
                    @input="formatarCPFLogin"
                  />
                </div>
              </CardField>

              <CardField label="Senha" for-id="login-senha">
                <div class="relative">
                  <LockClosedIcon class="field-icon" />
                  <input
                    id="login-senha"
                    v-model="formLogin.senha"
                    :type="mostrarSenhaLogin ? 'text' : 'password'"
                    required
                    minlength="8"
                    autocomplete="current-password"
                    class="input pl-11 pr-11"
                    placeholder="Sua senha"
                  />
                  <button
                    type="button"
                    class="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-button text-gray-500 hover:text-primary-600 dark:hover:text-primary-400 transition-colors"
                    :aria-label="mostrarSenhaLogin ? 'Ocultar senha' : 'Mostrar senha'"
                    @click="mostrarSenhaLogin = !mostrarSenhaLogin"
                  >
                    <EyeSlashIcon v-if="mostrarSenhaLogin" class="w-5 h-5" />
                    <EyeIcon v-else class="w-5 h-5" />
                  </button>
                </div>
              </CardField>

              <button
                type="submit"
                :disabled="authStore.loading || !formLogin.cpf || !formLogin.senha || cpfLoginInvalido"
                class="w-full btn-primary mt-2"
              >
                <ArrowRightOnRectangleIcon class="w-5 h-5" />
                <span>{{ authStore.loading ? 'Entrando...' : 'Entrar' }}</span>
              </button>

              <p class="text-center text-sm">
                <button
                  type="button"
                  class="text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 font-semibold hover:underline"
                  @click="abrirRecuperarSenha"
                >
                  Esqueci minha senha
                </button>
              </p>

              <p class="text-center text-sm text-gray-600 dark:text-gray-400">
                Primeira vez aqui?
                <button
                  type="button"
                  class="text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 font-semibold hover:underline ml-1"
                  @click="abaPadrao = 'cadastro'"
                >
                  Cadastre-se
                </button>
              </p>
            </form>

            <!-- Recuperar senha -->
            <div v-else-if="abaPadrao === 'recuperar'" class="space-y-4">
              <p class="text-sm text-gray-600 dark:text-gray-400 text-center">
                Escolha como deseja receber o link ou código para redefinir sua senha.
              </p>

              <div v-if="!recuperarEnviado" class="space-y-4">
                <CardField label="CPF" for-id="rec-cpf">
                  <div class="relative">
                    <IdentificationIcon class="field-icon" />
                    <input
                      id="rec-cpf"
                      v-model="formRecuperar.cpf"
                      type="text"
                      required
                      class="input pl-11"
                      :class="{ 'input-error': cpfRecuperarInvalido }"
                      placeholder="000.000.000-00"
                      maxlength="14"
                      @input="formatarCPFRecuperar"
                    />
                  </div>
                  <p v-if="cpfRecuperarInvalido" class="text-xs text-danger mt-1">CPF inválido</p>
                </CardField>

                <CardField label="Enviar por" for-id="rec-canal">
                  <select id="rec-canal" v-model="formRecuperar.canal" class="input">
                    <option value="email">E-mail</option>
                    <option value="sms">SMS</option>
                    <option value="whatsapp">WhatsApp</option>
                  </select>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    A integração com provedores (SMTP, gateway SMS e WhatsApp Business) é configurada no servidor.
                  </p>
                </CardField>

                <button
                  type="button"
                  class="w-full btn-primary"
                  :disabled="authStore.loading || !formRecuperar.cpf || cpfRecuperarInvalido"
                  @click="handleSolicitarRecuperacao"
                >
                  {{ authStore.loading ? 'Enviando...' : 'Enviar instruções' }}
                </button>
              </div>

              <div v-else class="alert-success text-sm space-y-2">
                <p>{{ recuperarEnviado.mensagem }}</p>
                <p v-if="recuperarEnviado.destino_mascarado" class="text-xs opacity-90">
                  Canal: <strong>{{ rotuloCanal(recuperarEnviado.canal) }}</strong>
                  — destino {{ recuperarEnviado.destino_mascarado }}
                </p>
              </div>

              <details class="rounded-card border border-gray-200 dark:border-gray-700 p-4 text-sm">
                <summary class="font-semibold cursor-pointer text-primary-700 dark:text-primary-300">
                  Já tenho o código ou link
                </summary>
                <form class="mt-3 space-y-3" @submit.prevent="handleRedefinirSenha">
                  <input
                    v-model="formRedefinir.token"
                    type="text"
                    required
                    class="input text-sm"
                    placeholder="Cole o token recebido"
                    autocomplete="one-time-code"
                  />
                  <input
                    v-model="formRedefinir.novaSenha"
                    type="password"
                    required
                    minlength="8"
                    class="input"
                    placeholder="Nova senha (mín. 8 caracteres)"
                    autocomplete="new-password"
                  />
                  <input
                    v-model="formRedefinir.confirmacao"
                    type="password"
                    required
                    class="input"
                    :class="{ 'input-error': senhaRecuperarNaoConfere }"
                    placeholder="Confirmar nova senha"
                  />
                  <button
                    type="submit"
                    class="w-full btn-success"
                    :disabled="authStore.loading || senhaRecuperarNaoConfere"
                  >
                    Salvar nova senha
                  </button>
                </form>
              </details>

              <button type="button" class="w-full btn-ghost text-sm" @click="abaPadrao = 'login'">
                ← Voltar ao login
              </button>
            </div>

            <!-- Cadastro -->
            <form
              v-else
              @submit.prevent="handleCadastroPadrao"
              class="space-y-4 max-h-[58vh] overflow-y-auto pr-1 -mr-1 pb-2 custom-scrollbar"
            >
              <section class="rounded-card border border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30 p-4 space-y-3">
                <h3 class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-primary-600 text-white text-xs flex items-center justify-center high-contrast:bg-yellow-300 high-contrast:text-black">1</span>
                  Dados pessoais
                </h3>

                <CardField label="Nome completo" for-id="nome">
                  <input id="nome" v-model="formCadastro.nome" type="text" required class="input" placeholder="Seu nome completo" />
                </CardField>

                <CardField label="CPF" for-id="cpf">
                  <div class="relative">
                    <IdentificationIcon class="field-icon" />
                    <input
                      id="cpf"
                      v-model="formCadastro.cpf"
                      type="text"
                      required
                      class="input pl-11"
                      :class="{ 'input-error': cpfCadastroInvalido || cpfCadastroIndisponivel }"
                      placeholder="000.000.000-00"
                      maxlength="14"
                      @input="formatarCPFCadastro"
                      @blur="validarCpfCadastro"
                    />
                    <div
                      v-if="verificandoCpf"
                      class="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"
                    />
                  </div>
                  <p v-if="cpfCadastroInvalido" class="text-xs text-danger mt-1 font-medium">
                    Informe um CPF válido (dígitos verificadores).
                  </p>
                  <p
                    v-else-if="cpfCadastroMsg && !cpfCadastroIndisponivel"
                    class="text-xs text-green-700 dark:text-green-400 mt-1"
                  >
                    {{ cpfCadastroMsg }}
                  </p>
                </CardField>

                <CardField label="E-mail" for-id="email">
                  <input id="email" v-model="formCadastro.email" type="email" required class="input" placeholder="seu@email.com" autocomplete="email" />
                </CardField>

                <CardField label="Telefone" for-id="telefone">
                  <input
                    id="telefone"
                    v-model="formCadastro.telefone"
                    type="tel"
                    required
                    class="input"
                    placeholder="(00) 00000-0000"
                    maxlength="15"
                    @input="formatarTelefone"
                  />
                </CardField>

                <CardField label="Senha" for-id="senha">
                  <div class="relative">
                    <LockClosedIcon class="field-icon" />
                    <input
                      id="senha"
                      v-model="formCadastro.senha"
                      :type="mostrarSenhaCadastro ? 'text' : 'password'"
                      required
                      minlength="8"
                      class="input pl-11 pr-11"
                      placeholder="Mínimo 8 caracteres"
                      autocomplete="new-password"
                    />
                    <button
                      type="button"
                      class="absolute right-3 top-1/2 -translate-y-1/2 p-1 text-gray-500 hover:text-primary-600"
                      @click="mostrarSenhaCadastro = !mostrarSenhaCadastro"
                    >
                      <EyeSlashIcon v-if="mostrarSenhaCadastro" class="w-5 h-5" />
                      <EyeIcon v-else class="w-5 h-5" />
                    </button>
                  </div>
                </CardField>

                <CardField label="Confirmar senha" for-id="senha2">
                  <input
                    id="senha2"
                    v-model="formCadastro.senhaConfirmacao"
                    type="password"
                    required
                    class="input"
                    :class="{ 'input-error': senhasNaoConferem }"
                    placeholder="Repita a senha"
                    autocomplete="new-password"
                  />
                  <p v-if="senhasNaoConferem" class="text-xs text-danger mt-1 font-medium">As senhas não conferem</p>
                </CardField>
              </section>

              <section class="rounded-card border border-gray-100 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/30 p-4 space-y-3">
                <h3 class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 flex items-center gap-2">
                  <span class="w-6 h-6 rounded-full bg-primary-600 text-white text-xs flex items-center justify-center high-contrast:bg-yellow-300 high-contrast:text-black">2</span>
                  Endereço residencial
                </h3>
                <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white leading-relaxed">
                  Digite os 8 dígitos do CEP — o endereço é buscado automaticamente. Se preferir, use o botão
                  <strong class="font-semibold">Buscar</strong>.
                </p>

                <CardField label="CEP" for-id="cep">
                  <div class="flex gap-2">
                    <div class="relative flex-1 min-w-0">
                      <MapPinIcon class="field-icon" />
                      <input
                        id="cep"
                        v-model="formCadastro.cep"
                        type="text"
                        required
                        inputmode="numeric"
                        autocomplete="postal-code"
                        class="input pl-11 pr-3"
                        :class="{ 'input-error': cepErro }"
                        placeholder="00000-000"
                        maxlength="9"
                        :disabled="buscandoCep"
                        :aria-busy="buscandoCep"
                        :aria-describedby="cepAjudaId"
                        @input="handleCepInput"
                        @blur="() => buscarEnderecoPorCep()"
                      />
                    </div>
                    <button
                      type="button"
                      class="btn-secondary shrink-0 px-3 sm:px-4"
                      :disabled="buscandoCep || cepIncompleto"
                      :title="cepIncompleto ? 'Digite o CEP completo' : 'Buscar endereço pelo CEP'"
                      @click="() => buscarEnderecoPorCep()"
                    >
                      <MagnifyingGlassIcon v-if="!buscandoCep" class="w-5 h-5" />
                      <span v-else class="inline-block w-5 h-5 border-2 border-primary-600 border-t-transparent rounded-full animate-spin" />
                      <span class="sr-only">Buscar CEP</span>
                    </button>
                  </div>
                  <p :id="cepAjudaId" class="text-xs mt-1.5" :class="cepStatusClasse">
                    {{ cepStatusTexto }}
                  </p>
                </CardField>

                <div
                  v-if="!enderecoEncontrado && cepCompleto && !buscandoCep && !cepErro"
                  class="rounded-card border border-dashed border-gray-300 dark:border-gray-600 p-3 text-xs text-gray-500 dark:text-gray-400 text-center"
                >
                  O logradouro, bairro e cidade aparecerão aqui após a busca do CEP.
                </div>

                <div v-if="enderecoEncontrado" class="space-y-3 animate-slide-up">
                  <input v-model="formCadastro.endereco.logradouro" readonly class="input bg-gray-50 dark:bg-gray-900" placeholder="Logradouro" />
                  <div class="grid grid-cols-2 gap-3">
                    <div class="space-y-1">
                      <input
                        id="numero-endereco"
                        v-model="formCadastro.endereco.numero"
                        required
                        inputmode="numeric"
                        class="input"
                        :class="{ 'input-error': tentouCadastrar && !formCadastro.endereco.numero?.trim() }"
                        placeholder="Número *"
                        @blur="atualizarGeocoding"
                      />
                      <p class="text-[11px] text-gray-500 dark:text-gray-400">
                        Obrigatório para concluir o cadastro.
                      </p>
                    </div>
                    <input v-model="formCadastro.endereco.complemento" class="input" placeholder="Complemento" />
                  </div>
                  <div class="grid grid-cols-3 gap-2">
                    <input v-model="formCadastro.endereco.bairro" readonly class="input text-sm bg-gray-50 dark:bg-gray-900" />
                    <input v-model="formCadastro.endereco.cidade" readonly class="input text-sm bg-gray-50 dark:bg-gray-900" />
                    <input v-model="formCadastro.endereco.estado" readonly class="input text-sm bg-gray-50 dark:bg-gray-900" />
                  </div>
                  <div
                    v-if="formCadastro.endereco.coordenadas"
                    class="alert-success text-sm"
                  >
                    <MapPinIcon class="w-5 h-5 flex-shrink-0" />
                    <div>
                      <strong>Localização no mapa</strong>
                      <p class="text-xs opacity-80 mt-0.5">
                        {{
                          formCadastro.endereco.coordenadas.precisao === 'cidade'
                            ? 'Aproximada pelo bairro/cidade'
                            : 'Atualizada com o número informado'
                        }}
                      </p>
                    </div>
                  </div>
                  <p v-else-if="geocodificando" class="text-xs text-gray-600 dark:text-gray-400 flex items-center gap-2">
                    <span class="inline-block w-3 h-3 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                    Ajustando localização no mapa…
                  </p>
                </div>
              </section>

              <div
                class="sticky bottom-0 -mx-1 px-1 pt-2 pb-1 space-y-2 bg-white dark:bg-gray-800 high-contrast:bg-black border-t border-gray-100 dark:border-gray-700 high-contrast:border-yellow-300"
              >
                <p
                  v-if="dicaCadastro"
                  class="text-xs font-medium text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950/50 rounded-card px-3 py-2"
                  role="status"
                >
                  {{ dicaCadastro }}
                </p>
                <button
                  type="submit"
                  :disabled="authStore.loading || buscandoCep"
                  class="w-full btn-success"
                >
                  <UserPlusIcon class="w-5 h-5" />
                  <span v-if="authStore.loading">Cadastrando...</span>
                  <span v-else-if="buscandoCep">Buscando endereço...</span>
                  <span v-else>Cadastrar e entrar</span>
                </button>
              </div>
            </form>

            <button
              type="button"
              class="w-full btn-ghost text-sm"
              @click="fecharModoPadrao"
            >
              ← Outras formas de acesso
            </button>
          </div>
        </transition>

        <div class="mt-6 pt-6 border-t-2 border-gray-200 dark:border-gray-700 high-contrast:border-gray-600">
          <p class="text-xs text-center text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
            Ao continuar, você concorda com nossos<br>
            <a href="#" class="text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 hover:underline font-medium">Termos de Uso</a>
            e
            <a href="#" class="text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 hover:underline font-medium">Política de Privacidade</a>
          </p>
        </div>
      </div>

      <p class="mt-6 text-center text-sm text-white/80">
        Servidor municipal?
        <router-link to="/backoffice/login" class="text-cyan-300 hover:text-cyan-200 font-semibold underline-offset-2 hover:underline">
          Acesse o Backoffice
        </router-link>
      </p>

      <div class="mt-2 text-center text-sm text-white/70 high-contrast:text-gray-400 high-contrast:font-bold">
        {{ BRAND.name }} — {{ BRAND.description }}
      </div>
    </div>

    <div v-if="authStore.loading" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300 rounded-card p-8 flex flex-col items-center gap-4 animate-scale-in shadow-float">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent"></div>
        <p class="text-gray-900 dark:text-white high-contrast:text-yellow-300 high-contrast:font-bold font-semibold">Autenticando...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, defineComponent, h, watch, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { cpfValido, normalizarCpf } from '@/utils/cpf'
import { BRAND } from '@/constants/brand'
import { useAuthStore } from '@/stores/auth'
import { useCepLookup } from '@/composables/useCepLookup'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import {
  ArrowRightOnRectangleIcon,
  BuildingOffice2Icon,
  CheckBadgeIcon,
  ExclamationCircleIcon,
  EyeIcon,
  EyeSlashIcon,
  FingerPrintIcon,
  IdentificationIcon,
  LockClosedIcon,
  MagnifyingGlassIcon,
  MapPinIcon,
  UserPlusIcon
} from '@heroicons/vue/24/outline'

const CardField = defineComponent({
  name: 'CardField',
  props: {
    label: { type: String, required: true },
    forId: { type: String, default: null }
  },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'space-y-1.5' }, [
        h(
          'label',
          {
            for: props.forId,
            class:
              'block text-sm font-semibold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 high-contrast:font-bold'
          },
          props.label
        ),
        slots.default?.()
      ])
  }
})

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { buscarCepComGeocoding, formatarCep } = useCepLookup()

const modoPadrao = ref(false)
const abaPadrao = ref('login')
const buscandoCep = ref(false)
const geocodificando = ref(false)
const enderecoEncontrado = ref(false)
const cepErro = ref('')
const tentouCadastrar = ref(false)
const dicaCadastro = ref('')
const cepAjudaId = 'cep-ajuda-cadastro'
let cepAutoBuscaTimer = null
let numeroGeoTimer = null
let ultimoCepBuscado = ''
const mostrarSenhaLogin = ref(false)
const mostrarSenhaCadastro = ref(false)

const formLogin = ref({ cpf: '', senha: '' })

const cpfCadastroMsg = ref('')
const cpfCadastroIndisponivel = ref(false)
const verificandoCpf = ref(false)

const recuperarEnviado = ref(null)
const formRecuperar = ref({ cpf: '', canal: 'email' })
const formRedefinir = ref({ token: '', novaSenha: '', confirmacao: '' })

const formCadastro = ref({
  nome: '',
  cpf: '',
  email: '',
  senha: '',
  senhaConfirmacao: '',
  telefone: '',
  cep: '',
  endereco: {
    cep: '',
    logradouro: '',
    numero: '',
    complemento: '',
    bairro: '',
    cidade: '',
    estado: '',
    coordenadas: null
  }
})

const cepCompleto = computed(() => formCadastro.value.cep.replace(/\D/g, '').length === 8)
const cepIncompleto = computed(() => !cepCompleto.value)

const cepStatusTexto = computed(() => {
  if (buscandoCep.value) return 'Buscando endereço…'
  if (cepErro.value) return cepErro.value
  if (enderecoEncontrado.value) return 'Endereço encontrado. Confira os dados abaixo.'
  const faltam = 8 - formCadastro.value.cep.replace(/\D/g, '').length
  if (faltam > 0 && faltam < 8) return `Faltam ${faltam} dígito${faltam > 1 ? 's' : ''} do CEP.`
  if (cepCompleto.value) return 'CEP completo — localizando endereço…'
  return 'Somente números, com ou sem hífen.'
})

const cepStatusClasse = computed(() => {
  if (cepErro.value) return 'text-danger font-medium'
  if (enderecoEncontrado.value) return 'text-green-700 dark:text-green-400'
  if (buscandoCep.value || cepCompleto.value) return 'text-primary-700 dark:text-primary-300'
  return 'text-gray-500 dark:text-gray-400'
})

const senhasNaoConferem = computed(
  () =>
    formCadastro.value.senhaConfirmacao.length > 0 &&
    formCadastro.value.senha !== formCadastro.value.senhaConfirmacao
)

const cpfCadastroInvalido = computed(() => {
  const digits = normalizarCpf(formCadastro.value.cpf)
  if (digits.length < 11) return false
  return !cpfValido(formCadastro.value.cpf)
})

const cpfLoginInvalido = computed(() => {
  const digits = normalizarCpf(formLogin.value.cpf)
  if (digits.length < 11) return false
  return !cpfValido(formLogin.value.cpf)
})

const cpfRecuperarInvalido = computed(() => {
  const digits = normalizarCpf(formRecuperar.value.cpf)
  if (digits.length < 11) return false
  return !cpfValido(formRecuperar.value.cpf)
})

const senhaRecuperarNaoConfere = computed(
  () =>
    formRedefinir.value.confirmacao.length > 0 &&
    formRedefinir.value.novaSenha !== formRedefinir.value.confirmacao
)

function validarPreCadastro() {
  dicaCadastro.value = ''
  if (!cpfValido(formCadastro.value.cpf)) {
    dicaCadastro.value = 'Informe um CPF válido na etapa 1.'
    return false
  }
  if (cpfCadastroIndisponivel.value) {
    dicaCadastro.value = 'Este CPF já possui cadastro. Use Entrar ou Recuperar senha.'
    return false
  }
  if (!cepCompleto.value) {
    dicaCadastro.value = 'Informe o CEP completo na etapa 2.'
    return false
  }
  if (!enderecoEncontrado.value) {
    dicaCadastro.value = 'Aguarde a busca do CEP ou toque em Buscar ao lado do campo.'
    return false
  }
  if (!formCadastro.value.endereco.numero?.trim()) {
    dicaCadastro.value = 'Informe o número do imóvel (casa, apartamento, lote).'
    void nextTick(() => document.getElementById('numero-endereco')?.focus())
    return false
  }
  if (formCadastro.value.senha.length < 8) {
    dicaCadastro.value = 'A senha deve ter pelo menos 8 caracteres.'
    return false
  }
  if (senhasNaoConferem.value) {
    dicaCadastro.value = 'As senhas informadas não conferem.'
    return false
  }
  return true
}

onMounted(() => {
  const token = route.query.token
  if (token) {
    modoPadrao.value = true
    abaPadrao.value = 'recuperar'
    formRedefinir.value.token = String(token)
  }
})

function abrirModoPadrao(aba = 'login') {
  authStore.error = null
  abaPadrao.value = aba
  modoPadrao.value = true
}

function fecharModoPadrao() {
  modoPadrao.value = false
  authStore.error = null
  formLogin.value = { cpf: '', senha: '' }
  resetFormCadastro()
}

watch(abaPadrao, () => {
  authStore.error = null
  if (abaPadrao.value !== 'cadastro') {
    cpfCadastroMsg.value = ''
    cpfCadastroIndisponivel.value = false
  }
  if (abaPadrao.value !== 'recuperar') {
    recuperarEnviado.value = null
  }
})

function resetFormCadastro() {
  formCadastro.value = {
    nome: '',
    cpf: '',
    email: '',
    senha: '',
    senhaConfirmacao: '',
    telefone: '',
    cep: '',
    endereco: {
      cep: '',
      logradouro: '',
      numero: '',
      complemento: '',
      bairro: '',
      cidade: '',
      estado: '',
      coordenadas: null
    }
  }
  enderecoEncontrado.value = false
  cpfCadastroMsg.value = ''
  cpfCadastroIndisponivel.value = false
  cepErro.value = ''
  dicaCadastro.value = ''
  tentouCadastrar.value = false
  ultimoCepBuscado = ''
  clearTimeout(cepAutoBuscaTimer)
  clearTimeout(numeroGeoTimer)
}

watch(
  () => formCadastro.value.cep,
  (cep) => {
    const limpo = cep.replace(/\D/g, '')
    if (limpo.length !== 8) return
    clearTimeout(cepAutoBuscaTimer)
    cepAutoBuscaTimer = setTimeout(() => {
      void buscarEnderecoPorCep({ automatico: true })
    }, 350)
  }
)

watch(
  () => formCadastro.value.endereco.numero,
  (numero) => {
    if (!enderecoEncontrado.value || !numero?.trim()) return
    clearTimeout(numeroGeoTimer)
    numeroGeoTimer = setTimeout(() => {
      void atualizarGeocoding()
    }, 700)
  }
)

function rotuloCanal(canal) {
  if (canal === 'sms') return 'SMS'
  if (canal === 'whatsapp') return 'WhatsApp'
  return 'E-mail'
}

function irParaLoginComCpf(origem) {
  authStore.error = null
  abaPadrao.value = 'login'
  const cpf = origem === 'cadastro' ? formCadastro.value.cpf : formRecuperar.value.cpf
  if (cpf) formLogin.value.cpf = cpf
}

function abrirRecuperarSenha() {
  authStore.error = null
  recuperarEnviado.value = null
  formRecuperar.value.cpf = formLogin.value.cpf || ''
  abaPadrao.value = 'recuperar'
}

function abrirRecuperarDesdeCadastro() {
  formRecuperar.value.cpf = formCadastro.value.cpf
  abrirRecuperarSenha()
}

async function validarCpfCadastro() {
  const { cpf } = formCadastro.value
  const digits = normalizarCpf(cpf)
  if (digits.length < 11) {
    cpfCadastroMsg.value = ''
    cpfCadastroIndisponivel.value = false
    return
  }
  if (!cpfValido(cpf)) {
    cpfCadastroMsg.value = 'CPF inválido. Confira os números digitados.'
    cpfCadastroIndisponivel.value = false
    return
  }
  verificandoCpf.value = true
  try {
    const resultado = await authStore.verificarCpf(cpf)
    cpfCadastroIndisponivel.value = Boolean(resultado.ja_cadastrado)
    cpfCadastroMsg.value = resultado.mensagem || ''
  } finally {
    verificandoCpf.value = false
  }
}

async function redirecionarAposLogin() {
  await authStore.refreshPerfil()
  if (authStore.isBackoffice) {
    router.push('/backoffice/mesa-trabalho')
  } else {
    router.push('/app/dashboard')
  }
}

async function handleGovBrLogin() {
  const result = await authStore.loginComGovBr()
  if (result.success) await redirecionarAposLogin()
}

async function handleSsoLogin() {
  const result = await authStore.loginComSsoMunicipal()
  if (result.success) await redirecionarAposLogin()
}

async function handleLoginPadrao() {
  authStore.error = null
  const result = await authStore.login(formLogin.value.cpf, formLogin.value.senha)
  if (result.success) await redirecionarAposLogin()
}

async function handleCadastroPadrao() {
  authStore.error = null
  tentouCadastrar.value = true

  if (cepCompleto.value && !enderecoEncontrado.value) {
    await buscarEnderecoPorCep({ automatico: true })
  }
  if (enderecoEncontrado.value && formCadastro.value.endereco.numero?.trim()) {
    await atualizarGeocoding()
  }

  if (!validarPreCadastro()) {
    return
  }

  formCadastro.value.endereco.cep = formCadastro.value.cep

  const result = await authStore.loginPadrao(formCadastro.value)
  if (result.success) {
    await redirecionarAposLogin()
    return
  }
  if (result.code === 'CPF_ALREADY_REGISTERED') {
    cpfCadastroIndisponivel.value = true
    cpfCadastroMsg.value = result.error
  }
}

async function handleSolicitarRecuperacao() {
  authStore.error = null
  if (!cpfValido(formRecuperar.value.cpf)) {
    authStore.error = 'Informe um CPF válido.'
    return
  }
  const result = await authStore.solicitarRecuperacaoSenha(
    formRecuperar.value.cpf,
    formRecuperar.value.canal
  )
  if (result.success) recuperarEnviado.value = result.data
}

async function handleRedefinirSenha() {
  if (senhaRecuperarNaoConfere.value) return
  const result = await authStore.redefinirSenhaRecuperacao(
    formRedefinir.value.token.trim(),
    formRedefinir.value.novaSenha
  )
  if (result.success) {
    authStore.error = null
    recuperarEnviado.value = null
    formRedefinir.value = { token: '', novaSenha: '', confirmacao: '' }
    abaPadrao.value = 'login'
    router.replace({ path: '/app/login', query: {} })
  }
}

function aplicarMascaraCpf(target, setter) {
  let value = target.value.replace(/\D/g, '')
  if (value.length <= 11) {
    value = value.replace(/(\d{3})(\d)/, '$1.$2')
    value = value.replace(/(\d{3})(\d)/, '$1.$2')
    value = value.replace(/(\d{3})(\d{1,2})$/, '$1-$2')
    setter(value)
  }
}

function formatarCPFLogin(event) {
  aplicarMascaraCpf(event.target, (v) => {
    formLogin.value.cpf = v
  })
}

function formatarCPFCadastro(event) {
  aplicarMascaraCpf(event.target, (v) => {
    formCadastro.value.cpf = v
    cpfCadastroIndisponivel.value = false
    if (normalizarCpf(v).length < 11) cpfCadastroMsg.value = ''
  })
}

function formatarCPFRecuperar(event) {
  aplicarMascaraCpf(event.target, (v) => {
    formRecuperar.value.cpf = v
  })
}

function formatarTelefone(event) {
  let value = event.target.value.replace(/\D/g, '')
  if (value.length <= 11) {
    value = value.replace(/(\d{2})(\d)/, '($1) $2')
    value = value.replace(/(\d{5})(\d)/, '$1-$2')
    formCadastro.value.telefone = value
  }
}

function handleCepInput(event) {
  const formatado = formatarCep(event.target.value)
  formCadastro.value.cep = formatado
  const limpo = formatado.replace(/\D/g, '')
  if (limpo.length < 8) {
    enderecoEncontrado.value = false
    cepErro.value = ''
    if (ultimoCepBuscado && limpo !== ultimoCepBuscado) {
      ultimoCepBuscado = ''
    }
  }
}

/**
 * @returns {Promise<boolean>} se o endereço ficou disponível para o cadastro
 */
async function buscarEnderecoPorCep({ automatico = false } = {}) {
  const cepLimpo = formCadastro.value.cep.replace(/\D/g, '')
  if (cepLimpo.length !== 8) {
    if (!automatico) {
      cepErro.value = 'Digite o CEP completo (8 dígitos).'
    }
    return false
  }
  if (buscandoCep.value) return enderecoEncontrado.value
  if (ultimoCepBuscado === cepLimpo && enderecoEncontrado.value) return true

  buscandoCep.value = true
  cepErro.value = ''
  try {
    const result = await buscarCepComGeocoding(
      formCadastro.value.cep,
      formCadastro.value.endereco.numero || ''
    )
    if (result.success) {
      formCadastro.value.endereco = {
        ...result.endereco,
        cep: result.endereco.cep || formCadastro.value.cep,
        numero: formCadastro.value.endereco.numero || '',
        complemento: formCadastro.value.endereco.complemento || '',
        coordenadas: result.coordenadas
      }
      enderecoEncontrado.value = true
      ultimoCepBuscado = cepLimpo
      dicaCadastro.value = ''
      return true
    }
    enderecoEncontrado.value = false
    cepErro.value = result.error || 'CEP não encontrado. Verifique e tente novamente.'
    return false
  } catch {
    enderecoEncontrado.value = false
    cepErro.value = 'Não foi possível buscar o CEP. Verifique sua conexão.'
    return false
  } finally {
    buscandoCep.value = false
  }
}

async function atualizarGeocoding() {
  if (!enderecoEncontrado.value || !formCadastro.value.endereco.numero?.trim()) return
  geocodificando.value = true
  try {
    const result = await buscarCepComGeocoding(
      formCadastro.value.cep,
      formCadastro.value.endereco.numero
    )
    if (result.success && result.coordenadas) {
      formCadastro.value.endereco.coordenadas = result.coordenadas
    }
  } finally {
    geocodificando.value = false
  }
}
</script>

<style scoped>
.field-icon {
  @apply absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 dark:text-gray-500 pointer-events-none;
}

.slide-fade-enter-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-fade-leave-active {
  transition: all 0.3s cubic-bezier(1, 0.5, 0.8, 1);
}

.slide-fade-enter-from {
  transform: translateY(-12px);
  opacity: 0;
}

.slide-fade-leave-to {
  transform: translateY(8px);
  opacity: 0;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-gray-300 dark:bg-gray-600 rounded-full;
}
</style>
