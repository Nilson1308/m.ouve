import { ref } from 'vue'
import { catalogoLookupService } from '@/services/api'
import {
  LOOKUP_DATASOURCE_EQUIPAMENTOS,
  LOOKUP_DATASOURCE_UNIDADES
} from '@/constants/fluxoTramitacao'

const cacheUnidades = ref(null)
let carregamentoUnidades = null
const cacheEquipamentos = ref(null)
let carregamentoEquipamentos = null

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

  const equipamentos = ref([])

  async function carregarEquipamentos({ busca = '', filtro = {}, force = false } = {}) {
    const cacheKey = JSON.stringify(filtro)
    if (!force && !busca && cacheEquipamentos.value?.key === cacheKey) {
      equipamentos.value = cacheEquipamentos.value.items
      return equipamentos.value
    }

    const params = { ...filtro, ...(busca ? { busca } : {}) }
    loading.value = true
    erro.value = null
    const tarefa = catalogoLookupService
      .listarEquipamentos(params)
      .then((items) => {
        if (!busca) {
          cacheEquipamentos.value = { key: cacheKey, items }
        }
        equipamentos.value = items
        return items
      })
      .catch((err) => {
        erro.value = err?.message || 'Não foi possível carregar os equipamentos.'
        equipamentos.value = []
        throw err
      })
      .finally(() => {
        loading.value = false
        if (carregamentoEquipamentos === tarefa) {
          carregamentoEquipamentos = null
        }
      })

    if (!busca && !force) {
      carregamentoEquipamentos = tarefa
    }
    return tarefa
  }

  function isLookupUnidades(prop = {}) {
    return prop['x-ouvia-datasource'] === LOOKUP_DATASOURCE_UNIDADES
  }

  function isLookupEquipamentos(prop = {}) {
    return prop['x-ouvia-datasource'] === LOOKUP_DATASOURCE_EQUIPAMENTOS
  }

  return {
    unidades,
    equipamentos,
    loading,
    erro,
    carregarUnidades,
    carregarEquipamentos,
    isLookupUnidades,
    isLookupEquipamentos
  }
}