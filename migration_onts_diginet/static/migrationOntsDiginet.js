
async function searchOntsUnauthorized() {
    setIdentificator()

    const host = document.getElementById('select-olt').value
    const slot = document.getElementById('select-slot').value
    const port = document.getElementById('select-port').value

    // Connect with websocket server 
    // Send PON location
    // Wait and save response with unauthorized ONTs
    // Send response to front-end to show in table in a new page

    const socket = new WebSocket('ws://127.0.0.1:8001/get_unauthorized_onts_by_port/')

}