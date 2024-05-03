function selectAllDevices() {
    const checkboxSelectAll = document.getElementById('cbx-select-all')
    const checkboxesSingleItems = document.querySelectorAll('#cbx-single-item')

    checkboxesSingleItems.forEach((singleCheckbox) => {
        if (checkboxSelectAll.checked) {
            singleCheckbox.checked = true
        } else {
            singleCheckbox.checked = false
        }
    })

    markSelectedItem()
}

function markSelectedItem() {
    const singleSelect = document.querySelectorAll('#cbx-single-item')
    const selectAll = document.querySelectorAll('#cbx-select-all')

    singleSelect.forEach( input => {
        if (selectAll.checked || input.checked) {
            input.parentElement.parentElement.style.color = 'rgb(64, 76, 87)'
            input.parentElement.parentElement.style.background = 'rgb(222, 222, 222)'
        } else {
            input.parentElement.parentElement.style.color = 'black'
            input.parentElement.parentElement.style.background = 'white'
        }
    })
}

async function searchOntsViaSsh(operationMode) {
    loadingAnimation(true)
    const baseUrl = "http://10.0.30.252:8000" + (operationMode == 'generator' ? '/generator' : '/attenuator')
    const loadingText = document.getElementById('loader-message')
    const pon = document.getElementById('pon').textContent
    const host = document.getElementById('host').textContent
    const socket = new WebSocket('ws://10.0.30.252:5678/get-onts')
    const tabId = getIdentificator()
    const onts = []
    let total_number_onts = 0
    let controllerPercentage = 0

    socket.onopen = () => {
        socket.send(JSON.stringify({
            pon, 
            host, 
            tab_id: tabId
        }))
        console.log('Sessão com o servidor Websocket iniciada')
    }

    socket.onmessage = (event) => {
        const currentMessage = JSON.parse(event.data)

        if (currentMessage.total_number_onts){
            total_number_onts = currentMessage.total_number_onts
            loadingText.textContent = `Carregando dados dos dispositivos - 0%`

        } else if (currentMessage.id) {
            controllerPercentage+=1
            let percentage = Math.trunc((100 * controllerPercentage) / total_number_onts)
            loadingText.textContent = `Carregando dados dos dispositivos  - ${percentage}%`
            onts.push(currentMessage)

        } else if (currentMessage.message == "No ont were found") {
            socket.close()
            alert('Não existem dispositivos na localização informada! Vamos te redirecionar para a homepage.')
            return window.location =  `${baseUrl}/home`
        }
    }

    socket.onclose = () => {
        console.log('Sessão com o servidor Websocket finalizada')
        return window.location = `${baseUrl}/render_onts_table?tab_id=${tabId}`
    }
}