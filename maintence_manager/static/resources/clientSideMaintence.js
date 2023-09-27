async function getHost(){
    const slot = document.getElementById('select-slot-source')
    const port = document.getElementById('select-port-source')
    const olt = document.getElementById('select-olt-source').value

    let hostBoards = await fetch(`https://nmt.nmultifibra.com.br/files/hosts?olt=${olt}`)
    hostBoards = await hostBoards.json()

    if (hostBoards.length == 0 || hostBoards == undefined){
        return window.alert(`Ocorreu um erro aos buscar as informações da ${olt} no NMT`)
    }

    hostBoards.forEach(board => {
        const optionElement = document.createElement('option')
        optionElement.textContent = board.split('/')[1]
        slot.append(optionElement)
    })

    if (!slot || !port || !port) return window.alert('Preencha a OLT e o F/S/P')

}

async function getDevices(){

}