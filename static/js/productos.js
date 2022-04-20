function ajax_info() {
    $.ajax({
        url: "/productos",
        type: "GET",
        success: (response) => create_table(response),
    });
    create_table(response)
}

const create_table = (response) => {
    let body = document.getElementsByTagName("body")[0];
    let tabla = document.getElementsByTagName("table")[0];
    let tblBody = document.createElement("tbody");
    console.log(response.data)
    console.log("holi")

    for (let i = 0; i < 3; i++) {
        let hilera = document.createElement("tr");
        for (let j = 0; j < 3; j++) {
        let celda = document.createElement("td");
        let textoCelda = document.createTextNode("celda en la hilera "+(i+1)+", columna "+(j+1));
        celda.appendChild(textoCelda);
        hilera.appendChild(celda);
        }
        tblBody.appendChild(hilera);
    }
    tabla.appendChild(tblBody);
    body.appendChild(tabla);
};

document.addEventListener('DOMContentLoaded', ajax_info);