/**
 * Composable para gerenciar dialogs nativos HTML5
 * Substitui window.alert, window.confirm e modais genéricos
 */

// Singleton para armazenar a referência do AppDialog
let dialogInstance = null

export function useDialog() {
  
  /**
   * Registra a instância do AppDialog (chamado pelo App.vue)
   */
  function registerDialog(instance) {
    dialogInstance = instance
  }

  /**
   * Mostra um dialog de informação
   * @param {string} message - Mensagem a ser exibida
   * @param {string} title - Título opcional
   * @param {Object} options - Opções adicionais
   */
  function info(message, title = 'Informação', options = {}) {
    if (!dialogInstance) {
      console.warn('Dialog não registrado. Usando fallback.')
      window.alert(message)
      return
    }

    dialogInstance.show({
      type: 'info',
      title,
      message,
      confirmText: options.confirmText || 'OK',
      onConfirm: options.onConfirm
    })
  }

  /**
   * Mostra um dialog de sucesso
   * @param {string} message - Mensagem de sucesso
   * @param {string} title - Título opcional
   * @param {Object} options - Opções adicionais
   */
  function success(message, title = 'Sucesso', options = {}) {
    if (!dialogInstance) {
      console.warn('Dialog não registrado. Usando fallback.')
      window.alert(message)
      return
    }

    dialogInstance.show({
      type: 'success',
      title,
      message,
      confirmText: options.confirmText || 'OK',
      onConfirm: options.onConfirm
    })
  }

  /**
   * Mostra um dialog de erro
   * @param {string} message - Mensagem de erro
   * @param {string} title - Título opcional
   * @param {Object} options - Opções adicionais
   */
  function error(message, title = 'Erro', options = {}) {
    if (!dialogInstance) {
      console.warn('Dialog não registrado. Usando fallback.')
      window.alert(message)
      return
    }

    dialogInstance.show({
      type: 'error',
      title,
      message,
      confirmText: options.confirmText || 'OK',
      onConfirm: options.onConfirm
    })
  }

  /**
   * Mostra um dialog de aviso
   * @param {string} message - Mensagem de aviso
   * @param {string} title - Título opcional
   * @param {Object} options - Opções adicionais
   */
  function warning(message, title = 'Atenção', options = {}) {
    if (!dialogInstance) {
      console.warn('Dialog não registrado. Usando fallback.')
      window.alert(message)
      return
    }

    dialogInstance.show({
      type: 'warning',
      title,
      message,
      confirmText: options.confirmText || 'OK',
      onConfirm: options.onConfirm
    })
  }

  /**
   * Mostra um dialog de confirmação
   * @param {string} message - Mensagem de confirmação
   * @param {string} title - Título opcional
   * @param {Object} options - Opções adicionais
   * @returns {Promise<boolean>} - Retorna true se confirmado, false se cancelado
   */
  function confirm(message, title = 'Confirmação', options = {}) {
    if (!dialogInstance) {
      console.warn('Dialog não registrado. Usando fallback.')
      return Promise.resolve(window.confirm(message))
    }

    return new Promise((resolve) => {
      dialogInstance.show({
        type: 'confirm',
        title,
        message,
        confirmText: options.confirmText || 'Confirmar',
        cancelText: options.cancelText || 'Cancelar',
        onConfirm: () => resolve(true),
        onCancel: () => resolve(false)
      })
    })
  }

  /**
   * Substituto direto para window.alert
   * @param {string} message - Mensagem
   */
  function alert(message) {
    info(message, 'Aviso')
  }

  return {
    // Registro
    registerDialog,
    
    // Métodos principais
    info,
    success,
    error,
    warning,
    confirm,
    
    // Alias para compatibilidade
    alert
  }
}
