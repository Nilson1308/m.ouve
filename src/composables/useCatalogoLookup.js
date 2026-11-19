import { ref } from 'vue'
import { catalogoLookupService } from '@/services/api'
import { LOOKUP_DATASOURCE_UNIDADES } from '@/constants/fluxoTramitacao'

const cacheUnidades = ref(null)
let carregamentoUnidades = null

export function useCatalogoLookup() {
  const unidades = ref([])
  const loading = ref(false)
  const erro = ref(null)

  async function carregarUnidades({ busca = '', force = false } = {}) {
    if (!force && !busca && cacheUnidades.value?.length) {
      unidades.value = cacheUnidades.value
      return unidades.value
    }

    if (carregamentoUnidades && !busca && !force) {
      await carregamentoUnidades
      unidades.value = cacheUnidades.value || []
      return unidades.value
    }

    loading.value = true
    erro.value = null

    const tarefa = catalogoLookupService
      .listarUnidades({ busca })
      .then((items) => {
        if (!busca) {
          cacheUnidades.value = items
        }
        unidades.value = items
        return items
      })
      .catch((err) => {
        erro.value = err?.message || 'Não foi possível carregar as unidades.'
        unidades.value = []
        throw err
      })
      .finally(() => {
        loading.value = false
        if (carregamentoUnidades === tarefa) {
          carregamentoUnidades = null
        }
      })

    if (!busca && !force) {
      carregamentoUnidades = tarefa
    }

    return tarefa
  }

  function isLookupUnidades(prop = {}) {
    return (
      prop['x-ouvia-datasource'] === LOOKUP_DATASOURCE_UNIDADES ||
      prop['x-ouvia-tipo-campo'] === 'lookup'
    )
  }

  return {
    unidades,
    loading,
    erro,
    carregarUnidades,
    isLookupUnidades
  }
}