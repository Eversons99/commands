const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value

async function getNumbersToSendSms() {
    const allDevices = document.querySelectorAll('#cbx-single-item')
    const serialNumbers = []

    allDevices.forEach((device) => {
        if (device.checked) {
            const serialNumber = device.parentNode.parentNode.children[2].innerHTML
            serialNumbers.push(serialNumber)
        }
    })

    if (serialNumbers.length == 0) return alert('Selecione ao menos um dispositivo')

    const tabId = getIdentificator()

    const requestOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
            serialNumbers
        })
    }

    let getContacts = await fetch('http://10.0.30.241:8000/sms/get_contacts', requestOptions)
    getContacts = await getContacts.json()
    
    if (getContacts.error) {
        messageError =  getContacts.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/sms/render_contacts_page?tab_id=${tabId}` 
}

async function createRupture() {
    const previsao = document.getElementById('input-previsao').value
    const tipoRompimento = document.getElementById('input-tipo').value
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const tabId = getIdentificator()

    if (!previsao || !tipoRompimento) return alert("ATENÇÃO: Informe a Previsão e o tipo do rompimento!")

    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
            previsao,
            tipoRompimento
        })
    }

    const createRuptureRequest = await fetch('http://10.0.30.241:8000/sms/create_rupture', requestOptions)
    const ruptureResponse = await createRuptureRequest.json()

    if (ruptureResponse.error) {
        messageError =  ruptureResponse.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/sms/render_rupture_page?tab_id=${tabId}` 
}

async function sendSms() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value
    const tabId = getIdentificator()

    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            tabId,
        })
    }

    const sendSmsRequest = await fetch('http://10.0.30.241:8000/sms/send_sms', requestOptions)
    const smsResponse = await sendSmsRequest.json()

    if (smsResponse.error) {
        messageError =  smsResponse.message
        return window.location = `http://10.0.30.241:8000/sms/render_error_page?message=${messageError}`
    }
    return window.location = `http://10.0.30.241:8000/sms/render_sms_result_page?tab_id=${tabId}` 
}