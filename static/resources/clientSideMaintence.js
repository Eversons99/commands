async function getBoardsHost(){
    const host = document.getElementById('select-olt-source').value
    let hostSlots = await fetch(`https://nmt.nmultifibra.com.br/files/hosts?olt=${host}`)
    hostSlots = await hostSlots.json()

    if (hostSlots.message == 'Host not Found'){
        return alert(`Ocorreu um erro aos buscar as informações da ${host} no NMT`)
    }

    fillElementsOptions(hostSlots)
    setIdentificator()
}

function fillElementsOptions(slots){
    const slotSelectElement = document.getElementById('select-slot-source')
    const portSelectElement = document.getElementById('select-port-source')
    let counterPorts = 0

    slots.forEach(slot => {
        const optionPortElement = document.createElement('option')
        const currentPortValue = slot.split('/')[1]
        optionPortElement.textContent = currentPortValue
        slotSelectElement.append(optionPortElement)
    })

    while(counterPorts < 16){
        const optionPortElement = document.createElement('option')
        optionPortElement.textContent = counterPorts
        portSelectElement.append(optionPortElement)
        counterPorts++
    }
}

function setIdentificator(){
    const identificatorTab = Date.now()
    window.sessionStorage.setItem('tabId', identificatorTab)
}

async function searchOnts(){
    const sourceHost = document.getElementById('select-olt-source').value
    const sourceSlot = document.getElementById('select-slot-source').value
    const sourcePort = document.getElementById('select-port-source').value
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const sourcePonLocation = `0/${sourceSlot}/${sourcePort}`
    
    if(!sourceHost || !sourceSlot || !sourcePort) return alert("ATENÇÃO: Preencha o F/S/P!")

    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId: getIdentificator(),
            sourceHost,
            sourceSlot,
            sourcePort,
            sourcePonLocation
        })
    }

    const ontsRequest = await fetch('http://localhost:8000/generator/search_onts', requestOptions)
    const responsOfontsRequest = await ontsRequest.json()
    
    if(responsOfontsRequest.error == true){
        const message = responsOfontsRequest.error
        return window.location = `https://localhost:8000/generator/error_page?message=${message}`
    }
}

function getIdentificator(){
    const identificatorTab = window.sessionStorage.getItem('tabId')
    return identificatorTab
}
