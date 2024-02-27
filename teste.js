import fetch from "node-fetch"

async function teste() {
    const identificatorTab = Date.now()
    const requestOptions = {
        method: 'POST',
        headers: { 
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            tabId: identificatorTab,
            sourceGpon: {
                host: "OLT_CCDA_01",
                gpon: "0/1/0"
            }
        })
    }
    
    const ontsRequest = await fetch('http://10.0.30.241:8000/generator/search_onts', requestOptions)
    const responsOfontsRequest = await ontsRequest.json()
    
    console.log(responsOfontsRequest)
}

teste()
