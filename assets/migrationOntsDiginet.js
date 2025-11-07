

async function searchOntsUnauthorized() {
    const loadingText = document.getElementById('loader-message')
    const host = document.getElementById('select-olt').value
    const slot = document.getElementById('select-slot').value
    const port = document.getElementById('select-port').value
    let sessionStarted = false

    if (!host || !slot || !port) return alert('Por favor, selecione a OLT, slot e porta para continuar.')
    
    loadingAnimation(true)
    const socket = new WebSocket('ws://127.0.0.1:8001/get_unauthorized_onts_by_port')
    // Connect with websocket server -- OK
    // Send PON location -- OK
    // Wait and save response with unauthorized ONTs - OK
    // Send response to front-end to show in table in a new page

    try {
        socket.onopen = () => {
            socket.send(JSON.stringify({ host, slot, port }))
            sessionStarted = true
            loadingText.textContent = 'Iniciando sessão com o servidor websocket...'
        }

        socket.onmessage = async (event) => {
            const currentMessage = JSON.parse(event.data)

            if (currentMessage.status == 'failed') {
                loadingAnimation(false)
                return alert(currentMessage.message)
            }
            const snsUnauthorized = currentMessage.data
            await renderUnauthorizedOntsTable(snsUnauthorized)
        }

        socket.onclose = () => {
            loadingAnimation(false)
            if (!sessionStarted) return alert('Sessão com o servidor websocket encerrada')
        }

        socket.onerror = (event) => {
            loadingAnimation(false)
            alert(`Ocorreu um erro durante a conexão websocket. Err: ${event.message}`);
        }
    } catch (err) {
        return console.error(`WebSocket error: ${err}`)
    }
}

async function renderUnauthorizedOntsTable(snsUnauthorized) {
    if (!snsUnauthorized) return alert('A lista de equipamentos não autorizados está vazia.')

    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sns: snsUnauthorized })
    }

    await fetch('http://127.0.0.1:8000/render_unauthorized_onts_table', requestOptions)
}