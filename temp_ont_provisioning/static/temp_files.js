

async function searchOntsUnauthorized() {
    setIdentificator()
    loadingAnimation(true);
    const sourceHost = document.getElementById('select-olt').value
    const sourceSlot = document.getElementById('select-slot').value
    const sourcePort = document.getElementById('select-port').value

    if (!sourceHost || !sourceSlot || !sourcePort) {
        loadingAnimation(false)
        return alert("ATENÇÃO: Preencha o F/S/P!")
    } 

    const gponInfo = {
        'host': sourceHost,
        'fsp': `0/${sourceSlot}/${sourcePort}`,
        'tab_id': getIdentificator()
    }
    console.log(gponInfo)
    // Pegar o FSP -- OK
    // Me conectar via websocket
    // Enviar FSP para websocket server começar a buscar as ONTs não autorizadas
    // renderizar ONTs não autorizadas na tela para o usuário selecionar
}