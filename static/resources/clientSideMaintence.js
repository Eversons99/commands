async function getHost(){
    const slot = document.getElementById('select-slot-source').value
    const port = document.getElementById('select-port-source').value
    const olt = document.getElementById('select-olt-source').value

    //if (!slot || !port || !port) return window.alert('Preencha a OLT e o F/S/P')

    let host = await fetch(`https://nmt.nmultifibra.com.br/files/hosts?olt=${olt}`)
    console.log(host)
}

async function getDevices(){

}