

async function searchOntsUnauthorized(params) {
    setIdentificator()
    loadingAnimation(true);
    const sourceHost = document.getElementById('select-olt').value
    const sourceSlot = document.getElementById('select-slot').value
    const sourcePort = document.getElementById('select-port').value
    const tabId = getIdentificator()

    if (!sourceHost || !sourceSlot || !sourcePort) {
        loadingAnimation(false)
        return alert("ATENÇÃO: Preencha o F/S/P!")
    } 

    // Pegar o FSP
    // Me conectar via websocket
    // Enviar FSP para websocket server começar a buscar as ONTs não autorizadas
    // renderizar ONTs não autorizadas na tela para o usuário selecionar
}